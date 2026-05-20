"""
generate_data.py
Generates 400 synthetic support tickets with realistic correlations for the
AI Agent Workflow Observability & Performance Optimization project.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

# ── Reproducibility ──────────────────────────────────────────────────────────
np.random.seed(42)

# ── Constants ────────────────────────────────────────────────────────────────
N = 400
BASE_DATE = datetime(2026, 5, 20)
START_DATE = BASE_DATE - timedelta(days=90)

CUSTOMER_TIERS = ["bronze", "silver", "gold", "enterprise"]
ISSUE_CATEGORIES = [
    "billing", "refund", "shipping", "login",
    "account_access", "technical_support", "subscription_cancellation"
]
PRIORITY_LEVELS = ["low", "medium", "high", "critical"]

# SLA targets in minutes
SLA_TARGETS = {"low": 1440, "medium": 240, "high": 60, "critical": 60}

# ── Ticket IDs & User IDs ────────────────────────────────────────────────────
ticket_ids = [f"TKT-{str(i).zfill(5)}" for i in range(1, N + 1)]
user_ids = [f"USR-{np.random.randint(1000, 9999)}" for _ in range(N)]

# ── Timestamps ───────────────────────────────────────────────────────────────
seconds_in_90_days = 90 * 24 * 3600
random_offsets = np.random.randint(0, seconds_in_90_days, size=N)
timestamps = [START_DATE + timedelta(seconds=int(s)) for s in random_offsets]

# ── Customer Tier (enterprise/gold weighted higher) ──────────────────────────
tier_weights = [0.35, 0.30, 0.22, 0.13]  # bronze, silver, gold, enterprise
customer_tier = np.random.choice(CUSTOMER_TIERS, size=N, p=tier_weights)

# ── Issue Category ───────────────────────────────────────────────────────────
category_weights = [0.18, 0.13, 0.12, 0.16, 0.14, 0.17, 0.10]
issue_category = np.random.choice(ISSUE_CATEGORIES, size=N, p=category_weights)

# ── Priority Level (enterprise/gold → higher priority) ───────────────────────
priority_level = []
for tier in customer_tier:
    if tier == "enterprise":
        p = [0.05, 0.25, 0.45, 0.25]
    elif tier == "gold":
        p = [0.10, 0.30, 0.40, 0.20]
    elif tier == "silver":
        p = [0.25, 0.40, 0.25, 0.10]
    else:  # bronze
        p = [0.40, 0.35, 0.18, 0.07]
    priority_level.append(np.random.choice(PRIORITY_LEVELS, p=p))
priority_level = np.array(priority_level)

# ── AI Confidence Score (category-dependent) ─────────────────────────────────
CONFIDENCE_PARAMS = {
    "technical_support":           (0.55, 0.15),
    "billing":                     (0.65, 0.14),
    "account_access":              (0.65, 0.13),
    "login":                       (0.75, 0.12),
    "shipping":                    (0.75, 0.11),
    "refund":                      (0.70, 0.13),
    "subscription_cancellation":   (0.70, 0.14),
}

ai_confidence_score = np.array([
    np.clip(np.random.normal(*CONFIDENCE_PARAMS[cat]), 0.01, 0.99)
    for cat in issue_category
])

# ── AI Correct Response ───────────────────────────────────────────────────────
# Probability of correct response increases with confidence
ai_correct_prob = np.clip(ai_confidence_score * 1.1 - 0.05, 0.10, 0.97)
ai_correct_response = np.random.random(N) < ai_correct_prob

# ── Routing Decision & Correctness ───────────────────────────────────────────
# Low confidence → higher escalation probability
escalation_prob = np.where(
    ai_confidence_score < 0.6, 0.70,
    np.where(ai_confidence_score >= 0.8, 0.15, 0.35)
)
escalated_flag = np.random.random(N) < escalation_prob
routing_decision = np.where(escalated_flag, "escalated_to_human", "ai_handled")

# Routing is correct ~85% of the time
routing_correct = np.random.random(N) < 0.85

# ── Hallucination ─────────────────────────────────────────────────────────────
hallucination_prob = np.where(ai_confidence_score < 0.6, 0.12, 0.03)
hallucination_flag = np.random.random(N) < hallucination_prob

# ── Retry Count ───────────────────────────────────────────────────────────────
retry_count = np.array([
    np.random.choice([0, 1, 2, 3],
                     p=[0.40, 0.30, 0.20, 0.10] if c < 0.6 else [0.65, 0.22, 0.10, 0.03])
    for c in ai_confidence_score
])

# ── Failure Type ──────────────────────────────────────────────────────────────
def assign_failure_type(conf, halluc, routed_correct, retries):
    if halluc:
        return "hallucination"
    if not routed_correct:
        return "routing_failure"
    if retries >= 2:
        return "timeout" if np.random.random() < 0.5 else "low_confidence"
    if conf < 0.6 and np.random.random() < 0.25:
        return "low_confidence"
    return "none"

failure_type = np.array([
    assign_failure_type(ai_confidence_score[i], hallucination_flag[i],
                        routing_correct[i], retry_count[i])
    for i in range(N)
])

# ── Response Time (seconds) ───────────────────────────────────────────────────
# Escalated tickets take longer
base_response = np.where(
    escalated_flag,
    np.random.normal(45, 15, N),   # 45s mean for escalated (hold time)
    np.random.normal(8, 4, N)      # 8s mean for AI-handled
)
response_time_seconds = np.clip(base_response, 2, 180).astype(int)

# ── Escalation Required & Escalated to Human ─────────────────────────────────
escalation_required = escalated_flag.copy()
# Sometimes escalation is required but not done (edge case ~5%)
escalated_to_human = np.where(
    escalation_required,
    np.random.random(N) < 0.95,
    False
)

# ── Human Resolution Time ─────────────────────────────────────────────────────
human_resolution_time_minutes = np.where(
    escalated_to_human,
    np.clip(np.random.lognormal(mean=3.8, sigma=0.7, size=N), 10, 480),
    np.nan
)

# ── Total Resolution Time ─────────────────────────────────────────────────────
ai_resolution_minutes = np.clip(
    np.random.lognormal(mean=2.5, sigma=0.6, size=N), 2, 90
)
total_resolution_time_minutes = np.where(
    escalated_to_human,
    (response_time_seconds / 60) + human_resolution_time_minutes,
    ai_resolution_minutes
)

# ── SLA Breach ────────────────────────────────────────────────────────────────
sla_target_minutes = np.array([SLA_TARGETS[p] for p in priority_level])
sla_breached = total_resolution_time_minutes > sla_target_minutes

# ── Repeat Issue ──────────────────────────────────────────────────────────────
repeat_base = 0.18
repeat_prob = np.where(hallucination_flag, repeat_base + 0.10, repeat_base)
repeat_issue = np.random.random(N) < repeat_prob

# ── Customer Rating ───────────────────────────────────────────────────────────
rating_base = np.full(N, 3.8)
rating_base = rating_base + np.where(ai_correct_response, 0.5, 0.0)
rating_base = rating_base - np.where(hallucination_flag, 0.7, 0.0)
rating_base = rating_base - np.where(sla_breached, 0.4, 0.0)
rating_base = rating_base - np.where(repeat_issue, 0.3, 0.0)
# Add noise
rating_base = rating_base + np.random.normal(0, 0.25, N)
customer_rating = np.clip(rating_base, 1.0, 5.0).round(1)

# ── Estimated Cost Per Ticket ─────────────────────────────────────────────────
estimated_cost_per_ticket = np.where(
    escalated_to_human,
    np.random.uniform(18, 35, N),
    np.random.uniform(5, 12, N)
)
estimated_cost_per_ticket = estimated_cost_per_ticket.round(2)

# ── Assemble DataFrame ────────────────────────────────────────────────────────
df = pd.DataFrame({
    "ticket_id":                    ticket_ids,
    "user_id":                      user_ids,
    "timestamp":                    timestamps,
    "customer_tier":                customer_tier,
    "issue_category":               issue_category,
    "priority_level":               priority_level,
    "ai_confidence_score":          ai_confidence_score.round(4),
    "ai_correct_response":          ai_correct_response,
    "routing_decision":             routing_decision,
    "routing_correct":              routing_correct,
    "response_time_seconds":        response_time_seconds,
    "escalation_required":          escalation_required,
    "escalated_to_human":           escalated_to_human,
    "human_resolution_time_minutes": human_resolution_time_minutes.round(2),
    "total_resolution_time_minutes": total_resolution_time_minutes.round(2),
    "hallucination_flag":           hallucination_flag,
    "retry_count":                  retry_count,
    "failure_type":                 failure_type,
    "customer_rating":              customer_rating,
    "repeat_issue":                 repeat_issue,
    "sla_breached":                 sla_breached,
    "estimated_cost_per_ticket":    estimated_cost_per_ticket,
})

# ── Save ──────────────────────────────────────────────────────────────────────
output_path = "/Users/yiyaoli/ai-workflow-observability/data/raw/support_tickets.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False)
print(f"Saved {len(df)} tickets to {output_path}\n")

# ── Summary Stats ─────────────────────────────────────────────────────────────
print("=" * 60)
print("DATASET SUMMARY")
print("=" * 60)
print(f"Total tickets:          {N}")
print(f"Date range:             {min(timestamps).strftime('%Y-%m-%d')} to {max(timestamps).strftime('%Y-%m-%d')}")
print(f"\nCustomer tier dist:\n{df['customer_tier'].value_counts().to_string()}")
print(f"\nIssue category dist:\n{df['issue_category'].value_counts().to_string()}")
print(f"\nPriority dist:\n{df['priority_level'].value_counts().to_string()}")
print(f"\nAI confidence score:    mean={df['ai_confidence_score'].mean():.3f}, "
      f"std={df['ai_confidence_score'].std():.3f}")
print(f"AI correct response:    {df['ai_correct_response'].mean()*100:.1f}%")
print(f"Escalation rate:        {df['escalated_to_human'].mean()*100:.1f}%")
print(f"Hallucination rate:     {df['hallucination_flag'].mean()*100:.1f}%")
print(f"SLA breach rate:        {df['sla_breached'].mean()*100:.1f}%")
print(f"Repeat issue rate:      {df['repeat_issue'].mean()*100:.1f}%")
print(f"Avg customer rating:    {df['customer_rating'].mean():.2f}")
print(f"Avg cost per ticket:    ${df['estimated_cost_per_ticket'].mean():.2f}")
print(f"Total estimated cost:   ${df['estimated_cost_per_ticket'].sum():.2f}")
print(f"\nFailure type dist:\n{df['failure_type'].value_counts().to_string()}")
