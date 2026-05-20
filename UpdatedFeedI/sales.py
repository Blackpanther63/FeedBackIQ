import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


# ── Model ───────────────────────────────────────────────────────
#
# "Before bad reviews" = peak launch potential (product always starts
#  higher — hype, early-adopter boost, no negative signal yet).
#
# "After bad reviews"  = current state reduced by:
#   • negative reviews  → heavy drag  (×0.75 per neg-ratio point)
#   • neutral reviews   → light drag  (×0.12 per neu-ratio point)
#   • natural product-age decay (minimum 5 % always shown)
#
# This guarantees before > after even for fully-positive products,
# which is realistic — no product sustains its launch peak forever.


_LAUNCH_BOOST = 1.30   # peak is always 30 % above the settled baseline
_MIN_DROP     = 0.05   # at least 5 % natural decay even with zero bad reviews


def estimate_sales_impact(result, rating):
    total = result["positive"] + result["negative"] + result["neutral"]
    if total == 0:
        return None

    pos_ratio = result["positive"] / total
    neg_ratio = result["negative"] / total
    neu_ratio = result["neutral"]  / total

    # Settled baseline driven by rating + positive share
    rating_factor = 0.4 + (rating / 5) * 0.6          # 0.40 – 1.00
    base = 1000 * rating_factor * (0.5 + pos_ratio)    # ~200 – 1500

    sales_before = round(base * _LAUNCH_BOOST)

    neg_drag  = neg_ratio * 0.75
    neu_drag  = neu_ratio * 0.12
    total_drag = max(_MIN_DROP, neg_drag + neu_drag)   # floor at 5 %

    sales_after = round(sales_before * (1 - total_drag))
    drop_pct    = round((sales_before - sales_after) / sales_before * 100, 1)

    if drop_pct < 10:
        severity = "Low"
    elif drop_pct < 30:
        severity = "Moderate"
    elif drop_pct < 55:
        severity = "High"
    else:
        severity = "Critical"

    return {
        "sales_before": sales_before,
        "sales_after":  sales_after,
        "drop_pct":     drop_pct,
        "neg_pct":      round(neg_ratio * 100, 1),
        "pos_pct":      round(pos_ratio * 100, 1),
        "severity":     severity,
    }


# ── Chart ───────────────────────────────────────────────────────

def generate_sales_chart(impact):
    before = impact["sales_before"]
    after  = impact["sales_after"]
    drop   = impact["drop_pct"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    fig.patch.set_facecolor("#f8faff")

    # ── Panel 1 : Bar comparison ────────────────────────────────
    bars = ax1.bar(
        ["Before\nBad Reviews", "After\nBad Reviews"],
        [before, after],
        color=["#2563eb", "#ef4444"],
        width=0.45,
        edgecolor="white",
        linewidth=1.5,
        zorder=3,
    )
    ax1.set_facecolor("#f8faff")
    ax1.yaxis.grid(True, color="#e2e8f0", linewidth=0.8, zorder=0)
    ax1.set_axisbelow(True)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_color("#e2e8f0")
    ax1.spines["bottom"].set_color("#e2e8f0")
    ax1.set_ylabel("Sales Index (units)", fontsize=9, color="#475569")
    ax1.set_title("Sales Impact: Before vs After", fontsize=11,
                  fontweight="bold", color="#1e293b", pad=10)
    ax1.tick_params(colors="#475569", labelsize=9)

    # Value label inside "Before" bar
    ax1.text(
        bars[0].get_x() + bars[0].get_width() / 2,
        bars[0].get_height() * 0.5,
        f"{before:,}",
        ha="center", va="center",
        fontsize=11, fontweight="bold", color="white",
    )

    # Value + drop label inside "After" bar
    ax1.text(
        bars[1].get_x() + bars[1].get_width() / 2,
        bars[1].get_height() * 0.5,
        f"{after:,}\n▼ {drop}% drop",
        ha="center", va="center",
        fontsize=10, fontweight="bold", color="white",
        linespacing=1.6,
    )

    # ── Panel 2 : Monthly trend line ────────────────────────────
    months = np.arange(1, 13)
    ramp   = np.linspace(before * 0.55, before, 6)
    decay  = np.linspace(before, after, 6)
    sales  = np.concatenate([ramp, decay])

    ax2.set_facecolor("#f8faff")
    ax2.fill_between(months[:6], sales[:6], alpha=0.13, color="#2563eb")
    ax2.fill_between(months[5:], sales[5:], alpha=0.10, color="#ef4444")
    ax2.plot(months[:6], sales[:6], color="#2563eb", linewidth=2.2,
             label="Growth phase")
    ax2.plot(months[5:], sales[5:], color="#ef4444", linewidth=2.2,
             linestyle="--", label="Post bad-review decline")

    # Inflection marker (placed at top-left of right half to avoid overlap)
    ax2.axvline(x=6, color="#f59e0b", linewidth=1.4, linestyle=":")
    ax2.text(6.2, sales.min() + (sales.max() - sales.min()) * 0.15,
             "Bad reviews\ninflection",
             fontsize=7.5, color="#92400e", va="bottom")

    ax2.yaxis.grid(True, color="#e2e8f0", linewidth=0.8, zorder=0)
    ax2.set_axisbelow(True)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_color("#e2e8f0")
    ax2.spines["bottom"].set_color("#e2e8f0")
    ax2.set_xlabel("Month", fontsize=9, color="#475569")
    ax2.set_ylabel("Sales Index (units)", fontsize=9, color="#475569")
    ax2.set_title("Simulated Monthly Sales Trend", fontsize=11,
                  fontweight="bold", color="#1e293b", pad=10)
    ax2.set_xticks(months)
    ax2.tick_params(colors="#475569", labelsize=8)
    ax2.legend(fontsize=8, frameon=False, loc="lower left")

    plt.tight_layout(pad=2.0)
    plt.savefig("static/sales_impact.png", bbox_inches="tight", dpi=120,
                facecolor="#f8faff")
    plt.close()
