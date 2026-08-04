"""
Table 1: Division-level HPAI burden summary, Bangladesh 2007-2025.
"""
import pandas as pd
from pathlib import Path

OUTBREAKS = Path(__file__).parent.parent / "data" / "processed" / "hpai_outbreaks_division_semester.csv"
SPECIES = Path(__file__).parent.parent / "data" / "processed" / "hpai_species_quantitative.csv"
OUT = Path(__file__).parent.parent / "data" / "table1_division_summary.csv"


def main():
    outbreaks = pd.read_csv(OUTBREAKS)
    species = pd.read_csv(SPECIES)

    ob = outbreaks.groupby("division")["new_outbreaks"].sum(min_count=1).rename("total_new_outbreaks")
    sp = species.groupby("division")[["susceptible", "cases", "killed_disposed", "deaths"]].sum(min_count=1)

    first_last = outbreaks.dropna(subset=["new_outbreaks"]).groupby("division")["Year"].agg(["min", "max"])
    first_last.columns = ["first_year_reported", "last_year_reported"]

    table = ob.to_frame().join(sp, how="outer").join(first_last, how="outer")
    table = table.sort_values("total_new_outbreaks", ascending=False)

    table.to_csv(OUT)
    print(f"Saved: {OUT}")
    print(table)


if __name__ == "__main__":
    main()
