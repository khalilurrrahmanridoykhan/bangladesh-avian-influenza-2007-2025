"""
Figure 1: Semester-level reporting status of highly pathogenic avian
influenza (HPAI) in Bangladesh poultry and wild birds, 2007-2025.

Data tier: WAHIS six-month country report (presence/absence/no-information
per semester). This is a national reporting-status timeline, not a
district-level outbreak map -- see ../README.md for the data-tier caveat.
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "processed" / "hpai_semester_status_bgd.csv"
OUT = Path(__file__).parent.parent / "figures" / "fig1_semester_status_timeline.png"

COLOR_PRESENT = "#C0392B"     # critical / status red
COLOR_ABSENT = "#D9E8DC"      # good / status pale green
COLOR_NOINFO = "#BDBDBD"      # muted gray, hatched

SERIES = [
    ("HPAI_poultry", "Domestic", "Poultry (domestic)"),
    ("HPAI_poultry", "Wild", "Wild birds\n(poultry-listing)"),
    ("HPAI_nonpoultry_wildbird", "Wild", "Wild birds\n(2017- listing)"),
]


def cell_style(present):
    if pd.isna(present):
        return COLOR_NOINFO, "///"
    return (COLOR_PRESENT, None) if present == 1 else (COLOR_ABSENT, None)


def main():
    df = pd.read_csv(DATA, parse_dates=["period_start"])
    all_periods = sorted(df["period_start"].unique())
    period_index = {p: i for i, p in enumerate(all_periods)}

    fig, ax = plt.subplots(figsize=(14, 3.6))

    for row_i, (disease_code, category, label) in enumerate(SERIES):
        sub = df[(df["disease_code"] == disease_code) & (df["animal_category"] == category)]
        for _, r in sub.iterrows():
            x = period_index[r["period_start"]]
            color, hatch = cell_style(r["present"])
            ax.add_patch(mpatches.Rectangle((x, row_i), 1, 0.9, facecolor=color,
                                             edgecolor="white", linewidth=1.2, hatch=hatch))

    n_periods = len(all_periods)
    ax.set_xlim(0, n_periods)
    ax.set_ylim(0, len(SERIES))
    ax.set_yticks([i + 0.45 for i in range(len(SERIES))])
    ax.set_yticklabels([s[2] for s in SERIES], fontsize=9)
    ax.invert_yaxis()

    year_ticks, year_labels = [], []
    for i, p in enumerate(all_periods):
        if p.month == 1:
            year_ticks.append(i)
            year_labels.append(str(p.year))
    ax.set_xticks(year_ticks)
    ax.set_xticklabels(year_labels, fontsize=8, rotation=0)
    ax.set_xlabel("Year (each cell = one WAHIS reporting semester)", fontsize=10)

    for t in year_ticks:
        ax.axvline(t, color="white", linewidth=0.6, zorder=0)

    legend_handles = [
        mpatches.Patch(facecolor=COLOR_PRESENT, edgecolor="white", label="Present"),
        mpatches.Patch(facecolor=COLOR_ABSENT, edgecolor="white", label="Absent"),
        mpatches.Patch(facecolor=COLOR_NOINFO, edgecolor="white", hatch="///", label="No information reported"),
    ]
    ax.legend(handles=legend_handles, loc="upper center", bbox_to_anchor=(0.5, -0.28),
              ncol=3, fontsize=9, frameon=False)

    ax.set_title("Figure 1. HPAI Reporting Status in Bangladesh by Semester, 2007-2025\n"
                 "(WAHIS six-month country reports; national level, not outbreak-level)",
                 fontsize=11, fontweight="bold")
    ax.spines[:].set_visible(False)
    ax.tick_params(left=False, bottom=False)

    fig.tight_layout()
    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"Saved: {OUT}")
    plt.close()


if __name__ == "__main__":
    main()
