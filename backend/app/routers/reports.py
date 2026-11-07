# -*- coding: utf-8 -*-
"""安全：一键举报（24 小时内响应，生产接运营后台工单）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..api_helpers import ok
from ..database import get_db
from ..models import Report
from ..security import get_current_user
from .bottles import ReportBody

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("")
def create_report(body: ReportBody, db: Session = Depends(get_db),
                  user=Depends(get_current_user)):
    if body.target_type not in ("bottle", "user"):
        raise HTTPException(status_code=400, detail="举报对象类型不正确")
    reason = (body.reason or "").strip()[:200]
    if not reason:
        raise HTTPException(status_code=400, detail="请填写举报理由")
    db.add(Report(reporter_id=user.id, target_type=body.target_type,
                  target_id=body.target_id, reason=reason))
    db.commit()
    return ok(None, "举报已提交，我们将在 24 小时内核实处理")
