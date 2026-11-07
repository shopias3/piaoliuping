# -*- coding: utf-8 -*-
"""认证：短信验证码（60 秒频控）+ 手机号验证码登入（未注册自动注册）。"""
import re
import random

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..activity import log_activity, refresh_user_activity
from ..api_helpers import ok
from ..config import SMS_MOCK, SMS_RESEND_SECONDS
from ..database import get_db
from ..limiter import sms_limiter, sms_store
from ..models import User
from ..security import create_token, phone_encode, phone_hash, mask_phone

router = APIRouter(prefix="/auth", tags=["auth"])
PHONE_RE = re.compile(r"^1[3-9]\d{9}$")


class SmsSendBody(BaseModel):
    phone: str


class LoginBody(BaseModel):
    phone: str
    code: str
    agreed: bool = True


def _random_nickname() -> str:
    sea_words = ["海风", "浪花", "灯塔", "星光", "海鸥", "潮汐", "贝壳", "远帆"]
    return sea_words[random.randint(0, len(sea_words) - 1)] + "捞瓶人" + str(random.randint(100, 999))


@router.post("/sms/send")
def sms_send(body: SmsSendBody):
    phone = body.phone.strip()
    if not PHONE_RE.match(phone):
        raise HTTPException(status_code=400, detail="手机号格式不正确")
    if not sms_limiter.allow("sms:" + phone, SMS_RESEND_SECONDS):
        raise HTTPException(status_code=429, detail="发送太频繁，请 60 秒后再试")
    code = sms_store.issue(phone)
    data = {}
    if SMS_MOCK:
        data["mock_code"] = code  # 演示模式直接回显验证码；生产由短信通道下发
    return ok(data, "验证码已发送" + ("（演示模式）" if SMS_MOCK else ""))


@router.post("/login")
def login(body: LoginBody, db: Session = Depends(get_db)):
    phone = body.phone.strip()
    if not PHONE_RE.match(phone):
        raise HTTPException(status_code=400, detail="手机号格式不正确")
    if not body.agreed:
        raise HTTPException(status_code=400, detail="请先阅读并同意《用户协议》与《隐私政策》")
    if not sms_store.verify(phone, body.code):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    user = db.execute(
        __import__("sqlalchemy").select(User).where(User.phone_hash == phone_hash(phone))
    ).scalar_one_or_none()
    if not user:
        user = User(
            phone_hash=phone_hash(phone), phone_enc=phone_encode(phone),
            nickname=_random_nickname(),
        )
        db.add(user)
        db.flush()
    log_activity(db, user.id, "login", 2)
    refresh_user_activity(db, user)
    db.commit()

    token = create_token(user.id)
    profile = {
        "id": user.id, "nickname": user.nickname, "phone_masked": mask_phone(phone),
        "region_id": user.region_id, "interest_tags": user.interest_tags,
        "crowd": user.crowd, "big_font": user.big_font,
        "is_new": user.interest_tags == [] and user.region_id == 0,
    }
    return ok({"token": token, "profile": profile}, "登录成功")
