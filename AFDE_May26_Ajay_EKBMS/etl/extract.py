"""EKBMS Phase 2 — EXTRACT step. Read articles + search log."""
import pandas as pd
from pathlib import Path


def _read(path):
    p = Path(path)
    if not p.exists(): raise FileNotFoundError(path)
    df = pd.read_csv(path) if p.suffix.lower()==".csv" else pd.read_excel(path)
    print(f"[EXTRACT] {len(df)} rows from {path}")
    return df


def extract(articles_path: str = "datasets/articles_raw.csv",
            search_log_path: str = "datasets/search_log_raw.csv"):
    return {"articles": _read(articles_path), "search_log": _read(search_log_path)}


if __name__ == "__main__":
    out = extract()
    for k,v in out.items(): print(f"\n{k}:"); print(v.head())
