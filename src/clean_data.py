"""
clean_data.py
Loads raw support tickets, validates data quality, adds derived columns,
and exports a cleaned dataset for analysis and Tableau consumption.
"""

import pandas as pd
import numpy as np
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW_PATH = "/Users/yiyaoli/ai-workflow-observability/data/raw/support_tickets.csv"
EXPORT_PATH = "/Users/yiyaoli/ai-workflow-observability/data/exports/tickets_cleaned.csv"
os.makedirs(os.path.dirname(EXPORT_PATH), exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading raw data...")
df = pd.read_csv(RAW_PATH, parse_dates=["timestamp"])
print(f"  Loaded {len(df)} rows, {len(df.columns)} columns.\n")

# ── Validation Helpers ────────────────────────────────────────────────────────
issues = []

def check(condition, message):
    if not condition:
        issues.append(message)

# ── Column Type Coercion ──────────────────────────────────────────────────────
bool_cols = [
    "ai_correct_response", "routing_correct", "escalation_required",
    "escalated_to_human", "hallucination_flag", "repeat_issue", "sla_breached"
]
for col in bool_cols:
    df[col] = df[col].astype(bool)

int_cols = ["response_time_seconds", "retry_count"]
for col in int_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

float_cols = [
    "ai_confidence_score", "human_resolution_time_minutes",
    "total_resolution_time_minutes", "customer_rating", "estimated_cost_per_ticket"
]
for col in float_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ── Range Validation ──────────────────────────────────────────────────────────
check(df["ai_confidence_score"].between(0.0, 1.0).all(),
      "ai_confidence_score has values outside [0, 1]")
check(df["customer_rating"].between(1.0, 5.0).all(),
      "customer_rating has values outside [1, 5]")
check(df["retry_count"].dropna().between(0, 3).all(),
      "retry_count has values outside [0, 3]")
check(df["estimated_cost_per_ticket"].gt(0).all(),
      "estimated_cost_per_ticket has non-positive values")
check(df["response_time_seconds"].dropna().gt(0).all(),
      "response_time_seconds has non-positive values")

# ── Categorical Validation ────────────────────────────────────────────────────
valid_tiers = {"bronze", "silver", "gold", "enterprise"}
valid_categories = {
    "billing", "refund", "shipping", "login",
    "account_access", "technical_support", "subscription_cancellation"
}
valid_priorities = {"low", "medium", "high", "critical"}
valid_routing = {"ai_handled", "escalated_to_human"}
valid_failures = {"none", "routing_failure", "hallucination", "timeout", "low_confidence"}

check(set(df["customer_tier"].unique()).issubset(valid_tiers),
      f"Unexpected customer_tier values: {set(df['customer_tier'].unique()) - valid_tiers}")
check(set(df["issue_category"].unique()).issubset(valid_categories),
      f"Unexpected issue_category values: {set(df['issue_category'].unique()) - valid_categories}")
check(set(df["priority_level"].unique()).issubset(valid_priorities),
      f"Unexpected priority_level values: {set(df['priority_level'].unique()) - valid_priorities}")
check(set(df["routing_decision"].unique()).issubset(valid_routing),
      f"Unexpected routing_decision values")
check(set(df["failure_type"].unique()).issubset(valid_failures),
      f"Unexpected failure_type values")

# ── Missing Value Audit ───────────────────────────────────────────────────────
# human_resolution_time_minutes is legitimately NaN for non-escalated tickets
non_escalated_nan = df.loc[~df["escalated_to_human"], "human_resolution_time_minutes"].isna().all()
escalated_nan_count = df.loc[df["escalated_to_human"], "human_resolution_time_minutes"].isna().sum()

check(non_escalated_nan,
      "human_resolution_time_minutes is not NaN for all non-escalated tickets (unexpected)")
if escalated_nan_count > 0:
    issues.append(f"human_resolution_time_minutes is NaN for {escalated_nan_count} escalated tickets")

# Check all other columns for unexpected nulls
other_cols = [c for c in df.columns if c != "human_resolution_time_minutes"]
for col in other_cols:
    null_count = df[col].isna().sum()
    if null_count > 0:
        issues.append(f"Unexpected nulls in '{col}': {null_count} rows")

# ── Derived Columns ───────────────────────────────────────────────────────────
# Confidence band
df["confidence_band"] = pd.cut(
    df["ai_confidence_score"],
    bins=[-np.inf, 0.6, 0.8, np.inf],
    labels=["low", "medium", "high"]
).astype(str)

# Resolution speed
df["resolution_speed"] = pd.cut(
    df["total_resolution_time_minutes"],
    bins=[-np.inf, 30, 120, np.inf],
    labels=["fast", "moderate", "slow"]
).astype(str)

# Cost tier
df["cost_tier"] = pd.cut(
    df["estimated_cost_per_ticket"],
    bins=[-np.inf, 10, 20, np.inf],
    labels=["low_cost", "medium_cost", "high_cost"]
).astype(str)

# Day of week and hour of day (useful for Tableau time analysis)
df["day_of_week"] = df["timestamp"].dt.day_name()
df["hour_of_day"] = df["timestamp"].dt.hour
df["week_number"] = df["timestamp"].dt.isocalendar().week.astype(int)
df["date"] = df["timestamp"].dt.date.astype(str)

# ── Ordered Categoricals for sorting ─────────────────────────────────────────
df["priority_level"] = pd.Categorical(
    df["priority_level"],
    categories=["low", "medium", "high", "critical"],
    ordered=True
)
df["customer_tier"] = pd.Categorical(
    df["customer_tier"],
    categories=["bronze", "silver", "gold", "enterprise"],
    ordered=True
)

# ── Export ────────────────────────────────────────────────────────────────────
df.to_csv(EXPORT_PATH, index=False)
print(f"Exported cleaned data → {EXPORT_PATH}")

# ── Data Quality Report ───────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("DATA QUALITY REPORT")
print("=" * 60)

print(f"\n{'Column':<40} {'Dtype':<15} {'Non-Null':<10} {'Null':<8}")
print("-" * 73)
for col in df.columns:
    non_null = df[col].notna().sum()
    null = df[col].isna().sum()
    print(f"  {col:<38} {str(df[col].dtype):<15} {non_null:<10} {null:<8}")

print(f"\nValidation checks: {len(issues)} issue(s) found")
if issues:
    for i, iss in enumerate(issues, 1):
        print(f"  [{i}] WARNING: {iss}")
else:
    print("  All validation checks passed.")

print(f"\nLegitimate NaN handling:")
print(f"  human_resolution_time_minutes NaN for non-escalated: "
      f"{df.loc[~df['escalated_to_human'], 'human_resolution_time_minutes'].isna().sum()} rows (expected)")
print(f"  human_resolution_time_minutes populated for escalated: "
      f"{df.loc[df['escalated_to_human'], 'human_resolution_time_minutes'].notna().sum()} rows")

print(f"\nDerived column distributions:")
print(f"\n  confidence_band:\n{df['confidence_band'].value_counts().to_string()}")
print(f"\n  resolution_speed:\n{df['resolution_speed'].value_counts().to_string()}")
print(f"\n  cost_tier:\n{df['cost_tier'].value_counts().to_string()}")

print(f"\nFinal dataset shape: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"Export complete.")
