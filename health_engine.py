"""
health_engine.py
----------------
AD Control Tower — Fund Health Score Engine

Calculates a composite health score (0–100) for each fund
based on five operational metrics. Higher score = healthier fund.

Score Bands:
    70–100  →  Healthy   (Green)
    40–69   →  At Risk   (Amber)
    0–39    →  Critical  (Red)

Metric Weights:
    Open Exceptions      25%
    Overdue Tasks        25%
    SLA Breaches         20%
    Client Escalations   20%
    Resource Utilization 10%  (penalty for over- or under-utilization)
"""

import pandas as pd
import numpy as np


class HealthEngine:
    """Scores funds and aggregates portfolio-level intelligence."""

    # ── Scoring weights (must sum to 1.0) ──────────────────────────────────
    WEIGHTS = {
        "open_exceptions": 0.25,
        "overdue_tasks": 0.25,
        "sla_breaches": 0.20,
        "client_escalations": 0.20,
        "resource_utilization": 0.10,
    }

    # ── Max expected values for normalization ───────────────────────────────
    THRESHOLDS = {
        "open_exceptions": 50,
        "overdue_tasks": 40,
        "client_escalations": 10,
        "sla_breaches": 15,
    }

    # ── Resource utilization bands ──────────────────────────────────────────
    UTIL_OPTIMAL_LOW = 60
    UTIL_OPTIMAL_HIGH = 80

    # ── Health score bands ──────────────────────────────────────────────────
    HEALTHY_THRESHOLD = 70
    CRITICAL_THRESHOLD = 40

    # ── Label / color maps ──────────────────────────────────────────────────
    LABELS = {
        "healthy": "Healthy",
        "at_risk": "At Risk",
        "critical": "Critical",
    }

    COLORS = {
        "Healthy": "#3fb950",
        "At Risk": "#d29922",
        "Critical": "#f85149",
    }

    # ───────────────────────────────────────────────────────────────────────
    # Public API
    # ───────────────────────────────────────────────────────────────────────

    def calculate_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add health_score, health_label, and health_color columns to df.
        Returns a new DataFrame (input is not mutated).
        """
        df = df.copy()
        df["health_score"] = df.apply(self._score_row, axis=1)
        df["health_label"] = df["health_score"].apply(self._label)
        df["health_color"] = df["health_label"].map(self.COLORS)
        return df

    def portfolio_score(self, df: pd.DataFrame) -> float:
        """Return the mean health score across all funds in df."""
        if "health_score" not in df.columns:
            df = self.calculate_scores(df)
        return round(float(df["health_score"].mean()), 1)

    def score_breakdown(self, df: pd.DataFrame) -> dict:
        """
        Return portfolio-level aggregate statistics used by the dashboard
        KPI row and executive insights panel.
        """
        return {
            "avg_open_exceptions": round(float(df["open_exceptions"].mean()), 1),
            "avg_overdue_tasks": round(float(df["overdue_tasks"].mean()), 1),
            "avg_client_escalations": round(float(df["client_escalations"].mean()), 1),
            "avg_resource_utilization": round(float(df["resource_utilization"].mean()), 1),
            "avg_sla_breaches": round(float(df["sla_breaches"].mean()), 1),
            "total_open_exceptions": int(df["open_exceptions"].sum()),
            "total_overdue_tasks": int(df["overdue_tasks"].sum()),
            "total_client_escalations": int(df["client_escalations"].sum()),
            "total_sla_breaches": int(df["sla_breaches"].sum()),
        }

    # ───────────────────────────────────────────────────────────────────────
    # Private helpers
    # ───────────────────────────────────────────────────────────────────────

    def _score_row(self, row) -> float:
        """
        Compute a single fund's health score.

        Each metric is normalised to a 0–1 penalty (0 = no problem,
        1 = worst possible). The weighted sum of penalties is subtracted
        from 100 to produce the final score.
        """
        exc_penalty = self._clamp(row["open_exceptions"] / self.THRESHOLDS["open_exceptions"])
        task_penalty = self._clamp(row["overdue_tasks"] / self.THRESHOLDS["overdue_tasks"])
        esc_penalty = self._clamp(row["client_escalations"] / self.THRESHOLDS["client_escalations"])
        sla_penalty = self._clamp(row["sla_breaches"] / self.THRESHOLDS["sla_breaches"])
        util_penalty = self._utilization_penalty(float(row["resource_utilization"]))

        weighted_penalty = (
            exc_penalty * self.WEIGHTS["open_exceptions"]
            + task_penalty * self.WEIGHTS["overdue_tasks"]
            + esc_penalty * self.WEIGHTS["client_escalations"]
            + sla_penalty * self.WEIGHTS["sla_breaches"]
            + util_penalty * self.WEIGHTS["resource_utilization"]
        )

        score = round((1.0 - weighted_penalty) * 100, 1)
        return float(max(0.0, min(100.0, score)))

    def _utilization_penalty(self, util: float) -> float:
        """
        Resource utilization penalty curve:
            < 60%      mild penalty  (under-staffed / idle capacity)
            60–80%     no penalty    (optimal operating zone)
            80–100%    sharp penalty (overloaded, burnout / error risk)
        """
        if util < self.UTIL_OPTIMAL_LOW:
            penalty = ((self.UTIL_OPTIMAL_LOW - util) / self.UTIL_OPTIMAL_LOW) * 0.30
        elif util <= self.UTIL_OPTIMAL_HIGH:
            penalty = 0.0
        else:
            penalty = (util - self.UTIL_OPTIMAL_HIGH) / (100.0 - self.UTIL_OPTIMAL_HIGH)
        return self._clamp(penalty)

    @staticmethod
    def _clamp(value: float) -> float:
        return float(max(0.0, min(1.0, value)))

    def _label(self, score: float) -> str:
        if score >= self.HEALTHY_THRESHOLD:
            return self.LABELS["healthy"]
        if score >= self.CRITICAL_THRESHOLD:
            return self.LABELS["at_risk"]
        return self.LABELS["critical"]
