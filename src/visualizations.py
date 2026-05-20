"""
visualizations.py
Generates 10 operational dashboard charts for the
AI Agent Workflow Observability & Performance Optimization project.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import warnings
warnings.filterwarnings("ignore")

# ── Style ─────────────────────────────────────────────────────────────────────
for style in ("seaborn-v0_8-whitegrid", "seaborn-whitegrid", "ggplot"):
    try:
        plt.style.use(style)
        break
    except OSError:
        continue

plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "axes.titlecolor":   "#1A3A5C",
    "axes.labelsize":    11,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "xtick.labelsize":   10,
    "ytick.labelsize":   10,
    "legend.fontsize":   10,
    "figure.dpi":        150,
})

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE        = "/Users/yiyaoli/ai-workflow-observability"
CLEANED     = f"{BASE}/data/exports/tickets_cleaned.csv"
FIGURES_DIR = f"{BASE}/outputs/figures/"
os.makedirs(FIGURES_DIR, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────────
df = pd.read_csv(CLEANED)
BOOL_COLS = [
    "ai_correct_response", "routing_correct", "escalation_required",
    "escalated_to_human", "hallucination_flag", "repeat_issue", "sla_breached",
]
for col in BOOL_COLS:
    df[col] = df[col].astype(bool)

# ── Palette ───────────────────────────────────────────────────────────────────
BLUE       = "#2E6DA4"
ORANGE     = "#E07B39"
RED        = "#C0392B"
GREEN      = "#27AE60"
GRAY       = "#95A5A6"
DARK_BLUE  = "#1A3A5C"
LIGHT_GRAY = "#F4F6F7"

DPI = 150


def _save(fig, name):
    fig.savefig(os.path.join(FIGURES_DIR, name), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {name}")


def _footnote(ax, text="Source: Synthetic dataset · 400 tickets · 90-day window"):
    ax.figure.text(0.99, 0.01, text, ha="right", va="bottom",
                   fontsize=7.5, color=GRAY, style="italic")


# ═══════════════════════════════════════════════════════════════════════════════
# 1  KPI SUMMARY TABLE
# ═══════════════════════════════════════════════════════════════════════════════
def plot_kpi_table():
    rows = [
        ("AI Accuracy Rate",           f"{df['ai_correct_response'].mean()*100:.1f}%",          "Good",     GREEN),
        ("Hallucination Rate",         f"{df['hallucination_flag'].mean()*100:.1f}%",            "Monitor",  ORANGE),
        ("Low-Confidence Rate (< 0.6)",f"{(df['ai_confidence_score']<0.6).mean()*100:.1f}%",    "Monitor",  ORANGE),
        ("Routing Accuracy Rate",      f"{df['routing_correct'].mean()*100:.1f}%",               "Good",     GREEN),
        ("Escalation Rate",            f"{df['escalated_to_human'].mean()*100:.1f}%",            "Monitor",  ORANGE),
        ("SLA Breach Rate",            f"{df['sla_breached'].mean()*100:.1f}%",                  "Critical", RED),
        ("Repeat Issue Rate",          f"{df['repeat_issue'].mean()*100:.1f}%",                  "Monitor",  ORANGE),
        ("Avg Customer Rating",        f"{df['customer_rating'].mean():.2f} / 5.0",              "Good",     GREEN),
        ("Avg Cost Per Ticket",        f"${df['estimated_cost_per_ticket'].mean():.2f}",         "Monitor",  ORANGE),
        ("Avg Total Resolution Time",  f"{df['total_resolution_time_minutes'].mean():.1f} min",  "Monitor",  ORANGE),
    ]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.axis("off")

    tbl = ax.table(
        cellText=[(r[0], r[1], r[2]) for r in rows],
        colLabels=["KPI", "Value", "Status"],
        loc="center",
        cellLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)
    tbl.scale(1.0, 2.1)

    for j in range(3):
        tbl[0, j].set_facecolor(DARK_BLUE)
        tbl[0, j].set_text_props(color="white", fontweight="bold", fontsize=11.5)

    for i, (_, _, _, color) in enumerate(rows):
        row_bg = LIGHT_GRAY if i % 2 == 0 else "white"
        for j in range(3):
            cell = tbl[i + 1, j]
            if j == 2:
                cell.set_facecolor(color)
                cell.set_text_props(color="white", fontweight="bold")
            else:
                cell.set_facecolor(row_bg)
                cell.set_text_props(color=DARK_BLUE)

    ax.set_title("AI Workflow — Operational KPI Summary", pad=16)
    _footnote(ax)
    _save(fig, "kpi_summary_table.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 2  TICKET VOLUME BY CATEGORY
# ═══════════════════════════════════════════════════════════════════════════════
def plot_ticket_volume():
    counts = df["issue_category"].value_counts().sort_values()
    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.barh(counts.index, counts.values, color=BLUE, edgecolor="white",
                   height=0.62)
    for bar, val in zip(bars, counts.values):
        ax.text(val + 0.8, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=10.5, color=DARK_BLUE, fontweight="bold")

    ax.set_xlabel("Number of Tickets")
    ax.set_title("Ticket Volume by Issue Category")
    ax.set_xlim(0, counts.max() * 1.14)
    ax.tick_params(axis="y", labelsize=10.5)
    _footnote(ax)
    plt.tight_layout()
    _save(fig, "ticket_volume_by_category.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 3  ESCALATION RATE BY CATEGORY
# ═══════════════════════════════════════════════════════════════════════════════
def plot_escalation_rate_by_category():
    esc = (df.groupby("issue_category")["escalated_to_human"].mean() * 100).sort_values(ascending=False)
    colors = [RED if v >= 50 else ORANGE if v >= 35 else BLUE for v in esc.values]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(esc.index, esc.values, color=colors, edgecolor="white", width=0.6)
    ax.axhline(y=50, color=RED, linestyle="--", linewidth=1.5, alpha=0.75, label="50% threshold")

    for bar, val in zip(bars, esc.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=9.5, fontweight="bold",
                color=DARK_BLUE)

    ax.set_ylabel("Escalation Rate (%)")
    ax.set_title("Escalation Rate by Issue Category")
    ax.set_ylim(0, esc.max() * 1.2)
    ax.tick_params(axis="x", rotation=18, labelsize=9.5)
    ax.legend()
    _footnote(ax)
    plt.tight_layout()
    _save(fig, "escalation_rate_by_category.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 4  CONFIDENCE SCORE DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════════
def plot_confidence_distribution():
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(df["ai_confidence_score"], bins=30, color=BLUE, edgecolor="white", alpha=0.85)
    ax.axvline(x=0.6, color=RED,   linestyle="--", linewidth=2, label="Low threshold  (0.60)")
    ax.axvline(x=0.8, color=GREEN, linestyle="--", linewidth=2, label="High threshold (0.80)")

    # Compute after hist so ylim is known
    ymax = ax.get_ylim()[1]
    low  = (df["ai_confidence_score"] < 0.6).mean() * 100
    mid  = ((df["ai_confidence_score"] >= 0.6) & (df["ai_confidence_score"] < 0.8)).mean() * 100
    high = (df["ai_confidence_score"] >= 0.8).mean() * 100

    band_y = ymax * 0.87
    ax.text(0.30, band_y, f"Low\n{low:.0f}%",    color=RED,    fontsize=10, fontweight="bold", ha="center")
    ax.text(0.70, band_y, f"Medium\n{mid:.0f}%",  color=ORANGE, fontsize=10, fontweight="bold", ha="center")
    ax.text(0.90, band_y, f"High\n{high:.0f}%",   color=GREEN,  fontsize=10, fontweight="bold", ha="center")

    ax.set_xlabel("AI Confidence Score")
    ax.set_ylabel("Ticket Count")
    ax.set_title("Distribution of AI Confidence Scores")
    ax.legend()
    _footnote(ax)
    plt.tight_layout()
    _save(fig, "confidence_distribution.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 5  CUSTOMER RATING BY CATEGORY
# ═══════════════════════════════════════════════════════════════════════════════
def plot_customer_rating_by_category():
    rating = df.groupby("issue_category")["customer_rating"].mean().sort_values()
    colors = [GREEN if v >= 4.0 else ORANGE if v >= 3.5 else RED for v in rating.values]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(rating.index, rating.values, color=colors, edgecolor="white", height=0.62)
    ax.axvline(x=3.5, color=GRAY, linestyle="--", linewidth=1.5, alpha=0.8, label="3.5 baseline")

    for bar, val in zip(bars, rating.values):
        ax.text(val + 0.03, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}", va="center", fontsize=10.5, fontweight="bold", color=DARK_BLUE)

    ax.set_xlabel("Avg Customer Rating (1–5 scale)")
    ax.set_title("Average Customer Rating by Issue Category")
    ax.set_xlim(0, 5.6)
    ax.legend()
    _footnote(ax)
    plt.tight_layout()
    _save(fig, "customer_rating_by_category.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 6  SLA BREACH RATE BY PRIORITY
# ═══════════════════════════════════════════════════════════════════════════════
def plot_sla_breach_by_priority():
    order = ["low", "medium", "high", "critical"]
    breach = df.groupby("priority_level")["sla_breached"].mean() * 100
    breach = breach.reindex(order)
    bar_colors = [GREEN, ORANGE, ORANGE, RED]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(breach.index, breach.values, color=bar_colors, edgecolor="white", width=0.52)

    for bar, val in zip(bars, breach.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=11.5, fontweight="bold",
                color=DARK_BLUE)

    ax.set_ylabel("SLA Breach Rate (%)")
    ax.set_xlabel("Priority Level")
    ax.set_title("SLA Breach Rate by Priority Level")
    ax.set_ylim(0, breach.max() * 1.2)
    ax.legend(handles=[
        mpatches.Patch(color=GREEN,  label="On Track"),
        mpatches.Patch(color=ORANGE, label="Warning"),
        mpatches.Patch(color=RED,    label="Critical"),
    ])
    _footnote(ax)
    plt.tight_layout()
    _save(fig, "sla_breach_by_priority.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 7  COST BY ESCALATION STATUS
# ═══════════════════════════════════════════════════════════════════════════════
def plot_cost_by_escalation():
    ai_cost  = df.loc[~df["escalated_to_human"], "estimated_cost_per_ticket"].mean()
    esc_cost = df.loc[df["escalated_to_human"],  "estimated_cost_per_ticket"].mean()
    multiplier = esc_cost / ai_cost

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(["AI-Handled", "Escalated to Human"],
                  [ai_cost, esc_cost],
                  color=[GREEN, RED], edgecolor="white", width=0.46)

    for bar, val in zip(bars, [ai_cost, esc_cost]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.25,
                f"${val:.2f}", ha="center", va="bottom", fontsize=13, fontweight="bold",
                color=DARK_BLUE)

    ax.set_ylabel("Avg Cost Per Ticket (USD)")
    ax.set_title("Avg Ticket Cost: AI-Handled vs Escalated")
    ax.set_ylim(0, esc_cost * 1.22)
    ax.text(0.5, 0.90, f"{multiplier:.1f}× cost multiplier",
            transform=ax.transAxes, ha="center", fontsize=11.5,
            color=RED, fontweight="bold", style="italic")
    _footnote(ax)
    plt.tight_layout()
    _save(fig, "cost_by_escalation_status.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 8  CONFIDENCE VS CUSTOMER RATING (SCATTER)
# ═══════════════════════════════════════════════════════════════════════════════
def plot_confidence_vs_rating():
    esc = df[df["escalated_to_human"]]
    ai  = df[~df["escalated_to_human"]]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.scatter(ai["ai_confidence_score"],  ai["customer_rating"],
               color=BLUE,   alpha=0.40, s=26, label="AI-Handled",       edgecolors="none")
    ax.scatter(esc["ai_confidence_score"], esc["customer_rating"],
               color=ORANGE, alpha=0.50, s=26, label="Escalated to Human", edgecolors="none")

    for subset, color in [(ai, BLUE), (esc, ORANGE)]:
        z = np.polyfit(subset["ai_confidence_score"], subset["customer_rating"], 1)
        xline = np.linspace(subset["ai_confidence_score"].min(),
                            subset["ai_confidence_score"].max(), 100)
        ax.plot(xline, np.poly1d(z)(xline), color=color, linewidth=2, alpha=0.9)

    ax.axvline(x=0.6, color=RED,   linestyle="--", linewidth=1.4, alpha=0.65, label="Low threshold  (0.60)")
    ax.axvline(x=0.8, color=GREEN, linestyle="--", linewidth=1.4, alpha=0.65, label="High threshold (0.80)")
    ax.set_xlabel("AI Confidence Score")
    ax.set_ylabel("Customer Rating (1–5)")
    ax.set_title("AI Confidence Score vs Customer Rating")
    ax.legend()
    _footnote(ax)
    plt.tight_layout()
    _save(fig, "confidence_vs_rating_scatter.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 9  WORKFLOW FRICTION HEATMAP
# ═══════════════════════════════════════════════════════════════════════════════
def plot_workflow_friction_heatmap():
    agg = df.groupby("issue_category").agg(
        escalation_rate    = ("escalated_to_human", "mean"),
        hallucination_rate = ("hallucination_flag",  "mean"),
        sla_breach_rate    = ("sla_breached",         "mean"),
        avg_rating         = ("customer_rating",      "mean"),
        avg_cost           = ("estimated_cost_per_ticket", "mean"),
    ).round(4)

    heat = agg.copy()
    for col in ["escalation_rate", "hallucination_rate", "sla_breach_rate", "avg_cost"]:
        lo, hi = heat[col].min(), heat[col].max()
        heat[col] = (heat[col] - lo) / (hi - lo + 1e-9)
    lo, hi = heat["avg_rating"].min(), heat["avg_rating"].max()
    heat["avg_rating"] = 1 - (heat["avg_rating"] - lo) / (hi - lo + 1e-9)

    heat.columns = ["Escalation\nRate", "Hallucination\nRate",
                    "SLA Breach\nRate", "Low Rating\n(inverted)", "Avg Cost\n(norm.)"]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    try:
        import seaborn as sns
        sns.heatmap(heat, ax=ax, cmap="YlOrRd", annot=True, fmt=".2f",
                    linewidths=0.5, linecolor="white",
                    cbar_kws={"label": "Normalized friction (0 = low, 1 = high)", "shrink": 0.85})
    except ImportError:
        im = ax.imshow(heat.values, cmap="YlOrRd", aspect="auto", vmin=0, vmax=1)
        plt.colorbar(im, ax=ax, label="Normalized friction", shrink=0.85)
        ax.set_xticks(range(len(heat.columns)))
        ax.set_xticklabels(heat.columns, fontsize=9)
        ax.set_yticks(range(len(heat.index)))
        ax.set_yticklabels(heat.index, fontsize=9)
        for i in range(len(heat.index)):
            for j in range(len(heat.columns)):
                ax.text(j, i, f"{heat.values[i,j]:.2f}",
                        ha="center", va="center", fontsize=9, fontweight="bold")

    ax.set_title("Workflow Friction Heatmap — Normalized by Issue Category")
    ax.set_ylabel("Issue Category")
    _footnote(ax)
    plt.tight_layout()
    _save(fig, "workflow_friction_heatmap.png")


# ═══════════════════════════════════════════════════════════════════════════════
# 10  ESCALATION FUNNEL
# ═══════════════════════════════════════════════════════════════════════════════
def plot_escalation_funnel():
    total        = len(df)
    ai_handled   = int((~df["escalated_to_human"]).sum())
    esc_required = int(df["escalation_required"].sum())
    esc_to_human = int(df["escalated_to_human"].sum())
    sla_breached = int(df["sla_breached"].sum())

    stages = [
        ("Total Tickets Received",  total,        BLUE),
        ("AI-Handled (resolved)",   ai_handled,   GREEN),
        ("Escalation Required",     esc_required, ORANGE),
        ("Escalated to Human",      esc_to_human, ORANGE),
        ("SLA Breached",            sla_breached, RED),
    ]

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, (label, val, color) in enumerate(stages):
        ax.barh(i, val, height=0.56, color=color, alpha=0.88, edgecolor="white")
        pct = f"  ({val/total*100:.1f}%)" if i > 0 else ""
        ax.text(val + total * 0.012, i, f"{val:,}{pct}",
                va="center", fontsize=11, fontweight="bold", color=DARK_BLUE)

    ax.set_yticks(range(len(stages)))
    ax.set_yticklabels([s[0] for s in stages], fontsize=11, fontweight="bold")
    ax.set_xlabel("Number of Tickets")
    ax.set_title("Ticket Escalation Funnel — AI Support Workflow")
    ax.set_xlim(0, total * 1.22)
    ax.invert_yaxis()
    _footnote(ax)
    plt.tight_layout()
    _save(fig, "escalation_funnel.png")


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
