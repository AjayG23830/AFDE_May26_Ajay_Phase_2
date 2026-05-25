/**
 * EKBMS Phase 2 — Analytics Page
 * Drop into frontend/src/pages/Analytics.js
 * In App.js add: <Route path="/analytics" element={<Analytics />} />
 * In Sidebar.js add: <NavLink to="/analytics">📈 Analytics</NavLink>
 * Uses existing api.js (which injects JWT token automatically).
 */
import React, { useEffect, useState } from "react";
import api from "../services/api";

function Bar({ label, value, max, color = "#7c3aed", suffix = "" }) {
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

function LineChart({ data, valueKey = "articles_created", height = 220 }) {
  if (!data.length) return <p style={{ color: "#94a3b8" }}>No data</p>;
  const max = Math.max(...data.map(d => d[valueKey] || 0), 1);
  const W = Math.max(data.length * 60, 400);
  const H = height; const pad = 40;
  const points = data.map((d, i) => {
    const x = pad + (i * (W - 2 * pad)) / Math.max(data.length - 1, 1);
    const y = H - pad - ((d[valueKey] / max) * (H - 2 * pad));
    return { x, y, ...d };
  });
  const path = points.map((p, i) => (i === 0 ? "M" : "L") + p.x + " " + p.y).join(" ");
  return (
    <div style={{ overflowX: "auto" }}>
      <svg width={W} height={H}>
        <line x1={pad} y1={H - pad} x2={W - pad} y2={H - pad} stroke="#cbd5e1" />
        <line x1={pad} y1={pad} x2={pad} y2={H - pad} stroke="#cbd5e1" />
        <path d={path} fill="none" stroke="#7c3aed" strokeWidth="2" />
        {points.map((p, i) => (
          <g key={i}>
            <circle cx={p.x} cy={p.y} r="4" fill="#7c3aed" />
            <text x={p.x} y={H - pad + 14} textAnchor="middle" fontSize="9" fill="#64748b">{p.month}</text>
            <text x={p.x} y={p.y - 8} textAnchor="middle" fontSize="9" fontWeight="600">{p[valueKey]}</text>
          </g>
        ))}
      </svg>
    </div>
  );
}

function TagCloud({ tags }) {
  if (!tags.length) return <p style={{ color: "#94a3b8" }}>No tags</p>;
  const max = Math.max(...tags.map(t => t.usage_count), 1);
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", padding: "0.5rem" }}>
      {tags.map(t => {
        const size = 0.75 + (t.usage_count / max) * 0.9;
        const opacity = 0.5 + (t.usage_count / max) * 0.5;
        return (
          <span key={t.tag} style={{
            fontSize: `${size}rem`, fontWeight: 700, color: "#5b21b6",
            background: "#ede9fe", padding: "0.25rem 0.7rem", borderRadius: 20,
            opacity, transition: "all 0.3s"
          }}>
            #{t.tag} <span style={{ color: "#94a3b8", fontSize: "0.7rem" }}>({t.usage_count})</span>
          </span>
        );
      })}
    </div>
  );
}

function Analytics() {
  const [summary, setSummary] = useState(null);
  const [topArts, setTopArts] = useState([]);
  const [cats, setCats] = useState([]);
  const [tags, setTags] = useState([]);
  const [authors, setAuthors] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [trend, setTrend] = useState([]);
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [msg, setMsg] = useState({ type: "", text: "" });

  const load = async () => {
    setLoading(true);
    try {
      const [s, m, c, t, a, st, tr, kw] = await Promise.all([
        api.get("/analytics/summary"),
        api.get("/analytics/most-viewed"),
        api.get("/analytics/category-usage"),
        api.get("/analytics/tag-stats"),
        api.get("/analytics/author-stats"),
        api.get("/analytics/status-distribution"),
        api.get("/analytics/monthly-trend"),
        api.get("/analytics/keyword-stats"),
      ]);
      setSummary(s.data); setTopArts(m.data); setCats(c.data); setTags(t.data);
      setAuthors(a.data); setStatuses(st.data); setTrend(tr.data); setKeywords(kw.data);
    } catch { setMsg({ type: "error", text: "Failed to load. Run the ETL first." }); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const triggerETL = async () => {
    setRunning(true); setMsg({ type: "", text: "" });
    try { await api.post("/analytics/run-etl"); setMsg({ type: "success", text: "ETL completed!" }); await load(); }
    catch (err) { setMsg({ type: "error", text: err.response?.data?.detail || "ETL failed" }); }
    finally { setRunning(false); }
  };

  if (loading) return <div className="loading">⏳ Loading...</div>;

  const maxArt = Math.max(...topArts.map(a => a.view_count), 1);
  const maxCat = Math.max(...cats.map(c => c.article_count), 1);
  const maxAuth = Math.max(...authors.map(a => a.articles_written), 1);
  const maxStatus = Math.max(...statuses.map(s => s.count), 1);
  const maxKw = Math.max(...keywords.map(k => k.search_count), 1);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700 }}>📈 Knowledge Base Analytics</h1>
          <p style={{ color: "#64748b", fontSize: "0.9rem" }}>Article popularity, tag usage, author activity from ETL output</p>
        </div>
        <button className="btn btn-primary" onClick={triggerETL} disabled={running}>{running ? "⏳ Running..." : "🔄 Run ETL"}</button>
      </div>
      {msg.text && <div className={`alert alert-${msg.type === "error" ? "error" : "success"}`}>{msg.text}</div>}

      {summary && (
        <div className="stats-grid" style={{ marginBottom: "1.5rem" }}>
          <div className="stat-card s-purple"><div className="stat-icon">📄</div><div className="stat-value">{summary.total_articles}</div><div className="stat-label">Total Articles</div></div>
          <div className="stat-card s-blue"><div className="stat-icon">👁️</div><div className="stat-value">{summary.total_views}</div><div className="stat-label">Total Views</div></div>
          <div className="stat-card s-green"><div className="stat-icon">✍️</div><div className="stat-value">{summary.total_authors}</div><div className="stat-label">Authors</div></div>
          <div className="stat-card s-orange"><div className="stat-icon">🏷️</div><div className="stat-value">{summary.total_categories}</div><div className="stat-label">Categories</div></div>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>🔥 Most Viewed Articles</h3>
          {topArts.slice(0, 10).map((a, i) => <Bar key={i} label={`${a.title.substring(0,50)} — ${a.author}`} value={a.view_count} max={maxArt} />)}
        </div>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>📂 Category Usage</h3>
          {cats.map(c => <Bar key={c.category} label={`${c.category} (${c.total_views} views)`} value={c.article_count} max={maxCat} color="#0ea5e9" />)}
        </div>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>✍️ Author Activity</h3>
          {authors.slice(0, 10).map(a => <Bar key={a.author} label={`${a.author} (${a.approved_count} approved)`} value={a.articles_written} max={maxAuth} color="#16a34a" />)}
        </div>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>📊 Article Status</h3>
          {statuses.map(s => <Bar key={s.status} label={s.status} value={s.count} max={maxStatus} color="#d97706" />)}
        </div>
      </div>

      <div className="card" style={{ marginBottom: "1rem" }}>
        <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>🏷️ Top Tags (Tag Cloud)</h3>
        <TagCloud tags={tags} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>🔎 Top Search Keywords</h3>
          {keywords.map(k => <Bar key={k.keyword} label={`"${k.keyword}"`} value={k.search_count} max={maxKw} color="#dc2626" />)}
        </div>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>📅 Monthly Publication Trend</h3>
          <LineChart data={trend} />
        </div>
      </div>
    </div>
  );
}

export default Analytics;
