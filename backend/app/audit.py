# -*- coding: utf-8 -*-
"""内容机审：敏感词库 + 规则。演示实现；生产接入阿里云内容安全/数美/易盾 + LLM 兜底。"""
import re

from .config import CONTENT_MAX_LEN

# 演示敏感词库（涉赌博诈骗、色情低俗、违法导流等类别，持续运营中应扩充并接外部机审 API）
SENSITIVE_WORDS = [
    "赌博", "博彩", "赌球", "赌场", "六合彩", "外围下注",
    "代开发票", "办证刻章", "办假证", "洗钱", "套现",
    "色情", "裸聊", "援交", "约炮", "一夜情服务",
    "毒品", "冰毒", "大麻", "枪支买卖", "买枪", "爆炸物",
    "刷单", "兼职刷信誉", "高利贷", "套路贷",
    "加微信转账", "先转账", "汇款到安全账户", "给我转账", "打钱给我",
    "反动", "分裂国家", "恐怖袭击",
    "贷款包过", "无抵押放款", "内部渠道买分",
    "加我QQ", "加我微信", "加V", "威信同号", "飞机号",
]

URL_RE = re.compile(r"(https?://|www\.)\S+", re.IGNORECASE)
PHONE_RE = re.compile(r"1[3-9]\d{9}")


def machine_audit(text: str) -> dict:
    """机审：返回 {'result': 'pass'|'reject', 'hit_word': str, 'reason': str}"""
    cleaned = (text or "").strip()
    if not cleaned:
        return {"result": "reject", "hit_word": "", "reason": "心愿内容不能为空"}
    if len(cleaned) > CONTENT_MAX_LEN:
        return {"result": "reject", "hit_word": "", "reason": f"心愿最多 {CONTENT_MAX_LEN} 字"}
    for w in SENSITIVE_WORDS:
        if w in cleaned:
            return {"result": "reject", "hit_word": w, "reason": "内容含违禁词，请修改后再投入"}
    if URL_RE.search(cleaned):
        return {"result": "reject", "hit_word": "url", "reason": "请勿在心愿中留链接"}
    return {"result": "pass", "hit_word": "", "reason": ""}
