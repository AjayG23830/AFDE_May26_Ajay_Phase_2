/**
 * HDMS Phase 2 — Analytics Page
 * Wire-up:
 *   1. Drop into frontend/src/pages/Analytics.js
 *   2. In App.js add: import Analytics from "./pages/Analytics";
 *      <Route path="/analytics" element={<Analytics />} />
 *   3. Add NavLink: <NavLink to="/analytics">Analytics</NavLink>
 */
import React, { useEffect, useState } from "react";
import axios from "axios";
const API = "http://localhost:8000";

function Bar({ label, value, max, color = "#2563eb", suffix = "" }) {
  const pct = max > 0 ? (value / max) * 100 : 0;
  return (
    <div style={{ marginBottom: "0.6rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "0.2rem" }}>
        <span style={{ fontWeight: 600 }}>{label}</span>
        <span style={{ color: "#64748b" }}>{value}{suffix}</span>
      </div>
      <div style={{ height: 14, background: "#f1f5f9", borderRadius: 8, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: color, transition: "width 0.4s" }} />
      </div>
    </div>
  );
}

function LineChart({ data, valueKey = "ticket_count", height = 200 }) {
  if (!data.length) return <p style={{ color: "#94a3b8" }}>No data</p>;
  const max = Math.max(...data.map(d => d[valueKey] || 0));
  const W = Math.max(data.length * 60, 400);
  const H = height; const pad = 35;
  const points = data.map((d, i) => {
    const x = pad + (i * (W - 2 * pad)) / Math.max(data.length - 1, 1);
    const y = H - pad - ((d[valueKey] / max) * (H - 2 * pad));
    return { x, y, ...d };
  });
  const path = points.map((p, i) => (i === 0 ? "M" : "L") + p.x + " " + p.y).join(" ");
  return (
    <div style={{ overflowX: "auto" }}>
      <svg width={W} height={H} style={{ display: "block" }}>
        <line x1={pad} y1={H - pad} x2={W - pad} y2={H - pad} stroke="#cbd5e1" />
        <line x1={pad} y1={pad} x2={pad} y2={H - pad} stroke="#cbd5e1" />
        <path d={path} fill="none" stroke="#2563eb" strokeWidth="2" />
        {points.map((p, i) => (
          <g key={i}>
            <circle cx={p.x} cy={p.y} r="4" fill="#2563eb" />
            <text x={p.x} y={H - pad + 15} textAnchor="middle" fontSize="10" fill="#64748b">{p.month}</text>
            <text x={p.x} y={p.y - 8} textAnchor="middle" fontSize="10" fontWeight="600">{p[valueKey]}</text>
          </g>
        ))}
      </svg>
    </div>
  );
}

const PRIO_COLOR = { Low: "#16a34a", Medium: "#d97706", High: "#ea580c", Critical: "#dc2626" };
const STATUS_COLOR = { Open: "#2563eb", "In Progress": "#d97706", Resolved: "#16a34a", Closed: "#64748b" };

function Analytics() {
  const [summary, setSummary] = useState(null);
  const [cats, setCats] = useState([]);
  const [prio, setPrio] = useState([]);
  const [depts, setDepts] = useState([]);
  const [trend, setTrend] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [msg, setMsg] = useState({ type: "", text: "" });

  const load = async () => {
    setLoading(true);
    try {
      const [s, c, p, d, t, st] = await Promise.all([
        axios.get(`${API}/analytics/summary`),
        axios.get(`${API}/analytics/category-stats`),
        axios.get(`${API}/analytics/priority-distribution`),
        axios.get(`${API}/analytics/department-stats`),
        axios.get(`${API}/analytics/monthly-trend`),
        axios.get(`${API}/analytics/status-distribution`),
      ]);
      setSummary(s.data); setCats(c.data); setPrio(p.data); setDepts(d.data); setTrend(t.data); setStatuses(st.data);
    } catch { setMsg({ type: "error", text: "Failed to load. Run the ETL first." }); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const triggerETL = async () => {
    setRunning(true); setMsg({ type: "", text: "" });
    try {
      await axios.post(`${API}/analytics/run-etl`);
      setMsg({ type: "success", text: "ETL completed!" });
      await load();
    } catch (err) { setMsg({ type: "error", text: err.response?.data?.detail || "ETL failed" }); }
    finally { setRunning(false); }
  };

  if (loading) return <div className="loading">⏳ Loading...</div>;

  const maxCat = Math.max(...cats.map(c => c.ticket_count), 1);
  const maxPrio = Math.max(...prio.map(p => p.count), 1);
  const maxDept = Math.max(...depts.map(d => d.ticket_count), 1);
  const maxStatus = Math.max(...statuses.map(s => s.count), 1);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700 }}>📈 Ticket Analytics</h1>
          <p style={{ color: "#64748b", fontSize: "0.9rem" }}>ETL-powered insights from historical tickets</p>
        </div>
        <button className="btn btn-primary" onClick={triggerETL} disabled={running}>{running ? "⏳ Running..." : "🔄 Run ETL"}</button>
      </div>
      {msg.text && <div className={`alert alert-${msg.type === "error" ? "error" : "success"}`}>{msg.text}</div>}

      {summary && (
        <div className="stats-grid" style={{ marginBottom: "1.5rem" }}>
          <div className="stat-card s-blue"><div className="stat-icon">🎫</div><div className="stat-value">{summary.total_clean_tickets}</div><div className="stat-label">Clean Tickets</div></div>
          <div className="stat-card s-orange"><div className="stat-icon">⏱️</div><div className="stat-value">{summary.avg_resolution_hours}h</div><div className="stat-label">Avg Resolution</div></div>
          <div className="stat-card s-purple"><div className="stat-icon">🏷️</div><div className="stat-value">{summary.total_categories}</div><div className="stat-label">Categories</div></div>
          <div className="stat-card s-gray"><div className="stat-icon">🏢</div><div className="stat-value">{summary.total_departments}</div><div className="stat-label">Departments</div></div>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>🔥 Top Issue Categories</h3>
          {cats.map(c => <Bar key={c.issue_category} label={`${c.issue_category} (avg ${c.avg_resolution_hours||"-"}h)`} value={c.ticket_count} max={maxCat} />)}
        </div>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>⚠️ Priority Distribution</h3>
          {prio.map(p => <Bar key={p.priority} label={p.priority} value={p.count} max={maxPrio} color={PRIO_COLOR[p.priority]} />)}
        </div>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>🏢 Department-wise Tickets</h3>
          {depts.map(d => <Bar key={d.department} label={d.department} value={d.ticket_count} max={maxDept} color="#7c3aed" />)}
        </div>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>📊 Status Distribution</h3>
          {statuses.map(s => <Bar key={s.status} label={s.status} value={s.count} max={maxStatus} color={STATUS_COLOR[s.status]} />)}
        </div>
      </div>

      <div className="card">
        <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>📅 Monthly Ticket Trend</h3>
        <LineChart data={trend} />
      </div>
    </div>
  );
}

export default Analytics;
