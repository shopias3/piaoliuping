# -*- coding: utf-8 -*-
"""配置：关于我们页内容（生产由运营后台配置）。"""
from fastapi import APIRouter

from ..api_helpers import ok
from ..config import PICK_DAILY_LIMIT, THROW_DAILY_LIMIT

router = APIRouter(prefix="/config", tags=["config"])

STATEMENT = (
    "本应用由微信公众号 Daboshik 团队开发运营，严格遵守《中华人民共和国网络安全法》"
    "《中华人民共和国数据安全法》《中华人民共和国个人信息保护法》《网络信息内容生态治理规定》"
    "等法律法规。漂流瓶全部内容经 AI 智能审核后展示，严禁发布、传播涉政有害、色情低俗、"
    "暴力恐怖、赌博诈骗、侵权盗版及虚假信息；发布违法信息必究，平台将依法采取删除、屏蔽、"
    "封禁等措施并留存记录，涉嫌违法犯罪的依法向有关部门报告。请勿向陌生人转账汇款，"
    "谨防诈骗。发现违规内容请通过页内举报功能或微信公众号 Daboshik 反馈，我们将及时处理。"
)


@router.get("/about")
def about():
    return ok({
        "app_name": "漂流瓶",
        "version": "1.0.0",
        "operator": "微信公众号 Daboshik",
        "slogan": "愿每一个愿望，都能漂到对岸",
        "rules": [
            {"title": "投捞次数", "desc": f"公测期投瓶、捞瓶均免费：每日投瓶 {THROW_DAILY_LIMIT} 次、捞瓶 {PICK_DAILY_LIMIT} 次，防滥用上限。"},
            {"title": "沉底机制", "desc": "沉默 7 天以上的瓶子自动「沉底」降权，用户回归后自动浮起。"},
            {"title": "回池机制", "desc": "被捞起后选择「放回海里」的瓶子立即回池继续漂流。"},
            {"title": "活跃度与上浮权重", "desc": "活跃度 = 登录 40% + 漂流 30% + 互动 30%（单项封顶防刷）；漂移五档：静水深流 → 微波荡漾 → 川流不息 → 乘风破浪 → 潮头弄浪，段位越高漂移越快、瓶子越容易被捞起。"},
            {"title": "违规处置", "desc": "先审后显：AI 机审 + 存疑人审；违规内容分级处置（删瓶 / 禁投 7 天 / 封号），涉嫌违法的依法报告有关部门。"},
        ],
        "statement": STATEMENT,
        "agreements": {
            "user": "《用户协议》：本应用为陌生人轻社交平台，用户需遵守法律法规与社区规范，不得发布违法信息；平台有权依规处置违规内容与账号。",
            "privacy": "《隐私政策》：手机号加密存储、脱敏展示（138****0000）；信息最小化收集，昵称头像可选；个性化推荐可关闭。",
            "logout": "《账号注销指引》：可在公众号 Daboshik 提交注销申请，7 个工作日内完成数据删除。",
        },
        "contact": "客服与反馈：微信公众号 Daboshik",
    })
