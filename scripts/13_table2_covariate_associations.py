"""
Table 2: Association between HPAI outbreak counts and climate/poultry
covariates, plus the dry-season vs. monsoon-season split.

Note: statsmodels is unavailable in this environment (scipy version
mismatch unrelated to this project), so this is a descriptive/correlational
first pass (Pearson r on division-semester counts), not a fitted
negative-binomial regression -- see README for how to extend this.
"""
import pandas as pd
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "processed" / "hpai_modeling_dataset.csv"
OUT_CORR = Path(__file__).parent.parent / "data" / "table2_covariate_correlation.csv"
OUT_SEASON = Path(__file__).parent.parent / "data" / "table2b_seasonal_split.csv"


def main():
    df = pd.read_csv(DATA, parse_dates=["period_start"])

    corr_cols = ["new_outbreaks", "temp_mean_c", "humidity_mean_pct", "precip_total_mm", "chicken_density_mean_per_km2"]
    corr = df[corr_cols].corr(numeric_only=True)[["new_outbreaks"]].rename(columns={"new_outbreaks": "pearson_r_with_new_outbreaks"})
    corr = corr.drop(index="new_outbreaks")
    corr.to_csv(OUT_CORR)
    print(f"Saved -> {OUT_CORR}")
    print(corr)

    df["half"] = df["period_start"].dt.month.map({1: "Jan-Jun (dry/cool)", 7: "Jul-Dec (monsoon/warm)"})
    season = df.groupby("half").agg(
        total_outbreaks=("new_outbreaks", "sum"),
        mean_outbreaks_per_division_semester=("new_outbreaks", "mean"),
        mean_humidity_pct=("humidity_mean_pct", "mean"),
        mean_precip_mm=("precip_total_mm", "mean"),
        mean_temp_c=("temp_mean_c", "mean"),
        n_division_semesters=("new_outbreaks", "count"),
    )
    season.to_csv(OUT_SEASON)
    print(f"\nSaved -> {OUT_SEASON}")
    print(season)


if __name__ == "__main__":
    main()
