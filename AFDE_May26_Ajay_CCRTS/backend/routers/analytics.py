"""CCRTS Phase 2 — Analytics Router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from dependencies import get_current_user
import subprocess, os, sys

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/category-stats")
def category_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(text("SELECT category, complaint_count, avg_resolution_hours, sla_breach_count "
                           "FROM analytics_category_stats ORDER BY complaint_count DESC")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/priority-distribution")
def priority_distribution(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(text("SELECT priority, count FROM analytics_priority_dist")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/status-distribution")
def status_distribution(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(text("SELECT status, count FROM analytics_status_dist ORDER BY count DESC")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/sla-report")
def sla_report(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(text("SELECT priority, total, breached, breach_rate FROM analytics_sla_report")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/monthly-trend")
def monthly_trend(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(text("SELECT month, complaint_count, resolved_count, breach_count, avg_resolution_hours "
                           "FROM analytics_monthly_trend ORDER BY month")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/agent-performance")
def agent_performance(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(text("SELECT agent_name, total_assigned, resolved, breached, avg_resolution_hours, resolution_rate "
                           "FROM analytics_agent_performance ORDER BY resolution_rate DESC")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/summary")
def summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total = db.execute(text("SELECT COUNT(*) FROM analytics_complaints_clean")).scalar() or 0
    breached = db.execute(text("SELECT COUNT(*) FROM analytics_complaints_clean WHERE sla_breached=1")).scalar() or 0
    resolved = db.execute(text("SELECT COUNT(*) FROM analytics_complaints_clean WHERE is_resolved=1")).scalar() or 0
    avg = db.execute(text("SELECT AVG(resolution_hours) FROM analytics_complaints_clean WHERE resolution_hours IS NOT NULL")).scalar()
    last = db.execute(text("SELECT run_at, rows_extracted, rows_loaded, status FROM etl_runs ORDER BY run_id DESC LIMIT 1")).mappings().first()
    return {
        "total_complaints": total, "sla_breached": breached, "resolved": resolved,
        "avg_resolution_hours": round(float(avg), 2) if avg else 0,
        "breach_rate": round(breached / total * 100, 2) if total else 0,
        "last_etl_run": dict(last) if last else None,
    }


@router.post("/run-etl")
def run_etl(_=Depends(get_current_user)):
    script_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "etl"))
    try:
        r = subprocess.run([sys.executable, "run_etl.py"], cwd=script_dir, capture_output=True, text=True, timeout=120)
        if r.returncode != 0: raise HTTPException(500, f"ETL failed: {r.stderr or r.stdout}")
        return {"status": "success", "output": r.stdout}
    except Exception as e:
        raise HTTPException(500, str(e))
