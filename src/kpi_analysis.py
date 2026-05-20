"""
kpi_analysis.py
Calculates all project KPIs and exports Tableau-ready CSVs.
"""

import pandas as pd
import numpy as np
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
CLEANED_PATH = "/Users/yiyaoli/ai-workflow-observability/data/exports/tickets_cleaned.csv"
EXPORT_DIR   = "/Users/yiyaoli/ai-workflow-observability/data/exports/"
os.makedirs(EXPORT_DIR, exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(CLEANED_PATH)

# Restore booleans (CSV drops dtype info)
bool_cols = [
    "ai_correct_response", "routing_correct", "escalation_required",
    "escalated_to_human", "hallucination_flag", "repeat_issue", "sla_breached"
]
for col in bool_cols:
    df[col] = df[col].astype(bool)

print(f"Loaded {len(df)} tickets from {CLEANED_PATH}\n")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: KPI CALCULATIONS
# ═══════════════════════════════════════════════════════════════════════════════

# ── AI / Reliability KPIs ─────────────────────────────────────────────────────
ai_accuracy_rate          = df["ai_correct_response"].mean()
hallucination_rate         = df["hallucination_flag"].mean()
low_confidence_rate        = (df["ai_confidence_score"] < 0.6).mean()
routing_accuracy_rate      = df["routing_correct"].mean()
retry_rate                 = (df["retry_count"] > 0).mean()
avg_confidence_score       = df["ai_confidence_score"].mean()

# ── Workflow KPIs ─────────────────────────────────────────────────────────────
escalation_rate            = df["escalated_to_human"].mean()
avg_total_resolution_time  = df["total_resolution_time_minutes"].mean()
avg_human_resolution_time  = df.loc[df["escalated_to_human"], "human_resolution_time_minutes"].mean()
sla_breach_rate            = df["sla_breached"].mean()
repeat_issue_rate          = df["repeat_issue"].mean()
escalation_required_rate   = df["escalation_required"].mean()

# ── Customer KPIs ─────────────────────────────────────────────────────────────
avg_customer_rating        = df["customer_rating"].mean()
rating_by_category         = df.groupby("issue_category")["customer_rating"].mean().round(3)
rating_escalated           = df.loc[df["escalated_to_human"],  "customer_rating"].mean()
rating_not_escalated       = df.loc[~df["escalated_to_human"], "customer_rating"].mean()

# ── Business KPIs ─────────────────────────────────────────────────────────────
avg_cost_overall           = df["estimated_cost_per_ticket"].mean()
avg_cost_by_category       = df.groupby("issue_category")["estimated_cost_per_ticket"].mean().round(2)
total_cost_escalated       = df.loc[df["escalated_to_human"],  "estimated_cost_per_ticket"].sum()
total_cost_not_escalated   = df.loc[~df["escalated_to_human"], "estimated_cost_per_ticket"].sum()
total_cost_overall         = df["estimated_cost_per_ticket"].sum()
avg_cost_escalated         = df.loc[df["escalated_to_human"],  "estimated_cost_per_ticket"].mean()
avg_cost_not_escalated     = df.loc[~df["escalated_to_human"], "estimated_cost_per_ticket"].mean()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: PRINT KPIs
# ═══════════════════════════════════════════════════════════════════════════════

print("=" * 65)
print("AI / RELIABILITY KPIs")
print("=" * 65)
print(f"  AI Accuracy Rate:           {ai_accuracy_rate*100:.1f}%")
print(f"  Hallucination Rate:         {hallucination_rate*100:.1f}%")
print(f"  Low-Confidence Rate (<0.6): {low_confidence_rate*100:.1f}%")
print(f"  Routing Accuracy Rate:      {routing_accuracy_rate*100:.1f}%")
print(f"  Retry Rate (>0 retries):    {retry_rate*100:.1f}%")
print(f"  Avg AI Confidence Score:    {avg_confidence_score:.3f}")

print("\n" + "=" * 65)
print("WORKFLOW KPIs")
print("=" * 65)
print(f"  Escalation Rate:            {escalation_rate*100:.1f}%")
print(f"  Escalation Required Rate:   {escalation_required_rate*100:.1f}%")
print(f"  Avg Total Resolution Time:  {avg_total_resolution_time:.1f} min")
print(f"  Avg Human Resolution Time:  {avg_human_resolution_time:.1f} min (escalated only)")
print(f"  SLA Breach Rate:            {sla_breach_rate*100:.1f}%")
print(f"  Repeat Issue Rate:          {repeat_issue_rate*100:.1f}%")

print("\n" + "=" * 65)
print("CUSTOMER KPIs")
print("=" * 65)
print(f"  Overall Avg Customer Rating: {avg_customer_rating:.2f} / 5.0")
print(f"  Rating (Escalated):          {rating_escalated:.2f} / 5.0")
print(f"  Rating (Not Escalated):      {rating_not_escalated:.2f} / 5.0")
print(f"\n  Rating by Issue Category:")
for cat, val in rating_by_category.sort_values().items():
    print(f"    {cat:<32} {val:.2f}")

print("\n" + "=" * 65)
print("BUSINESS KPIs")
print("=" * 65)
print(f"  Avg Cost Per Ticket (Overall):     ${avg_cost_overall:.2f}")
print(f"  Avg Cost Per Ticket (Escalated):   ${avg_cost_escalated:.2f}")
print(f"  Avg Cost Per Ticket (AI-Handled):  ${avg_cost_not_escalated:.2f}")
print(f"  Total Cost (Escalated):            ${total_cost_escalated:,.2f}")
print(f"  Total Cost (AI-Handled):           ${total_cost_not_escalated:,.2f}")
print(f"  Total Cost Overall:                ${total_cost_overall:,.2f}")
print(f"\n  Avg Cost by Issue Category:")
for cat, val in avg_cost_by_category.sort_values(ascending=False).items():
    print(f"    {cat:<32} ${val:.2f}")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: TABLEAU-READY CSV EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

# ── kpi_summary.csv ───────────────────────────────────────────────────────────
kpi_summary = pd.DataFrame([{
    "ai_accuracy_rate_pct":          round(ai_accuracy_rate * 100, 2),
    "hallucination_rate_pct":         round(hallucination_rate * 100, 2),
    "low_confidence_rate_pct":        round(low_confidence_rate * 100, 2),
    "routing_accuracy_rate_pct":      round(routing_accuracy_rate * 100, 2),
    "retry_rate_pct":                 round(retry_rate * 100, 2),
    "avg_confidence_score":           round(avg_confidence_score, 4),
    "escalation_rate_pct":            round(escalation_rate * 100, 2),
    "avg_total_resolution_min":       round(avg_total_resolution_time, 2),
    "avg_human_resolution_min":       round(avg_human_resolution_time, 2),
    "sla_breach_rate_pct":            round(sla_breach_rate * 100, 2),
    "repeat_issue_rate_pct":          round(repeat_issue_rate * 100, 2),
    "avg_customer_rating":            round(avg_customer_rating, 3),
    "rating_escalated":               round(rating_escalated, 3),
    "rating_not_escalated":           round(rating_not_escalated, 3),
    "avg_cost_overall_usd":           round(avg_cost_overall, 2),
    "avg_cost_escalated_usd":         round(avg_cost_escalated, 2),
    "avg_cost_not_escalated_usd":     round(avg_cost_not_escalated, 2),
    "total_cost_escalated_usd":       round(total_cost_escalated, 2),
    "total_cost_not_escalated_usd":   round(total_cost_not_escalated, 2),
    "total_cost_overall_usd":         round(total_cost_overall, 2),
    "total_tickets":                  len(df),
}])
kpi_summary.to_csv(os.path.join(EXPORT_DIR, "kpi_summary.csv"), index=False)
print(f"\n  Exported: kpi_summary.csv ({kpi_summary.shape[1]} KPI columns)")

# ── by_category.csv ───────────────────────────────────────────────────────────
by_category = df.groupby("issue_category").agg(
    ticket_count            = ("ticket_id", "count"),
    escalation_rate         = ("escalated_to_human", "mean"),
    hallucination_rate      = ("hallucination_flag", "mean"),
    sla_breach_rate         = ("sla_breached", "mean"),
    avg_rating              = ("customer_rating", "mean"),
    avg_cost                = ("estimated_cost_per_ticket", "mean"),
    avg_resolution_time     = ("total_resolution_time_minutes", "mean"),
    avg_confidence          = ("ai_confidence_score", "mean"),
    ai_accuracy_rate        = ("ai_correct_response", "mean"),
    repeat_issue_rate       = ("repeat_issue", "mean"),
    routing_accuracy_rate   = ("routing_correct", "mean"),
).round(4).reset_index()
by_category.to_csv(os.path.join(EXPORT_DIR, "by_category.csv"), index=False)
print(f"  Exported: by_category.csv ({len(by_category)} categories)")

# ── by_priority.csv ───────────────────────────────────────────────────────────
by_priority = df.groupby("priority_level").agg(
    ticket_count            = ("ticket_id", "count"),
    escalation_rate         = ("escalated_to_human", "mean"),
    hallucination_rate      = ("hallucination_flag", "mean"),
    sla_breach_rate         = ("sla_breached", "mean"),
    avg_rating              = ("customer_rating", "mean"),
    avg_cost                = ("estimated_cost_per_ticket", "mean"),
    avg_resolution_time     = ("total_resolution_time_minutes", "mean"),
    avg_confidence          = ("ai_confidence_score", "mean"),
    ai_accuracy_rate        = ("ai_correct_response", "mean"),
).round(4).reset_index()
# Sort by priority order
priority_order = ["low", "medium", "high", "critical"]
by_priority["priority_level"] = pd.Categorical(
    by_priority["priority_level"], categories=priority_order, ordered=True
)
by_priority = by_priority.sort_values("priority_level").reset_index(drop=True)
by_priority.to_csv(os.path.join(EXPORT_DIR, "by_priority.csv"), index=False)
print(f"  Exported: by_priority.csv ({len(by_priority)} priority levels)")

# ── by_confidence_band.csv ────────────────────────────────────────────────────
by_confidence_band = df.groupby("confidence_band").agg(
    ticket_count            = ("ticket_id", "count"),
    escalation_rate         = ("escalated_to_human", "mean"),
    hallucination_rate      = ("hallucination_flag", "mean"),
    sla_breach_rate         = ("sla_breached", "mean"),
    avg_rating              = ("customer_rating", "mean"),
    avg_cost                = ("estimated_cost_per_ticket", "mean"),
    avg_resolution_time     = ("total_resolution_time_minutes", "mean"),
    avg_confidence          = ("ai_confidence_score", "mean"),
    ai_accuracy_rate        = ("ai_correct_response", "mean"),
    retry_rate              = ("retry_count", lambda x: (x > 0).mean()),
).round(4).reset_index()
band_order = ["low", "medium", "high"]
by_confidence_band["confidence_band"] = pd.Categorical(
    by_confidence_band["confidence_band"], categories=band_order, ordered=True
)
by_confidence_band = by_confidence_band.sort_values("confidence_band").reset_index(drop=True)
by_confidence_band.to_csv(os.path.join(EXPORT_DIR, "by_confidence_band.csv"), index=False)
print(f"  Exported: by_confidence_band.csv ({len(by_confidence_band)} bands)")

# ── escalation_analysis.csv ───────────────────────────────────────────────────
escalation_analysis = df.groupby("escalated_to_human").agg(
    ticket_count            = ("ticket_id", "count"),
    hallucination_rate      = ("hallucination_flag", "mean"),
    sla_breach_rate         = ("sla_breached", "mean"),
    avg_rating              = ("customer_rating", "mean"),
    avg_cost                = ("estimated_cost_per_ticket", "mean"),
    avg_resolution_time     = ("total_resolution_time_minutes", "mean"),
    avg_confidence          = ("ai_confidence_score", "mean"),
    ai_accuracy_rate        = ("ai_correct_response", "mean"),
    repeat_issue_rate       = ("repeat_issue", "mean"),
    total_cost              = ("estimated_cost_per_ticket", "sum"),
).round(4).reset_index()
escalation_analysis["escalated_to_human"] = escalation_analysis["escalated_to_human"].map(
    {True: "Escalated", False: "AI-Handled"}
)
escalation_analysis.rename(columns={"escalated_to_human": "escalation_status"}, inplace=True)
escalation_analysis.to_csv(os.path.join(EXPORT_DIR, "escalation_analysis.csv"), index=False)
print(f"  Exported: escalation_analysis.csv")

print(f"\nAll exports saved to: {EXPORT_DIR}")
print("\nKPI analysis complete.")
