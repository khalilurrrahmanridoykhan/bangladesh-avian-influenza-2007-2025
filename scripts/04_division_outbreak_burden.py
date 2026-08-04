"""
Figure 2: Total reported HPAI outbreaks by administrative division,
Bangladesh, 2007-2025 (WAHIS Quantitative data export).
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "processed" / "hpai_outbreaks_division_semester.csv"
OUT = Path(__file__).parent.parent / "figures" / "fig2_division_outbreak_burden.png"

BAR_COLOR = "#3A6EA5"


def main():
    df = pd.read_csv(DATA)
    totals = df.groupby("division")["new_outbreaks"].sum().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(totals.index, totals.values, color=BAR_COLOR, height=0.6)

    for bar, val in zip(bars, totals.values):
        ax.text(val + max(totals.values) * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{int(val)}", va="center", fontsize=9)

    ax.set_xlabel("Total reported new outbreaks, 2007-2025", fontsize=10)
    ax.set_title("Figure 2. Reported HPAI Outbreaks by Administrative Division,\nBangladesh 2007-2025 (WAHIS event-level reports)",
                 fontsize=11, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.35, zorder=0)
    ax.set_xlim(0, totals.max() * 1.12)

    fig.tight_layout()
    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"Saved: {OUT}")
    plt.close()


if __name__ == "__main__":
    main()
