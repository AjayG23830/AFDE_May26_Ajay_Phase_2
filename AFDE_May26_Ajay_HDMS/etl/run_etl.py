"""HDMS Phase 2 — ETL orchestrator. Run: python run_etl.py"""
import os
from pathlib import Path
# Ensure script runs from project root regardless of cwd
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

import sys
from extract import extract
from transform import transform
from load import load


def run_etl(dataset_path: str = "datasets/tickets_raw.csv", db_path: str = "backend/hdms.db"):
    print("=" * 60); print(f" HDMS ETL PIPELINE — {dataset_path}"); print("=" * 60)
    df = extract(dataset_path)
    out = transform(df)
    load(out, rows_extracted=len(df), db_path=db_path)
    print("=" * 60); print(" ETL COMPLETED ✅"); print("=" * 60)
    return {"extracted": len(df), "loaded": len(out["cleaned"])}


if __name__ == "__main__":
    run_etl(sys.argv[1] if len(sys.argv) > 1 else "datasets/tickets_raw.csv")
