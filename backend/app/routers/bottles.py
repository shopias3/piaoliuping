# -*- coding: utf-8 -*-
"""瓶池：投瓶 / 加权随机捞瓶 / 打开-放回-回应 / 我的瓶子。"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..activity import log_activity, refresh_user_activity, weighted_random_pick
from ..api_helpers import ok
from ..audit import machine_audit
from ..config import (
    BOTTLE_SINK_DAYS, DUP_CONTENT_HOURS, PICK_DAILY_LIMIT, THROW_DAILY_LIMIT,
)
from ..constants import (
    ACTION_BACK, ACTION_OPEN, ACTION_PICK, ACTION_REPLY, BOTTLE_TYPES,
    CROWDS, DEFAULT_BOTTLE_TYPE, STATUS_DRIFTING, STATUS_PICKED, STATUS_SUNK,
    float_weight_of,
)
from ..database import get_db
from ..models import Bottle, BottleOpen, Region, User
from ..security import get_current_user

router = APIRouter(prefix="/bottles", tags=["bottles"])


class ThrowBody(BaseModel):
    city_id: int
    target_crowd: str = "不限"
    type: int = DEFAULT_BOTTLE_TYPE
    content: str


class ActionBody(BaseModel):
    action: str            # open / back / reply
    reply_content: str = ""


class ReportBody(BaseModel):
    target_type: str = "bottle"   # bottle / user
    target_id: int
    reason: str


def _city_name(db: Session, city_id: int) -> str:
    node = db.get(Region, city_id)
    if not node:
        return "未知城市"
    if node.level == 1:
        return node.name
    parent = db.get(Region, node.parent_id)
    if parent and parent.region_type in ("直辖市", "特别行政区"):
        return parent.name
    return (parent.name if parent else "") + node.name


def _bottle_meta(db: Session, b: Bottle, with_content=False) -> dict:
    data = {
        "id": b.id, "type": b.type, "type_name": BOTTLE_TYPES.get(b.type, "漂流瓶"),
        "city_id": b.city_id, "city_name": _city_name(db, b.city_id),
        "target_crowd": b.target_crowd, "status": b.status,
        "created_at": b.created_at.strftime("%m-%d %H:%M"),
    }
    if with_content:
        data["content"] = b.content
    return data


def _today_count_throw(db: Session, user_id: int) -> int:
    start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    rows = db.execute(select(Bottle).where(Bottle.user_id == user_id)).scalars().all()
    return sum(1 for b in rows if b.created_at >= start)


def _today_count_pick(db: Session, user_id: int) -> int:
    start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    rows = db.execute(select(BottleOpen).where(
        BottleOpen.catcher_id == user_id, BottleOpen.action == ACTION_PICK)).scalars().all()
    return sum(1 for o in rows if o.created_at >= start)


def _sink_expired(db: Session):
    """沉默 7 天以上的瓶子自动沉底降权（生产由定时任务跑）。"""
    now = datetime.now()
    expired = db.execute(select(Bottle).where(
        Bottle.status == STATUS_DRIFTING, Bottle.expire_at < now)).scalars().all()
    for b in expired:
        b.status = STATUS_SUNK
        b.float_weight = max(0.3, b.float_weight * 0.6)
    if expired:
        db.flush()


@router.post("")
def throw_bottle(body: ThrowBody, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    content = (body.content or "").strip()
    audit = machine_audit(content)
    if audit["result"] != "pass":
        raise HTTPException(status_code=400, detail=audit["reason"])
    if body.type not in BOTTLE_TYPES:
        raise HTTPException(status_code=400, detail="瓶签不正确")
    if body.target_crowd not in CROWDS:
        raise HTTPException(status_code=400, detail="人群选项不正确")
    if not db.get(Region, body.city_id):
        raise HTTPException(status_code=400, detail="目标城市不存在")

    # 同一内容 24 小时内不可重复投递
    dup_start = datetime.now() - timedelta(hours=DUP_CONTENT_HOURS)
    mine = db.execute(select(Bottle).where(Bottle.user_id == user.id)).scalars().all()
    if any(b.content == content and b.created_at >= dup_start for b in mine):
        raise HTTPException(status_code=400, detail="同一心愿 24 小时内只能投递一次")

    # 每日次数上限（活跃度高的用户小幅上浮）
    limit = THROW_DAILY_LIMIT + (1 if user.activity_score > 60 else 0)
    used = _today_count_throw(db, user.id)
    if used >= limit:
        raise HTTPException(status_code=429, detail=f"今日 {limit} 次投瓶次数已用完，明天再来吧")

    refresh_user_activity(db, user)
    bottle = Bottle(
        user_id=user.id, type=body.type, city_id=body.city_id,
        target_crowd=body.target_crowd, content=content,
        status=STATUS_DRIFTING,                       # 机审通过即入池漂流（先审后显）
        float_weight=float_weight_of(user.activity_score),
        expire_at=datetime.now() + timedelta(days=BOTTLE_SINK_DAYS),
    )
    db.add(bottle)
    db.flush()
    log_activity(db, user.id, "throw", 1)
    refresh_user_activity(db, user)
    db.commit()
    data = _bottle_meta(db, bottle, with_content=True)
    data["left"] = limit - used - 1
    return ok(data, "封瓶成功，愿它漂到对岸")


@router.get("/random")
def pick_bottle(scope: str = "city", city_id: int = 0, crowd: str = "不限",
                types: str = "", db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    _sink_expired(db)
    db.commit()

    used = _today_count_pick(db, user.id)
    if used >= PICK_DAILY_LIMIT:
        raise HTTPException(status_code=429, detail=f"今日 {PICK_DAILY_LIMIT} 次捞瓶次数已用完，明天再来吧")

    # 瓶池范围：本市 / 全省 / 全国
    city_ids = []
    if scope != "nation":
        target_id = city_id or user.region_id
        node = db.get(Region, target_id) if target_id else None
        if not node:
            raise HTTPException(status_code=400, detail="请先选择常驻地区")
        if scope == "province":
            # 传入省 → 全部子城市；传入市 → 扩展到同省所有城市
            parent_id = node.id if node.level == 1 else node.parent_id
            city_ids = [c.id for c in db.execute(
                select(Region).where(Region.parent_id == parent_id)).scalars().all()]
        else:
            city_ids = [node.id]

    type_list = [int(t) for t in types.split(",") if t.strip().isdigit()]
    picked = weighted_random_pick(db, user.id, city_ids, crowd, type_list, limit=1)
    if not picked:
        return ok({"bottle": None}, "这片海面暂时没有匹配的瓶子，稍后再试试")

    b = picked[0]
    db.add(BottleOpen(bottle_id=b.id, catcher_id=user.id, action=ACTION_PICK))
    log_activity(db, user.id, "pick", 1)
    refresh_user_activity(db, user)
    db.commit()
    return ok({"bottle": _bottle_meta(db, b), "left": PICK_DAILY_LIMIT - used - 1}, "捞到瓶子啦")


@router.post("/{bottle_id}/action")
def bottle_action(bottle_id: int, body: ActionBody, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    bottle = db.get(Bottle, bottle_id)
    if not bottle or bottle.status in ("removed", "sunk"):
        raise HTTPException(status_code=404, detail="瓶子不在海面上了")

    if body.action == ACTION_OPEN:
        already = db.execute(select(BottleOpen).where(
            BottleOpen.bottle_id == bottle.id, BottleOpen.catcher_id == user.id,
            BottleOpen.action == ACTION_OPEN)).scalars().first()
        if not already:
            db.add(BottleOpen(bottle_id=bottle.id, catcher_id=user.id, action=ACTION_OPEN))
            db.commit()
        data = _bottle_meta(db, bottle, with_content=True)
        data["anti_fraud"] = "谨防诈骗：请勿向陌生人转账汇款，如遇诱导请立即举报。"
        return ok(data, "打开瓶子")

    if body.action == ACTION_BACK:
        db.add(BottleOpen(bottle_id=bottle.id, catcher_id=user.id, action=ACTION_BACK))
        if bottle.status == STATUS_PICKED:
            bottle.status = STATUS_DRIFTING  # 放回海里继续漂流
        db.commit()
        return ok(None, "已放回海里，瓶子继续漂流")

    if body.action == ACTION_REPLY:
        reply = (body.reply_content or "").strip()
        audit = machine_audit(reply)
        if audit["result"] != "pass":
            raise HTTPException(status_code=400, detail=audit["reason"] or "回应内容不合规")
        if not reply:
            raise HTTPException(status_code=400, detail="回应内容不能为空")
        db.add(BottleOpen(bottle_id=bottle.id, catcher_id=user.id,
                          action=ACTION_REPLY, reply_content=reply))
        bottle.status = STATUS_PICKED           # 已回应：被捞起
        log_activity(db, user.id, "reply", 0.75)
        refresh_user_activity(db, user)
        db.commit()
        # 生产环境此处触发 uni-push 推送提醒瓶主
        return ok(None, "回应已封好漂回给对方")

    raise HTTPException(status_code=400, detail="不支持的操作")


@router.get("/mine")
def my_bottles(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    thrown = db.execute(select(Bottle).where(Bottle.user_id == user.id)
                        .order_by(Bottle.created_at.desc()).limit(50)).scalars().all()
    my_replies = db.execute(select(BottleOpen).where(
        BottleOpen.catcher_id == user.id, BottleOpen.action == ACTION_REPLY)).scalars().all()
    reply_map = {}
    for r in my_replies:
        reply_map.setdefault(r.bottle_id, r.reply_content)
    picked_ids = list(dict.fromkeys([r.bottle_id for r in my_replies]))

    return ok({
        "thrown": [{
            **_bottle_meta(db, b, with_content=True),
            "reply_count": sum(1 for o in db.execute(select(BottleOpen).where(
                BottleOpen.bottle_id == b.id, BottleOpen.action == ACTION_REPLY)).scalars().all()),
        } for b in thrown],
        "replied": [{
            "bottle_id": rid, "reply": reply_map[rid],
        } for rid in picked_ids],
    })
