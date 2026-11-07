# -*- coding: utf-8 -*-
"""频控与验证码：内存实现（单进程演示）。
生产环境将两个类替换为 Redis 版本即可（接口一致），或直接用 DRIFT_REDIS_URL。"""
import random
import time
from threading import Lock

from .config import SMS_RESEND_SECONDS


class RateLimiter:
    """滑动窗口频控：allow(key, window_sec)。"""

    def __init__(self):
        self._hits = {}
        self._lock = Lock()

    def allow(self, key: str, window_sec: int) -> bool:
        now = time.time()
        with self._lock:
            last = self._hits.get(key, 0)
            if now - last < window_sec:
                return False
            self._hits[key] = now
            return True

    def clear(self):
        with self._lock:
            self._hits.clear()


class SmsCodeStore:
    """验证码存储：演示模式验证码直接回传给前端（生产走短信通道 + Redis TTL）。"""

    def __init__(self):
        self._codes = {}
        self._lock = Lock()

    def issue(self, phone: str) -> str:
        code = str(random.randint(100000, 999999))
        with self._lock:
            self._codes[phone] = {"code": code, "ts": time.time()}
        return code

    def verify(self, phone: str, code: str) -> bool:
        with self._lock:
            item = self._codes.get(phone)
        if not item:
            return False
        if time.time() - item["ts"] > 5 * 60:  # 5 分钟有效
            return False
        return item["code"] == str(code).strip()


sms_limiter = RateLimiter()
sms_store = SmsCodeStore()
