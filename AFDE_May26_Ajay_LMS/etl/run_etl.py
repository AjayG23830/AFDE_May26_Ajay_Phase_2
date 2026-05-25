"""LMS Phase 2 — ETL orchestrator. Run: python run_etl.py"""
import os
from pathlib import Path
# Ensure script runs from project root regardless of cwd
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

import sys
from extract import extract
from transform import transform
from load import load


def run_etl(books_path="datasets/books_raw.csv",
            borrowers_path="datasets/borrowers_raw.csv",
            txn_path="datasets/transactions_raw.csv",
            db_path="backend/lms.db"):
    print("=" * 60); print(" LMS ETL PIPELINE"); print("=" * 60)
    data = extract(books_path, borrowers_path, txn_path)
    out = transform(data)
    load(out, rows_extracted=len(data["transactions"]), db_path=db_path)
    print("=" * 60); print(" ETL COMPLETED ✅"); print("=" * 60)
    return {"extracted": len(data["transactions"]), "loaded": len(out["cleaned_transactions"])}


if __name__ == "__main__":
    run_etl()
