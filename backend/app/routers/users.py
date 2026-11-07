# -*- coding: utf-8 -*-
"""用户：个人信息 + 活跃度 + 段位；头像上传；更新资料/地区/兴趣标签/大字模式等。"""
import os
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..activity import refresh_user_activity
from ..api_helpers import ok
from ..config import DATA_DIR, PICK_DAILY_LIMIT, THROW_DAILY_LIMIT
from ..constants import ACTION_PICK, tier_of
from ..database import get_db
from ..models import Bottle, BottleOpen, Region, User
from ..security import get_current_user

router = APIRouter(prefix="/user", tags=["user"])

AVATAR_DIR = os.path.join(DATA_DIR, "uploads", "avatars")
ALLOWED_IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
AVATAR_MAX_BYTES = 2 * 1024 * 1024   # 2MB


class UpdateMeBody(BaseModel):
    nickname: str | None = None
    region_id: int | None = None
    interest_tags: list[str] | None = None
    crowd: str | None = None
    big_font: bool | None = None
    gender: str | None = None
    birth_year: int | None = None
    age: int | None = None          # 便捷字段：传年龄自动换算出生年
    ethnicity: str | None = None    # 民族
    address: str | None = None      # 现住址（详细地址）


def _region_chain(db: Session, region_id: int):
    """返回 省/市/区 名称链与城市 id。"""
    if not region_id:
        return None
    node = db.get(Region, region_id)
    if not node:
        return None
    if node.level == 3:
        city = db.get(Region, node.parent_id)
        prov = db.get(Region, city.parent_id) if city else None
        return {"province": prov.name if prov else "", "city": city.name if city else node.name,
                "district": node.name, "city_id": city.id if city else region_id}
    if node.level == 2:
        prov = db.get(Region, node.parent_id)
        return {"province": prov.name if prov else "", "city": node.name, "district": "",
                "city_id": node.id}
    return {"province": node.name, "city": node.name, "district": "", "city_id": node.id}


@router.get("/me")
def me(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    refresh_user_activity(db, user)
    db.commit()
    today = datetime.now().date()
    # 今日投瓶数
    throw_count = 0
    for b in db.execute(select(Bottle).where(Bottle.user_id == user.id)).scalars().all():
        if b.created_at.date() == today:
            throw_count += 1
    # 今日捞瓶数
    pick_count = 0
    for o in db.execute(select(BottleOpen).where(
            BottleOpen.catcher_id == user.id, BottleOpen.action == ACTION_PICK)).scalars().all():
        if o.created_at.date() == today:
            pick_count += 1

    score = user.activity_score
    age = datetime.now().year - user.birth_year if user.birth_year else None
    data = {
        "id": user.id, "nickname": user.nickname,
        "phone_masked": "", "avatar_url": user.avatar_url,
        "gender": user.gender, "birth_year": user.birth_year, "age": age,
        "ethnicity": user.ethnicity, "address": user.address,
        "region": _region_chain(db, user.region_id),
        "interest_tags": user.interest_tags, "crowd": user.crowd,
        "big_font": user.big_font,
        "activity_score": score, "tier": tier_of(score),
        "today": {
            "throw_used": throw_count, "throw_limit": THROW_DAILY_LIMIT,
            "pick_used": pick_count, "pick_limit": PICK_DAILY_LIMIT,
        },
    }
    return ok(data)


@router.put("/me")
def update_me(body: UpdateMeBody, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if body.nickname is not None:
        nickname = body.nickname.strip()
        if not nickname:
            raise HTTPException(status_code=400, detail="昵称不能为空")
        user.nickname = nickname[:16]
    if body.region_id is not None:
        node = db.get(Region, body.region_id)
        if not node:
            raise HTTPException(status_code=400, detail="地区不存在")
        # 用户表 region_id 统一存到「市」一级（直辖市为区县级）
        user.region_id = node.id if node.level <= 2 else node.parent_id
    if body.interest_tags is not None:
        tags = [t for t in body.interest_tags if t][:5]
        if len(tags) < 3:
            raise HTTPException(status_code=400, detail="请挑选 3 个兴趣主题")
        user.interest_tags = tags
    if body.crowd is not None:
        user.crowd = body.crowd or "不限"
    if body.big_font is not None:
        user.big_font = bool(body.big_font)
    if body.gender is not None:
        user.gender = body.gender or "保密"
    if body.birth_year is not None:
        user.birth_year = int(body.birth_year or 0)
    if body.age is not None:
        # 年龄换算出生年（16-60 全龄定位）
        age = int(body.age or 0)
        if age < 16 or age > 60:
            raise HTTPException(status_code=400, detail="年龄需在 16-60 岁之间")
        user.birth_year = datetime.now().year - age
    if body.ethnicity is not None:
        user.ethnicity = (body.ethnicity or "")[:16]
    if body.address is not None:
        user.address = (body.address or "").strip()[:128]
    db.commit()
    return ok({"updated": True})


@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...), db: Session = Depends(get_db),
                        user: User = Depends(get_current_user)):
    """上传头像：注册引导/个人中心通用，覆盖同名旧头像。"""
    ext = ALLOWED_IMAGE_TYPES.get(file.content_type or "")
    if not ext:
        raise HTTPException(status_code=400, detail="仅支持 JPG / PNG / WebP 图片")
    data = await file.read()
    if len(data) > AVATAR_MAX_BYTES:
        raise HTTPException(status_code=400, detail="图片不能超过 2MB")
    if not data:
        raise HTTPException(status_code=400, detail="图片内容为空")
    os.makedirs(AVATAR_DIR, exist_ok=True)
    fname = f"avatar_{user.id}{ext}"   # 同名覆盖，旧图不残留
    with open(os.path.join(AVATAR_DIR, fname), "wb") as f:
        f.write(data)
    user.avatar_url = f"/uploads/avatars/{fname}"
    db.commit()
    return ok({"avatar_url": user.avatar_url}, "头像已更新")
