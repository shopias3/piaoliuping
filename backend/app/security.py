# -*- coding: utf-8 -*-
"""安全模块：JWT、手机号哈希/脱敏、登录态依赖。"""
import base64
import hashlib
import secrets
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, Request

from .config import PHONE_SALT, SECRET_KEY, TOKEN_EXPIRE_HOURS
from .database import get_db
from .models import User


def phone_hash(phone: str) -> str:
    """手机号哈希（用于唯一索引查找），生产环境盐请走密钥管理。"""
    return hashlib.sha256((PHONE_SALT + phone).encode("utf-8")).hexdigest()


def phone_encode(phone: str) -> str:
    """演示用可逆编码存储（生产请替换为 AES/KMS 加密）。"""
    raw = phone.encode("utf-8")
    key = hashlib.sha256(SECRET_KEY.encode()).digest()
    enc = bytes(b ^ key[i % len(key)] for i, b in enumerate(raw))
    return base64.b64encode(enc).decode("ascii")


def mask_phone(phone: str) -> str:
    return phone[:3] + "****" + phone[-4:] if len(phone) >= 7 else phone


def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),
        "jti": secrets.token_hex(8),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def _unauthorized(msg="登录已失效，请重新登录"):
    raise HTTPException(status_code=401, detail=msg)


def get_current_user(request: Request, db=Depends(get_db)) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        _unauthorized("请先登录")
    token = auth[7:].strip()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        _unauthorized("登录已过期，请重新登录")
    except jwt.PyJWTError:
        _unauthorized()
    user = db.get(User, int(payload.get("sub", 0)))
    if not user or user.status != "active":
        _unauthorized("账号不可用")
    return user
