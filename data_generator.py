"""
data_generator.py
-----------------
AD Control Tower — Synthetic Fund Data Generator

Generates a realistic 100-fund operational dataset with:
    ~20% Critical-profile funds
    ~35% At-Risk-profile funds
    ~45% Healthy-profile funds

Usage:
    python data_generator.py          # generates sample_dataset.csv
    from data_generator import DataGenerator
    df = DataGenerator().generate(100)
"""

import pandas as pd
import numpy as np
import sys


class DataGenerator:
    """Generates synthetic fund operational metrics."""

    # ── Fund name vocabulary ────────────────────────────────────────────────
    PREFIXES = [
        "Apex", "Zenith", "Meridian", "Pinnacle", "Summit", "Vertex", "Nexus",
        "Horizon", "Catalyst", "Vantage", "Bridgepoint", "Carlyle", "Hamilton",
        "Sterling", "Atlas", "Titan", "Orion", "Phoenix", "Pegasus", "Ares",
        "Apollo", "Athena", "Minerva", "Epsilon", "Sigma", "Delta", "Omega",
        "Alpha", "Beta", "Gamma", "Tau", "Zeta", "Northern", "Southern",
        "Eastern", "Western", "Global", "European", "Pacific", "Atlantic",
        "Sovereign", "Prestige", "Heritage", "Legacy", "Prime", "Premier",
        "Elite", "Monarch", "Cobalt", "Argent", "Aurum", "Platinum", "Sapphire",
        "Emerald", "Diamond", "Crystal", "Cascade", "Forte", "Luminary",
    ]

    FUND_TYPES = {
        "Private Equity": 0.30,
        "Private Debt": 0.25,
        "Real Estate": 0.20,
        "Infrastructure": 0.15,
        "Hedge Fund": 0.10,
    }

    TYPE_ABBREV = {
        "Private Equity": "PE",
        "Private Debt": "PD",
        "Real Estate": "RE",
        "Infrastructure": "INF",
        "Hedge Fund": "HF",
    }

    ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]

    # ── Risk profile definitions ────────────────────────────────────────────
    # Ranges are (low_inclusive, high_exclusive) for integers,
    # (low, high) for floats.
    PROFILES = {
        "critical": {
            "weight": 0.20,
            "open_exceptions": (30, 51),
            "overdue_tasks": (25, 41),
            "client_escalations": (6, 11),
            "resource_utilization": (88.0, 100.0),
            "sla_breaches": (8, 16),
        },
        "at_risk": {
            "weight": 0.35,
            "open_exceptions": (15, 33),
            "overdue_tasks": (10, 27),
            "client_escalations": (3, 7),
            "resource_utilization": (75.0, 92.0),
            "sla_breaches": (3, 9),
        },
        "healthy": {
            "weight": 0.45,
            "open_exceptions": (0, 16),
            "overdue_tasks": (0, 12),
            "client_escalations": (0, 4),
            "resource_utilization": (52.0, 82.0),
            "sla_breaches": (0, 4),
        },
    }

    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self._used_names: set = set()

    # ── Public API ──────────────────────────────────────────────────────────

    def generate(self, n: int = 100) -> pd.DataFrame:
        """Return a DataFrame with n fund records."""
        fund_types = list(self.FUND_TYPES.keys())
        type_weights = list(self.FUND_TYPES.values())

        profile_names = list(self.PROFILES.keys())
        profile_weights = [self.PROFILES[p]["weight"] for p in profile_names]

        records = []
        for _ in range(n):
            ftype = np.random.choice(fund_types, p=type_weights)
            profile = np.random.choice(profile_names, p=profile_weights)
            records.append(self._make_record(ftype, profile))

        return pd.DataFrame(records)

    # ── Private helpers ─────────────────────────────────────────────────────

    def _make_record(self, fund_type: str, profile: str) -> dict:
        p = self.PROFILES[profile]
        return {
            "fund_name": self._unique_name(fund_type),
            "fund_type": fund_type,
            "open_exceptions": int(np.random.randint(*p["open_exceptions"])),
            "overdue_tasks": int(np.random.randint(*p["overdue_tasks"])),
            "client_escalations": int(np.random.randint(*p["client_escalations"])),
            "resource_utilization": round(float(np.random.uniform(*p["resource_utilization"])), 1),
            "sla_breaches": int(np.random.randint(*p["sla_breaches"])),
        }

    def _unique_name(self, fund_type: str) -> str:
        abbrev = self.TYPE_ABBREV.get(fund_type, "F")
        for _ in range(100):
            prefix = np.random.choice(self.PREFIXES)
            roman = np.random.choice(self.ROMAN)
            name = f"{prefix} {abbrev} Fund {roman}"
            if name not in self._used_names:
                self._used_names.add(name)
                return name
        # Fallback: append random int to guarantee uniqueness
        name = f"{np.random.choice(self.PREFIXES)} {abbrev} Fund {np.random.randint(100, 999)}"
        self._used_names.add(name)
        return name


# ── CLI entry point ─────────────────────────────────────────────────────────

def main():
    output_path = "sample_dataset.csv"
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100

    gen = DataGenerator(seed=42)
    df = gen.generate(n=n)
    df.to_csv(output_path, index=False)

    print(f"✅ Generated {n} fund records → {output_path}")
    print(f"\nFund type distribution:")
    print(df["fund_type"].value_counts().to_string())
    print(f"\nMetric summary:")
    print(df[["open_exceptions", "overdue_tasks", "client_escalations",
               "resource_utilization", "sla_breaches"]].describe().round(1).to_string())


if __name__ == "__main__":
    main()
