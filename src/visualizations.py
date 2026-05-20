"""
visualizations.py
Generates 10 publication-quality visualizations for the
AI Agent Workflow Observability & Performance Optimization project.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import os
import warnings
warnings.filterwarnings("ignore")

# ── Try preferred style, fall back gracefully ─────────────────────────────────
try:
    plt.style.use("seaborn-v0_8-whitegrid")
except OSError:
    try:
        plt.style.use("seaborn-whitegrid")
    except OSError:
        plt.style.use("ggplot")

# ── Paths ─────────────────────────────────────────────────────────────────────
CLEANED_PATH = "/Users/yiyaoli/ai-workflow-observability/data/exports/tickets_cleaned.csv"
EXPORT_DIR   = "/Users/yiyaoli/ai-workflow-observability/data/exports/"
FIGURES_DIR  = "/Users/yiyaoli/ai-workflow-observability/outputs/figures/"
os.makedirs(FIGURES_DIR, exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(CLEANED_PATH)
bool_cols = [
    "ai_correct_response", "routing_correct", "escalation_required",
    "escalated_to_human", "hallucination_flag", "repeat_issue", "sla_breached"
]
for col in bool_cols:
    df[col] = df[col].astype(bool)

# ── Color palette ─────────────────────────────────────────────────────────────
BLUE      = "#2E6DA4"
ORANGE    = "#E07B39"
RED       = "#C0392B"
GREEN     = "#27AE60"
GRAY      = "#7F8C8D"
LIGHT_BLUE = "#AED6F1"
DARK_BLUE  = "#1A3A5C"
YELLOW    = "#F1C40F"

DPI = 150

def save(fig, name):
    path = os.path.join(FIGURES_DIR, name)
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {name}")


# ═══════════════════════════════════════════════════════════════════════════════
# 1. KPI SUMMARY TABLE
# ═══════════════════════════════════════════════════════════════════════════════
def plot_kpi_table():
    kpi_data = [
        ("AI Accuracy Rate",           f"{df['ai_correct_response'].mean()*100:.1f}%",   "Good",     GREEN),
        ("Hallucination Rate",         f"{df['hallucination_flag'].mean()*100:.1f}%",    "Warning",  ORANGE),
        ("Low-Confidence Rate",        f"{(df['ai_confidence_score']<0.6).mean()*100:.1f}%", "Warning", ORANGE),
        ("Routing Accuracy Rate",      f"{df['routing_correct'].mean()*100:.1f}%",       "Good",     GREEN),
        ("Escalation Rate",            f"{df['escalated_to_human'].mean()*100:.1f}%",    "Warning",  ORANGE),
        ("SLA Breach Rate",            f"{df['sla_breached'].mean()*100:.1f}%",          "Critical", RED),
        ("Repeat Issue Rate",          f"{df['repeat_issue'].mean()*100:.1f}%",          "Warning",  ORANGE),
        ("Avg Customer Rating",        f"{df['customer_rating'].mean():.2f} / 5.0",      "Good",     GREEN),
        ("Avg Cost Per Ticket",        f"${df['estimated_cost_per_ticket'].mean():.2f}", "Warning",  ORANGE),
        ("Avg Resolution Time",        f"{df['total_resolution_time_minutes'].mean():.1f} min", "Warning", ORANGE),
    ]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.axis("off")

    col_labels = ["KPI", "Value", "Status"]
    table_data = [(row[0], row[1], row[2]) for row in kpi_data]

    table = ax.table(
        cellText=table_data,
        colLabels=col_labels,
        loc="center",
        cellLoc="center"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.0, 2.0)

    # Header styling
    for j in range(3):
        table[0, j].set_facecolor(DARK_BLUE)
        table[0, j].set_text_props(color="white", fontweight="bold")

    # Row styling
    for i, row in enumerate(kpi_data):
        status_color = row[3]
        for j in range(3):
            cell = table[i + 1, j]
            if j == 2:
                cell.set_facecolor(status_color)
                cell.set_text_props(color="white", fontweight="bold")
            else:
                cell.set_facecolor("#F4F6F7" if i % 2 == 0 else "white")

    ax.set_title("AI Workflow — Top 10 KPI Summary", fontsize=14,
                 fontweight="bold", pad=12, color=DARK_BLUE)
    save(fig, "kpi_summary_table.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. TICKET VOLUME BY CATEGORY
# ═══════════════════════════════════════════════════════════════════════════════
def plot_ticket_volume():
    counts = df["issue_category"].value_counts().sort_values()
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(counts.index, counts.values, color=BLUE, edgecolor="white", height=0.6)
    for bar, val in zip(bars, counts.values):
        ax.text(val + 1, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=10, color=DARK_BLUE, fontweight="bold")
    ax.set_xlabel("Number of Tickets", fontsize=11)
    ax.set_title("Ticket Volume by Issue Category", fontsize=13, fontweight="bold",
                 color=DARK_BLUE, pad=10)
    ax.set_xlim(0, counts.max() * 1.12)
    ax.tick_params(axis="y", labelsize=10)
    plt.tight_layout()
    save(fig, "ticket_volume_by_category.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. ESCALATION RATE BY CATEGORY
# ═══════════════════════════════════════════════════════════════════════════════
def plot_escalation_rate_by_category():
    esc_rate = (df.groupby("issue_category")["escalated_to_human"].mean() * 100).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [RED if v >= 50 else ORANGE if v >= 35 else BLUE for v in esc_rate.values]
    bars = ax.bar(esc_rate.index, esc_rate.values, color=colors, edgecolor="white", width=0.6)
    ax.axhline(y=50, color=RED, linestyle="--", linewidth=1.5, alpha=0.8, label="50% Threshold")
    for bar, val in zip(bars, esc_rate.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_ylabel("Escalation Rate (%)", fontsize=11)
    ax.set_title("Escalation Rate by Issue Category", fontsize=13, fontweight="bold",
                 color=DARK_BLUE, pad=10)
    ax.set_ylim(0, max(esc_rate.values) * 1.18)
    ax.tick_params(axis="x", rotation=20, labelsize=9)
    ax.legend(fontsize=10)
    plt.tight_layout()
    save(fig, "escalation_rate_by_category.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CONFIDENCE SCORE DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════════
def plot_confidence_distribution():
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(df["ai_confidence_score"], bins=30, color=BLUE, edgecolor="white",
            alpha=0.85, label="Confidence Score")
    ax.axvline(x=0.6, color=RED, linestyle="--", linewidth=2,
               label="Low Threshold (0.6)")
    ax.axvline(x=0.8, color=GREEN, linestyle="--", linewidth=2,
               label="High Threshold (0.8)")
    low_pct  = (df["ai_confidence_score"] < 0.6).mean() * 100
    mid_pct  = ((df["ai_confidence_score"] >= 0.6) & (df["ai_confidence_score"] < 0.8)).mean() * 100
    high_pct = (df["ai_confidence_score"] >= 0.8).mean() * 100
    ax.text(0.30, ax.get_ylim()[1] * 0.88, f"Low: {low_pct:.1f}%",
            color=RED, fontsize=10, fontweight="bold", ha="center")
    ax.text(0.70, ax.get_ylim()[1] * 0.88, f"Medium: {mid_pct:.1f}%",
            color=ORANGE, fontsize=10, fontweight="bold", ha="center")
    ax.text(0.91, ax.get_ylim()[1] * 0.88, f"High: {high_pct:.1f}%",
            color=GREEN, fontsize=10, fontweight="bold", ha="center")
    ax.set_xlabel("AI Confidence Score", fontsize=11)
    ax.set_ylabel("Ticket Count", fontsize=11)
    ax.set_title("Distribution of AI Confidence Scores", fontsize=13,
                 fontweight="bold", color=DARK_BLUE, pad=10)
    ax.legend(fontsize=10)
    plt.tight_layout()
    save(fig, "confidence_distribution.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. CUSTOMER RATING BY CATEGORY
# ═══════════════════════════════════════════════════════════════════════════════
def plot_customer_rating_by_category():
    rating = df.groupby("issue_category")["customer_rating"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [GREEN if v >= 4.0 else ORANGE if v >= 3.5 else RED for v in rating.values]
    bars = ax.barh(rating.index, rating.values, color=colors, edgecolor="white", height=0.6)
    ax.axvline(x=3.5, color=GRAY, linestyle="--", linewidth=1.5, alpha=0.7, label="3.5 Baseline")
    for bar, val in zip(bars, rating.values):
        ax.text(val + 0.02, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}", va="center", fontsize=10, fontweight="bold")
    ax.set_xlabel("Avg Customer Rating (1–5)", fontsize=11)
    ax.set_title("Average Customer Rating by Issue Category", fontsize=13,
                 fontweight="bold", color=DARK_BLUE, pad=10)
    ax.set_xlim(0, 5.5)
    ax.legend(fontsize=10)
    plt.tight_layout()
    save(fig, "customer_rating_by_category.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. SLA BREACH RATE BY PRIORITY
# ═══════════════════════════════════════════════════════════════════════════════
def plot_sla_breach_by_priority():
    priority_order = ["low", "medium", "high", "critical"]
    breach = df.groupby("priority_level")["sla_breached"].mean() * 100
    breach = breach.reindex(priority_order)

    fig, ax = plt.subplots(figsize=(8, 5))
    bar_colors = [GREEN, ORANGE, ORANGE, RED]
    bars = ax.bar(breach.index, breach.values, color=bar_colors, edgecolor="white", width=0.5)
    for bar, val in zip(bars, breach.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_ylabel("SLA Breach Rate (%)", fontsize=11)
    ax.set_xlabel("Priority Level", fontsize=11)
    ax.set_title("SLA Breach Rate by Priority Level", fontsize=13, fontweight="bold",
                 color=DARK_BLUE, pad=10)
    ax.set_ylim(0, max(breach.values) * 1.18)

    legend_patches = [
        mpatches.Patch(color=GREEN, label="On Track"),
        mpatches.Patch(color=ORANGE, label="Warning"),
        mpatches.Patch(color=RED, label="Critical"),
    ]
    ax.legend(handles=legend_patches, fontsize=10)
    plt.tight_layout()
    save(fig, "sla_breach_by_priority.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 7. COST BY ESCALATION STATUS
# ═══════════════════════════════════════════════════════════════════════════════
def plot_cost_by_escalation():
    avg_cost_esc  = df.loc[df["escalated_to_human"],  "estimated_cost_per_ticket"].mean()
    avg_cost_ai   = df.loc[~df["escalated_to_human"], "estimated_cost_per_ticket"].mean()
    labels = ["AI-Handled", "Escalated to Human"]
    values = [avg_cost_ai, avg_cost_esc]
    colors = [GREEN, RED]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", width=0.45)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"${val:.2f}", ha="center", va="bottom", fontsize=13, fontweight="bold")
    ax.set_ylabel("Avg Cost Per Ticket (USD)", fontsize=11)
    ax.set_title("Average Ticket Cost: AI-Handled vs Escalated", fontsize=13,
                 fontweight="bold", color=DARK_BLUE, pad=10)
    ax.set_ylim(0, max(values) * 1.2)
    multiplier = avg_cost_esc / avg_cost_ai
    ax.text(0.5, 0.88, f"{multiplier:.1f}x cost multiplier for escalation",
            transform=ax.transAxes, ha="center", fontsize=11, color=RED,
            fontweight="bold", style="italic")
    plt.tight_layout()
    save(fig, "cost_by_escalation_status.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 8. CONFIDENCE VS RATING SCATTER
# ═══════════════════════════════════════════════════════════════════════════════
def plot_confidence_vs_rating():
    fig, ax = plt.subplots(figsize=(9, 6))
    escalated     = df[df["escalated_to_human"] == True]
    not_escalated = df[df["escalated_to_human"] == False]

    ax.scatter(not_escalated["ai_confidence_score"], not_escalated["customer_rating"],
               color=BLUE, alpha=0.45, s=28, label="AI-Handled", edgecolors="none")
    ax.scatter(escalated["ai_confidence_score"], escalated["customer_rating"],
               color=ORANGE, alpha=0.55, s=28, label="Escalated", edgecolors="none")

    # Trend lines
    for subset, color in [(not_escalated, BLUE), (escalated, ORANGE)]:
        z = np.polyfit(subset["ai_confidence_score"], subset["customer_rating"], 1)
        p = np.poly1d(z)
        x_line = np.linspace(subset["ai_confidence_score"].min(),
                             subset["ai_confidence_score"].max(), 100)
        ax.plot(x_line, p(x_line), color=color, linewidth=2, alpha=0.9)

    ax.axvline(x=0.6, color=RED, linestyle="--", linewidth=1.4, alpha=0.7,
               label="Low Conf. Threshold")
    ax.axvline(x=0.8, color=GREEN, linestyle="--", linewidth=1.4, alpha=0.7,
               label="High Conf. Threshold")
    ax.set_xlabel("AI Confidence Score", fontsize=11)
    ax.set_ylabel("Customer Rating", fontsize=11)
    ax.set_title("AI Confidence Score vs Customer Rating\n(by Escalation Status)",
                 fontsize=13, fontweight="bold", color=DARK_BLUE)
    ax.legend(fontsize=10)
    plt.tight_layout()
    save(fig, "confidence_vs_rating_scatter.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 9. WORKFLOW FRICTION HEATMAP
# ═══════════════════════════════════════════════════════════════════════════════
def plot_workflow_friction_heatmap():
    try:
        import seaborn as sns
        use_seaborn = True
    except ImportError:
        use_seaborn = False

    agg = df.groupby("issue_category").agg(
        escalation_rate   = ("escalated_to_human", "mean"),
        hallucination_rate = ("hallucination_flag", "mean"),
        sla_breach_rate   = ("sla_breached", "mean"),
        avg_rating        = ("customer_rating", "mean"),
        avg_cost          = ("estimated_cost_per_ticket", "mean"),
    ).round(4)

    # Normalize each column to 0–1 for comparability (higher = more friction, invert rating)
    heat_data = agg.copy()
    for col in ["escalation_rate", "hallucination_rate", "sla_breach_rate", "avg_cost"]:
        mn, mx = heat_data[col].min(), heat_data[col].max()
        heat_data[col] = (heat_data[col] - mn) / (mx - mn + 1e-9)
    # Invert rating (lower rating = higher friction)
    mn, mx = heat_data["avg_rating"].min(), heat_data["avg_rating"].max()
    heat_data["avg_rating"] = 1 - (heat_data["avg_rating"] - mn) / (mx - mn + 1e-9)

    heat_data.columns = ["Escalation\nRate", "Hallucination\nRate",
                          "SLA Breach\nRate", "Rating\n(inverted)", "Avg Cost\n(normalized)"]

    fig, ax = plt.subplots(figsize=(10, 6))
    if use_seaborn:
        sns.heatmap(
            heat_data, ax=ax, cmap="YlOrRd", annot=True, fmt=".2f",
            linewidths=0.5, linecolor="white",
            cbar_kws={"label": "Normalized Friction Score (0=Low, 1=High)"}
        )
    else:
        im = ax.imshow(heat_data.values, cmap="YlOrRd", aspect="auto", vmin=0, vmax=1)
        plt.colorbar(im, ax=ax, label="Normalized Friction Score")
        ax.set_xticks(range(len(heat_data.columns)))
        ax.set_xticklabels(heat_data.columns, fontsize=9)
        ax.set_yticks(range(len(heat_data.index)))
        ax.set_yticklabels(heat_data.index, fontsize=9)
        for i in range(len(heat_data.index)):
            for j in range(len(heat_data.columns)):
                ax.text(j, i, f"{heat_data.values[i, j]:.2f}",
                        ha="center", va="center", fontsize=8, fontweight="bold")

    ax.set_title("Workflow Friction Heatmap by Issue Category\n(Normalized — Higher = More Friction)",
                 fontsize=12, fontweight="bold", color=DARK_BLUE, pad=12)
    ax.set_ylabel("Issue Category", fontsize=11)
    plt.tight_layout()
    save(fig, "workflow_friction_heatmap.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. ESCALATION FUNNEL
# ═══════════════════════════════════════════════════════════════════════════════
def plot_escalation_funnel():
    total         = len(df)
    ai_handled    = int((~df["escalated_to_human"]).sum())
    esc_required  = int(df["escalation_required"].sum())
    esc_to_human  = int(df["escalated_to_human"].sum())
    sla_breached  = int(df["sla_breached"].sum())

    stages = [
        ("Total Tickets",           total,        BLUE),
        ("AI Handled",              ai_handled,   GREEN),
        ("Escalation Required",     esc_required, ORANGE),
        ("Escalated to Human",      esc_to_human, ORANGE),
        ("SLA Breached",            sla_breached, RED),
    ]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    y_pos = range(len(stages))
    bar_heights = 0.55

    max_val = total
    for i, (label, val, color) in enumerate(stages):
        ax.barh(i, val, height=bar_heights, color=color, alpha=0.85, edgecolor="white")
        pct = f"({val/total*100:.1f}%)" if i > 0 else ""
        ax.text(val + max_val * 0.01, i, f"  {val:,} {pct}",
                va="center", fontsize=11, fontweight="bold", color=DARK_BLUE)

    ax.set_yticks(list(y_pos))
    ax.set_yticklabels([s[0] for s in stages], fontsize=11, fontweight="bold")
    ax.set_xlabel("Number of Tickets", fontsize=11)
    ax.set_title("Escalation Funnel — AI Workflow Support Operations",
                 fontsize=13, fontweight="bold", color=DARK_BLUE, pad=12)
    ax.set_xlim(0, max_val * 1.22)
    ax.invert_yaxis()
    plt.tight_layout()
    save(fig, "escalation_funnel.png")


# ═══════════════════════════════════════════════════════════════════════════════
# RUN ALL
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating visualizations...\n")
    plot_kpi_table()
    plot_ticket_volume()
    plot_escalation_rate_by_category()
    plot_confidence_distribution()
    plot_customer_rating_by_category()
    plot_sla_breach_by_priority()
    plot_cost_by_escalation()
    plot_confidence_vs_rating()
    plot_workflow_friction_heatmap()
    plot_escalation_funnel()
    print(f"\nAll 10 figures saved to: {FIGURES_DIR}")
