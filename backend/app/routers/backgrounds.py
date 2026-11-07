# -*- coding: utf-8 -*-
"""背景库：按主题拉取长图列表。演示版返回渐变配色；生产 oss_url 指向 CDN WebP 长图。"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..api_helpers import ok
from ..database import get_db
from ..models import Background

router = APIRouter(prefix="/backgrounds", tags=["backgrounds"])


@router.get("")
def list_backgrounds(theme: str | None = None, db: Session = Depends(get_db)):
    q = select(Background).where(Background.status == 1)
    if theme:
        q = q.where(Background.theme == theme)
    rows = db.execute(q.order_by(Background.weight.desc(), Background.id)).scalars().all()
    data = [{
        "id": b.id, "theme": b.theme, "oss_url": b.oss_url, "css": b.css,
        "tags": b.tags, "weight": b.weight,
    } for b in rows]
    return ok(data)
