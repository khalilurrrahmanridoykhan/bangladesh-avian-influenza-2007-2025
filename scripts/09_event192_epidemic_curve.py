"""
Figure 4: Report-level epidemic curve of the 2007-2013 HPAI poultry wave
in Bangladesh (WAHIS event 192), at near-monthly resolution -- new
outbreaks per report and cumulative outbreaks.
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "processed" / "hpai_event192_report_history.csv"
OUT = Path(__file__).parent.parent / "figures" / "fig4_event192_epidemic_curve.png"


def main():
    df = pd.read_csv(DATA, parse_dates=["reportingDate"])

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(12, 6.5), sharex=True,
        gridspec_kw={"height_ratios": [1, 1], "hspace": 0.12},
    )

    ax_top.bar(df["reportingDate"], df["newOutbreaks"], width=12, color="#3A6EA5", zorder=3)
    peak_idx = df["newOutbreaks"].idxmax()
    ax_top.annotate(f"Peak: {int(df.loc[peak_idx, 'newOutbreaks'])} new outbreaks\n"
                     f"({df.loc[peak_idx, 'reportingDate'].strftime('%b %Y')} report)",
                     xy=(df.loc[peak_idx, "reportingDate"], df.loc[peak_idx, "newOutbreaks"]),
                     xytext=(15, -5), textcoords="offset points", fontsize=8.5, color="#1A3A6A")
    ax_top.set_ylabel("New outbreaks\nper report", fontsize=9.5)
    ax_top.set_title("Figure 4. Report-Level Epidemic Curve of the 2007-2013 HPAI Poultry Wave\n"
                     "Bangladesh, WAHIS Event 192 (46 follow-up reports, near-monthly resolution)",
                     fontsize=11, fontweight="bold")
    ax_top.grid(axis="y", linestyle="--", alpha=0.3, zorder=0)
    ax_top.spines[["top", "right"]].set_visible(False)

    ax_bot.plot(df["reportingDate"], df["totalOutbreaks"], color="#A0522D", linewidth=2.2,
               marker="o", markersize=3.5, zorder=3)
    ax_bot.fill_between(df["reportingDate"], df["totalOutbreaks"], color="#A0522D", alpha=0.12, zorder=2)
    ax_bot.set_ylabel("Cumulative\noutbreaks", fontsize=9.5)
    ax_bot.grid(axis="y", linestyle="--", alpha=0.3, zorder=0)
    ax_bot.spines[["top", "right"]].set_visible(False)

    ax_bot.xaxis.set_major_locator(mdates.YearLocator())
    ax_bot.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax_bot.set_xlabel("Report date (each point = one immediate notification / follow-up report)", fontsize=9.5)
    ax_bot.set_xlim(pd.Timestamp("2006-11-01"), pd.Timestamp("2014-03-01"))

    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"Saved: {OUT}")
    plt.close()


if __name__ == "__main__":
    main()
