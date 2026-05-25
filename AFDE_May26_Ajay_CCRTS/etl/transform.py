"""CCRTS Phase 2 — TRANSFORM. Clean and build SLA + complaint analytics."""
import pandas as pd
from datetime import datetime

VALID_PRIORITIES = {"Low","Medium","High","Critical"}
VALID_STATUSES = {"Open","Assigned","In Progress","Pending Customer Response","Escalated","Resolved","Closed"}


def transform(df: pd.DataFrame) -> dict:
    n0 = len(df)

    # Normalize text
    for col in ["category","priority","status","agent_name","title","complaint_number"]:
        df[col] = df[col].fillna("").astype(str).str.strip()
    df["category"] = df["category"].str.title()

    # Drop rows with missing priority or status
    df = df[df["priority"].isin(VALID_PRIORITIES) & df["status"].isin(VALID_STATUSES)].copy()

    # Parse dates
    for c in ["created_at","sla_deadline","resolved_at"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    df = df.dropna(subset=["created_at","sla_deadline"]).copy()

    # Compute resolution time + SLA breach
    df["resolution_hours"] = ((df["resolved_at"] - df["created_at"]).dt.total_seconds() / 3600).round(2)
    df["sla_breached"] = (df["resolved_at"].notna() & (df["resolved_at"] > df["sla_deadline"])) | \
                        (df["resolved_at"].isna() & (pd.Timestamp(datetime.utcnow()) > df["sla_deadline"]) & ~df["status"].isin(["Resolved","Closed"]))
    df["is_resolved"] = df["status"].isin(["Resolved","Closed"])

    # Drop duplicates
    df = df.drop_duplicates(subset=["complaint_number"])

    n1 = len(df)
    print(f"[TRANSFORM] {n0} → {n1} rows ({n0-n1} dropped)")

    # ── Aggregations ──
    # 1. Category analysis
    cat_stats = df.groupby("category").agg(
        complaint_count=("category","count"),
        avg_resolution_hours=("resolution_hours", lambda s: round(s.dropna().mean(),2) if s.dropna().size else None),
        sla_breach_count=("sla_breached","sum"),
    ).reset_index().sort_values("complaint_count", ascending=False)

    # 2. Priority distribution
    prio_dist = df["priority"].value_counts().reindex(["Low","Medium","High","Critical"], fill_value=0).reset_index()
    prio_dist.columns = ["priority","count"]

    # 3. Status distribution
    status_dist = df["status"].value_counts().reset_index()
    status_dist.columns = ["status","count"]

    # 4. SLA breach report (per priority)
    sla_report = df.groupby("priority").agg(
        total=("priority","count"),
        breached=("sla_breached","sum"),
    ).reset_index()
    sla_report["breach_rate"] = (sla_report["breached"] / sla_report["total"] * 100).round(2)
    sla_report = sla_report.reindex(columns=["priority","total","breached","breach_rate"])

    # 5. Resolution time trend by month
    df["month"] = df["created_at"].dt.to_period("M").astype(str)
    monthly = df.groupby("month").agg(
        complaint_count=("month","count"),
        resolved_count=("is_resolved","sum"),
        breach_count=("sla_breached","sum"),
        avg_resolution_hours=("resolution_hours", lambda s: round(s.dropna().mean(),2) if s.dropna().size else None),
    ).reset_index().sort_values("month")

    # 6. Agent performance
    agent_df = df[df["agent_name"] != ""].copy()
    agent_perf = agent_df.groupby("agent_name").agg(
        total_assigned=("agent_name","count"),
        resolved=("is_resolved","sum"),
        breached=("sla_breached","sum"),
        avg_resolution_hours=("resolution_hours", lambda s: round(s.dropna().mean(),2) if s.dropna().size else None),
    ).reset_index()
    agent_perf["resolution_rate"] = (agent_perf["resolved"] / agent_perf["total_assigned"] * 100).round(2)
    agent_perf = agent_perf.sort_values("resolution_rate", ascending=False)

    print(f"[TRANSFORM] {len(cat_stats)} categories, {len(agent_perf)} agents, {len(monthly)} months")
    return {
        "cleaned": df,
        "category_stats": cat_stats,
        "priority_distribution": prio_dist,
        "status_distribution": status_dist,
        "sla_report": sla_report,
        "monthly_trend": monthly,
        "agent_performance": agent_perf,
    }


if __name__ == "__main__":
    from extract import extract
    out = transform(extract())
    for k,v in out.items():
        if k != "cleaned": print(f"\n── {k} ──"); print(v)
