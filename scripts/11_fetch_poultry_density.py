"""
Download the FAO GLW4 (Gridded Livestock of the World v4, 2020, 10km)
chicken-density raster and compute zonal statistics (mean density per
km^2, and an approximate total headcount) for each Bangladesh division,
for use as a poultry-exposure covariate in HPAI risk modeling.

Source: FAO GeoNetwork catalog, CC BY 4.0.
https://data.apps.fao.org/catalog//iso/9d1e149b-d63f-4213-978b-317a8eb42d02
"""
import requests
import geopandas as gpd
import rasterio
from rasterstats import zonal_stats
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DIVISIONS_GEOJSON = BASE_DIR / "data" / "external" / "bgd_adm1_wahis7.geojson"
RASTER_URL = "https://storage.googleapis.com/fao-gismgr-glw4-2020-data/DATA/GLW4-2020/MAPSET/D-DA/GLW4-2020.D-DA.CHK.tif"
RASTER_PATH = BASE_DIR / "data" / "external" / "glw4_2020_chicken_density_global.tif"
OUT = BASE_DIR / "data" / "processed" / "poultry_density_by_division.csv"


def download_raster():
    if RASTER_PATH.exists():
        print(f"Already downloaded: {RASTER_PATH}")
        return
    print("Downloading GLW4 chicken density raster (~12 MB)...")
    resp = requests.get(RASTER_URL, timeout=120)
    resp.raise_for_status()
    RASTER_PATH.parent.mkdir(parents=True, exist_ok=True)
    RASTER_PATH.write_bytes(resp.content)
    print(f"Saved -> {RASTER_PATH}")


def main():
    download_raster()

    divisions = gpd.read_file(DIVISIONS_GEOJSON)
    with rasterio.open(RASTER_PATH) as src:
        raster_crs = src.crs
    divisions_proj = divisions.to_crs(raster_crs)

    # Let rasterstats read nodata from the raster's own metadata (float32 min,
    # not a round number like -9999) rather than guessing it.
    stats = zonal_stats(divisions_proj, str(RASTER_PATH), stats=["mean", "min", "max", "count"])
    divisions["chicken_density_mean_per_km2"] = [s["mean"] for s in stats]
    divisions["chicken_density_max_per_km2"] = [s["max"] for s in stats]

    # Area in km^2 via an equal-area projection, for an approximate headcount.
    divisions_eq = divisions.to_crs("ESRI:54009")  # World Mollweide (equal-area)
    divisions["area_km2"] = divisions_eq.geometry.area / 1e6
    divisions["est_chicken_headcount"] = divisions["chicken_density_mean_per_km2"] * divisions["area_km2"]

    out = divisions[["wahis_division", "area_km2", "chicken_density_mean_per_km2",
                      "chicken_density_max_per_km2", "est_chicken_headcount"]]
    out = out.sort_values("chicken_density_mean_per_km2", ascending=False)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"Saved -> {OUT}")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
