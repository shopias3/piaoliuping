# -*- coding: utf-8 -*-
"""一次性迁移：把 10 张 AI 生成的主题长卷挂到 backgrounds 表的 oss_url。
演示资源位于前端 /static/themes/*.jpg；生产替换为 OSS/CDN WebP 地址。"""
from sqlalchemy import select

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal  # noqa: E402
from app.models import Background  # noqa: E402

URL_MAP = {
    "城市": "/static/themes/city.jpg",
    "自然": "/static/themes/nature.jpg",
    "星空": "/static/themes/starry.jpg",
    "世界景点": "/static/themes/landmark.jpg",
    "世界人文": "/static/themes/folk.jpg",
    "科技创新": "/static/themes/tech.jpg",
    "漫画": "/static/themes/comic.jpg",
    "名画": "/static/themes/painting.jpg",
    "交通": "/static/themes/transport.jpg",
    "战争与武器": "/static/themes/ships.jpg",
}

db = SessionLocal()
try:
    rows = db.execute(select(Background)).scalars().all()
    updated = 0
    for b in rows:
        url = URL_MAP.get(b.theme)
        if url and b.oss_url != url:
            b.oss_url = url
            updated += 1
    db.commit()
    print(f"updated {updated}/{len(rows)} rows")
    for b in db.execute(select(Background)).scalars().all():
        print(b.theme, "->", b.oss_url)
finally:
    db.close()
