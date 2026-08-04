"""
Clean the report-by-report history of WAHIS event 192 -- the 2007-2013
HPAI poultry epidemic wave in Bangladesh -- into a tidy, date-sorted table.
Report dates give near-monthly resolution, much finer than the semester
bins used elsewhere in this repo (see data/processed/hpai_outbreaks_division_semester.csv).

Caveat: "reportingDate" is when the report was submitted to WAHIS, not
necessarily the exact outbreak date -- treat this as report-level, not
outbreak-level, temporal resolution.
"""
import pandas as pd
from pathlib import Path

RAW = Path(__file__).parent.parent / "data" / "raw" / "historical_report_event192_2007-2013wave.csv"
OUT = Path(__file__).parent.parent / "data" / "processed" / "hpai_event192_report_history.csv"


def main():
    df = pd.read_csv(RAW, sep=";", encoding="utf-8-sig")
    df["reportingDate"] = pd.to_datetime(df["reportingDate"], format="%d/%m/%Y")
    df = df.sort_values("reportingDate").reset_index(drop=True)
    df = df[["reportId", "reportNumber", "reportType", "newOutbreaks", "totalOutbreaks", "reportingDate"]]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Saved {len(df)} report-dated rows -> {OUT}")
    print(f"Date range: {df['reportingDate'].min().date()} to {df['reportingDate'].max().date()}")
    print(f"Cumulative outbreaks reported: {df['totalOutbreaks'].max()}")


if __name__ == "__main__":
    main()
