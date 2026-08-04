"""
Fetch daily temperature, relative humidity, and precipitation for each
Bangladesh division centroid from the NASA POWER API (2007-2025), then
aggregate to WAHIS reporting semesters for use as HPAI risk covariates.

NASA POWER (power.larc.nasa.gov) is a public, no-auth-required point API
maintained by NASA Langley -- one query per division centroid, not one per
semester, to keep this to 7 requests total.

Division centroid = centroid of the WAHIS 7-division dissolve (Mymensingh
merged into Dhaka; see data/external/bgd_adm1_wahis7.geojson) -- a coarse
division-average, not village-level climate.
"""
import time
import requests
import pandas as pd
import geopandas as gpd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DIVISIONS_GEOJSON = BASE_DIR / "data" / "external" / "bgd_adm1_wahis7.geojson"
OUT_DAILY = BASE_DIR / "data" / "external" / "climate_daily_by_division.csv"
OUT_SEMESTER = BASE_DIR / "data" / "processed" / "climate_semester_by_division.csv"

POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS = "T2M,RH2M,PRECTOTCORR"
START, END = "20070101", "20251231"


def fetch_division(name: str, lat: float, lon: float) -> pd.DataFrame:
    resp = requests.get(POWER_URL, params={
        "parameters": PARAMS, "community": "AG", "longitude": lon, "latitude": lat,
        "start": START, "end": END, "format": "JSON",
    }, timeout=60)
    resp.raise_for_status()
    data = resp.json()["properties"]["parameter"]
    df = pd.DataFrame({k: pd.Series(v) for k, v in data.items()})
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df = df.replace(-999, pd.NA)  # NASA POWER fill value for missing days
    df["division"] = name
    return df.reset_index(names="date")


def semester_of(date: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(year=date.year, month=1 if date.month <= 6 else 7, day=1)


def main():
    divisions = gpd.read_file(DIVISIONS_GEOJSON)
    divisions["centroid"] = divisions.geometry.centroid

    daily_frames = []
    for _, row in divisions.iterrows():
        name = row["wahis_division"]
        print(f"Fetching NASA POWER daily data for {name}...")
        df = fetch_division(name, row["centroid"].y, row["centroid"].x)
        daily_frames.append(df)
        time.sleep(1)  # be polite to the public API

    daily = pd.concat(daily_frames, ignore_index=True)
    daily.to_csv(OUT_DAILY, index=False)
    print(f"Saved daily climate -> {OUT_DAILY} ({len(daily)} rows)")

    daily["period_start"] = daily["date"].map(semester_of)
    semester = daily.groupby(["division", "period_start"]).agg(
        temp_mean_c=("T2M", "mean"),
        humidity_mean_pct=("RH2M", "mean"),
        precip_total_mm=("PRECTOTCORR", "sum"),
    ).reset_index()

    OUT_SEMESTER.parent.mkdir(parents=True, exist_ok=True)
    semester.to_csv(OUT_SEMESTER, index=False)
    print(f"Saved semester climate -> {OUT_SEMESTER} ({len(semester)} rows)")


if __name__ == "__main__":
    main()
