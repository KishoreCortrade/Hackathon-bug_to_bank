# 🗼 AD Control Tower
**From Reactive Operations to Predictive Operations**

> Alter Domus Hackathon — Operational Intelligence MVP

---

## Team Members

| Name | Role |
|---|---|
| ANANTHA KISHORE REDDY | QA Engineer |
---

## Presentation Recording

> 📹 [AD Control Tower — 5-Minute Presentation](https://alterdomusgroup-my.sharepoint.com/:v:/g/personal/ananthakishore_reddy_cortlandglobal_com/IQBZmzO6vMFJS7eRS-gDE-oCATcbv5KXDUqUPP5VaUaDjaM?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D&e=BorAzL)

---

## Repo Contents

| File / Document | Purpose |
|---|---|
| `PROBLEM_STATEMENT.md` | Problem statement brief |
| `METRICS_AND_ROI.md` | Metrics & ROI report |
| `app.py` | Working prototype — runnable end-to-end |
| `AD_Control_Tower_Complete.docx` | Full project documentation (all 22 sections) |
| `README.md` | This file — team members, links, quick start |

---

## What It Does

AD Control Tower is a single-page operational intelligence dashboard that ingests a CSV of fund operational data and instantly produces:

| Output | Description |
|---|---|
| Portfolio Health Score | Composite 0–100 index across all funds |
| Fund Health Scores | Per-fund score with risk tier |
| Risk Classification | Critical / At Risk / Healthy tiers with override rules |
| Capacity Analysis | Resource utilisation heatmap and zone breakdown |
| Bottleneck Detection | Systemic portfolio-wide issues |
| Recommended Actions | Prioritised P1/P2/P3 action plan |
| Executive Insights | Worst fund, portfolio snapshot, top performer |
| Operational Heatmap | Multi-metric view of top risk funds |

---

## Quick Start

```bash
# 1. Clone / download
cd ad-control-tower

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

Then open **http://localhost:8501** and click **"Load Sample Dataset (100 Funds)"**.

---

## CSV Input Format

Upload your own CSV with these exact column names:

| Column | Type | Description |
|---|---|---|
| `fund_name` | string | Unique fund identifier |
| `fund_type` | string | Private Equity / Private Debt / Real Estate / Infrastructure / Hedge Fund |
| `open_exceptions` | integer | Number of currently open exceptions |
| `overdue_tasks` | integer | Number of tasks past due date |
| `client_escalations` | integer | Active client escalations |
| `resource_utilization` | float | Team utilisation percentage (0–100) |
| `sla_breaches` | integer | Number of SLA breaches this period |

---

## Generate Synthetic Data

```bash
python data_generator.py        # generates sample_dataset.csv (100 funds)
python data_generator.py 200    # generates 200 funds
```

---

## Project Structure

```
ad-control-tower/
├── app.py                    # Streamlit dashboard (main entry point)
├── health_engine.py          # Health score calculation engine
├── risk_engine.py            # Risk tier classification + bottleneck detection
├── recommendation_engine.py  # Smart recommendation generation
├── data_generator.py         # Synthetic data generator
├── sample_dataset.csv        # Pre-generated 100-fund dataset
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## Health Score Formula

```
health_score = (1 - weighted_penalty) × 100

weighted_penalty =
    (open_exceptions / 50)      × 0.25
  + (overdue_tasks / 40)        × 0.25
  + (sla_breaches / 15)         × 0.20
  + (client_escalations / 10)   × 0.20
  + utilization_penalty         × 0.10

utilization_penalty:
    < 60%  → mild penalty (under-staffed)
    60–80% → 0 (optimal)
    > 80%  → sharp penalty (overloaded)
```

---

## Risk Tier Rules

| Tier | Condition |
|---|---|
| **Critical** | health_score < 40, OR escalations ≥ 8, OR (SLA ≥ 10 AND exceptions ≥ 30), OR utilisation ≥ 98% |
| **At Risk** | health_score < 70, OR escalations ≥ 5, OR SLA ≥ 8, OR utilisation ≥ 95% |
| **Healthy** | All other funds |

---

## Tech Stack

- **Python 3.10+**
- **Streamlit** — dashboard framework
- **Pandas** — data processing
- **Plotly** — interactive charts
- **NumPy** — numerical computation

---

*Built for the Alter Domus Hackathon · AD Control Tower v1.0*
