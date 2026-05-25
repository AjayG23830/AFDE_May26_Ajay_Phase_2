"""EKBMS Phase 2 — ETL orchestrator. Run: python run_etl.py"""
import os
from pathlib import Path
# Ensure script runs from project root regardless of cwd
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

from extract import extract
from transform import transform
from load import load


def run_etl(db_path: str = "backend/ekbms.db"):
    print("=" * 60); print(" EKBMS ETL PIPELINE"); print("=" * 60)
    data = extract()
    out = transform(data)
    load(out, rows_extracted=len(data["articles"]), db_path=db_path)
    print("=" * 60); print(" ETL COMPLETED ✅"); print("=" * 60)
    return {"extracted": len(data["articles"]), "loaded": len(out["cleaned_articles"])}


if __name__ == "__main__":
    run_etl()
