"""EKBMS Phase 2 — TRANSFORM step. Clean and aggregate articles + searches."""
import pandas as pd

VALID_STATUSES = {"Draft","Pending Approval","Approved","Rejected","Archived"}


def transform(data: dict) -> dict:
    articles, search_log = data["articles"].copy(), data["search_log"].copy()
    n0 = len(articles)

    # Articles cleaning
    for col in ["title","category","tags","author","status"]:
        articles[col] = articles[col].fillna("").astype(str).str.strip()
    articles["category"] = articles["category"].str.title()
    articles["view_count"] = pd.to_numeric(articles["view_count"], errors="coerce").fillna(0).astype(int)
    articles = articles[articles["status"].isin(VALID_STATUSES)].copy()
    articles["created_at"] = pd.to_datetime(articles["created_at"], errors="coerce")
    articles = articles.dropna(subset=["created_at"]).copy()
    articles = articles.drop_duplicates(subset=["title","author","created_at"])

    n1 = len(articles)
    print(f"[TRANSFORM] Articles: {n0} → {n1}")

    # ── Aggregations ──
    # 1. Most viewed (top 15)
    most_viewed = articles[articles["status"]=="Approved"].sort_values("view_count", ascending=False).head(15)[
        ["title","author","category","view_count"]
    ].reset_index(drop=True)

    # 2. Category usage trends
    cat_usage = articles.groupby("category").agg(
        article_count=("category","count"),
        total_views=("view_count","sum"),
        avg_views=("view_count","mean"),
    ).reset_index().sort_values("article_count", ascending=False)
    cat_usage["avg_views"] = cat_usage["avg_views"].round(2)

    # 3. Tag frequency (explode tags column)
    tags_exploded = articles.assign(tag=articles["tags"].str.split("|")).explode("tag")
    tags_exploded["tag"] = tags_exploded["tag"].astype(str).str.strip().str.lower()
    tags_exploded = tags_exploded[tags_exploded["tag"] != ""]
    tag_stats = tags_exploded.groupby("tag").size().reset_index(name="usage_count").sort_values("usage_count", ascending=False).head(20)

    # 4. Author activity
    author_stats = articles.groupby("author").agg(
        articles_written=("author","count"),
        approved_count=("status", lambda s: int((s=="Approved").sum())),
        total_views=("view_count","sum"),
    ).reset_index().sort_values("articles_written", ascending=False)

    # 5. Article status distribution
    status_dist = articles["status"].value_counts().reset_index()
    status_dist.columns = ["status","count"]

    # 6. Monthly publication trend
    articles["month"] = articles["created_at"].dt.to_period("M").astype(str)
    monthly = articles.groupby("month").agg(
        articles_created=("month","count"),
        total_views=("view_count","sum"),
    ).reset_index().sort_values("month")

    # 7. Search keyword analysis
    search_log["keyword"] = search_log["keyword"].astype(str).str.strip().str.lower()
    search_log["searched_at"] = pd.to_datetime(search_log["searched_at"], errors="coerce")
    search_log = search_log.dropna(subset=["searched_at","keyword"])
    keyword_stats = search_log.groupby("keyword").size().reset_index(name="search_count").sort_values("search_count", ascending=False).head(15)

    print(f"[TRANSFORM] {len(most_viewed)} top articles, {len(cat_usage)} cats, {len(tag_stats)} tags, {len(author_stats)} authors, {len(keyword_stats)} keywords")
    return {
        "cleaned_articles": articles.drop(columns=["month"]),
        "most_viewed": most_viewed,
        "category_usage": cat_usage,
        "tag_stats": tag_stats,
        "author_stats": author_stats,
        "status_distribution": status_dist,
        "monthly_trend": monthly,
        "keyword_stats": keyword_stats,
    }


if __name__ == "__main__":
    from extract import extract
    out = transform(extract())
    print("\n── Most viewed ──"); print(out["most_viewed"].head())
    print("\n── Top tags ──"); print(out["tag_stats"].head(10))
    print("\n── Search keywords ──"); print(out["keyword_stats"])
