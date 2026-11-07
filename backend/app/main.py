# -*- coding: utf-8 -*-
"""漂流瓶 App 后端入口：FastAPI + 统一前缀 /api/v1。

启动：uvicorn app.main:app --host 0.0.0.0 --port 8010
- 若存在前端构建产物 frontend/dist/build/h5，则同端口托管 H5（界面+接口单端口对外，灯塔模式）
- 生产：Docker Compose + MySQL + Redis；本演示默认 SQLite + 内存频控。
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api_helpers import ok
from .config import DATA_DIR
from .database import Base, SessionLocal, engine
from .routers import appconfig, auth, backgrounds, bottles, regions, reports, users
from .seed import seed_all

# 前端 H5 构建产物目录（npm run build:h5 生成）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H5_DIST = os.path.normpath(os.path.join(BASE_DIR, "..", "frontend", "dist", "build", "h5"))
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)   # StaticFiles 挂载要求目录已存在


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    from .database import ensure_columns
    ensure_columns()                      # 为已存在的表补齐后加的列
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    db = SessionLocal()
    try:
        stats = seed_all(db)
        print("[seed] " + (str(stats) if stats else "已存在，跳过"))
    finally:
        db.close()
    yield


app = FastAPI(title="漂流瓶 App API", version="1.0.0", lifespan=lifespan)

# 演示环境放开跨域；生产按域名白名单收紧
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(regions.router, prefix="/api/v1")
app.include_router(backgrounds.router, prefix="/api/v1")
app.include_router(bottles.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(appconfig.router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    return ok({"status": "up", "service": "drift-bottle-api", "version": "1.0.0"})


# 用户上传（头像等）：必须先于 "/" 兜底托管注册
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


# 灯塔模式：同端口托管 H5 前端（放最后，兜底所有非 API 路径）
if os.path.isdir(H5_DIST):
    app.mount("/", StaticFiles(directory=H5_DIST, html=True), name="h5")
    print(f"[h5] 已托管前端: {H5_DIST}")
else:
    print(f"[h5] 未找到前端构建产物，仅提供 API: {H5_DIST}")
