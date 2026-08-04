"""
Figure 5: HPAI outbreaks by division-semester against mean relative
humidity, split by dry/cool vs. monsoon/warm semester -- showing the
seasonal mechanism behind the humidity/precipitation correlations in
Table 2 (525 of 563 reported outbreaks fall in Jan-Jun semesters).
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "processed" / "hpai_modeling_dataset.csv"
OUT = Path(__file__).parent.parent / "figures" / "fig5_climate_seasonality.png"

COLORS = {"Jan-Jun (dry/cool)": "#3A6EA5", "Jul-Dec (monsoon/warm)": "#E07B54"}


def main():
    df = pd.read_csv(DATA, parse_dates=["period_start"])
    df["half"] = df["period_start"].dt.month.map({1: "Jan-Jun (dry/cool)", 7: "Jul-Dec (monsoon/warm)"})

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for half, color in COLORS.items():
        sub = df[df["half"] == half]
        ax.scatter(sub["humidity_mean_pct"], sub["new_outbreaks"], s=45, color=color,
                  alpha=0.75, edgecolor="white", linewidth=0.8, label=half, zorder=3)

    ax.set_xlabel("Mean relative humidity (%), division-semester", fontsize=10)
    ax.set_ylabel("New outbreaks (division-semester)", fontsize=10)
    ax.set_title("Figure 5. HPAI Outbreaks vs. Humidity by Season,\nBangladesh Divisions 2007-2025",
                fontsize=11, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9, framealpha=0.9, title="Semester")
    ax.grid(linestyle="--", alpha=0.3, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"Saved: {OUT}")
    plt.close()


if __name__ == "__main__":
    main()
