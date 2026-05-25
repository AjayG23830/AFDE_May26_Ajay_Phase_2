"""CCRTS Phase 2 — EXTRACT."""
import pandas as pd
from pathlib import Path


def extract(path: str = "datasets/complaints_raw.csv") -> pd.DataFrame:
    p = Path(path)
    if not p.exists(): raise FileNotFoundError(path)
    df = pd.read_csv(path) if p.suffix.lower()==".csv" else pd.read_excel(path)
    print(f"[EXTRACT] {len(df)} raw rows from {path}")
    return df


if __name__ == "__main__":
    print(extract().head())
