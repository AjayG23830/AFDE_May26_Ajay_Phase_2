"""EKBMS Phase 2 — LOAD step."""
import sqlite3
DB_PATH = "../backend/ekbms.db"


def _create_tables(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS analytics_articles_clean (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, category TEXT, tags TEXT, author TEXT, status TEXT,
        view_count INTEGER, created_at TIMESTAMP,
        loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_most_viewed (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, author TEXT, category TEXT, view_count INTEGER
    );
    CREATE TABLE IF NOT EXISTS analytics_category_usage (
        category TEXT PRIMARY KEY, article_count INTEGER, total_views INTEGER, avg_views REAL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_tag_stats (tag TEXT PRIMARY KEY, usage_count INTEGER);
    CREATE TABLE IF NOT EXISTS analytics_author_stats (
        author TEXT PRIMARY KEY, articles_written INTEGER, approved_count INTEGER, total_views INTEGER
    );
    CREATE TABLE IF NOT EXISTS analytics_article_status_dist (status TEXT PRIMARY KEY, count INTEGER);
    CREATE TABLE IF NOT EXISTS analytics_monthly_articles (
        month TEXT PRIMARY KEY, articles_created INTEGER, total_views INTEGER
    );
    CREATE TABLE IF NOT EXISTS analytics_keyword_stats (keyword TEXT PRIMARY KEY, search_count INTEGER);
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

        cur.execute("DELETE FROM analytics_articles_clean")
        out["cleaned_articles"][["title","category","tags","author","status","view_count","created_at"]].to_sql(
            "analytics_articles_clean", conn, if_exists="append", index=False)

        for tbl, df in [
            ("analytics_most_viewed",          out["most_viewed"]),
            ("analytics_category_usage",       out["category_usage"]),
            ("analytics_tag_stats",            out["tag_stats"]),
            ("analytics_author_stats",         out["author_stats"]),
            ("analytics_article_status_dist",  out["status_distribution"]),
            ("analytics_monthly_articles",     out["monthly_trend"]),
            ("analytics_keyword_stats",        out["keyword_stats"]),
        ]:
            cur.execute(f"DELETE FROM {tbl}")
            df.to_sql(tbl, conn, if_exists="append", index=False)

        n = len(out["cleaned_articles"])
        cur.execute("INSERT INTO etl_runs (rows_extracted,rows_loaded,status,notes) VALUES (?,?,?,?)",
                    (rows_extracted, n, "success", "EKBMS articles ETL"))
        conn.commit()
        print(f"[LOAD] {n} articles + analytics tables written")
    finally:
        conn.close()


if __name__ == "__main__":
    from extract import extract
    from transform import transform
    data = extract()
    load(transform(data), rows_extracted=len(data["articles"]))
