# -*- coding: utf-8 -*-
"""全局配置。生产环境请通过环境变量覆盖（MySQL / Redis / 正式短信等）。"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ---- 安全 ----
SECRET_KEY = os.environ.get("DRIFT_SECRET_KEY", "drift-bottle-dev-secret-2026")
TOKEN_EXPIRE_HOURS = 24 * 7          # JWT 有效期 7 天
PHONE_SALT = "drift-bottle-phone"    # 手机号哈希盐（生产请换为密钥管理服务）

# ---- 数据库：默认 SQLite，生产可切 MySQL ----
# 例如：DRIFT_DATABASE_URL=mysql+pymysql://user:pass@127.0.0.1:3306/driftbottle?charset=utf8mb4
DATABASE_URL = os.environ.get(
    "DRIFT_DATABASE_URL", "sqlite:///" + os.path.join(DATA_DIR, "driftbottle.db")
)

# ---- 短信：演示模式直接返回验证码，生产接入阿里云/腾讯云 SMS ----
SMS_MOCK = os.environ.get("DRIFT_SMS_MOCK", "1") == "1"
SMS_RESEND_SECONDS = 60              # 同一号码 60 秒频控

# ---- 业务规则（与开发框架文档一致）----
THROW_DAILY_LIMIT = 5                # 每日投瓶次数
PICK_DAILY_LIMIT = 10                # 每日捞瓶次数
CONTENT_MAX_LEN = 200                # 心愿最大字数
BOTTLE_SINK_DAYS = 7                 # 沉默 7 天沉底
DUP_CONTENT_HOURS = 24               # 同内容 24 小时内不可重复投递
