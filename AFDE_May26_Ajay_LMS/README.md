# LMS Phase 2 — ETL Pipeline & Borrowing Analytics

Extension to Phase 1 Library Management System adding **borrowing trends and overdue analytics**.

---

## 📦 Phase 2 Deliverables

```
LMS/
├── etl/
│   ├── generate_dataset.py   # 30 books + 30 borrowers + 188 transactions
│   ├── extract.py            # reads 3 CSVs
│   ├── transform.py          # cleans + 5 aggregations + overdue calc
│   ├── load.py               # SQLite writer
│   └── run_etl.py            # orchestrator
├── datasets/
│   ├── books_raw.csv
│   ├── borrowers_raw.csv
│   └── transactions_raw.csv
├── backend/routers/analytics.py
└── frontend/src/pages/Analytics.js
```

## 🔄 ETL Workflow

**Sources:** 3 CSV files — books, borrowers, transactions (188 rows + 8 duplicates).
**Overdue rule:** Books not returned within **14 days** are flagged.

### EXTRACT → TRANSFORM → LOAD
1. **EXTRACT** — reads all 3 CSVs into a dict of DataFrames
2. **TRANSFORM:**
   - Normalize book categories (Title Case, `Ai/Ml → AI/ML`)
   - Lowercase borrower emails
   - Parse `borrow_date` / `return_date`
   - Compute `borrow_days = return_date OR today - borrow_date`
   - Flag `is_returned`, `is_overdue` (>14 days unreturned)
   - Drop duplicates
3. **LOAD** — Writes to `lms.db`:
   - `analytics_transactions_clean`
   - `analytics_most_borrowed` (top 15 books)
   - `analytics_category_borrow`
   - `analytics_monthly_borrow` (borrow vs returned by month)
   - `analytics_overdue_summary` + `analytics_overdue_detail`
   - `etl_runs`

---

## 🚀 How to Run

```bash
pip install pandas openpyxl

# Wire up backend/main.py:
#   from routers import analytics
#   app.include_router(analytics.router)

cd etl
python generate_dataset.py
python run_etl.py
```

Expected: `188 → 180 transactions; 15 top books, 10 categories, 54 overdue`

Add to `frontend/src/App.js`:
```jsx
import Analytics from "./pages/Analytics";
<Route path="/analytics" element={<Analytics />} />
```

---

## 📊 Analytics Dashboard
- KPIs: total transactions, returned, active, overdue
- 🔥 Most borrowed books (top 10)
- 📂 Category-wise borrowing
- 📅 Monthly borrowing vs returns (dual-bar chart)
- ⚠️ Overdue books list (sorted by days overdue)

## 📚 API Endpoints
| Method | Endpoint |
|--------|----------|
| GET | /analytics/most-borrowed |
| GET | /analytics/category-borrow |
| GET | /analytics/monthly-trend |
| GET | /analytics/overdue-summary |
| GET | /analytics/overdue-list |
| GET | /analytics/summary |
| POST | /analytics/run-etl |

Repo naming: `AFDE_Jan26_<YourName>_LMS`
