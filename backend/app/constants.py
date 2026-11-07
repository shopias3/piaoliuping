# -*- coding: utf-8 -*-
"""瓶签、人群、段位等业务常量，与前端 utils/drift.js 保持一致。"""

# 八大瓶签（id 1-8，与文档 1.2 映射表一致）
BOTTLE_TYPES = {
    1: "学习提升瓶",
    2: "合作机会瓶",
    3: "好物展示瓶",
    4: "求职瓶",
    5: "交友瓶",
    6: "缘分瓶",   # 限 18+
    7: "招聘瓶",
    8: "出国圆梦瓶",
}
DEFAULT_BOTTLE_TYPE = 5  # 默认「交友瓶」

# 人群
CROWDS = ["不限", "青年16-30", "中坚31-45", "沉淀46-60"]

# 瓶子状态
STATUS_AUDITING = "auditing"    # 审核中
STATUS_DRIFTING = "drifting"    # 漂流中
STATUS_PICKED = "picked"        # 被捞起
STATUS_SUNK = "sunk"            # 沉底
STATUS_REMOVED = "removed"      # 违规删除

# 捞取动作
ACTION_PICK = "pick"    # 捞起（服务端内部记录，用于频控/活跃度）
ACTION_OPEN = "open"    # 打开
ACTION_BACK = "back"    # 放回海里
ACTION_REPLY = "reply"  # 回应

# 活跃度五档段位（0-20 / 21-40 / 41-60 / 61-80 / 81-100）
TIERS = [
    (0, "静水深流"),
    (21, "微波荡漾"),
    (41, "川流不息"),
    (61, "乘风破浪"),
    (81, "潮头弄浪"),
]


def tier_of(score: int) -> str:
    name = TIERS[0][1]
    for low, n in TIERS:
        if score >= low:
            name = n
    return name


def float_weight_of(score: int) -> float:
    """瓶子上浮权重：与漂移速度分档一致（0.6 / 0.8 / 1.0 / 1.3 / 1.6）。"""
    if score > 80:
        return 1.6
    if score > 60:
        return 1.3
    if score > 40:
        return 1.0
    if score > 20:
        return 0.8
    return 0.6
