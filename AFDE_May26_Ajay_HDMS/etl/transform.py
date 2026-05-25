"""HDMS Phase 2 — TRANSFORM step. Clean tickets and build analytics aggregations."""
import pandas as pd

VALID_PRIORITIES = {"Low","Medium","High","Critical"}
VALID_STATUSES   = {"Open","In Progress","Resolved","Closed"}

def transform(df: pd.DataFrame) -> dict:
    n0 = len(df)

    # 1. Strip / normalize text
    for col in ["employee_name","department","issue_category","priority","status","description"]:
        df[col] = df[col].astype(str).str.strip()

    # 2. Standardize categories: convert uppercase noise back to Title Case
    df["issue_category"] = df["issue_category"].str.title()
    df["issue_category"] = df["issue_category"].replace({"Vpn Issue":"VPN Issue"})  # acronym fix

    # 3. Drop rows with missing department
    df = df[df["department"].astype(str).str.strip() != ""].copy()
    df = df[df["department"].astype(str).str.lower() != "nan"].copy()

    # 4. Drop rows with invalid priority or status
    df = df[df["priority"].isin(VALID_PRIORITIES) & df["status"].isin(VALID_STATUSES)].copy()

    # 5. Parse dates
    df["created_at"]  = pd.to_datetime(df["created_at"], errors="coerce")
    df["resolved_at"] = pd.to_datetime(df["resolved_at"], errors="coerce")
    df = df.dropna(subset=["created_at"]).copy()

    # 6. Compute resolution_hours where resolved_at is present
    df["resolution_hours"] = ((df["resolved_at"] - df["created_at"]).dt.total_seconds() / 3600).round(2)

    # 7. Remove exact duplicates
    df = df.drop_duplicates(subset=["employee_name","department","issue_category","created_at"])

    n1 = len(df)
    print(f"[TRANSFORM] {n0} → {n1} rows ({n0-n1} dropped)")

    # ── Aggregations ────────────────────────────────────────
    cats = df.groupby("issue_category").agg(
        ticket_count=("issue_category","count"),
        avg_resolution_hours=("resolution_hours", lambda s: round(s.dropna().mean(),2) if s.dropna().size else None),
    ).reset_index().sort_values("ticket_count", ascending=False)

    prio = df["priority"].value_counts().reindex(["Low","Medium","High","Critical"], fill_value=0).reset_index()
    prio.columns = ["priority","count"]

    depts = df.groupby("department").agg(ticket_count=("department","count")).reset_index().sort_values("ticket_count", ascending=False)

    # Monthly trend
    df["month"] = df["created_at"].dt.to_period("M").astype(str)
    monthly = df.groupby("month").agg(
        ticket_count=("month","count"),
        resolved_count=("status", lambda s: int((s.isin(["Resolved","Closed"])).sum())),
        avg_resolution_hours=("resolution_hours", lambda s: round(s.dropna().mean(),2) if s.dropna().size else None),
    ).reset_index().sort_values("month")

    status_counts = df["status"].value_counts().reindex(["Open","In Progress","Resolved","Closed"], fill_value=0).reset_index()
    status_counts.columns = ["status","count"]

    print(f"[TRANSFORM] {len(cats)} categories, {len(depts)} departments, {len(monthly)} months")
    return {
        "cleaned": df, "category_stats": cats, "priority_distribution": prio,
        "department_stats": depts, "monthly_trend": monthly, "status_distribution": status_counts,
    }

if __name__ == "__main__":
    from extract import extract
    out = transform(extract("datasets/tickets_raw.csv"))
    for k,v in out.items():
        if k != "cleaned":
            print(f"\n── {k} ──"); print(v)
