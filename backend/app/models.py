# -*- coding: utf-8 -*-
"""数据模型：8 张核心表（users / regions / bottles / bottle_opens / activity_logs /
audit_tasks / reports / backgrounds），字段与开发框架文档第四章一致。"""
from datetime import datetime, date

from sqlalchemy import (
    Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    phone_enc: Mapped[str] = mapped_column(String(256), default="")   # 手机号（演示为简单可逆编码，生产用 KMS/AES）
    nickname: Mapped[str] = mapped_column(String(32), default="")
    avatar_url: Mapped[str] = mapped_column(String(256), default="")
    gender: Mapped[str] = mapped_column(String(8), default="保密")
    birth_year: Mapped[int] = mapped_column(Integer, default=0)
    ethnicity: Mapped[str] = mapped_column(String(16), default="")   # 民族
    address: Mapped[str] = mapped_column(String(128), default="")    # 现住址（详细地址）
    region_id: Mapped[int] = mapped_column(Integer, default=0)        # 常驻城市（region.id）
    interest_tags: Mapped[list] = mapped_column(JSON, default=list)   # 兴趣主题（背景偏好）
    crowd: Mapped[str] = mapped_column(String(16), default="不限")
    big_font: Mapped[bool] = mapped_column(Boolean, default=False)    # 适老化大字模式
    activity_score: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Region(Base):
    __tablename__ = "regions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(Integer, default=0, index=True)
    level: Mapped[int] = mapped_column(Integer)               # 1 省 / 2 市(区) / 3 区县
    name: Mapped[str] = mapped_column(String(32))
    adcode: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    region_type: Mapped[str] = mapped_column(String(16), default="省份")


class Bottle(Base):
    __tablename__ = "bottles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    type: Mapped[int] = mapped_column(Integer)                # 1-8 瓶签
    city_id: Mapped[int] = mapped_column(Integer, index=True) # 投入的城市（region.id）
    target_crowd: Mapped[str] = mapped_column(String(16), default="不限")
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="drifting", index=True)
    float_weight: Mapped[float] = mapped_column(Float, default=1.0)
    expire_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class BottleOpen(Base):
    __tablename__ = "bottle_opens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bottle_id: Mapped[int] = mapped_column(Integer, index=True)
    catcher_id: Mapped[int] = mapped_column(Integer, index=True)
    action: Mapped[str] = mapped_column(String(16))           # pick/open/back/reply
    reply_content: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    action: Mapped[str] = mapped_column(String(16))           # login/throw/pick/reply/report
    score: Mapped[float] = mapped_column(Float, default=0)
    log_date: Mapped[date] = mapped_column(Date, default=date.today)


class AuditTask(Base):
    __tablename__ = "audit_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target_type: Mapped[str] = mapped_column(String(16))      # bottle / reply
    target_id: Mapped[int] = mapped_column(Integer, index=True)
    machine_result: Mapped[str] = mapped_column(String(16))   # pass / reject
    hit_word: Mapped[str] = mapped_column(String(64), default="")
    human_result: Mapped[str] = mapped_column(String(16), default="")
    auditor_id: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reporter_id: Mapped[int] = mapped_column(Integer, index=True)
    target_type: Mapped[str] = mapped_column(String(16))      # bottle / user
    target_id: Mapped[int] = mapped_column(Integer, index=True)
    reason: Mapped[str] = mapped_column(String(200))
    handle_status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Background(Base):
    __tablename__ = "backgrounds"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    theme: Mapped[str] = mapped_column(String(32))            # 10 大主题
    oss_url: Mapped[str] = mapped_column(String(256), default="")  # 生产：CDN 长图 WebP
    css: Mapped[str] = mapped_column(Text, default="")        # 演示：渐变配色（替代长图）
    tags: Mapped[str] = mapped_column(String(128), default="")
    weight: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[int] = mapped_column(Integer, default=1)   # 1 上线 0 下线
