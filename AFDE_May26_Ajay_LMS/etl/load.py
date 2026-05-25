"""LMS Phase 2 — LOAD step. Write analytics tables."""
import sqlite3, pandas as pd
DB_PATH = "../backend/lms.db"


def _create_tables(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS analytics_transactions_clean (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER, borrower_id INTEGER, borrow_date TIMESTAMP, return_date TIMESTAMP,
        borrow_days INTEGER, is_returned INTEGER, is_overdue INTEGER,
        loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_most_borrowed (
        book_id INTEGER PRIMARY KEY, title TEXT, author TEXT, category TEXT,
        borrow_count INTEGER, last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_category_borrow (
        category TEXT PRIMARY KEY, borrow_count INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_monthly_borrow (
        month TEXT PRIMARY KEY, borrow_count INTEGER, returned_count INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_overdue_summary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total_overdue INTEGER, total_active INTEGER, total_returned INTEGER, avg_borrow_days REAL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_overdue_detail (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER, title TEXT, author TEXT, borrower_id INTEGER,
        borrow_date TIMESTAMP, borrow_days INTEGER
    );
    CREATE TABLE IF NOT EXISTS etl_runs (
        run_id INTEGER PRIMARY KEY AUTOINCREMENT, run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        rows_extracted INTEGER, rows_loaded INTEGER, status TEXT, notes TEXT
    );
    """)
    conn.commit()


def load(out: dict, rows_extracted: int, db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    try:
        _create_tables(conn); cur = conn.cursor()

        cur.execute("DELETE FROM analytics_transactions_clean")
        out["cleaned_transactions"].assign(
            is_returned=out["cleaned_transactions"]["is_returned"].astype(int),
            is_overdue=out["cleaned_transactions"]["is_overdue"].astype(int),
        )[["book_id","borrower_id","borrow_date","return_date","borrow_days","is_returned","is_overdue"]].to_sql(
            "analytics_transactions_clean", conn, if_exists="append", index=False)

        for tbl, df, cols in [
            ("analytics_most_borrowed",     out["most_borrowed"],     ["book_id","title","author","category","borrow_count"]),
            ("analytics_category_borrow",   out["category_stats"],    ["category","borrow_count"]),
            ("analytics_monthly_borrow",    out["monthly_trend"],     ["month","borrow_count","returned_count"]),
            ("analytics_overdue_summary",   out["overdue_summary"],   ["total_overdue","total_active","total_returned","avg_borrow_days"]),
            ("analytics_overdue_detail",    out["overdue_detail"],    ["book_id","title","author","borrower_id","borrow_date","borrow_days"]),
        ]:
            cur.execute(f"DELETE FROM {tbl}")
            df[cols].to_sql(tbl, conn, if_exists="append", index=False)

        n = len(out["cleaned_transactions"])
        cur.execute("INSERT INTO etl_runs (rows_extracted,rows_loaded,status,notes) VALUES (?,?,?,?)",
                    (rows_extracted, n, "success", "LMS transactions ETL"))
        conn.commit()
        print(f"[LOAD] {n} cleaned transactions + analytics tables written")
    finally:
        conn.close()


if __name__ == "__main__":
    from extract import extract
    from transform import transform
    data = extract()
    load(transform(data), rows_extracted=len(data["transactions"]))
