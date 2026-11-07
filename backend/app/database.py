# -*- coding: utf-8 -*-
"""数据库连接与 ORM 基类。默认 SQLite，生产通过 DRIFT_DATABASE_URL 切换 MySQL。"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_columns():
    """轻量迁移：为已存在的表补齐后加的列（SQLite/MySQL 通用）。"""
    from sqlalchemy import inspect, text

    plan = {
        "users": {
            "ethnicity": "VARCHAR(16) DEFAULT ''",
            "address": "VARCHAR(128) DEFAULT ''",
        },
    }
    insp = inspect(engine)
    with engine.connect() as conn:
        for table, cols in plan.items():
            if table not in insp.get_table_names():
                continue
            existing = {c["name"] for c in insp.get_columns(table)}
            for col, ddl in cols.items():
                if col not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}"))
        conn.commit()
