# CCRTS Phase 2 — ETL Pipeline & SLA / Agent Analytics

Extension to Phase 1 Customer Complaint & Resolution Tracking System adding **SLA reports, complaint trends, and agent performance analytics**.

---

## 📦 Phase 2 Deliverables

```
CCRTS/
├── etl/
│   ├── generate_dataset.py   # 250+ complaints
│   ├── extract.py
│   ├── transform.py          # SLA calc + 6 aggregations
│   ├── load.py
│   └── run_etl.py
├── datasets/
│   └── complaints_raw.csv    # 260 records
├── backend/routers/analytics.py
└── frontend/src/pages/Analytics.js
```

## 🔄 ETL Workflow

**Source:** 260 complaint records containing UPPERCASE noise, blank priorities/statuses, and 10 duplicates.

**SLA Hours per priority:** Low=72h, Medium=48h, High=24h, Critical=4h.

### EXTRACT → TRANSFORM → LOAD
1. **EXTRACT** — pandas reads `complaints_raw.csv`
2. **TRANSFORM:**
   - Strip + Title-case `category`
   - Drop rows with invalid priority/status
   - Parse `created_at`, `sla_deadline`, `resolved_at`
   - Compute `resolution_hours`
   - Flag `sla_breached`:
     - `resolved_at > sla_deadline` (resolved late), OR
     - Currently unresolved AND `now > sla_deadline` AND status ≠ Resolved/Closed
   - Flag `is_resolved` (status ∈ Resolved/Closed)
   - Drop duplicates (by complaint_number)
3. **LOAD** — Writes to `ccrts.db`:
   - `analytics_complaints_clean`
   - `analytics_category_stats` (count + avg resolution + breach count)
   - `analytics_priority_dist`
   - `analytics_status_dist`
   - `analytics_sla_report` (per-priority total/breached/breach_rate)
   - `analytics_monthly_trend`
   - `analytics_agent_performance` (assigned/resolved/breached/resolution_rate)
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

Expected: `260 → 243 records (17 dropped); 7 categories, 8 agents`

Add to `frontend/src/App.js`:
```jsx
import Analytics from "./pages/Analytics";
<Route path="/analytics" element={<Analytics />} />
```
And in `Sidebar.js`: `<NavLink to="/analytics">📈 Analytics</NavLink>`

---

## 📊 Analytics Dashboard
- KPIs: total complaints, resolved, SLA breached, breach rate %, avg resolution hours
- 🚨 SLA breach rate by priority
- ⚠️ Priority distribution
- 📊 Category analysis (with breach counts)
- 📌 Status distribution
- 📅 Monthly trend (complaints vs SLA breaches dual line)
- 👤 Agent performance table (resolution_rate %, breaches, avg hours)

## 📚 API Endpoints
| Method | Endpoint |
|--------|----------|
| GET | /analytics/category-stats |
| GET | /analytics/priority-distribution |
| GET | /analytics/status-distribution |
| GET | /analytics/sla-report |
| GET | /analytics/monthly-trend |
| GET | /analytics/agent-performance |
| GET | /analytics/summary |
| POST | /analytics/run-etl |

**All endpoints require JWT** (uses existing `get_current_user` dependency).

Repo naming: `AFDE_Jan26_<YourName>_CCRTS`
