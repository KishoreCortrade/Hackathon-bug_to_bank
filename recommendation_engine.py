"""
recommendation_engine.py
------------------------
AD Control Tower — Smart Recommendation Engine

Generates prioritised, actionable recommendations based on fund-level
and portfolio-level metric patterns.

Priority tiers:
    P1 - Immediate   (24–72 hours)
    P2 - This Week   (3–7 days)
    P3 - This Month  (2–4 weeks)

Each recommendation includes:
    priority, category, action, impact, timeline,
    affected_funds, funds (sample list), icon
"""

import pandas as pd
from typing import List, Dict


class RecommendationEngine:
    """Generates prioritised operational recommendations."""

    # ── Metric thresholds used for rule evaluation ──────────────────────────
    HIGH_ESC = 5
    CRITICAL_ESC = 8
    HIGH_SLA = 8
    WATCH_SLA_LOW = 3
    WATCH_SLA_HIGH = 8
    OVERLOADED_UTIL = 90
    CAUTION_UTIL_LOW = 80
    CAUTION_UTIL_HIGH = 90
    UNDERUTIL = 50
    HIGH_EXC = 30
    MED_EXC_LOW = 15
    MED_EXC_HIGH = 30
    HIGH_OVERDUE = 25
    LOW_PORTFOLIO_HEALTH = 60

    PRIORITY_ORDER = {"P1 - Immediate": 0, "P2 - This Week": 1, "P3 - This Month": 2}

    # ───────────────────────────────────────────────────────────────────────
    # Public API
    # ───────────────────────────────────────────────────────────────────────

    def generate(self, df: pd.DataFrame) -> List[Dict]:
        """Return a sorted list of recommendation dicts."""
        recs: List[Dict] = []
        recs.extend(self._client_escalation_recs(df))
        recs.extend(self._sla_recs(df))
        recs.extend(self._resource_recs(df))
        recs.extend(self._exception_recs(df))
        recs.extend(self._task_recs(df))
        recs.extend(self._portfolio_recs(df))

        recs.sort(key=lambda r: self.PRIORITY_ORDER.get(r["priority"], 99))
        return recs

    # ───────────────────────────────────────────────────────────────────────
    # Rule methods
    # ───────────────────────────────────────────────────────────────────────

    def _client_escalation_recs(self, df: pd.DataFrame) -> List[Dict]:
        recs = []
        critical_esc = df[df["client_escalations"] >= self.CRITICAL_ESC]
        high_esc = df[
            (df["client_escalations"] >= self.HIGH_ESC)
            & (df["client_escalations"] < self.CRITICAL_ESC)
        ]

        if len(critical_esc) > 0:
            recs.append(self._rec(
                priority="P1 - Immediate",
                category="Client Risk — Critical",
                action=(
                    f"Immediately escalate {len(critical_esc)} fund(s) with 8+ client escalations "
                    f"to the Head of Relationship Management and COO. Initiate client recovery plan."
                ),
                impact="Prevent client churn and protect AUM retention. Each lost mandate averages $2M+ in annual fees.",
                timeline="24 hours",
                affected=len(critical_esc),
                funds=critical_esc["fund_name"].tolist()[:5],
                icon="🚨",
            ))

        if len(high_esc) > 0:
            recs.append(self._rec(
                priority="P1 - Immediate",
                category="Client Risk — Elevated",
                action=(
                    f"Schedule client health calls for {len(high_esc)} fund(s) with 5–7 escalations. "
                    f"Assign senior relationship manager as single point of contact."
                ),
                impact="Reduce escalation rate and restore client confidence before churn risk materialises.",
                timeline="48 hours",
                affected=len(high_esc),
                funds=high_esc["fund_name"].tolist()[:5],
                icon="⚠️",
            ))
        return recs

    def _sla_recs(self, df: pd.DataFrame) -> List[Dict]:
        recs = []
        sla_critical = df[df["sla_breaches"] >= self.HIGH_SLA]
        sla_watch = df[
            (df["sla_breaches"] >= self.WATCH_SLA_LOW)
            & (df["sla_breaches"] < self.WATCH_SLA_HIGH)
        ]

        if len(sla_critical) > 0:
            recs.append(self._rec(
                priority="P1 - Immediate",
                category="SLA Recovery",
                action=(
                    f"Initiate formal SLA recovery protocol for {len(sla_critical)} fund(s) with 8+ breaches. "
                    f"Engage Fund Accounting Manager and Compliance. Issue client breach notifications per contractual SLA."
                ),
                impact="Contractual obligation protection, avoidance of penalty clauses, client trust recovery.",
                timeline="48 hours",
                affected=len(sla_critical),
                funds=sla_critical["fund_name"].tolist()[:5],
                icon="🔴",
            ))

        if len(sla_watch) > 0:
            recs.append(self._rec(
                priority="P2 - This Week",
                category="SLA Monitoring",
                action=(
                    f"Increase monitoring frequency to daily for {len(sla_watch)} fund(s) "
                    f"approaching SLA breach threshold (3–7 breaches). Set automated alerts."
                ),
                impact="Proactive breach prevention. Estimated 40% reduction in SLA breach rate with early intervention.",
                timeline="3 days",
                affected=len(sla_watch),
                funds=sla_watch["fund_name"].tolist()[:5],
                icon="👁️",
            ))
        return recs

    def _resource_recs(self, df: pd.DataFrame) -> List[Dict]:
        recs = []
        overloaded = df[df["resource_utilization"] >= self.OVERLOADED_UTIL]
        caution = df[
            (df["resource_utilization"] >= self.CAUTION_UTIL_LOW)
            & (df["resource_utilization"] < self.CAUTION_UTIL_HIGH)
        ]
        underutil = df[df["resource_utilization"] < self.UNDERUTIL]

        if len(overloaded) > 0:
            recs.append(self._rec(
                priority="P1 - Immediate",
                category="Resource Rebalancing — Critical",
                action=(
                    f"Rebalance workload immediately: {len(overloaded)} team(s) operating at 90%+ capacity. "
                    f"Options: (1) Cross-train staff from low-utilisation funds, "
                    f"(2) Engage contracted supplemental resources, "
                    f"(3) Defer non-critical deliverables."
                ),
                impact="Prevent team burnout, service quality degradation, and downstream SLA breaches.",
                timeline="48 hours",
                affected=len(overloaded),
                funds=overloaded["fund_name"].tolist()[:5],
                icon="🔥",
            ))

        if len(underutil) > 0 and len(overloaded) > 0:
            recs.append(self._rec(
                priority="P2 - This Week",
                category="Capacity Optimisation",
                action=(
                    f"Redirect {len(underutil)} under-utilised team(s) (<50% capacity) "
                    f"to support overloaded funds. Assign cross-fund task ownership temporarily."
                ),
                impact="Optimise existing headcount at zero incremental cost. Estimated 15–20% workload redistribution.",
                timeline="5 days",
                affected=len(underutil) + len(overloaded),
                funds=[],
                icon="⚖️",
            ))

        if len(caution) > 0 and len(overloaded) == 0:
            recs.append(self._rec(
                priority="P2 - This Week",
                category="Capacity Planning",
                action=(
                    f"Review Q-quarter staffing plans for {len(caution)} fund(s) in the 80–90% caution zone. "
                    f"Pre-approve contractor pipeline before threshold breach."
                ),
                impact="Proactive capacity management avoids reactive hiring cost premium (est. 25–30% premium).",
                timeline="1 week",
                affected=len(caution),
                funds=caution["fund_name"].tolist()[:5],
                icon="📊",
            ))
        return recs

    def _exception_recs(self, df: pd.DataFrame) -> List[Dict]:
        recs = []
        high_exc = df[df["open_exceptions"] >= self.HIGH_EXC]
        med_exc = df[
            (df["open_exceptions"] >= self.MED_EXC_LOW)
            & (df["open_exceptions"] < self.HIGH_EXC)
        ]

        if len(high_exc) > 0:
            recs.append(self._rec(
                priority="P1 - Immediate",
                category="Exception Resolution Sprint",
                action=(
                    f"Launch 72-hour exception resolution sprint for {len(high_exc)} fund(s) with 30+ open exceptions. "
                    f"Assign dedicated exception handler. Daily stand-up until below 15 exceptions."
                ),
                impact="Estimated 15–25 point health score improvement per fund. Reduces downstream NAV and reporting risk.",
                timeline="72 hours",
                affected=len(high_exc),
                funds=high_exc["fund_name"].tolist()[:5],
                icon="🔧",
            ))

        if len(med_exc) > 0:
            recs.append(self._rec(
                priority="P2 - This Week",
                category="Exception Management",
                action=(
                    f"Schedule structured exception review sessions for {len(med_exc)} fund(s) "
                    f"with 15–30 exceptions. Root-cause analysis required before next NAV cycle."
                ),
                impact="Prevent escalation to critical exception levels. Maintain fund reporting integrity.",
                timeline="1 week",
                affected=len(med_exc),
                funds=med_exc["fund_name"].tolist()[:5],
                icon="📋",
            ))
        return recs

    def _task_recs(self, df: pd.DataFrame) -> List[Dict]:
        recs = []
        high_overdue = df[df["overdue_tasks"] >= self.HIGH_OVERDUE]

        if len(high_overdue) > 0:
            recs.append(self._rec(
                priority="P2 - This Week",
                category="Task Management",
                action=(
                    f"Conduct task triage for {len(high_overdue)} fund(s) with 25+ overdue tasks. "
                    f"Identify blockers, reprioritise backlog, and set daily completion targets."
                ),
                impact="Restore workflow velocity. Overdue tasks are the leading indicator of SLA breaches.",
                timeline="1 week",
                affected=len(high_overdue),
                funds=high_overdue["fund_name"].tolist()[:5],
                icon="📅",
            ))
        return recs

    def _portfolio_recs(self, df: pd.DataFrame) -> List[Dict]:
        recs = []
        avg_health = float(df["health_score"].mean()) if "health_score" in df.columns else 50.0

        if avg_health < self.LOW_PORTFOLIO_HEALTH:
            recs.append(self._rec(
                priority="P2 - This Week",
                category="Portfolio Governance",
                action=(
                    f"Schedule emergency portfolio review with Operations leadership. "
                    f"Portfolio health score is {avg_health:.0f}/100 — below the 60-point threshold. "
                    f"Present top 10 at-risk funds and resource gap analysis."
                ),
                impact="Strategic alignment on recovery priorities across COO, Fund Managers, and Operations Directors.",
                timeline="3 days",
                affected=len(df),
                funds=[],
                icon="🏢",
            ))

        recs.append(self._rec(
            priority="P3 - This Month",
            category="Operational Maturity",
            action=(
                "Implement daily health score review cadence in all team stand-ups. "
                "Set automated Control Tower alerts for any fund dropping below 50. "
                "Integrate with existing ITSM/ticketing system for automatic exception creation."
            ),
            impact="Structural shift from reactive to predictive operations. Target: eliminate all P1 surprises within 90 days.",
            timeline="30 days",
            affected=len(df),
            funds=[],
            icon="🎯",
        ))
        return recs

    # ───────────────────────────────────────────────────────────────────────
    # Factory helper
    # ───────────────────────────────────────────────────────────────────────

    @staticmethod
    def _rec(
        priority: str,
        category: str,
        action: str,
        impact: str,
        timeline: str,
        affected: int,
        funds: list,
        icon: str,
    ) -> Dict:
        return {
            "priority": priority,
            "category": category,
            "action": action,
            "impact": impact,
            "timeline": timeline,
            "affected_funds": affected,
            "funds": funds,
            "icon": icon,
        }
