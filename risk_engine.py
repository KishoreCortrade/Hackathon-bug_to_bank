"""
risk_engine.py
--------------
AD Control Tower — Risk Classification & Bottleneck Engine

Classifies each fund into a risk tier using both:
  (a) Health score thresholds
  (b) Hard override rules based on individual metric severity

Override logic ensures that a fund with, e.g., 8+ client escalations
is always flagged Critical even if its composite score looks moderate.

Also identifies systemic portfolio-level bottlenecks.
"""

import pandas as pd
from typing import List, Dict


class RiskEngine:
    """Tier classification and portfolio bottleneck detection."""

    # ── Risk tier labels ────────────────────────────────────────────────────
    TIERS = {"critical": "Critical", "at_risk": "At Risk", "healthy": "Healthy"}

    COLORS = {
        "Critical": "#f85149",
        "At Risk": "#d29922",
        "Healthy": "#3fb950",
    }

    PRIORITY = {"Critical": 1, "At Risk": 2, "Healthy": 3}

    # ── Thresholds ──────────────────────────────────────────────────────────
    # Health score band boundaries
    CRITICAL_SCORE = 40
    AT_RISK_SCORE = 70

    # Metric override thresholds — At Risk floor
    ESC_AT_RISK = 5          # client escalations ≥ 5  → minimum At Risk
    SLA_AT_RISK = 8          # sla_breaches ≥ 8        → minimum At Risk
    UTIL_AT_RISK = 95        # resource_utilization ≥ 95% → minimum At Risk

    # Metric override thresholds — Critical floor
    ESC_CRITICAL = 8         # client escalations ≥ 8  → Critical
    SLA_CRITICAL = 10        # sla_breaches ≥ 10       → Critical (if exceptions also high)
    EXC_CRITICAL = 30        # open_exceptions ≥ 30    → used in combo rule
    UTIL_CRITICAL = 98       # resource_utilization ≥ 98% → Critical

    # Bottleneck portfolio thresholds
    BN_EXCEPTION_AVG = 20
    BN_EXCEPTION_HIGH = 25
    BN_OVERDUE_AVG = 15
    BN_OVERDUE_HIGH = 20
    BN_UTIL_OVERLOADED_PCT = 0.25
    BN_UTIL_OVERLOADED = 85
    BN_SLA_AVG = 5
    BN_SLA_HIGH = 5
    BN_ESC_TOTAL_RATIO = 2  # total escalations > N * fund_count

    # ───────────────────────────────────────────────────────────────────────
    # Public API
    # ───────────────────────────────────────────────────────────────────────

    def classify(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add risk_tier, risk_color, risk_priority columns. Returns new df."""
        df = df.copy()
        df["risk_tier"] = df.apply(self._classify_row, axis=1)
        df["risk_color"] = df["risk_tier"].map(self.COLORS)
        df["risk_priority"] = df["risk_tier"].map(self.PRIORITY)
        return df

    def risk_summary(self, df: pd.DataFrame) -> dict:
        """Portfolio-level risk count and percentages."""
        counts = df["risk_tier"].value_counts().to_dict()
        total = max(len(df), 1)
        return {
            "critical_count": counts.get("Critical", 0),
            "at_risk_count": counts.get("At Risk", 0),
            "healthy_count": counts.get("Healthy", 0),
            "critical_pct": round(counts.get("Critical", 0) / total * 100, 1),
            "at_risk_pct": round(counts.get("At Risk", 0) / total * 100, 1),
            "healthy_pct": round(counts.get("Healthy", 0) / total * 100, 1),
        }

    def get_critical_funds(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df["risk_tier"] == "Critical"].sort_values("health_score")

    def get_at_risk_funds(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df["risk_tier"] == "At Risk"].sort_values("health_score")

    def identify_bottlenecks(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect systemic operational patterns that indicate portfolio-wide
        bottlenecks rather than isolated fund problems.
        """
        bottlenecks: List[Dict] = []
        total = len(df)

        # ── Exception management ──────────────────────────────────────────
        avg_exc = df["open_exceptions"].mean()
        if avg_exc > self.BN_EXCEPTION_AVG:
            bottlenecks.append({
                "area": "Exception Management",
                "severity": "High",
                "detail": (
                    f"Portfolio average of {avg_exc:.0f} open exceptions per fund "
                    f"indicates systemic exception handling breakdown."
                ),
                "affected_funds": int((df["open_exceptions"] > self.BN_EXCEPTION_HIGH).sum()),
            })

        # ── Task completion ───────────────────────────────────────────────
        avg_tasks = df["overdue_tasks"].mean()
        if avg_tasks > self.BN_OVERDUE_AVG:
            bottlenecks.append({
                "area": "Task Completion",
                "severity": "High",
                "detail": (
                    f"Average {avg_tasks:.0f} overdue tasks across funds — "
                    f"workflow velocity has deteriorated."
                ),
                "affected_funds": int((df["overdue_tasks"] > self.BN_OVERDUE_HIGH).sum()),
            })

        # ── Resource capacity ─────────────────────────────────────────────
        overloaded_mask = df["resource_utilization"] > self.BN_UTIL_OVERLOADED
        overloaded_count = overloaded_mask.sum()
        if overloaded_count > total * self.BN_UTIL_OVERLOADED_PCT:
            bottlenecks.append({
                "area": "Resource Capacity",
                "severity": "Critical",
                "detail": (
                    f"{overloaded_count} funds ({overloaded_count/total*100:.0f}%) "
                    f"operating above {self.BN_UTIL_OVERLOADED}% utilization — "
                    f"team burnout and service quality degradation risk."
                ),
                "affected_funds": int(overloaded_count),
            })

        # ── SLA management ────────────────────────────────────────────────
        avg_sla = df["sla_breaches"].mean()
        if avg_sla > self.BN_SLA_AVG:
            bottlenecks.append({
                "area": "SLA Management",
                "severity": "High",
                "detail": (
                    f"Average {avg_sla:.1f} SLA breaches per fund — "
                    f"client contractual commitments systematically at risk."
                ),
                "affected_funds": int((df["sla_breaches"] > self.BN_SLA_HIGH).sum()),
            })

        # ── Client escalation pattern ─────────────────────────────────────
        total_esc = df["client_escalations"].sum()
        if total_esc > total * self.BN_ESC_TOTAL_RATIO:
            bottlenecks.append({
                "area": "Client Relationship",
                "severity": "Medium",
                "detail": (
                    f"{int(total_esc)} total client escalations across portfolio — "
                    f"relationship management requires immediate attention."
                ),
                "affected_funds": int((df["client_escalations"] > 2).sum()),
            })

        return bottlenecks

    # ───────────────────────────────────────────────────────────────────────
    # Private helpers
    # ───────────────────────────────────────────────────────────────────────

    def _classify_row(self, row) -> str:
        score = float(row.get("health_score", 100))
        esc = float(row["client_escalations"])
        sla = float(row["sla_breaches"])
        exc = float(row["open_exceptions"])
        util = float(row["resource_utilization"])

        # ── Critical override rules ───────────────────────────────────────
        if (
            score < self.CRITICAL_SCORE
            or esc >= self.ESC_CRITICAL
            or (sla >= self.SLA_CRITICAL and exc >= self.EXC_CRITICAL)
            or util >= self.UTIL_CRITICAL
        ):
            return self.TIERS["critical"]

        # ── At Risk override rules ────────────────────────────────────────
        if (
            score < self.AT_RISK_SCORE
            or esc >= self.ESC_AT_RISK
            or sla >= self.SLA_AT_RISK
            or util >= self.UTIL_AT_RISK
        ):
            return self.TIERS["at_risk"]

        return self.TIERS["healthy"]
