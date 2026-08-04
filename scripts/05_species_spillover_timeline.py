"""
Figure 3: Species detected positive for HPAI in Bangladesh over time,
domestic poultry vs. wild bird vs. wild mammal, 2007-2025.

Highlights the poultry -> wild bird -> mammal (Serval, 2025) spillover
pattern in the WAHIS event-level record.
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "processed" / "hpai_species_quantitative.csv"
OUT = Path(__file__).parent.parent / "figures" / "fig3_species_spillover_timeline.png"

XLIM = (pd.Timestamp("2006-06-01"), pd.Timestamp("2026-06-01"))

WILD_ROWS = [
    ("Wild", "House Crow", "Wild bird -\nHouse Crow", "#E8A33D"),
    ("Wild", "Phasianidae (unidentified)", "Wild bird -\nPhasianidae", "#6A4C93"),
    ("Wild", "Serval", "Wild mammal -\nServal", "#C0392B"),
]


def main():
    df = pd.read_csv(DATA, parse_dates=["period_start"])

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(11, 6.5), sharex=True,
        gridspec_kw={"height_ratios": [1.3, 1], "hspace": 0.15},
    )

    # Panel A: domestic poultry cases per semester, summed across divisions
    # (many divisions report in the same semester, so this is a national total).
    poultry = df[(df["animal_category"] == "Domestic") & (df["species"] == "Birds")]
    poultry_by_period = poultry.groupby("period_start")["cases"].sum(min_count=1)
    ax_top.bar(poultry_by_period.index, poultry_by_period.values, width=100,
               color="#3A6EA5", zorder=3)
    ax_top.set_ylabel("Domestic poultry\ncases per semester", fontsize=9.5)
    ax_top.set_title("Figure 3. HPAI Cases in Bangladesh, 2007-2025:\n"
                      "Domestic Poultry vs. Wild-Species Detections (Including the 2025 Serval Spillover)",
                      fontsize=11, fontweight="bold")
    ax_top.grid(axis="y", linestyle="--", alpha=0.3, zorder=0)
    ax_top.spines[["top", "right"]].set_visible(False)
    ax_top.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))

    # Panel B: sparse wild-species detections, one marker per semester per species.
    for row_i, (cat, sp, label, color) in enumerate(WILD_ROWS):
        sub = df[(df["animal_category"] == cat) & (df["species"] == sp)]
        # Sum across divisions reporting in the same semester so overlapping
        # points never collide (this loses the division breakdown -- see
        # data/processed/hpai_species_quantitative.csv for that detail).
        by_period = sub.groupby("period_start")["cases"].sum(min_count=1)
        sizes = (by_period.fillna(0).clip(lower=1) ** 0.5) * 14 + 70
        ax_bot.scatter(by_period.index, [row_i] * len(by_period), s=sizes, color=color,
                       alpha=0.9, edgecolor="white", linewidth=1.2, zorder=3)
        for period, cases in by_period.items():
            if pd.notna(cases):
                ax_bot.annotate(f"{int(cases):,}", (period, row_i),
                                textcoords="offset points", xytext=(0, 14), fontsize=7.5,
                                ha="center", color=color)

    ax_bot.set_yticks(range(len(WILD_ROWS)))
    ax_bot.set_yticklabels([r[2] for r in WILD_ROWS], fontsize=8.5)
    ax_bot.set_ylim(-0.6, len(WILD_ROWS) - 0.4)
    ax_bot.invert_yaxis()
    ax_bot.spines[["top", "right", "left"]].set_visible(False)
    ax_bot.tick_params(left=False)
    ax_bot.grid(axis="x", linestyle="--", alpha=0.3, zorder=0)

    ax_bot.set_xlim(*XLIM)
    ax_bot.xaxis.set_major_locator(mdates.YearLocator(2))
    ax_bot.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax_bot.set_xlabel("Semester of detection (marker size = reported cases)", fontsize=9.5)

    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"Saved: {OUT}")
    plt.close()


if __name__ == "__main__":
    main()
