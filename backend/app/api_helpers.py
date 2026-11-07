# -*- coding: utf-8 -*-
"""统一返回结构 {code, msg, data}。"""
from fastapi.responses import JSONResponse


def ok(data=None, msg="ok"):
    return {"code": 0, "msg": msg, "data": data or {}}


def err(msg: str, code: int = 1, status: int = 400):
    return JSONResponse(status_code=status, content={"code": code, "msg": msg, "data": {}})
