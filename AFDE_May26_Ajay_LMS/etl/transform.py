"""LMS Phase 2 — TRANSFORM step. Clean and build analytics aggregations."""
import pandas as pd
from datetime import datetime, timedelta

OVERDUE_DAYS = 14  # Books not returned within 14 days are overdue


def transform(data: dict) -> dict:
    books, borrowers, txns = data["books"].copy(), data["borrowers"].copy(), data["transactions"].copy()
    n0 = len(txns)

    # Books: strip + Title-case category
    books["title"]    = books["title"].astype(str).str.strip()
    books["author"]   = books["author"].astype(str).str.strip()
    books["category"] = books["category"].astype(str).str.strip().str.title()
    books["category"] = books["category"].replace({"Ai/Ml":"AI/ML"})

    # Borrowers: lowercase emails
    borrowers["email"] = borrowers["email"].astype(str).str.strip().str.lower()

    # Transactions: parse dates
    txns["borrow_date"] = pd.to_datetime(txns["borrow_date"], errors="coerce")
    txns["return_date"] = pd.to_datetime(txns["return_date"], errors="coerce")
    txns = txns.dropna(subset=["borrow_date"]).copy()

    # Drop duplicates
    txns = txns.drop_duplicates(subset=["book_id","borrower_id","borrow_date"])

    # Compute borrow_days and overdue flag
    today = pd.Timestamp(datetime.utcnow())
    txns["borrow_days"] = (txns["return_date"].fillna(today) - txns["borrow_date"]).dt.days
    txns["is_returned"] = txns["return_date"].notna()
    txns["is_overdue"] = (~txns["is_returned"]) & (txns["borrow_days"] > OVERDUE_DAYS)

    n1 = len(txns)
    print(f"[TRANSFORM] Transactions: {n0} → {n1} ({n0-n1} dropped)")

    # ── Aggregations ──
    # Most borrowed books (need book titles → merge)
    books_meta = books.reset_index().rename(columns={"index":"book_id"})
    books_meta["book_id"] = books_meta["book_id"] + 1  # match 1-based IDs from generator
    most_borrowed = txns.groupby("book_id").size().reset_index(name="borrow_count")
    most_borrowed = most_borrowed.merge(books_meta[["book_id","title","author","category"]], on="book_id", how="left")
    most_borrowed = most_borrowed.sort_values("borrow_count", ascending=False).head(15)

    # Category borrowing breakdown
    cat_borrow = most_borrowed.merge(txns[["book_id"]], on="book_id")
    # Simpler: count borrows joined to book category
    txn_cat = txns.merge(books_meta[["book_id","category"]], on="book_id", how="left")
    category_stats = txn_cat.groupby("category").size().reset_index(name="borrow_count").sort_values("borrow_count", ascending=False)

    # Monthly borrowing trend
    txns["month"] = txns["borrow_date"].dt.to_period("M").astype(str)
    monthly = txns.groupby("month").agg(
        borrow_count=("month","count"),
        returned_count=("is_returned","sum"),
    ).reset_index().sort_values("month")

    # Overdue stats
    overdue = txns[txns["is_overdue"]].copy()
    overdue_summary = pd.DataFrame([{
        "total_overdue": int(len(overdue)),
        "total_active": int((~txns["is_returned"]).sum()),
        "total_returned": int(txns["is_returned"].sum()),
        "avg_borrow_days": round(float(txns["borrow_days"].mean()), 2) if len(txns) else 0,
    }])

    # Active overdue list with details
    overdue_detail = overdue.merge(books_meta[["book_id","title","author"]], on="book_id", how="left")[
        ["book_id","title","author","borrower_id","borrow_date","borrow_days"]].sort_values("borrow_days", ascending=False).head(20)

    print(f"[TRANSFORM] {len(most_borrowed)} top books, {len(category_stats)} categories, {len(overdue)} overdue")
    return {
        "cleaned_transactions": txns.drop(columns=["month"]),
        "most_borrowed": most_borrowed,
        "category_stats": category_stats,
        "monthly_trend": monthly,
        "overdue_summary": overdue_summary,
        "overdue_detail": overdue_detail,
    }


if __name__ == "__main__":
    from extract import extract
    out = transform(extract())
    print("\n── Most borrowed (top 5) ──"); print(out["most_borrowed"].head())
    print("\n── Category stats ──"); print(out["category_stats"])
    print("\n── Overdue summary ──"); print(out["overdue_summary"])
