"""
Figure 6: Choropleth map of total reported HPAI outbreaks by division,
Bangladesh 2007-2025.
"""
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
BOUNDARY = BASE_DIR / "data" / "external" / "bgd_adm1_wahis7.geojson"
TABLE1 = BASE_DIR / "data" / "table1_division_summary.csv"
OUT = BASE_DIR / "figures" / "fig6_division_choropleth_map.png"


def main():
    gdf = gpd.read_file(BOUNDARY)
    table1 = pd.read_csv(TABLE1)

    # Narayanganj Sadar is an upazila within Dhaka division -- the boundary
    # file only resolves to the 7 WAHIS divisions, so fold it into Dhaka's
    # total rather than dropping it.
    table1["division"] = table1["division"].replace({"Narayanganj Sadar": "Dhaka"})
    burden = table1.groupby("division")["total_new_outbreaks"].sum().reset_index()

    gdf = gdf.merge(burden, left_on="wahis_division", right_on="division", how="left")

    fig, ax = plt.subplots(figsize=(8, 9))
    gdf.plot(column="total_new_outbreaks", cmap="Blues", linewidth=1.2, edgecolor="white",
             ax=ax, legend=True,
             legend_kwds={"label": "Total reported new outbreaks, 2007-2025", "shrink": 0.6})

    for _, row in gdf.iterrows():
        pt = row.geometry.representative_point()
        ax.annotate(f"{row['wahis_division']}\n{int(row['total_new_outbreaks']):,}",
                    xy=(pt.x, pt.y), ha="center", fontsize=8.5, fontweight="bold",
                    color="#1A1A1A")

    ax.set_title("Figure 6. HPAI Outbreak Burden by Division,\nBangladesh 2007-2025 (WAHIS event-level reports)",
                fontsize=12, fontweight="bold")
    ax.set_axis_off()

    fig.tight_layout()
    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"Saved: {OUT}")
    plt.close()


if __name__ == "__main__":
    main()
