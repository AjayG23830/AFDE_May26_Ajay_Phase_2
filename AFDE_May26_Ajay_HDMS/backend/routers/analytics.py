"""HDMS Phase 2 — Analytics Router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
import subprocess, os, sys

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/category-stats")
def category_stats(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT issue_category, ticket_count, avg_resolution_hours FROM analytics_category_stats ORDER BY ticket_count DESC")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/priority-distribution")
def priority_distribution(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT priority, count FROM analytics_priority_dist")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/department-stats")
def department_stats(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT department, ticket_count FROM analytics_department_stats ORDER BY ticket_count DESC")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/monthly-trend")
def monthly_trend(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT month, ticket_count, resolved_count, avg_resolution_hours FROM analytics_monthly_trend ORDER BY month")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/status-distribution")
def status_distribution(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT status, count FROM analytics_status_dist")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    total = db.execute(text("SELECT COUNT(*) FROM analytics_tickets_clean")).scalar() or 0
    avg = db.execute(text("SELECT AVG(resolution_hours) FROM analytics_tickets_clean WHERE resolution_hours IS NOT NULL")).scalar()
    cats = db.execute(text("SELECT COUNT(*) FROM analytics_category_stats")).scalar() or 0
    depts = db.execute(text("SELECT COUNT(*) FROM analytics_department_stats")).scalar() or 0
    last = db.execute(text("SELECT run_at, rows_extracted, rows_loaded, status FROM etl_runs ORDER BY run_id DESC LIMIT 1")).mappings().first()
    return {
        "total_clean_tickets": total,
        "avg_resolution_hours": round(float(avg), 2) if avg else 0,
        "total_categories": cats,
        "total_departments": depts,
        "last_etl_run": dict(last) if last else None,
    }


@router.post("/run-etl")
def run_etl(dataset_path: Optional[str] = None):
    script_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "etl"))
    cmd = [sys.executable, "run_etl.py"]
    if dataset_path: cmd.append(dataset_path)
    try:
        r = subprocess.run(cmd, cwd=script_dir, capture_output=True, text=True, timeout=120)
        if r.returncode != 0: raise HTTPException(500, f"ETL failed: {r.stderr or r.stdout}")
        return {"status": "success", "output": r.stdout}
    except Exception as e:
        raise HTTPException(500, str(e))
