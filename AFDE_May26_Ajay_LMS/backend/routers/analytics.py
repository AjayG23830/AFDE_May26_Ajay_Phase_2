"""LMS Phase 2 — Analytics Router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
import subprocess, os, sys

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/most-borrowed")
def most_borrowed(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT book_id, title, author, category, borrow_count FROM analytics_most_borrowed ORDER BY borrow_count DESC")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/category-borrow")
def category_borrow(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT category, borrow_count FROM analytics_category_borrow ORDER BY borrow_count DESC")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/monthly-trend")
def monthly_trend(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT month, borrow_count, returned_count FROM analytics_monthly_borrow ORDER BY month")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/overdue-summary")
def overdue_summary(db: Session = Depends(get_db)):
    row = db.execute(text("SELECT total_overdue, total_active, total_returned, avg_borrow_days FROM analytics_overdue_summary ORDER BY id DESC LIMIT 1")).mappings().first()
    return dict(row) if row else {"total_overdue":0,"total_active":0,"total_returned":0,"avg_borrow_days":0}


@router.get("/overdue-list")
def overdue_list(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT book_id, title, author, borrower_id, borrow_date, borrow_days FROM analytics_overdue_detail ORDER BY borrow_days DESC")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    total = db.execute(text("SELECT COUNT(*) FROM analytics_transactions_clean")).scalar() or 0
    last = db.execute(text("SELECT run_at, rows_extracted, rows_loaded, status FROM etl_runs ORDER BY run_id DESC LIMIT 1")).mappings().first()
    od = db.execute(text("SELECT total_overdue, total_active, total_returned FROM analytics_overdue_summary ORDER BY id DESC LIMIT 1")).mappings().first()
    return {
        "total_clean_transactions": total,
        "overdue": dict(od) if od else None,
        "last_etl_run": dict(last) if last else None,
    }


@router.post("/run-etl")
def run_etl():
    script_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "etl"))
    try:
        r = subprocess.run([sys.executable, "run_etl.py"], cwd=script_dir, capture_output=True, text=True, timeout=120)
        if r.returncode != 0: raise HTTPException(500, f"ETL failed: {r.stderr or r.stdout}")
        return {"status": "success", "output": r.stdout}
    except Exception as e:
        raise HTTPException(500, str(e))
