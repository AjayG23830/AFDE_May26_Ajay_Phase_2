# Capstone Phase 2 — ETL Pipelines for All 5 Projects

This package contains **Phase 2 ETL extensions** for all 5 Phase 1 capstone projects:

| Project | Focus |
|---------|-------|
| **FMS** | Feedback analytics — ratings, programs, monthly trend |
| **HDMS** | Ticket analytics — categories, priority, departments, monthly |
| **LMS** | Borrowing analytics — most borrowed, categories, overdue, monthly |
| **CCRTS** | Complaint analytics — SLA breaches, agent performance, categories |
| **EKBMS** | KB analytics — most viewed, tag cloud, authors, search keywords |

---

## 🏗 Common Architecture (all 5)

```
<PROJECT>/
├── etl/                          # Python + Pandas ETL pipeline
│   ├── generate_dataset.py       # creates realistic dirty sample data
│   ├── extract.py                # EXTRACT step
│   ├── transform.py              # TRANSFORM step (cleaning + aggregations)
│   ├── load.py                   # LOAD step (writes to SQLite)
│   └── run_etl.py                # Orchestrator (E → T → L)
├── datasets/                     # Source CSV files (100-260 records each)
├── backend/
│   ├── routers/analytics.py      # FastAPI analytics routes
│   └── main_patch.py             # 2-line wire-up instructions
├── frontend/src/pages/Analytics.js # React dashboard with charts
└── README.md                     # ETL workflow doc + setup
```

## 🚀 Quick Start (any project)

1. **Drop the Phase 2 files into the matching Phase 1 project folder**
2. **Install Pandas:** `pip install pandas openpyxl`
3. **Wire up the router** in Phase 1's `backend/main.py`:
   ```python
   from routers import analytics
   app.include_router(analytics.router)
   ```
4. **Run the ETL:**
   ```bash
   cd etl
   python run_etl.py
   ```
5. **Add the Analytics page** to your React `App.js`:
   ```jsx
   import Analytics from "./pages/Analytics";
   <Route path="/analytics" element={<Analytics />} />
   ```
6. **Visit** http://localhost:3000/analytics and click **🔄 Run ETL** to re-trigger from UI.

---

## ✅ Phase 2 Compliance Checklist (per project)

- [x] Python ETL scripts using Pandas
- [x] CSV datasets as input sources (Excel-compatible via `openpyxl`)
- [x] Clearly separated Extract / Transform / Load stages
- [x] Cleaned data in analytics/reporting tables (`analytics_*`)
- [x] Frontend dashboards reading from analytics tables
- [x] datasets/ folder with source data
- [x] README with ETL workflow explanation
- [ ] Daily GitHub commits (your responsibility)
- [ ] Submit screenshots of ETL execution + dashboards (your responsibility)

---

## 📦 Sample Dataset Sizes

| Project | Source Files | Records |
|---------|-------------|---------|
| FMS | `feedback_raw.csv` | 155 |
| HDMS | `tickets_raw.csv` | 228 |
| LMS | `books_raw.csv`, `borrowers_raw.csv`, `transactions_raw.csv` | 30 + 30 + 188 |
| CCRTS | `complaints_raw.csv` | 260 |
| EKBMS | `articles_raw.csv`, `search_log_raw.csv` | 125 + 400 |

Each dataset includes **intentional dirty data** (whitespace, invalid values, uppercase noise, duplicates) so the transform stage has something to actually do.

---

## 🎓 Submission Timeline
3 days per common Phase 2 instructions.

Repo naming: `AFDE_Jan26_<YourName>_<ProjectCode>`
