"""LMS Phase 2 — EXTRACT step. Read books, borrowers, transactions CSVs."""
import pandas as pd
from pathlib import Path


def _read(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists(): raise FileNotFoundError(path)
    df = pd.read_csv(path) if p.suffix.lower()==".csv" else pd.read_excel(path)
    print(f"[EXTRACT] {len(df)} rows from {path}")
    return df


def extract(books_path: str = "datasets/books_raw.csv",
            borrowers_path: str = "datasets/borrowers_raw.csv",
            txn_path: str = "datasets/transactions_raw.csv"):
    return {"books": _read(books_path), "borrowers": _read(borrowers_path), "transactions": _read(txn_path)}


if __name__ == "__main__":
    out = extract()
    for k,v in out.items(): print(f"\n{k}:"); print(v.head())
