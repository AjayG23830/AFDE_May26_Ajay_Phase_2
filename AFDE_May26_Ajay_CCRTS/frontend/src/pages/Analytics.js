/**
 * CCRTS Phase 2 — Analytics Page
 * Drop into frontend/src/pages/Analytics.js
 * In App.js add: <Route path="/analytics" element={<Analytics />} />
 * Add to Sidebar: <NavLink to="/analytics">📈 Analytics</NavLink>
 * (Note: uses Authorization header via existing api.js interceptor)
 */
import React, { useEffect, useState } from "react";
import api from "../services/api";

function Bar({ label, value, max, color = "#2563eb", suffix = "" }) {
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

function LineChart({ data, keys = [{ key: "complaint_count", color: "#2563eb", label: "Complaints" }, { key: "breach_count", color: "#dc2626", label: "Breached" }], height = 220 }) {
  if (!data.length) return <p style={{ color: "#94a3b8" }}>No data</p>;
  const max = Math.max(...data.flatMap(d => keys.map(k => d[k.key] || 0)), 1);
  const W = Math.max(data.length * 70, 400);
  const H = height; const pad = 40;
  return (
    <div style={{ overflowX: "auto" }}>
      <svg width={W} height={H} style={{ display: "block" }}>
        <line x1={pad} y1={H - pad} x2={W - pad} y2={H - pad} stroke="#cbd5e1" />
        <line x1={pad} y1={pad} x2={pad} y2={H - pad} stroke="#cbd5e1" />
        {keys.map((k, kIdx) => {
          const points = data.map((d, i) => {
            const x = pad + (i * (W - 2 * pad)) / Math.max(data.length - 1, 1);
            const y = H - pad - ((d[k.key] / max) * (H - 2 * pad));
            return { x, y, ...d };
          });
          const path = points.map((p, i) => (i === 0 ? "M" : "L") + p.x + " " + p.y).join(" ");
          return (
            <g key={kIdx}>
              <path d={path} fill="none" stroke={k.color} strokeWidth="2" />
              {points.map((p, i) => <circle key={i} cx={p.x} cy={p.y} r="3" fill={k.color} />)}
            </g>
          );
        })}
        {data.map((d, i) => {
          const x = pad + (i * (W - 2 * pad)) / Math.max(data.length - 1, 1);
          return <text key={i} x={x} y={H - pad + 14} textAnchor="middle" fontSize="9" fill="#64748b">{d.month}</text>;
        })}
        <g transform={`translate(${pad}, 5)`}>
          {keys.map((k, i) => (<g key={i} transform={`translate(${i * 120}, 0)`}>
            <rect width="10" height="10" fill={k.color} /><text x="15" y="9" fontSize="10">{k.label}</text>
          </g>))}
        </g>
      </svg>
    </div>
  );
}

const PRIO_COLOR = { Low: "#16a34a", Medium: "#d97706", High: "#ea580c", Critical: "#dc2626" };

function Analytics() {
  const [summary, setSummary] = useState(null);
  const [cats, setCats] = useState([]);
  const [prio, setPrio] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [sla, setSla] = useState([]);
  const [trend, setTrend] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [msg, setMsg] = useState({ type: "", text: "" });

  const load = async () => {
    setLoading(true);
    try {
      const [s, c, p, st, sl, t, a] = await Promise.all([
        api.get("/analytics/summary"), api.get("/analytics/category-stats"),
        api.get("/analytics/priority-distribution"), api.get("/analytics/status-distribution"),
        api.get("/analytics/sla-report"), api.get("/analytics/monthly-trend"),
        api.get("/analytics/agent-performance"),
      ]);
      setSummary(s.data); setCats(c.data); setPrio(p.data); setStatuses(st.data); setSla(sl.data); setTrend(t.data); setAgents(a.data);
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

  const maxCat = Math.max(...cats.map(c => c.complaint_count), 1);
  const maxPrio = Math.max(...prio.map(p => p.count), 1);
  const maxStatus = Math.max(...statuses.map(s => s.count), 1);
  const maxSla = Math.max(...sla.map(s => s.total), 1);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700 }}>📈 Complaint Analytics</h1>
          <p style={{ color: "#64748b", fontSize: "0.9rem" }}>SLA tracking, complaint trends, agent performance from ETL output</p>
        </div>
        <button className="btn btn-primary" onClick={triggerETL} disabled={running}>{running ? "⏳ Running..." : "🔄 Run ETL"}</button>
      </div>
      {msg.text && <div className={`alert alert-${msg.type === "error" ? "error" : "success"}`}>{msg.text}</div>}

      {summary && (
        <div className="stats-grid" style={{ marginBottom: "1.5rem" }}>
          <div className="stat-card stat-blue"><div className="stat-icon">📋</div><div className="stat-value">{summary.total_complaints}</div><div className="stat-label">Total Complaints</div></div>
          <div className="stat-card stat-green"><div className="stat-icon">✅</div><div className="stat-value">{summary.resolved}</div><div className="stat-label">Resolved</div></div>
          <div className="stat-card stat-red"><div className="stat-icon">🚨</div><div className="stat-value">{summary.sla_breached}</div><div className="stat-label">SLA Breached</div></div>
          <div className="stat-card stat-orange"><div className="stat-icon">📉</div><div className="stat-value">{summary.breach_rate}%</div><div className="stat-label">Breach Rate</div></div>
          <div className="stat-card stat-purple"><div className="stat-icon">⏱️</div><div className="stat-value">{summary.avg_resolution_hours}h</div><div className="stat-label">Avg Resolution</div></div>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>🚨 SLA Breach by Priority</h3>
          {sla.map(s => (
            <Bar key={s.priority} label={`${s.priority} (${s.breached}/${s.total})`} value={s.breach_rate} max={100}
                 color={PRIO_COLOR[s.priority]} suffix="%" />
          ))}
        </div>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>⚠️ Priority Distribution</h3>
          {prio.map(p => <Bar key={p.priority} label={p.priority} value={p.count} max={maxPrio} color={PRIO_COLOR[p.priority]} />)}
        </div>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>📊 Category Analysis</h3>
          {cats.map(c => <Bar key={c.category} label={`${c.category} (${c.sla_breach_count} breaches)`} value={c.complaint_count} max={maxCat} color="#7c3aed" />)}
        </div>
        <div className="card">
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>📌 Status Distribution</h3>
          {statuses.map(s => <Bar key={s.status} label={s.status} value={s.count} max={maxStatus} color="#0ea5e9" />)}
        </div>
      </div>

      <div className="card" style={{ marginBottom: "1rem" }}>
        <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>📅 Monthly Trend (Complaints vs SLA Breaches)</h3>
        <LineChart data={trend} />
      </div>

      <div className="card">
        <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>👤 Agent Performance</h3>
        <div className="table-wrap"><table>
          <thead><tr><th>Agent</th><th>Assigned</th><th>Resolved</th><th>Breached</th><th>Avg Resolution (h)</th><th>Resolution Rate</th></tr></thead>
          <tbody>{agents.map(a => (
            <tr key={a.agent_name}>
              <td><strong>{a.agent_name}</strong></td>
              <td>{a.total_assigned}</td>
              <td style={{ color: "#16a34a" }}>{a.resolved}</td>
              <td style={{ color: "#dc2626" }}>{a.breached}</td>
              <td>{a.avg_resolution_hours || "—"}</td>
              <td style={{ fontWeight: 700, color: a.resolution_rate >= 50 ? "#16a34a" : "#d97706" }}>{a.resolution_rate}%</td>
            </tr>
          ))}</tbody>
        </table></div>
      </div>
    </div>
  );
}

export default Analytics;
