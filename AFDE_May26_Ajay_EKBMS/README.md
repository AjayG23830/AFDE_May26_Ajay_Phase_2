# EKBMS Phase 2 — ETL Pipeline & Article / Search Analytics

Extension to Phase 1 Enterprise Knowledge Base Management System adding **article indexing, popularity tracking, and search keyword analysis**.

---

## 📦 Phase 2 Deliverables

```
EKBMS/
├── etl/
│   ├── generate_dataset.py   # 120 articles + 400 search log entries
│   ├── extract.py            # reads 2 CSVs
│   ├── transform.py          # 7 aggregations
│   ├── load.py               # SQLite writer
│   └── run_etl.py            # orchestrator
├── datasets/
│   ├── articles_raw.csv      # 125 article records
│   └── search_log_raw.csv    # 400 search log entries
├── backend/routers/analytics.py
└── frontend/src/pages/Analytics.js
```

## 🔄 ETL Workflow

**Sources:**
- `articles_raw.csv` — 125 articles with title, category, tags (pipe-separated), author, status, view_count
- `search_log_raw.csv` — 400 search keyword logs (keyword + timestamp)

### EXTRACT → TRANSFORM → LOAD
1. **EXTRACT** — pandas reads both CSVs
2. **TRANSFORM:**
   - Strip + Title-case categories
   - Coerce `view_count` to int
   - Drop rows with invalid status
   - Parse `created_at`
   - Drop duplicates (title + author + created_at)
   - **Tag explosion:** split pipe-separated tags → row-per-tag for frequency analysis
   - Lowercase keywords in search log
3. **LOAD** — Writes to `ekbms.db`:
   - `analytics_articles_clean`
   - `analytics_most_viewed` (top 15 approved articles)
   - `analytics_category_usage` (article count, total views, avg views)
   - `analytics_tag_stats` (top 20 tags by frequency)
   - `analytics_author_stats` (articles written, approved count, total views)
   - `analytics_article_status_dist`
   - `analytics_monthly_articles`
   - `analytics_keyword_stats` (top 15 search terms)
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

Expected: `125 articles → ~120 clean; tag explosion populates 15-20 unique tags`

Add to `frontend/src/App.js`:
```jsx
import Analytics from "./pages/Analytics";
<Route path="/analytics" element={<Analytics />} />
```
Add to `Sidebar.js`: `<NavLink to="/analytics">📈 Analytics</NavLink>`

---

## 📊 Analytics Dashboard
- KPIs: total articles, total views, authors, categories
- 🔥 Most viewed articles (top 10)
- 📂 Category usage (article count + total views)
- ✍️ Author activity (articles + approved)
- 📊 Article status distribution
- 🏷️ **Tag cloud** (size + opacity proportional to usage)
- 🔎 Top search keywords (from search log)
- 📅 Monthly publication trend

## 📚 API Endpoints
| Method | Endpoint |
|--------|----------|
| GET | /analytics/most-viewed |
| GET | /analytics/category-usage |
| GET | /analytics/tag-stats |
| GET | /analytics/author-stats |
| GET | /analytics/status-distribution |
| GET | /analytics/monthly-trend |
| GET | /analytics/keyword-stats |
| GET | /analytics/summary |
| POST | /analytics/run-etl |

**All endpoints require JWT** (uses existing `get_current_user` dependency).

Repo naming: `AFDE_Jan26_<YourName>_EKBMS`
