import React, { useState, useEffect } from "react";
import {
  LayoutDashboard,
  ShieldAlert,
  UserCheck,
  BarChart3,
  Settings,
  LogOut,
  User,
  Activity,
  Percent,
  TrendingUp,
  Users,
  Search,
  Download,
  AlertTriangle,
  RefreshCw
} from "lucide-react";

// API Base URL (Vite dev server proxy handles /api/v1 prefix, or we call localhost:5000 directly)
const API_BASE = "http://localhost:5000";

interface AuthState {
  token: string | null;
  username: string | null;
  role: string | null;
}

export default function App() {
  const [auth, setAuth] = useState<AuthState>({
    token: localStorage.getItem("token"),
    username: localStorage.getItem("username"),
    role: localStorage.getItem("role"),
  });

  const [activeTab, setActiveTab] = useState<string>("dashboard");

  // Force login active if token is missing
  useEffect(() => {
    if (!auth.token) {
      setActiveTab("login");
    } else if (activeTab === "login") {
      setActiveTab("dashboard");
    }
  }, [auth.token]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("role");
    setAuth({ token: null, username: null, role: null });
  };

  // Helper fetch method with JWT headers
  const apiFetch = async (endpoint: string, options: RequestInit = {}) => {
    const headers = new Headers(options.headers || {});
    if (auth.token) {
      headers.set("Authorization", `Bearer ${auth.token}`);
    }
    headers.set("Content-Type", "application/json");

    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (res.status === 401) {
      handleLogout();
      throw new Error("Unauthorized session expired");
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(err.detail || err.error || "Request failed");
    }
    return res.json();
  };

  return (
    <div className="app-container">
      {auth.token ? (
        <div className="dashboard-layout">
          {/* Sidebar */}
          <div className="sidebar">
            <div className="sidebar-logo">
              <ShieldAlert size={28} style={{ color: "#3b82f6" }} />
              <span>LOANRISK AI</span>
            </div>
            <ul className="sidebar-menu">
              <li
                className={`menu-item ${activeTab === "dashboard" ? "active" : ""}`}
                onClick={() => setActiveTab("dashboard")}
              >
                <LayoutDashboard size={20} />
                <span>Dashboard</span>
              </li>
              <li
                className={`menu-item ${activeTab === "predict" ? "active" : ""}`}
                onClick={() => setActiveTab("predict")}
              >
                <Activity size={20} />
                <span>Risk Prediction</span>
              </li>
              <li
                className={`menu-item ${activeTab === "borrowers" ? "active" : ""}`}
                onClick={() => setActiveTab("borrowers")}
              >
                <UserCheck size={20} />
                <span>Borrowers</span>
              </li>
              <li
                className={`menu-item ${activeTab === "metrics" ? "active" : ""}`}
                onClick={() => setActiveTab("metrics")}
              >
                <BarChart3 size={20} />
                <span>Model Metrics</span>
              </li>
              {auth.role === "admin" && (
                <li
                  className={`menu-item ${activeTab === "admin" ? "active" : ""}`}
                  onClick={() => setActiveTab("admin")}
                >
                  <Settings size={20} />
                  <span>Admin Panel</span>
                </li>
              )}
            </ul>
            <div style={{ marginTop: "auto" }}>
              <div
                className="menu-item"
                style={{ borderTop: "1px solid rgba(255,255,255,0.05)", paddingTop: "16px" }}
              >
                <User size={18} />
                <span style={{ fontSize: "13px", opacity: 0.8 }}>{auth.username} ({auth.role})</span>
              </div>
              <button
                className="btn btn-secondary"
                style={{ width: "100%", marginTop: "12px", justifyContent: "flex-start", gap: "10px" }}
                onClick={handleLogout}
              >
                <LogOut size={16} />
                <span>Sign Out</span>
              </button>
            </div>
          </div>

          {/* Main Workspace */}
          <div className="main-content">
            {activeTab === "dashboard" && <DashboardPage apiFetch={apiFetch} />}
            {activeTab === "predict" && <PredictionPage apiFetch={apiFetch} />}
            {activeTab === "borrowers" && <BorrowersPage apiFetch={apiFetch} />}
            {activeTab === "metrics" && <MetricsPage apiFetch={apiFetch} />}
            {activeTab === "admin" && <AdminPage apiFetch={apiFetch} />}
          </div>
        </div>
      ) : (
        <LoginPage setAuth={setAuth} />
      )}
    </div>
  );
}

/* ==========================================================================
   PAGE: LOGIN & REGISTRATION
   ========================================================================== */
function LoginPage({ setAuth }: { setAuth: React.Dispatch<React.SetStateAction<AuthState>> }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const endpoint = isRegister ? "/register" : "/login";
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || data.error || "Authentication failed");
      }

      if (isRegister) {
        setIsRegister(false);
        setError("Account created successfully! Please log in.");
      } else {
        localStorage.setItem("token", data.token);
        localStorage.setItem("username", data.username);
        localStorage.setItem("role", data.role);
        setAuth({ token: data.token, username: data.username, role: data.role });
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", padding: "20px" }}>
      <div className="glass-card animate-fade-in" style={{ width: "100%", maxWidth: "420px" }}>
        <div style={{ textAlign: "center", marginBottom: "28px" }}>
          <ShieldAlert size={48} style={{ color: "#3b82f6", margin: "0 auto 12px" }} />
          <h2 style={{ fontSize: "24px" }}>Loan Risk Platform</h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginTop: "4px" }}>
            {isRegister ? "Create analyst account credentials" : "Sign in to access risk dashboard"}
          </p>
        </div>

        {error && (
          <div
            style={{
              padding: "12px",
              backgroundColor: error.includes("success") ? "var(--success-glow)" : "var(--danger-glow)",
              color: error.includes("success") ? "#34d399" : "#f87171",
              border: `1px solid ${error.includes("success") ? "rgba(16,185,129,0.2)" : "rgba(239,68,68,0.2)"}`,
              borderRadius: "6px",
              fontSize: "14px",
              marginBottom: "16px",
            }}
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              type="text"
              className="form-input"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
            />
          </div>
          <div className="form-group" style={{ marginBottom: "24px" }}>
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: "100%" }} disabled={loading}>
            {loading ? <RefreshCw className="spin" size={16} /> : isRegister ? "Create Account" : "Access Console"}
          </button>
        </form>

        <div style={{ textAlign: "center", marginTop: "20px", fontSize: "14px", color: "var(--text-secondary)" }}>
          {isRegister ? "Already have an account? " : "New analyst? "}
          <span
            style={{ color: "var(--primary)", cursor: "pointer", fontWeight: 600 }}
            onClick={() => {
              setIsRegister(!isRegister);
              setError(null);
            }}
          >
            {isRegister ? "Sign In" : "Request Account"}
          </span>
        </div>
      </div>
    </div>
  );
}

/* ==========================================================================
   PAGE: DASHBOARD
   ========================================================================== */
function DashboardPage({ apiFetch }: { apiFetch: any }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch("/api/v1/dashboard-data")
      .then((res: any) => {
        setData(res);
        setLoading(false);
      })
      .catch((err: any) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "50vh" }}>
        <RefreshCw className="spin" size={36} style={{ color: "var(--primary)" }} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card" style={{ borderColor: "rgba(239,68,68,0.3)", padding: "20px", color: "#f87171" }}>
        <AlertTriangle size={24} style={{ marginBottom: "8px" }} />
        <h3>Failed to load Dashboard data</h3>
        <p>{error}</p>
      </div>
    );
  }

  const kpis = data?.kpis || { total_predictions: 0, approval_rate: 0, avg_risk: 0, users: 0 };
  const categories = data?.risk_categories || { "Low Risk": 0, "Medium Risk": 0, "High Risk": 0 };
  const trends = data?.trends || { x: [], y: [] };
  const recents = data?.recent_predictions || [];

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: "32px" }}>
        <h1>Overview Dashboard</h1>
        <p style={{ color: "var(--text-secondary)" }}>Real-time credit portfolio metrics and model assessment trends.</p>
      </div>

      {/* KPI Cards Grid */}
      <div className="metrics-grid">
        <div className="glass-card kpi-card">
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span className="kpi-title">Total Queries</span>
            <Activity size={18} style={{ color: "var(--primary)" }} />
          </div>
          <span className="kpi-value">{kpis.total_predictions}</span>
          <span className="kpi-indicator" style={{ color: "var(--text-muted)" }}>Cumulative system analyses</span>
        </div>

        <div className="glass-card kpi-card">
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span className="kpi-title">Approval Rate</span>
            <Percent size={18} style={{ color: "var(--success)" }} />
          </div>
          <span className="kpi-value">{kpis.approval_rate.toFixed(1)}%</span>
          <span className="kpi-indicator" style={{ color: "#34d399" }}>Favorable decisions</span>
        </div>

        <div className="glass-card kpi-card">
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span className="kpi-title">Portfolio Risk</span>
            <TrendingUp size={18} style={{ color: "var(--warning)" }} />
          </div>
          <span className="kpi-value">{kpis.avg_risk.toFixed(1)}</span>
          <span className="kpi-indicator" style={{ color: "#fbbf24" }}>Average risk index (0-100)</span>
        </div>

        <div className="glass-card kpi-card">
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span className="kpi-title">Active Analysts</span>
            <Users size={18} style={{ color: "var(--primary)" }} />
          </div>
          <span className="kpi-value">{kpis.users}</span>
          <span className="kpi-indicator" style={{ color: "var(--text-muted)" }}>Registered operator seats</span>
        </div>
      </div>

      {/* Analytics Charts Row */}
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "24px", marginBottom: "32px" }}>
        {/* Trend line chart (SVG based) */}
        <div className="glass-card">
          <h3 style={{ fontSize: "16px", marginBottom: "20px" }}>Portfolio Risk Trend</h3>
          {trends.x.length > 0 ? (
            <SVGTrendChart x={trends.x} y={trends.y} />
          ) : (
            <div style={{ height: "200px", display: "flex", justifyContent: "center", alignItems: "center", color: "var(--text-muted)" }}>
              No historical trend data available.
            </div>
          )}
        </div>

        {/* Risk Categories bar/doughnut visualization */}
        <div className="glass-card">
          <h3 style={{ fontSize: "16px", marginBottom: "20px" }}>Risk Categories</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {Object.entries(categories).map(([key, value]) => {
              const total = Object.values(categories).reduce((a: any, b: any) => a + b, 0) as number;
              const percent = total > 0 ? ((value as number) / total) * 100 : 0;
              const color =
                key.includes("Low") ? "var(--success)" :
                key.includes("Medium") ? "var(--warning)" : "var(--danger)";

              return (
                <div key={key}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px", fontSize: "14px" }}>
                    <span style={{ fontWeight: 600 }}>{key}</span>
                    <span style={{ color: "var(--text-secondary)" }}>{value as number} ({percent.toFixed(0)}%)</span>
                  </div>
                  <div style={{ height: "8px", backgroundColor: "rgba(255,255,255,0.05)", borderRadius: "4px", overflow: "hidden" }}>
                    <div style={{ height: "100%", width: `${percent}%`, backgroundColor: color, borderRadius: "4px" }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Recent Predictions Table */}
      <div className="glass-card">
        <h3 style={{ fontSize: "16px", marginBottom: "16px" }}>Recent Decisions</h3>
        <div className="table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Gender</th>
                <th>Age</th>
                <th>Income</th>
                <th>Loan Amount</th>
                <th>Probability</th>
                <th>Decision</th>
                <th>Risk Score</th>
                <th>Risk Status</th>
              </tr>
            </thead>
            <tbody>
              {recents.length > 0 ? (
                recents.map((r: any) => (
                  <tr key={r.id}>
                    <td>{r.gender}</td>
                    <td>{r.age}</td>
                    <td>${r.monthly_income.toLocaleString()}</td>
                    <td>${r.loan_amount.toLocaleString()}</td>
                    <td>{(r.approval_probability * 100).toFixed(0)}%</td>
                    <td>
                      <span className={`badge badge-${r.approval_status}`}>
                        {r.approval_status}
                      </span>
                    </td>
                    <td>{r.risk_score.toFixed(1)}</td>
                    <td>
                      <span className={`badge badge-${r.risk_category.toLowerCase().replace(" ", "-")}`}>
                        {r.risk_category}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} style={{ textAlign: "center", color: "var(--text-muted)" }}>
                    No decisions on record yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

/* ==========================================================================
   PAGE: RISK PREDICTION
   ========================================================================== */
function PredictionPage({ apiFetch }: { apiFetch: any }) {
  const [form, setForm] = useState({
    gender: "Male",
    age: 33,
    married: "Yes",
    dependents: 1,
    education: "Graduate",
    employment_type: "Salaried",
    monthly_income: 5500,
    coapplicant_income: 0,
    loan_amount: 120000,
    loan_term: 360,
    credit_history: 1.0,
    existing_debt: 10000,
    property_area: "Urban",
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await apiFetch("/api/v1/predict", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: "32px" }}>
        <h1>Credit Risk Assessment</h1>
        <p style={{ color: "var(--text-secondary)" }}>Input applicant metrics to run real-time predictions and explainable AI models.</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: result ? "1.2fr 1fr" : "1fr", gap: "32px" }}>
        {/* Form panel */}
        <div className="glass-card">
          <h3 style={{ fontSize: "16px", marginBottom: "20px" }}>Applicant Information</h3>
          <form onSubmit={handleSubmit}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
              <div className="form-group">
                <label className="form-label">Gender</label>
                <select
                  className="form-select"
                  value={form.gender}
                  onChange={(e) => setForm({ ...form, gender: e.target.value })}
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Age (years)</label>
                <input
                  type="number"
                  className="form-input"
                  min={18}
                  max={100}
                  value={form.age}
                  onChange={(e) => setForm({ ...form, age: parseInt(e.target.value) })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Married</label>
                <select
                  className="form-select"
                  value={form.married}
                  onChange={(e) => setForm({ ...form, married: e.target.value })}
                >
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Dependents</label>
                <input
                  type="number"
                  className="form-input"
                  min={0}
                  max={10}
                  value={form.dependents}
                  onChange={(e) => setForm({ ...form, dependents: parseInt(e.target.value) })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Education</label>
                <select
                  className="form-select"
                  value={form.education}
                  onChange={(e) => setForm({ ...form, education: e.target.value })}
                >
                  <option value="Graduate">Graduate</option>
                  <option value="Not Graduate">Not Graduate</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Employment Type</label>
                <select
                  className="form-select"
                  value={form.employment_type}
                  onChange={(e) => setForm({ ...form, employment_type: e.target.value })}
                >
                  <option value="Salaried">Salaried</option>
                  <option value="Self employed">Self employed</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Monthly Income ($)</label>
                <input
                  type="number"
                  className="form-input"
                  min={0}
                  value={form.monthly_income}
                  onChange={(e) => setForm({ ...form, monthly_income: parseFloat(e.target.value) })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Co-applicant Income ($)</label>
                <input
                  type="number"
                  className="form-input"
                  min={0}
                  value={form.coapplicant_income}
                  onChange={(e) => setForm({ ...form, coapplicant_income: parseFloat(e.target.value) })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Loan Amount Requested ($)</label>
                <input
                  type="number"
                  className="form-input"
                  min={0}
                  value={form.loan_amount}
                  onChange={(e) => setForm({ ...form, loan_amount: parseFloat(e.target.value) })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Loan Term (months)</label>
                <input
                  type="number"
                  className="form-input"
                  min={12}
                  max={600}
                  value={form.loan_term}
                  onChange={(e) => setForm({ ...form, loan_term: parseInt(e.target.value) })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Credit History</label>
                <select
                  className="form-select"
                  value={form.credit_history}
                  onChange={(e) => setForm({ ...form, credit_history: parseFloat(e.target.value) })}
                >
                  <option value={1.0}>Good Credit Score (1.0)</option>
                  <option value={0.0}>Poor / No Credit (0.0)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Existing Debt ($)</label>
                <input
                  type="number"
                  className="form-input"
                  min={0}
                  value={form.existing_debt}
                  onChange={(e) => setForm({ ...form, existing_debt: parseFloat(e.target.value) })}
                />
              </div>

              <div className="form-group" style={{ gridColumn: "span 2" }}>
                <label className="form-label">Property Location Type</label>
                <select
                  className="form-select"
                  value={form.property_area}
                  onChange={(e) => setForm({ ...form, property_area: e.target.value })}
                >
                  <option value="Urban">Urban</option>
                  <option value="Semiurban">Semiurban</option>
                  <option value="Rural">Rural</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: "100%", marginTop: "24px" }}
              disabled={loading}
            >
              {loading ? (
                <>
                  <RefreshCw className="spin" size={16} />
                  <span>Computing risk factors...</span>
                </>
              ) : (
                "Run Prediction & SHAP Analysis"
              )}
            </button>
          </form>

          {error && (
            <div
              style={{
                marginTop: "20px",
                padding: "12px",
                backgroundColor: "var(--danger-glow)",
                color: "#f87171",
                border: "1px solid rgba(239, 68, 68, 0.2)",
                borderRadius: "6px",
                fontSize: "14px",
              }}
            >
              {error}
            </div>
          )}
        </div>

        {/* Prediction Results Panel */}
        {result && (
          <div className="glass-card animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3 style={{ fontSize: "16px" }}>Prediction Output</h3>
              {result.pdf_report_path && (
                <a
                  href={`${API_BASE}${result.pdf_report_path}?token=${localStorage.getItem("token")}`}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-secondary"
                  style={{ padding: "8px 16px", fontSize: "13px" }}
                >
                  <Download size={14} />
                  <span>Report</span>
                </a>
              )}
            </div>

            {/* Gauge visualizer */}
            <div style={{ textAlign: "center", margin: "10px 0" }}>
              <SVGGaugeChart score={result.risk_score} category={result.risk_category} />
              <div style={{ marginTop: "12px" }}>
                <span style={{ fontSize: "14px", color: "var(--text-secondary)" }}>Approval Status</span>
                <div style={{ marginTop: "6px" }}>
                  <span className={`badge badge-${result.approval_status}`} style={{ fontSize: "18px", padding: "8px 16px" }}>
                    {result.approval_status.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>

            {/* Statistics */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", backgroundColor: "rgba(0,0,0,0.15)", padding: "16px", borderRadius: "8px" }}>
              <div>
                <span style={{ fontSize: "12px", color: "var(--text-secondary)", textTransform: "uppercase" }}>Approval Prob</span>
                <div style={{ fontSize: "18px", fontWeight: 700 }}>{(result.approval_probability * 100).toFixed(1)}%</div>
              </div>
              <div>
                <span style={{ fontSize: "12px", color: "var(--text-secondary)", textTransform: "uppercase" }}>Threshold</span>
                <div style={{ fontSize: "18px", fontWeight: 700 }}>{(result.approval_threshold * 100).toFixed(0)}%</div>
              </div>
            </div>

            {/* SHAP explanation */}
            <div>
              <h4 style={{ fontSize: "14px", marginBottom: "12px" }}>SHAP Feature Contributions</h4>
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {result.shap_feature_importance && result.shap_feature_importance.length > 0 ? (
                  result.shap_feature_importance.map((item: any, idx: number) => {
                    const positive = item.shap_value > 0;
                    return (
                      <div key={idx} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "13px" }}>
                        <span style={{ fontWeight: 500, color: "var(--text-secondary)" }}>
                          {item.feature.replace("num__", "").replace("cat__", "").replace("_", " ").toUpperCase()}
                        </span>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <span style={{ color: positive ? "#34d399" : "#f87171" }}>
                            {positive ? "+" : ""}{item.shap_value.toFixed(4)}
                          </span>
                          <span
                            className="badge"
                            style={{
                              fontSize: "10px",
                              backgroundColor: positive ? "var(--success-glow)" : "var(--danger-glow)",
                              color: positive ? "#34d399" : "#f87171"
                            }}
                          >
                            {positive ? "Favors approval" : "Favors rejection"}
                          </span>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <p style={{ color: "var(--text-muted)", fontSize: "13px" }}>No detailed attribute impact metrics computed.</p>
                )}
              </div>
            </div>

            {/* Static SHAP images if generated */}
            {result.shap_summary_path && (
              <div>
                <h4 style={{ fontSize: "14px", marginBottom: "12px" }}>SHAP Global Summary Density Map</h4>
                <img
                  src={`${API_BASE}${result.shap_summary_path}`}
                  alt="SHAP summary plot"
                  style={{ width: "100%", borderRadius: "8px", border: "1px solid var(--border-color)", backgroundColor: "white", padding: "10px" }}
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ==========================================================================
   PAGE: BORROWERS LIST
   ========================================================================== */
function BorrowersPage({ apiFetch }: { apiFetch: any }) {
  const [borrowers, setBorrowers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [selectedBorrower, setSelectedBorrower] = useState<any | null>(null);

  useEffect(() => {
    apiFetch("/api/v1/borrowers")
      .then((res: any) => {
        setBorrowers(res);
        setLoading(false);
      })
      .catch((err: any) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const filtered = borrowers.filter((b) => {
    const term = search.toLowerCase();
    return (
      b.gender.toLowerCase().includes(term) ||
      b.education.toLowerCase().includes(term) ||
      b.property_area.toLowerCase().includes(term) ||
      b.id.toString().includes(term)
    );
  });

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: "32px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1>Borrower Analysis</h1>
          <p style={{ color: "var(--text-secondary)" }}>Review profiles, income-to-loan ratios, and past prediction metrics.</p>
        </div>
        <div style={{ position: "relative", width: "240px" }}>
          <input
            type="text"
            className="form-input"
            style={{ paddingLeft: "40px" }}
            placeholder="Search profiles..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <Search size={16} style={{ position: "absolute", left: "14px", top: "15px", color: "var(--text-muted)" }} />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: selectedBorrower ? "1.5fr 1fr" : "1fr", gap: "24px" }}>
        {/* Table List */}
        <div className="glass-card">
          {loading ? (
            <div style={{ display: "flex", justifyContent: "center", padding: "40px" }}>
              <RefreshCw className="spin" size={28} />
            </div>
          ) : error ? (
            <p style={{ color: "#f87171" }}>{error}</p>
          ) : (
            <div className="table-container">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Gender</th>
                    <th>Age</th>
                    <th>Education</th>
                    <th>Monthly Income</th>
                    <th>Debt</th>
                    <th>Loan Requested</th>
                    <th>Property Area</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.length > 0 ? (
                    filtered.map((b) => (
                      <tr
                        key={b.id}
                        onClick={() => setSelectedBorrower(b)}
                        style={{ cursor: "pointer", backgroundColor: selectedBorrower?.id === b.id ? "rgba(255,255,255,0.03)" : "" }}
                      >
                        <td style={{ fontWeight: 700 }}>#{b.id}</td>
                        <td>{b.gender}</td>
                        <td>{b.age}</td>
                        <td>{b.education}</td>
                        <td>${b.monthly_income.toLocaleString()}</td>
                        <td>${b.existing_debt.toLocaleString()}</td>
                        <td>${b.loan_amount.toLocaleString()}</td>
                        <td>{b.property_area}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8} style={{ textAlign: "center", color: "var(--text-muted)" }}>
                        No profiles match search filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Profile Details Sidebar */}
        {selectedBorrower && (
          <div className="glass-card animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3 style={{ fontSize: "16px" }}>Borrower Profile</h3>
              <button
                className="btn btn-secondary"
                style={{ padding: "4px 8px", fontSize: "12px" }}
                onClick={() => setSelectedBorrower(null)}
              >
                Close
              </button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "12px", borderBottom: "1px solid var(--border-color)", paddingBottom: "16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Record Reference</span>
                <span style={{ fontWeight: 700 }}>ID #{selectedBorrower.id}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Demographics</span>
                <span>{selectedBorrower.gender}, Age {selectedBorrower.age}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Marital Status</span>
                <span>{selectedBorrower.married === "Yes" ? "Married" : "Single"}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Dependents</span>
                <span>{selectedBorrower.dependents}</span>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "12px", borderBottom: "1px solid var(--border-color)", paddingBottom: "16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Education Level</span>
                <span>{selectedBorrower.education}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Employment Status</span>
                <span>{selectedBorrower.employment_type}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Primary Monthly Income</span>
                <span>${selectedBorrower.monthly_income.toLocaleString()}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Co-applicant Income</span>
                <span>${selectedBorrower.coapplicant_income.toLocaleString()}</span>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Requested Principal</span>
                <span style={{ fontWeight: 600 }}>${selectedBorrower.loan_amount.toLocaleString()}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Amortization Term</span>
                <span>{selectedBorrower.loan_term} months</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Credit History Score</span>
                <span>{selectedBorrower.credit_history === 1.0 ? "Good (1.0)" : "Poor (0.0)"}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Existing Liabilities</span>
                <span>${selectedBorrower.existing_debt.toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/* ==========================================================================
   PAGE: MODEL PERFORMANCE METRICS
   ========================================================================== */
function MetricsPage({ apiFetch }: { apiFetch: any }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeModel, setActiveModel] = useState<string>("LightGBM");

  useEffect(() => {
    apiFetch("/api/v1/model-metrics")
      .then((res: any) => {
        setData(res);
        setLoading(false);
      })
      .catch((err: any) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", padding: "40px" }}>
        <RefreshCw className="spin" size={28} />
      </div>
    );
  }

  if (error) {
    return <p style={{ color: "#f87171" }}>{error}</p>;
  }

  const bestModel = data?.best_model || "LightGBM";
  const metricsMap = data?.metrics_by_model || {};

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: "32px" }}>
        <h1>ML Model Performance</h1>
        <p style={{ color: "var(--text-secondary)" }}>Compare accuracy, precision, recall, and ROC-AUC metrics for the trained estimators.</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "24px", marginBottom: "32px" }}>
        {/* Comparison grid */}
        <div className="glass-card">
          <h3 style={{ fontSize: "16px", marginBottom: "20px" }}>Metrics Comparison</h3>
          <div className="table-container">
            <table className="custom-table" style={{ fontSize: "13px" }}>
              <thead>
                <tr>
                  <th>Model Name</th>
                  <th>Accuracy</th>
                  <th>Precision</th>
                  <th>Recall</th>
                  <th>F1 Score</th>
                  <th>ROC-AUC</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(metricsMap).map(([name, m]: any) => (
                  <tr
                    key={name}
                    style={{ cursor: "pointer", backgroundColor: activeModel === name ? "rgba(255,255,255,0.03)" : "" }}
                    onClick={() => setActiveModel(name)}
                  >
                    <td style={{ fontWeight: 700 }}>
                      {name} {name === bestModel && <span style={{ color: "var(--success)", fontSize: "10px" }}>(Active)</span>}
                    </td>
                    <td>{m.accuracy.toFixed(3)}</td>
                    <td>{m.precision.toFixed(3)}</td>
                    <td>{m.recall.toFixed(3)}</td>
                    <td>{m.f1.toFixed(3)}</td>
                    <td style={{ fontWeight: 600, color: "var(--primary)" }}>{m.roc_auc.toFixed(3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected model details */}
        <div className="glass-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ fontSize: "16px" }}>{activeModel} Evaluation</h3>
            <span className="badge badge-low-risk" style={{ fontSize: "11px" }}>Trained Artifact</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <span style={{ fontSize: "12px", color: "var(--text-secondary)", textTransform: "uppercase" }}>Model Objective</span>
              <p style={{ fontSize: "14px", marginTop: "4px" }}>
                Predict the binary probability of loan approval using features extracted from borrower metrics.
              </p>
            </div>

            <div>
              <span style={{ fontSize: "12px", color: "var(--text-secondary)", textTransform: "uppercase", display: "block", marginBottom: "8px" }}>
                Performance metrics
              </span>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div style={{ padding: "12px", backgroundColor: "rgba(0,0,0,0.15)", borderRadius: "6px" }}>
                  <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>Accuracy</div>
                  <div style={{ fontSize: "18px", fontWeight: 700 }}>
                    {(metricsMap[activeModel]?.accuracy * 100 || 0).toFixed(1)}%
                  </div>
                </div>
                <div style={{ padding: "12px", backgroundColor: "rgba(0,0,0,0.15)", borderRadius: "6px" }}>
                  <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>ROC-AUC</div>
                  <div style={{ fontSize: "18px", fontWeight: 700, color: "var(--primary)" }}>
                    {(metricsMap[activeModel]?.roc_auc || 0).toFixed(3)}
                  </div>
                </div>
              </div>
            </div>

            {/* Mock confusion matrix representation if confusion matrix field exists */}
            {metricsMap[activeModel]?.confusion_matrix && (
              <div>
                <span style={{ fontSize: "12px", color: "var(--text-secondary)", textTransform: "uppercase", display: "block", marginBottom: "8px" }}>
                  Confusion Matrix
                </span>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "8px",
                    textAlign: "center",
                    fontFamily: "monospace",
                    maxWidth: "200px",
                    margin: "0 auto"
                  }}
                >
                  <div style={{ padding: "10px", border: "1px solid var(--border-color)", borderRadius: "4px" }}>
                    <div style={{ fontSize: "10px", color: "var(--text-muted)" }}>TN</div>
                    <div>{metricsMap[activeModel].confusion_matrix[0]?.[0]}</div>
                  </div>
                  <div style={{ padding: "10px", border: "1px solid var(--border-color)", borderRadius: "4px" }}>
                    <div style={{ fontSize: "10px", color: "var(--text-muted)" }}>FP</div>
                    <div>{metricsMap[activeModel].confusion_matrix[0]?.[1]}</div>
                  </div>
                  <div style={{ padding: "10px", border: "1px solid var(--border-color)", borderRadius: "4px" }}>
                    <div style={{ fontSize: "10px", color: "var(--text-muted)" }}>FN</div>
                    <div>{metricsMap[activeModel].confusion_matrix[1]?.[0]}</div>
                  </div>
                  <div style={{ padding: "10px", border: "1px solid var(--border-color)", borderRadius: "4px" }}>
                    <div style={{ fontSize: "10px", color: "var(--text-muted)" }}>TP</div>
                    <div>{metricsMap[activeModel].confusion_matrix[1]?.[1]}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ==========================================================================
   PAGE: ADMIN PANEL
   ========================================================================== */
function AdminPage({ apiFetch }: { apiFetch: any }) {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch("/api/v1/audit-logs")
      .then((res: any) => {
        setLogs(res);
        setLoading(false);
      })
      .catch((err: any) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: "32px" }}>
        <h1>Admin Operations</h1>
        <p style={{ color: "var(--text-secondary)" }}>System logs, login histories, database transaction auditing.</p>
      </div>

      <div className="glass-card">
        <h3 style={{ fontSize: "16px", marginBottom: "16px" }}>Audit Trail Logs</h3>
        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: "40px" }}>
            <RefreshCw className="spin" size={28} />
          </div>
        ) : error ? (
          <p style={{ color: "#f87171" }}>{error}</p>
        ) : (
          <div className="table-container">
            <table className="custom-table" style={{ fontSize: "13px" }}>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>User</th>
                  <th>Action</th>
                  <th>Status</th>
                  <th>IP Address</th>
                  <th>Transaction Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.length > 0 ? (
                  logs.map((log) => (
                    <tr key={log.id}>
                      <td style={{ color: "var(--text-secondary)" }}>
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                      <td style={{ fontWeight: 600 }}>{log.username || "anonymous"}</td>
                      <td style={{ fontFamily: "monospace" }}>{log.action}</td>
                      <td>
                        <span
                          className="badge"
                          style={{
                            backgroundColor: log.status === "SUCCESS" ? "var(--success-glow)" : "var(--danger-glow)",
                            color: log.status === "SUCCESS" ? "#34d399" : "#f87171",
                          }}
                        >
                          {log.status}
                        </span>
                      </td>
                      <td>{log.ip_address || "N/A"}</td>
                      <td style={{ maxWidth: "260px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {log.details || "-"}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} style={{ textAlign: "center", color: "var(--text-muted)" }}>
                      No audit logs captured.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

/* ==========================================================================
   CUSTOM SVG CHART SUB-COMPONENTS
   ========================================================================== */

// 1. Line Trend Chart
function SVGTrendChart({ x, y }: { x: string[]; y: number[] }) {
  const width = 500;
  const height = 200;
  const padding = 35;

  const minVal = 0;
  const maxVal = 100;

  const points = y.map((val, idx) => {
    const px = padding + (idx / (y.length - 1)) * (width - 2 * padding);
    const py = height - padding - ((val - minVal) / (maxVal - minVal)) * (height - 2 * padding);
    return { x: px, y: py, val, label: x[idx] };
  });

  const pathD = points.length > 0
    ? `M ${points[0].x} ${points[0].y} ` + points.slice(1).map((p) => `L ${p.x} ${p.y}`).join(" ")
    : "";

  const areaD = points.length > 0
    ? `${pathD} L ${points[points.length - 1].x} ${height - padding} L ${points[0].x} ${height - padding} Z`
    : "";

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="220" style={{ overflow: "visible" }}>
      <defs>
        <linearGradient id="chart-area-grad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.25" />
          <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.0" />
        </linearGradient>
      </defs>

      {/* Grid lines */}
      {[0, 25, 50, 75, 100].map((grid, idx) => {
        const py = height - padding - (grid / 100) * (height - 2 * padding);
        return (
          <g key={idx}>
            <line x1={padding} y1={py} x2={width - padding} y2={py} stroke="rgba(255,255,255,0.04)" strokeDasharray="4 4" />
            <text x={padding - 10} y={py + 4} fill="var(--text-muted)" fontSize="9" textAnchor="end">{grid}</text>
          </g>
        );
      })}

      {/* X Axis Labels */}
      {points.map((p, idx) => (
        <text key={idx} x={p.x} y={height - 12} fill="var(--text-muted)" fontSize="8" textAnchor="middle">
          {p.label}
        </text>
      ))}

      {/* Path Area */}
      {areaD && <path d={areaD} fill="url(#chart-area-grad)" />}

      {/* Line Path */}
      {pathD && <path d={pathD} fill="none" stroke="#3b82f6" strokeWidth="2.5" />}

      {/* Point dots */}
      {points.map((p, idx) => (
        <g key={idx}>
          <circle cx={p.x} cy={p.y} r="4" fill="#3b82f6" stroke="var(--bg-primary)" strokeWidth="1.5" style={{ cursor: "pointer" }} />
          <text x={p.x} y={p.y - 8} fill="var(--text-primary)" fontSize="9" fontWeight="bold" textAnchor="middle">
            {p.val.toFixed(0)}
          </text>
        </g>
      ))}
    </svg>
  );
}

// 2. Speedometer Gauge Chart
function SVGGaugeChart({ score, category }: { score: number; category: string }) {
  const r = 80;
  const cx = 100;
  const cy = 100;
  const angle = (score / 100) * 180; // 0 to 180 degrees

  // Angle in radians for pointer math
  const rad = ((180 - angle) * Math.PI) / 180;
  const pointerX = cx + (r - 15) * Math.cos(rad);
  const pointerY = cy - (r - 15) * Math.sin(rad);

  const color =
    score <= 30 ? "#10b981" : // success
    score <= 70 ? "#f59e0b" : // warning
    "#ef4444"; // danger

  return (
    <div style={{ display: "inline-block", position: "relative" }}>
      <svg width="200" height="120" viewBox="0 0 200 120" style={{ overflow: "visible" }}>
        <defs>
          <linearGradient id="gauge-grad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="50%" stopColor="#f59e0b" />
            <stop offset="100%" stopColor="#ef4444" />
          </linearGradient>
        </defs>

        {/* Dial track */}
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth="16"
          strokeLinecap="round"
        />

        {/* Colored Dial track overlay */}
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="url(#gauge-grad)"
          strokeWidth="16"
          strokeLinecap="round"
          opacity="0.85"
        />

        {/* Needle pointer */}
        <line
          x1={cx}
          y1={cy}
          x2={pointerX}
          y2={pointerY}
          stroke="#f3f4f6"
          strokeWidth="3.5"
          strokeLinecap="round"
        />
        <circle cx={cx} cy={cy} r="6" fill="#f3f4f6" />

        {/* Center label */}
        <text x={cx} y={cy + 16} fill="var(--text-primary)" fontSize="20" fontWeight="800" textAnchor="middle">
          {score.toFixed(1)}
        </text>
      </svg>
      <div style={{ fontSize: "14px", fontWeight: 700, color, marginTop: "-12px" }}>
        {category}
      </div>
    </div>
  );
}
