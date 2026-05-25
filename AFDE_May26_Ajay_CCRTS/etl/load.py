"""CCRTS Phase 2 — LOAD step."""
import sqlite3, pandas as pd
DB_PATH = "../backend/ccrts.db"


def _create_tables(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS analytics_complaints_clean (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_number TEXT, title TEXT, category TEXT, priority TEXT, status TEXT,
        agent_name TEXT, created_at TIMESTAMP, sla_deadline TIMESTAMP, resolved_at TIMESTAMP,
        resolution_hours REAL, sla_breached INTEGER, is_resolved INTEGER,
        loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_category_stats (
        category TEXT PRIMARY KEY, complaint_count INTEGER,
        avg_resolution_hours REAL, sla_breach_count INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_priority_dist (priority TEXT PRIMARY KEY, count INTEGER, last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS analytics_status_dist (status TEXT PRIMARY KEY, count INTEGER, last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS analytics_sla_report (
        priority TEXT PRIMARY KEY, total INTEGER, breached INTEGER, breach_rate REAL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_monthly_trend (
        month TEXT PRIMARY KEY,
        complaint_count INTEGER, resolved_count INTEGER, breach_count INTEGER, avg_resolution_hours REAL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_agent_performance (
        agent_name TEXT PRIMARY KEY,
        total_assigned INTEGER, resolved INTEGER, breached INTEGER,
        avg_resolution_hours REAL, resolution_rate REAL,
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
        _create_tables(conn); cur = conn.cursor()

        cur.execute("DELETE FROM analytics_complaints_clean")
        clean = out["cleaned"].assign(
            sla_breached=out["cleaned"]["sla_breached"].astype(int),
            is_resolved=out["cleaned"]["is_resolved"].astype(int),
        )[["complaint_number","title","category","priority","status","agent_name",
           "created_at","sla_deadline","resolved_at","resolution_hours","sla_breached","is_resolved"]]
        clean.to_sql("analytics_complaints_clean", conn, if_exists="append", index=False)

        for tbl, df in [
            ("analytics_category_stats",      out["category_stats"]),
            ("analytics_priority_dist",       out["priority_distribution"]),
            ("analytics_status_dist",         out["status_distribution"]),
            ("analytics_sla_report",          out["sla_report"]),
            ("analytics_monthly_trend",       out["monthly_trend"]),
            ("analytics_agent_performance",   out["agent_performance"]),
        ]:
            cur.execute(f"DELETE FROM {tbl}")
            # Coerce booleans to ints where present
            df_clean = df.copy()
            for col in df_clean.columns:
                if df_clean[col].dtype == bool: df_clean[col] = df_clean[col].astype(int)
            df_clean.to_sql(tbl, conn, if_exists="append", index=False)

        n = len(out["cleaned"])
        cur.execute("INSERT INTO etl_runs (rows_extracted,rows_loaded,status,notes) VALUES (?,?,?,?)",
                    (rows_extracted, n, "success", "CCRTS complaints ETL"))
        conn.commit()
        print(f"[LOAD] {n} complaints + analytics tables written")
    finally:
        conn.close()


if __name__ == "__main__":
    from extract import extract
    from transform import transform
    df = extract()
    load(transform(df), rows_extracted=len(df))
