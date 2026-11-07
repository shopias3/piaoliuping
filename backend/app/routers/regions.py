# -*- coding: utf-8 -*-
"""地区：三级行政区划树（内存缓存兜底，生产可上 CDN）。"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..api_helpers import ok
from ..database import get_db
from ..models import Region

router = APIRouter(prefix="/regions", tags=["regions"])
_tree_cache = None


def _node(r: Region):
    return {
        "id": r.id, "adcode": r.adcode, "name": r.name,
        "level": r.level, "region_type": r.region_type, "children": [],
    }


@router.get("/tree")
def tree(db: Session = Depends(get_db)):
    global _tree_cache
    if _tree_cache:
        return ok(_tree_cache)
    rows = db.execute(select(Region).order_by(Region.adcode)).scalars().all()
    by_id = {r.id: _node(r) for r in rows}
    roots = []
    for r in rows:
        node = by_id[r.id]
        if r.parent_id and r.parent_id in by_id:
            by_id[r.parent_id]["children"].append(node)
        else:
            roots.append(node)
    _tree_cache = roots
    return ok(roots)


def invalidate_tree_cache():
    global _tree_cache
    _tree_cache = None
