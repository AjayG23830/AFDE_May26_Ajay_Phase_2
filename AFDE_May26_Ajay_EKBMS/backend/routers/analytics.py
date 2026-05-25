"""EKBMS Phase 2 — Analytics Router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from dependencies import get_current_user
import subprocess, os, sys

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/most-viewed")
def most_viewed(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(text("SELECT title, author, category, view_count FROM analytics_most_viewed ORDER BY view_count DESC")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/category-usage")
def category_usage(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(text("SELECT category, article_count, total_views, avg_views FROM analytics_category_usage ORDER BY article_count DESC")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/tag-stats")
def tag_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(text("SELECT tag, usage_count FROM analytics_tag_stats ORDER BY usage_count DESC")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/author-stats")
def author_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(text("SELECT author, articles_written, approved_count, total_views FROM analytics_author_stats ORDER BY articles_written DESC")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/status-distribution")
def status_distribution(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(text("SELECT status, count FROM analytics_article_status_dist")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/monthly-trend")
def monthly_trend(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(text("SELECT month, articles_created, total_views FROM analytics_monthly_articles ORDER BY month")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/keyword-stats")
def keyword_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.execute(text("SELECT keyword, search_count FROM analytics_keyword_stats ORDER BY search_count DESC")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/summary")
def summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total = db.execute(text("SELECT COUNT(*) FROM analytics_articles_clean")).scalar() or 0
    views = db.execute(text("SELECT SUM(view_count) FROM analytics_articles_clean")).scalar() or 0
    authors = db.execute(text("SELECT COUNT(*) FROM analytics_author_stats")).scalar() or 0
    cats = db.execute(text("SELECT COUNT(*) FROM analytics_category_usage")).scalar() or 0
    last = db.execute(text("SELECT run_at, rows_extracted, rows_loaded, status FROM etl_runs ORDER BY run_id DESC LIMIT 1")).mappings().first()
    return {
        "total_articles": total, "total_views": int(views), "total_authors": authors,
        "total_categories": cats, "last_etl_run": dict(last) if last else None,
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
