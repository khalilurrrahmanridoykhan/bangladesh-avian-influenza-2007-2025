"""
Merge HPAI outbreak counts (division x semester), climate covariates
(division x semester), and poultry density (division, static 2020 snapshot)
into one analysis-ready table for risk modeling.

Caveats carried forward from upstream scripts:
- Outbreak counts are WAHIS-reported, not necessarily true incidence
  (surveillance intensity varies over time -- see README).
- Poultry density is a single 2020 cross-section applied to all years as a
  spatial covariate (relative exposure), not a year-matched population.
- Climate is a division-centroid average, not village-level.
"""
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTBREAKS = BASE_DIR / "data" / "processed" / "hpai_outbreaks_division_semester.csv"
CLIMATE = BASE_DIR / "data" / "processed" / "climate_semester_by_division.csv"
POULTRY = BASE_DIR / "data" / "processed" / "poultry_density_by_division.csv"
OUT = BASE_DIR / "data" / "processed" / "hpai_modeling_dataset.csv"

ALL_DIVISIONS = ["Barisal", "Chittagong", "Dhaka", "Khulna", "Rajshahi", "Rangpur", "Sylhet"]


def all_division_semesters(outbreaks: pd.DataFrame) -> pd.DataFrame:
    """A complete division x semester grid, 2007-2025, so that semesters with
    zero reported outbreaks are explicit rows (needed for count regression),
    not just absent from the data."""
    periods = pd.date_range("2007-01-01", "2025-07-01", freq="6MS")
    grid = pd.MultiIndex.from_product([ALL_DIVISIONS, periods], names=["division", "period_start"]).to_frame(index=False)
    agg = outbreaks.groupby(["division", "period_start"])["new_outbreaks"].sum(min_count=1).reset_index()
    merged = grid.merge(agg, on=["division", "period_start"], how="left")
    merged["new_outbreaks"] = merged["new_outbreaks"].fillna(0)
    return merged


def main():
    outbreaks = pd.read_csv(OUTBREAKS, parse_dates=["period_start"])
    climate = pd.read_csv(CLIMATE, parse_dates=["period_start"])
    poultry = pd.read_csv(POULTRY)

    grid = all_division_semesters(outbreaks)
    merged = grid.merge(climate, on=["division", "period_start"], how="left")
    merged = merged.merge(poultry, left_on="division", right_on="wahis_division", how="left").drop(columns="wahis_division")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUT, index=False)
    print(f"Saved {len(merged)} division-semester rows -> {OUT}")
    print(merged.head(10).to_string())

    corr_cols = ["new_outbreaks", "temp_mean_c", "humidity_mean_pct", "precip_total_mm", "chicken_density_mean_per_km2"]
    print("\nPairwise correlation with new_outbreaks:")
    print(merged[corr_cols].corr(numeric_only=True)["new_outbreaks"])


if __name__ == "__main__":
    main()
