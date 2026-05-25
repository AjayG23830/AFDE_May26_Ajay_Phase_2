/**
 * LMS Phase 2 — Analytics Page
 * Drop into frontend/src/pages/Analytics.js
 * Add to App.js: <Route path="/analytics" element={<Analytics />} />
 * Add NavLink: <NavLink to="/analytics">Analytics</NavLink>
 */
import React, { useEffect, useState } from "react";
import axios from "axios";
const API = "http://localhost:8000";

function Bar({ label, value, max, color = "#16a34a", suffix = "" }) {
  const pct = max > 0 ? (value / max) * 100 : 0;
  return (
    <div style={{ marginBottom: "0.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "0.2rem" }}>
        <span style={{ fontWeight: 600 }}>{label}</span>
        <span style={{ color: "#64748b" }}>{value}{suffix}</span>
      </div>
      <div style={{ height: 12, background: "#f1f5f9", borderRadius: 8, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: color, transition: "width 0.4s" }} />
      </div>
    </div>
  );
}

function DualBarChart({ data, height = 240 }) {
  if (!data.length) return <p style={{ color: "#94a3b8" }}>No data</p>;
  const max = Math.max(...data.map(d => Math.max(d.borrow_count, d.returned_count)), 1);
  const W = Math.max(data.length * 70, 400);
  const H = height; const pad = 40;
  const groupW = (W - 2 * pad) / data.length;
  const barW = groupW * 0.35;
  return (
    <div style={{ overflowX: "auto" }}>
      <svg width={W} height={H}>
        <line x1={pad} y1={H - pad} x2={W - pad} y2={H - pad} stroke="#cbd5e1" />
        {data.map((d, i) => {
          const cx = pad + i * groupW + groupW / 2;
          const bh = (d.borrow_count / max) * (H - 2 * pad);
          const rh = (d.returned_count / max) * (H - 2 * pad);
          return (
            <g key={i}>
              <rect x={cx - barW} y={H - pad - bh} width={barW} height={bh} fill="#2563eb" />
              <rect x={cx + 2} y={H - pad - rh} width={barW} height={rh} fill="#16a34a" />
              <text x={cx} y={H - pad + 14} textAnchor="middle" fontSize="10" fill="#64748b">{d.month}</text>
              <text x={cx - barW / 2} y={H - pad - bh - 4} textAnchor="middle" fontSize="9" fontWeight="600">{d.borrow_count}</text>
              <text x={cx + 2 + barW / 2} y={H - pad - rh - 4} textAnchor="middle" fontSize="9" fontWeight="600" fill="#16a34a">{d.returned_count}</text>
            </g>
          );
        })}
        <g transform={`translate(${pad}, 10)`}>
          <rect width="12" height="12" fill="#2563eb" /><text x="18" y="10" fontSize="10">Borrowed</text>
          <rect x="80" width="12" height="12" fill="#16a34a" /><text x="98" y="10" fontSize="10">Returned</text>
        </g>
      </svg>
    </div>
  );
}

function Analytics() {
  const [summary, setSummary] = useState(null);
  const [topBooks, setTopBooks] = useState([]);
  const [cats, setCats] = useState([]);
  const [trend, setTrend] = useState([]);
  const [overdueSum, setOverdueSum] = useState(null);
  const [overdueList, setOverdueList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [msg, setMsg] = useState({ type: "", text: "" });

  const load = async () => {
    setLoading(true);
    try {
      const [s, b, c, t, os, ol] = await Promise.all([
        axios.get(`${API}/analytics/summary`),
        axios.get(`${API}/analytics/most-borrowed`),
        axios.get(`${API}/analytics/category-borrow`),
        axios.get(`${API}/analytics/monthly-trend`),
        axios.get(`${API}/analytics/overdue-summary`),
        axios.get(`${API}/analytics/overdue-list`),
      ]);
      setSummary(s.data); setTopBooks(b.data); setCats(c.data); setTrend(t.data); setOverdueSum(os.data); setOverdueList(ol.data);
    } catch { setMsg({ type: "error", text: "Failed to load. Run the ETL first." }); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const triggerETL = async () => {
    setRunning(true); setMsg({ type: "", text: "" });
    try { await axios.post(`${API}/analytics/run-etl`); setMsg({ type: "success", text: "ETL completed!" }); await load(); }
    catch (err) { setMsg({ type: "error", text: err.response?.data?.detail || "ETL failed" }); }
    finally { setRunning(false); }
  };

  if (loading) return <div className="loading">⏳ Loading...</div>;

  const maxBook = Math.max(...topBooks.map(b => b.borrow_count), 1);
  const maxCat = Math.max(...cats.map(c => c.borrow_count), 1);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700 }}>📈 Library Analytics</h1>
          <p style={{ color: "#64748b", fontSize: "0.9rem" }}>Borrowing trends & overdue analysis from cleaned data</p>
        </div>
        <button className="btn btn-primary" onClick={triggerETL} disabled={running}>{running ? "⏳ Running..." : "🔄 Run ETL"}</button>
      </div>
      {msg.text && <div className={`alert alert-${msg.type === "error" ? "error" : "success"}`}>{msg.text}</div>}

      {summary && overdueSum && (
        <div className="stats-grid" style={{ marginBottom: "1.5rem" }}>
          <div className="stat-card s-blue"><div className="stat-icon">📚</div><div className="stat-value">{summary.total_clean_transactions}</div><div className="stat-label">Total Transactions</div></div>
          <div className="stat-card s-green"><div className="stat-icon">✅</div><div className="stat-value">{overdueSum.total_returned}</div><div className="stat-label">Returned</div></div>
          <div className="stat-card s-orange"><div className="stat-icon">⏳</div><div className="stat-value">{overdueSum.total_active}</div><div className="stat-label">Active</div></div>
          <div className="stat-card s-red"><div className="stat-icon">⚠️</div><div className="stat-value">{overdueSum.total_overdue}</div><div className="stat-label">Overdue</div></div>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>🔥 Most Borrowed Books</h3>
          {topBooks.slice(0, 10).map(b => <Bar key={b.book_id} label={`${b.title} — ${b.author}`} value={b.borrow_count} max={maxBook} color="#2563eb" />)}
        </div>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>📂 Category-wise Borrowing</h3>
          {cats.map(c => <Bar key={c.category} label={c.category} value={c.borrow_count} max={maxCat} color="#7c3aed" />)}
        </div>
      </div>

      <div className="card" style={{ marginBottom: "1rem" }}>
        <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>📅 Monthly Borrowing vs Returns</h3>
        <DualBarChart data={trend} />
      </div>

      <div className="card">
        <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>⚠️ Overdue Books (Top 20)</h3>
        {overdueList.length === 0 ? <p style={{ color: "#94a3b8" }}>No overdue books! 🎉</p> : (
          <div className="table-wrap"><table>
            <thead><tr><th>Book</th><th>Author</th><th>Borrower ID</th><th>Borrowed</th><th>Days Overdue</th></tr></thead>
            <tbody>{overdueList.map((r, i) => (
              <tr key={i}>
                <td><strong>{r.title}</strong></td><td>{r.author}</td><td>#{r.borrower_id}</td>
                <td>{new Date(r.borrow_date).toLocaleDateString("en-IN")}</td>
                <td style={{ color: "#dc2626", fontWeight: 700 }}>{r.borrow_days - 14} days</td>
              </tr>
            ))}</tbody>
          </table></div>
        )}
      </div>
    </div>
  );
}

export default Analytics;
