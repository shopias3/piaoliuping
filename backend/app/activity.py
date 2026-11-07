# -*- coding: utf-8 -*-
"""活跃度与漂移算法（服务端），与前端 utils/drift.js 公式一致。

活跃度 0–100：登录 40% + 漂流 30% + 互动 30%，单项封顶防刷：
- 登录活跃：近 30 天登录天数 × 2 分/天，封顶 20 天
- 漂流活跃：近 30 天投瓶+捞瓶 × 1 分/次，封顶 30 次
- 互动活跃：近 30 天回应/举报 × 0.75 分/次，封顶 40 次
"""
import random
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .constants import STATUS_DRIFTING, float_weight_of, tier_of
from .models import ActivityLog, Bottle, BottleOpen

DRIFT_ACTIONS = ("throw", "pick")
INTERACT_ACTIONS = ("reply", "report")


def part(weight: float, value: float, cap: float) -> float:
    return min(value / cap, 1.0) * weight * 100


def log_activity(db: Session, user_id: int, action: str, score: float):
    db.add(ActivityLog(user_id=user_id, action=action, score=score, log_date=date.today()))


def compute_activity(db: Session, user_id: int) -> int:
    since = date.today() - timedelta(days=30)
    q = select(ActivityLog.action, ActivityLog.log_date).where(
        ActivityLog.user_id == user_id, ActivityLog.log_date >= since
    )
    rows = db.execute(q).all()
    login_days = len({r.log_date for r in rows if r.action == "login"})
    bottle_times = sum(1 for r in rows if r.action in DRIFT_ACTIONS)
    reply_times = sum(1 for r in rows if r.action in INTERACT_ACTIONS)
    score = (
        part(0.4, login_days, 20)
        + part(0.3, bottle_times, 30)
        + part(0.3, reply_times, 40)
    )
    return int(round(score))


def refresh_user_activity(db: Session, user) -> int:
    """重算并落库用户活跃度。"""
    user.activity_score = compute_activity(db, user.id)
    return user.activity_score


def weighted_random_pick(db: Session, user_id: int, city_ids: list,
                         target_crowd: str, types: list, limit=1):
    """按筛选条件加权随机抽取瓶子：活跃度权重上浮；排除自己投的、已被当前用户捞起过的。"""
    q = select(Bottle).where(Bottle.status == STATUS_DRIFTING, Bottle.user_id != user_id)
    if city_ids:
        q = q.where(Bottle.city_id.in_(city_ids))
    if types:
        q = q.where(Bottle.type.in_(types))
    candidates = db.execute(q.order_by(Bottle.created_at.desc()).limit(500)).scalars().all()

    picked_before = set(db.execute(
        select(BottleOpen.bottle_id).where(
            BottleOpen.catcher_id == user_id, BottleOpen.action == "pick"
        )
    ).scalars().all())
    candidates = [b for b in candidates if b.id not in picked_before]
    if not candidates:
        return []

    def crowd_ok(b: Bottle) -> bool:
        if not target_crowd or target_crowd in ("不限", ""):
            return True
        return b.target_crowd in ("不限", target_crowd)

    candidates = [b for b in candidates if crowd_ok(b)]
    if not candidates:
        return []

    weights = [max(b.float_weight, 0.1) for b in candidates]
    return random.choices(candidates, weights=weights, k=min(limit, len(candidates)))
