# HDMS Phase 2 — ETL Pipeline & Ticket Analytics

Extension to Phase 1 Helpdesk Ticket Management System adding **historical ticket analytics**.

---

## 📦 Phase 2 Deliverables

```
HDMS/
├── etl/
│   ├── generate_dataset.py   # creates 220+ sample tickets
│   ├── extract.py            # CSV/Excel reader
│   ├── transform.py          # cleaning + 6 aggregations
│   ├── load.py               # SQLite writer
│   └── run_etl.py            # orchestrator
├── datasets/
│   └── tickets_raw.csv       # 228 tickets (with intentional noise)
├── backend/routers/analytics.py
└── frontend/src/pages/Analytics.js
```

## 🔄 ETL Workflow

**Source:** `tickets_raw.csv` with 228 records containing UPPERCASE category noise, blank departments, missing priority/status, and 8 duplicate rows.

### EXTRACT → TRANSFORM → LOAD
1. **EXTRACT** — pandas reads CSV/Excel
2. **TRANSFORM:**
   - Strip whitespace, Title-case categories (`VPN Issue` preserved as acronym)
   - Drop rows with missing department, invalid priority/status
   - Parse `created_at` and `resolved_at`
   - Compute `resolution_hours = resolved_at - created_at`
   - Drop duplicates
3. **LOAD** — Writes to `hdms.db`:
   - `analytics_tickets_clean`
   - `analytics_category_stats` (count + avg resolution hrs)
   - `analytics_priority_dist`
   - `analytics_department_stats`
   - `analytics_status_dist`
   - `analytics_monthly_trend`
   - `etl_runs`

---

## 🚀 How to Run

```bash
pip install pandas openpyxl

# Wire up: add to backend/main.py
#   from routers import analytics
#   app.include_router(analytics.router)

cd etl
python generate_dataset.py    # one-time
python run_etl.py             # E→T→L
```

Verified output: `228 → 220 rows (8 dropped); 7 categories, 9 departments, 14 months`

Then in App.js:
```jsx
import Analytics from "./pages/Analytics";
<Route path="/analytics" element={<Analytics />} />
```

---

## 📊 Analytics Dashboard
- KPIs: clean tickets, avg resolution hours, total categories, departments
- Top issue categories (with avg resolution time)
- Priority distribution (Low → Critical)
- Department-wise ticket volume
- Status distribution
- Monthly ticket trend (line chart)

## 📚 API Endpoints
| Method | Endpoint |
|--------|----------|
| GET | /analytics/category-stats |
| GET | /analytics/priority-distribution |
| GET | /analytics/department-stats |
| GET | /analytics/status-distribution |
| GET | /analytics/monthly-trend |
| GET | /analytics/summary |
| POST | /analytics/run-etl |

Repo naming: `AFDE_Jan26_<YourName>_HDMS`
