"""
app.py
------
AD Control Tower — Main Streamlit Dashboard

Run:
    streamlit run app.py

Requires:
    pip install -r requirements.txt
"""

import io
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

from health_engine import HealthEngine
from risk_engine import RiskEngine
from recommendation_engine import RecommendationEngine

# ─────────────────────────────────────────────────────────────────────────────
# Page configuration
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AD Control Tower",
    page_icon="🗼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS — dark enterprise theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 14px;
    }
    .section-hdr {
        font-size: 1.05rem;
        font-weight: 700;
        color: #58a6ff;
        border-bottom: 1px solid #30363d;
        padding-bottom: 6px;
        margin-bottom: 14px;
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDownloadButton > button {
        background-color: #21262d;
        border: 1px solid #30363d;
        color: #e6edf3;
    }
    .stDownloadButton > button:hover {
        background-color: #30363d;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Header banner
# ─────────────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1, 7, 3])
with c1:
    st.markdown("<h1 style='margin:0;font-size:2.5rem;'>🗼</h1>", unsafe_allow_html=True)
with c2:
    st.markdown(
        "<h2 style='margin:0;color:#58a6ff;'>AD Control Tower</h2>"
        "<p style='color:#8b949e;margin:0;'>From Reactive Operations to Predictive Operations</p>",
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        "<div style='text-align:right;color:#8b949e;font-size:0.82rem;'>"
        "Alter Domus | Operational Intelligence<br>"
        "Portfolio Health Platform</div>",
        unsafe_allow_html=True,
    )
st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar — data source & filters
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📁 Data Source")
    uploaded_file = st.file_uploader(
        "Upload Fund CSV",
        type=["csv"],
        help=(
            "Required columns: fund_name, fund_type, open_exceptions, "
            "overdue_tasks, client_escalations, resource_utilization, sla_breaches"
        ),
    )
    load_sample_btn = st.button("▶ Load Sample Dataset (100 Funds)", use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔍 Filters")

    fund_type_opts = [
        "Private Equity", "Private Debt", "Real Estate", "Infrastructure", "Hedge Fund"
    ]
    fund_type_filter = st.multiselect(
        "Fund Type", options=fund_type_opts, default=fund_type_opts
    )

    risk_tier_opts = ["Critical", "At Risk", "Healthy"]
    risk_tier_filter = st.multiselect(
        "Risk Tier", options=risk_tier_opts, default=risk_tier_opts
    )

    min_score = st.slider("Min Health Score", 0, 100, 0)

    st.markdown("---")
    st.markdown("### ⚙️ Display")
    show_raw = st.checkbox("Show Raw Data Table", value=False)
    top_n = st.slider("Top N Funds to Highlight", 5, 30, 10)

    st.markdown("---")
    st.markdown(
        "**AD Control Tower v1.0**  \nAlter Domus Hackathon  \n"
        "Powered by Python · Pandas · Plotly · Streamlit"
    )

# ─────────────────────────────────────────────────────────────────────────────
# Data loading helpers
# ─────────────────────────────────────────────────────────────────────────────
REQUIRED_COLS = [
    "fund_name", "fund_type", "open_exceptions",
    "overdue_tasks", "client_escalations",
    "resource_utilization", "sla_breaches",
]


@st.cache_data
def _load_sample() -> pd.DataFrame:
    try:
        return pd.read_csv("sample_dataset.csv")
    except FileNotFoundError:
        from data_generator import DataGenerator
        return DataGenerator().generate(100)


@st.cache_data
def _load_uploaded(raw_bytes: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(raw_bytes))


def _validate(df: pd.DataFrame):
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        st.error(f"CSV is missing columns: {', '.join(missing)}")
        st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# Session state — persist loaded data across reruns
# ─────────────────────────────────────────────────────────────────────────────
if "df_raw" not in st.session_state:
    st.session_state["df_raw"] = None

if load_sample_btn:
    st.session_state["df_raw"] = _load_sample()

if uploaded_file is not None:
    df_up = _load_uploaded(uploaded_file.read())
    _validate(df_up)
    st.session_state["df_raw"] = df_up

# ─────────────────────────────────────────────────────────────────────────────
# Welcome screen
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state["df_raw"] is None:
    st.markdown(
        """
        <div style='text-align:center;padding:80px 0;'>
            <div style='font-size:5rem;'>🗼</div>
            <h2 style='color:#58a6ff;'>Welcome to AD Control Tower</h2>
            <p style='color:#8b949e;font-size:1.1rem;max-width:560px;margin:auto;'>
                Your single operational intelligence platform for alternative fund administration.
                Upload your fund data or load the sample dataset to begin.
            </p>
            <br/>
            <p style='color:#30363d;font-size:0.9rem;'>← Use the sidebar to get started</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Process data
# ─────────────────────────────────────────────────────────────────────────────
health_engine = HealthEngine()
risk_engine = RiskEngine()
rec_engine = RecommendationEngine()

df_all = health_engine.calculate_scores(st.session_state["df_raw"])
df_all = risk_engine.classify(df_all)

# Apply sidebar filters
df = df_all.copy()
if fund_type_filter:
    df = df[df["fund_type"].isin(fund_type_filter)]
if risk_tier_filter:
    df = df[df["risk_tier"].isin(risk_tier_filter)]
df = df[df["health_score"] >= min_score]

if len(df) == 0:
    st.warning("No funds match the current filters. Adjust the sidebar filters.")
    st.stop()

# Aggregates
portfolio_score = health_engine.portfolio_score(df)
risk_sum = risk_engine.risk_summary(df)
breakdown = health_engine.score_breakdown(df)
bottlenecks = risk_engine.identify_bottlenecks(df)
recommendations = rec_engine.generate(df)

# ─────────────────────────────────────────────────────────────────────────────
# ① Portfolio Health Score — gauge + KPI row
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">① Portfolio Health Score</div>', unsafe_allow_html=True)

gauge_col, k1, k2, k3, k4 = st.columns([2.2, 1, 1, 1, 1])

with gauge_col:
    gauge_color = (
        "#3fb950" if portfolio_score >= 70
        else "#d29922" if portfolio_score >= 40
        else "#f85149"
    )
    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=portfolio_score,
            title={"text": "Portfolio Health Index", "font": {"size": 16, "color": "#e6edf3"}},
            delta={"reference": 70, "increasing": {"color": "#3fb950"}, "decreasing": {"color": "#f85149"}},
            number={"font": {"color": gauge_color, "size": 48}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#8b949e", "tickfont": {"color": "#8b949e"}},
                "bar": {"color": gauge_color},
                "bgcolor": "#161b22",
                "bordercolor": "#30363d",
                "steps": [
                    {"range": [0, 40], "color": "#2d1b1b"},
                    {"range": [40, 70], "color": "#2d2b1b"},
                    {"range": [70, 100], "color": "#1b2d1b"},
                ],
                "threshold": {"line": {"color": "#58a6ff", "width": 3}, "thickness": 0.75, "value": 70},
            },
        )
    )
    fig_gauge.update_layout(
        paper_bgcolor="#0d1117",
        font={"color": "#e6edf3"},
        height=250,
        margin=dict(l=20, r=20, t=40, b=10),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with k1:
    st.metric("🚨 Critical", risk_sum["critical_count"], f"{risk_sum['critical_pct']}%", delta_color="inverse")
    st.metric("Funds in View", len(df))
with k2:
    st.metric("⚠️ At Risk", risk_sum["at_risk_count"], f"{risk_sum['at_risk_pct']}%", delta_color="inverse")
    st.metric("Open Exceptions", breakdown["total_open_exceptions"])
with k3:
    st.metric("✅ Healthy", risk_sum["healthy_count"], f"{risk_sum['healthy_pct']}%")
    st.metric("SLA Breaches", breakdown["total_sla_breaches"], delta_color="inverse")
with k4:
    avg_u = breakdown["avg_resource_utilization"]
    st.metric("⚡ Avg Utilisation", f"{avg_u:.0f}%",
              f"{avg_u - 75:.1f}pp vs target", delta_color="inverse" if avg_u > 80 else "normal")
    st.metric("Escalations", breakdown["total_client_escalations"], delta_color="inverse")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ② Risk Distribution + Health Score Distribution
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">② Risk Classification</div>', unsafe_allow_html=True)

col_pie, col_hist = st.columns([1, 2])

with col_pie:
    fig_pie = go.Figure(
        go.Pie(
            labels=["Critical", "At Risk", "Healthy"],
            values=[risk_sum["critical_count"], risk_sum["at_risk_count"], risk_sum["healthy_count"]],
            hole=0.52,
            marker=dict(colors=["#f85149", "#d29922", "#3fb950"]),
            textfont=dict(color="white", size=12),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
        )
    )
    fig_pie.update_layout(
        paper_bgcolor="#0d1117",
        font={"color": "#e6edf3"},
        legend=dict(bgcolor="#161b22", font=dict(color="#e6edf3")),
        height=270,
        margin=dict(l=10, r=10, t=20, b=10),
        annotations=[dict(
            text=f"<b>{len(df)}</b><br>Funds",
            x=0.5, y=0.5, font_size=14, showarrow=False, font_color="#e6edf3",
        )],
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_hist:
    fig_hist = go.Figure()
    fig_hist.add_trace(
        go.Histogram(
            x=df["health_score"],
            nbinsx=20,
            marker=dict(
                color=df["health_score"],
                colorscale=[[0, "#f85149"], [0.4, "#d29922"], [0.7, "#3fb950"], [1, "#3fb950"]],
                showscale=False,
            ),
            opacity=0.85,
        )
    )
    fig_hist.add_vline(x=40, line_dash="dash", line_color="#f85149",
                       annotation_text="Critical (40)", annotation_font_color="#f85149")
    fig_hist.add_vline(x=70, line_dash="dash", line_color="#3fb950",
                       annotation_text="Healthy (70)", annotation_font_color="#3fb950")
    fig_hist.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
        font={"color": "#e6edf3"},
        xaxis=dict(title="Health Score", gridcolor="#30363d", color="#8b949e"),
        yaxis=dict(title="Fund Count", gridcolor="#30363d", color="#8b949e"),
        height=270,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ③ Fund Health Scores — bottom performers
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">③ Fund Health Scores — Bottom Performers</div>', unsafe_allow_html=True)

df_bottom = df.nsmallest(top_n, "health_score").sort_values("health_score")
bar_colors = df_bottom["health_score"].apply(
    lambda s: "#f85149" if s < 40 else "#d29922" if s < 70 else "#3fb950"
).tolist()

fig_bar = go.Figure(
    go.Bar(
        x=df_bottom["health_score"],
        y=df_bottom["fund_name"],
        orientation="h",
        marker=dict(color=bar_colors),
        text=df_bottom["health_score"].apply(lambda x: f"{x:.0f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Health Score: %{x:.1f}<extra></extra>",
    )
)
fig_bar.add_vline(x=40, line_dash="dash", line_color="#f85149")
fig_bar.add_vline(x=70, line_dash="dash", line_color="#3fb950")
fig_bar.update_layout(
    paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
    font={"color": "#e6edf3"},
    xaxis=dict(range=[0, 115], title="Health Score (0–100)", gridcolor="#30363d", color="#8b949e"),
    yaxis=dict(title="", color="#e6edf3"),
    height=max(300, top_n * 35),
    margin=dict(l=10, r=60, t=10, b=10),
)
st.plotly_chart(fig_bar, use_container_width=True)
st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ④ Capacity Analysis
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">④ Capacity Analysis — Resource Utilisation</div>', unsafe_allow_html=True)

cap_chart, cap_summary = st.columns([3, 1])

with cap_chart:
    df_util = df.sort_values("resource_utilization", ascending=False).head(top_n)
    util_colors = df_util["resource_utilization"].apply(
        lambda u: "#f85149" if u >= 90 else "#d29922" if u >= 80 else "#3fb950"
    ).tolist()

    fig_util = go.Figure(
        go.Bar(
            x=df_util["fund_name"],
            y=df_util["resource_utilization"],
            marker=dict(color=util_colors),
            text=df_util["resource_utilization"].apply(lambda u: f"{u:.0f}%"),
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Utilisation: %{y:.1f}%<extra></extra>",
        )
    )
    fig_util.add_hline(y=85, line_dash="dash", line_color="#d29922", annotation_text="Caution 85%")
    fig_util.add_hline(y=95, line_dash="dash", line_color="#f85149", annotation_text="Critical 95%")
    fig_util.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
        font={"color": "#e6edf3"},
        xaxis=dict(title="", gridcolor="#30363d", color="#8b949e", tickangle=-30),
        yaxis=dict(title="Utilisation %", range=[0, 115], gridcolor="#30363d", color="#8b949e"),
        height=340,
        margin=dict(l=10, r=10, t=10, b=80),
    )
    st.plotly_chart(fig_util, use_container_width=True)

with cap_summary:
    overloaded = int((df["resource_utilization"] >= 90).sum())
    caution_z = int(((df["resource_utilization"] >= 80) & (df["resource_utilization"] < 90)).sum())
    optimal_z = int(((df["resource_utilization"] >= 60) & (df["resource_utilization"] < 80)).sum())
    under_z = int((df["resource_utilization"] < 60).sum())

    st.markdown("**Capacity Zones**")
    st.markdown(f"🔴 **Overloaded (≥90%):** {overloaded} funds")
    st.markdown(f"🟡 **Caution (80–90%):** {caution_z} funds")
    st.markdown(f"🟢 **Optimal (60–80%):** {optimal_z} funds")
    st.markdown(f"⚪ **Under-utilised (<60%):** {under_z} funds")
    st.markdown("---")
    st.markdown("**By Fund Type**")
    for ftype, avg in df.groupby("fund_type")["resource_utilization"].mean().items():
        icon = "🔴" if avg >= 90 else "🟡" if avg >= 80 else "🟢"
        st.markdown(f"{icon} **{ftype}:** {avg:.0f}%")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ⑤ Bottleneck Detection
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">⑤ Bottleneck Detection</div>', unsafe_allow_html=True)

if bottlenecks:
    bn_cols = st.columns(min(len(bottlenecks), 3))
    for i, bn in enumerate(bottlenecks):
        sev_color = "#f85149" if bn["severity"] == "Critical" else "#d29922" if bn["severity"] == "High" else "#58a6ff"
        with bn_cols[i % 3]:
            st.markdown(
                f"""
                <div style='background:#161b22;border:1px solid #30363d;
                            border-left:4px solid {sev_color};border-radius:6px;
                            padding:14px;margin-bottom:10px;'>
                    <div style='color:{sev_color};font-weight:700;font-size:0.78rem;'>
                        {bn["severity"].upper()}
                    </div>
                    <div style='color:#e6edf3;font-weight:600;font-size:1rem;margin:4px 0;'>
                        {bn["area"]}
                    </div>
                    <div style='color:#8b949e;font-size:0.84rem;'>{bn["detail"]}</div>
                    <div style='color:#58a6ff;font-size:0.78rem;margin-top:8px;'>
                        Affects {bn["affected_funds"]} funds
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
else:
    st.success("No systemic bottlenecks detected. Portfolio is operating within normal parameters.")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ⑥ Recommended Actions
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">⑥ Recommended Actions</div>', unsafe_allow_html=True)

BORDER = {"P1 - Immediate": "#f85149", "P2 - This Week": "#d29922", "P3 - This Month": "#3fb950"}
BG = {"P1 - Immediate": "#2d1b1b", "P2 - This Week": "#2d2b1b", "P3 - This Month": "#1b2d1b"}

for rec in recommendations[:8]:
    bc = BORDER.get(rec["priority"], "#58a6ff")
    bg = BG.get(rec["priority"], "#161b22")
    st.markdown(
        f"""
        <div style='background:{bg};border:1px solid #30363d;border-left:5px solid {bc};
                    border-radius:6px;padding:14px 18px;margin-bottom:8px;'>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                <span style='color:{bc};font-weight:700;font-size:0.8rem;'>
                    {rec["priority"]} &nbsp;|&nbsp; {rec["category"]}
                </span>
                <span style='color:#8b949e;font-size:0.78rem;'>
                    ⏱ {rec["timeline"]} &nbsp;·&nbsp; {rec["affected_funds"]} fund(s)
                </span>
            </div>
            <div style='color:#e6edf3;font-size:0.95rem;margin-top:6px;'>
                {rec.get("icon","")} {rec["action"]}
            </div>
            <div style='color:#8b949e;font-size:0.82rem;margin-top:4px;'>
                Impact: {rec["impact"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ⑦ Operational Heatmap
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">⑦ Operational Heatmap — Top Risk Funds</div>', unsafe_allow_html=True)

df_heat_src = df.sort_values(["risk_priority", "health_score"]).head(20)
heat_metrics = ["open_exceptions", "overdue_tasks", "client_escalations", "resource_utilization", "sla_breaches"]
heat_labels = ["Open Exceptions", "Overdue Tasks", "Client Escalations", "Utilisation %", "SLA Breaches"]

raw_vals = df_heat_src[heat_metrics].copy()
norm_vals = (raw_vals - raw_vals.min()) / (raw_vals.max() - raw_vals.min() + 1e-6)

fig_heat = go.Figure(
    go.Heatmap(
        z=norm_vals.values,
        x=heat_labels,
        y=df_heat_src["fund_name"].tolist(),
        colorscale=[[0, "#1b2d1b"], [0.5, "#2d2b1b"], [1, "#2d1b1b"]],
        text=raw_vals.round(1).values,
        texttemplate="%{text}",
        textfont=dict(size=10, color="white"),
        hovertemplate="<b>%{y}</b><br>%{x}: %{text}<extra></extra>",
        showscale=True,
        colorbar=dict(
            title=dict(text="Risk Level", font=dict(color="#8b949e")),
            tickvals=[0, 0.5, 1],
            ticktext=["Low", "Med", "High"],
            tickfont=dict(color="#8b949e"),
        ),
    )
)
fig_heat.update_layout(
    paper_bgcolor="#0d1117",
    font={"color": "#e6edf3"},
    xaxis=dict(color="#8b949e"),
    yaxis=dict(color="#e6edf3", autorange="reversed"),
    height=max(420, len(df_heat_src) * 28),
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig_heat, use_container_width=True)
st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ⑧ Executive Insights
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">⑧ Executive Insights</div>', unsafe_allow_html=True)

ins1, ins2, ins3 = st.columns(3)

with ins1:
    if risk_sum["critical_count"] > 0:
        worst = df[df["risk_tier"] == "Critical"].nsmallest(1, "health_score").iloc[0]
        st.markdown(
            f"""<div style='background:#161b22;border:1px solid #f85149;
                            border-radius:8px;padding:16px;'>
                <div style='color:#f85149;font-weight:700;margin-bottom:8px;'>🚨 HIGHEST RISK FUND</div>
                <div style='color:#e6edf3;font-size:1.1rem;font-weight:600;'>{worst["fund_name"]}</div>
                <div style='color:#8b949e;font-size:0.83rem;'>{worst["fund_type"]}</div>
                <div style='color:#f85149;font-size:2rem;font-weight:700;margin:8px 0;'>{worst["health_score"]}<span style='font-size:1rem;'>/100</span></div>
                <div style='color:#8b949e;font-size:0.82rem;'>
                    Exceptions: {worst["open_exceptions"]} &nbsp;|&nbsp; Overdue: {worst["overdue_tasks"]}<br>
                    Escalations: {worst["client_escalations"]} &nbsp;|&nbsp; SLA Breaches: {worst["sla_breaches"]}
                </div>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.info("No Critical funds in current view.")

with ins2:
    score_color = "#3fb950" if portfolio_score >= 70 else "#d29922" if portfolio_score >= 40 else "#f85149"
    st.markdown(
        f"""<div style='background:#161b22;border:1px solid #30363d;
                        border-radius:8px;padding:16px;'>
            <div style='color:#58a6ff;font-weight:700;margin-bottom:8px;'>📊 PORTFOLIO SNAPSHOT</div>
            <div style='color:#e6edf3;line-height:2;'>
                Portfolio Score: <b style='color:{score_color};'>{portfolio_score}/100</b><br>
                Funds Needing Action: <b style='color:#f85149;'>{risk_sum["critical_count"] + risk_sum["at_risk_count"]}</b><br>
                Systemic Bottlenecks: <b style='color:#d29922;'>{len(bottlenecks)}</b><br>
                Active Recommendations: <b style='color:#58a6ff;'>{len(recommendations)}</b><br>
                Funds in Safe Zone: <b style='color:#3fb950;'>{risk_sum["healthy_pct"]:.0f}%</b>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

with ins3:
    best = df.nlargest(1, "health_score").iloc[0]
    st.markdown(
        f"""<div style='background:#161b22;border:1px solid #3fb950;
                        border-radius:8px;padding:16px;'>
            <div style='color:#3fb950;font-weight:700;margin-bottom:8px;'>🏆 TOP PERFORMING FUND</div>
            <div style='color:#e6edf3;font-size:1.1rem;font-weight:600;'>{best["fund_name"]}</div>
            <div style='color:#8b949e;font-size:0.83rem;'>{best["fund_type"]}</div>
            <div style='color:#3fb950;font-size:2rem;font-weight:700;margin:8px 0;'>{best["health_score"]}<span style='font-size:1rem;'>/100</span></div>
            <div style='color:#8b949e;font-size:0.82rem;'>
                Exceptions: {best["open_exceptions"]} &nbsp;|&nbsp; Overdue: {best["overdue_tasks"]}<br>
                Escalations: {best["client_escalations"]} &nbsp;|&nbsp; SLA Breaches: {best["sla_breaches"]}
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ⑨ Raw data table + download
# ─────────────────────────────────────────────────────────────────────────────
if show_raw:
    st.markdown('<div class="section-hdr">⑨ Fund Data Table</div>', unsafe_allow_html=True)

    display_cols = [
        "fund_name", "fund_type", "health_score", "risk_tier",
        "open_exceptions", "overdue_tasks", "client_escalations",
        "resource_utilization", "sla_breaches",
    ]
    display_labels = [
        "Fund Name", "Type", "Health Score", "Risk Tier",
        "Open Exceptions", "Overdue Tasks", "Client Escalations",
        "Utilisation %", "SLA Breaches",
    ]
    display_df = df[display_cols].copy()
    display_df.columns = display_labels
    display_df = display_df.sort_values("Health Score")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv_out = display_df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Analysis as CSV",
        data=csv_out,
        file_name="ad_control_tower_analysis.csv",
        mime="text/csv",
    )

# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#30363d;font-size:0.78rem;padding:6px;'>"
    "AD Control Tower v1.0 &nbsp;|&nbsp; Alter Domus Hackathon &nbsp;|&nbsp; "
    "Operational Intelligence Platform &nbsp;|&nbsp; From Reactive to Predictive"
    "</div>",
    unsafe_allow_html=True,
)
