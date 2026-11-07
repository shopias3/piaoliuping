# -*- coding: utf-8 -*-
"""种子数据：行政区划树、背景主题库、演示用户与瓶子（保证捞瓶流程开箱可用）。"""
import random
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .constants import (
    BOTTLE_TYPES, DEFAULT_BOTTLE_TYPE, STATUS_DRIFTING, float_weight_of,
)
from .data.regions_data import REGION_DATA, THEME_DATA
from .models import ActivityLog, Background, Bottle, Region, User
from .security import phone_encode, phone_hash


def seed_regions(db: Session) -> int:
    count = 0
    for adcode, name, rtype, cities in REGION_DATA:
        prov = Region(parent_id=0, level=1, name=name, adcode=adcode, region_type=rtype)
        db.add(prov)
        db.flush()
        for cadcode, cname, districts in cities:
            city = Region(parent_id=prov.id, level=2, name=cname, adcode=cadcode,
                          region_type="市辖区" if rtype != "直辖市" else "市辖区")
            db.add(city)
            db.flush()
            for dadcode, dname in districts:
                db.add(Region(parent_id=city.id, level=3, name=dname, adcode=dadcode,
                              region_type="区县"))
                count += 1
        count += 1 + len(cities)
    db.flush()
    return count


def seed_backgrounds(db: Session) -> int:
    for theme, css, tags in THEME_DATA:
        db.add(Background(theme=theme, oss_url="", css=css, tags=tags, weight=1, status=1))
    db.flush()
    return len(THEME_DATA)


# 演示用户：(昵称, 目标活跃度, 城市 adcode, 兴趣主题)
DEMO_USERS = [
    ("海风先生", 88, "330100", ["城市", "交通", "自然"]),
    ("灯塔keeper", 66, "440300", ["城市", "科技创新", "星空"]),
    ("拾贝少女", 47, "310000", ["名画", "漫画", "自然"]),
    ("蓝鲸出海", 33, "440100", ["世界人文", "自然"]),
    ("纸船与星", 18, "110000", ["星空", "名画"]),
    ("潮汐信使", 75, "510100", ["自然", "世界景点", "交通"]),
    ("浪花朵朵", 52, "420100", ["漫画", "城市"]),
    ("远方来客", 26, "370200", ["世界景点", "交通"]),
]

# 演示瓶子：(用户昵称, 瓶签, 城市adcode, 人群, 内容)
DEMO_BOTTLES = [
    ("拾贝少女", 1, "330100", "不限", "想找一位一起备考教师资格证的学习搭子，每周线上互相打卡，一起上岸！"),
    ("灯塔keeper", 2, "310000", "中坚31-45", "我在做宠物用品跨境供应链，想找有海外仓资源的朋友聊聊合作。"),
    ("浪花朵朵", 3, "440600", "不限", "家里三代做手工藤编，新出了藤编收纳筐，喜欢手作的朋友欢迎交流。"),
    ("蓝鲸出海", 4, "420100", "不限", "三年新媒体运营经验，擅长短视频策划，正在找武汉或远程的运营岗位。"),
    ("潮汐信使", 5, "510100", "不限", "刚来成都工作，周末喜欢爬山和逛博物馆，想认识同城的同频朋友。"),
    ("海风先生", 6, "110000", "青年16-30", "程序员，喜欢天文和胶片摄影，想认真找一个可以一起看星星的人。"),
    ("灯塔keeper", 7, "440300", "不限", "我们团队招一名资深前端工程师，Vue 技术栈，欢迎回复交流。"),
    ("远方来客", 8, "370200", "不限", "准备申请明年秋季的德国硕士，想找同样在准备留学的伙伴互通信息。"),
    ("纸船与星", 1, "110000", "不限", "在准备 CPA 考试，求已上岸的朋友分享笔记和备考时间表。"),
    ("浪花朵朵", 3, "530100", "不限", "自家花田的鲜花饼每周现烤直发，想找全国各地的小店主合作。"),
    ("潮汐信使", 5, "440100", "不限", "周末羽毛球搭子征集，水平不重要，重要的是坚持。"),
    ("拾贝少女", 6, "310000", "青年16-30", "喜欢逛美术馆和听爵士乐，希望遇到同样热爱生活的你。"),
    ("蓝鲸出海", 7, "330100", "不限", "电商公司招客服主管，双休五险，有意向欢迎回复。"),
    ("海风先生", 2, "120000", "中坚31-45", "小型软件开发工作室，承接小程序定制，找有稳定客源的渠道伙伴。"),
]


def _seed_activity_logs(db: Session, user_id: int, target_score: int):
    """按目标活跃度生成近 30 天行为流水（登录/投捞/回应三类分别推算）。"""
    today = datetime.now().date()
    login_days = min(max(int(round(target_score * 0.4 / 2)), 0), 20)
    bottle_times = min(max(int(round(target_score * 0.3 / 1)), 0), 30)
    reply_times = min(max(int(round(target_score * 0.3 / 0.75)), 0), 40)
    for i in range(login_days):
        db.add(ActivityLog(user_id=user_id, action="login", score=2,
                           log_date=today - timedelta(days=random.randint(0, 29))))
    for i in range(bottle_times):
        db.add(ActivityLog(user_id=user_id, action=random.choice(["throw", "pick"]), score=1,
                           log_date=today - timedelta(days=random.randint(0, 29))))
    for i in range(reply_times):
        db.add(ActivityLog(user_id=user_id, action="reply", score=0.75,
                           log_date=today - timedelta(days=random.randint(0, 29))))


def seed_demo_data(db: Session):
    region_by_adcode = {r.adcode: r for r in db.execute(select(Region)).scalars().all()}
    users = []
    for i, (nick, score, adcode, tags) in enumerate(DEMO_USERS):
        phone = "138%08d" % (10000000 + i)
        u = User(
            phone_hash=phone_hash(phone), phone_enc=phone_encode(phone),
            nickname=nick, region_id=region_by_adcode[adcode].id,
            interest_tags=tags, crowd="不限", activity_score=score,
            birth_year=random.randint(1980, 2000),
        )
        db.add(u)
        db.flush()
        _seed_activity_logs(db, u.id, score)
        users.append(u)
    db.flush()

    now = datetime.now()
    for nick, btype, adcode, crowd, content in DEMO_BOTTLES:
        u = next(x for x in users if x.nickname == nick)
        city = region_by_adcode[adcode]
        db.add(Bottle(
            user_id=u.id, type=btype, city_id=city.id, target_crowd=crowd,
            content=content, status=STATUS_DRIFTING,
            float_weight=float_weight_of(u.activity_score),
            expire_at=now + timedelta(days=7),
            created_at=now - timedelta(hours=random.randint(1, 60)),
        ))
    db.flush()


def seed_all(db: Session) -> dict:
    """幂等种子：任一表已有数据则跳过对应部分。"""
    stats = {}
    if db.execute(select(func.count(Region.id))).scalar() == 0:
        stats["regions"] = seed_regions(db)
    if db.execute(select(func.count(Background.id))).scalar() == 0:
        stats["backgrounds"] = seed_backgrounds(db)
    if db.execute(select(func.count(User.id))).scalar() == 0:
        seed_demo_data(db)
        stats["demo_users"] = len(DEMO_USERS)
        stats["demo_bottles"] = len(DEMO_BOTTLES)
    db.commit()
    return stats
