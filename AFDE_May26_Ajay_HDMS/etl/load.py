"""HDMS Phase 2 — LOAD step. Write cleaned + aggregated data to analytics tables."""
import sqlite3, pandas as pd

DB_PATH = "../backend/hdms.db"


def _create_tables(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS analytics_tickets_clean (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_name TEXT, department TEXT, issue_category TEXT, description TEXT,
        priority TEXT, status TEXT, created_at TIMESTAMP, resolved_at TIMESTAMP,
        resolution_hours REAL, loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_category_stats (
        issue_category TEXT PRIMARY KEY,
        ticket_count INTEGER, avg_resolution_hours REAL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_priority_dist (
        priority TEXT PRIMARY KEY, count INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_department_stats (
        department TEXT PRIMARY KEY, ticket_count INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_monthly_trend (
        month TEXT PRIMARY KEY,
        ticket_count INTEGER, resolved_count INTEGER, avg_resolution_hours REAL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_status_dist (
        status TEXT PRIMARY KEY, count INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        _create_tables(conn)
        cur = conn.cursor()

        cur.execute("DELETE FROM analytics_tickets_clean")
        out["cleaned"][["employee_name","department","issue_category","description","priority","status",
                        "created_at","resolved_at","resolution_hours"]].to_sql(
            "analytics_tickets_clean", conn, if_exists="append", index=False)

        for table, df in [
            ("analytics_category_stats",   out["category_stats"]),
            ("analytics_priority_dist",    out["priority_distribution"]),
            ("analytics_department_stats", out["department_stats"]),
            ("analytics_monthly_trend",    out["monthly_trend"]),
            ("analytics_status_dist",      out["status_distribution"]),
        ]:
            cur.execute(f"DELETE FROM {table}")
            df.to_sql(table, conn, if_exists="append", index=False)

        n = len(out["cleaned"])
        cur.execute("INSERT INTO etl_runs (rows_extracted, rows_loaded, status, notes) VALUES (?,?,?,?)",
                    (rows_extracted, n, "success", "HDMS ticket ETL"))
        conn.commit()
        print(f"[LOAD] {n} rows + aggregates loaded")
    finally:
        conn.close()


if __name__ == "__main__":
    from extract import extract
    from transform import transform
    df = extract("datasets/tickets_raw.csv")
    load(transform(df), len(df))
