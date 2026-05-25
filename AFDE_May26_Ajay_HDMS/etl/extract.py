"""HDMS Phase 2 — EXTRACT step. Read CSV/Excel into a DataFrame."""
import pandas as pd
from pathlib import Path

def extract(file_path: str) -> pd.DataFrame:
    p = Path(file_path)
    if not p.exists(): raise FileNotFoundError(file_path)
    df = pd.read_csv(file_path) if p.suffix.lower()==".csv" else pd.read_excel(file_path)
    print(f"[EXTRACT] {len(df)} raw rows from {file_path}")
    return df

if __name__ == "__main__":
    print(extract("datasets/tickets_raw.csv").head())
