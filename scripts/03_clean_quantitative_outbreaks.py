"""
Clean the WAHIS "Quantitative data" export (event/outbreak level) for
Bangladesh avian influenza into two tidy tables:

1. hpai_outbreaks_division_semester.csv -- new-outbreak counts by
   administrative division and semester ("Both animal categories" rows).
2. hpai_species_quantitative.csv -- susceptible/cases/killed/deaths by
   division, semester, animal category and species.

"-" in the WAHIS export means "not reported", not zero -- kept as NaN
throughout so absence of data is never silently treated as absence of
disease.
"""
import pandas as pd
from pathlib import Path

RAW = Path(__file__).parent.parent / "data" / "raw" / "wahis_quantitative_data_2026-08-04.csv"
OUT_DIR = Path(__file__).parent.parent / "data" / "processed"

HPAI_DISEASES = [
    "High pathogenicity avian influenza viruses (Inf. with) (poultry)",
    "Influenza A viruses of high pathogenicity (Inf. with) (non-poultry including wild birds) (2017-)",
]

NUMERIC_COLS = ["New outbreaks", "Susceptible", "Cases", "Killed and disposed of",
                 "Slaughtered", "Deaths", "Vaccinated"]


def semester_start_date(year: int, semester: str) -> pd.Timestamp:
    return pd.Timestamp(year=year, month=1 if semester.startswith("Jan") else 7, day=1)


def main():
    df = pd.read_csv(RAW, encoding="utf-8-sig")
    df = df[df["Disease"].isin(HPAI_DISEASES)].copy()

    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col].replace("-", pd.NA))

    df["period_start"] = df.apply(lambda r: semester_start_date(r["Year"], r["Semester"]), axis=1)
    df["disease_short"] = df["Disease"].map({
        HPAI_DISEASES[0]: "HPAI_poultry",
        HPAI_DISEASES[1]: "HPAI_nonpoultry_wildbird",
    })

    # The "outbreak count" is carried on whichever row has no Species value
    # (usually labelled "Both animal categories", but occasionally on a
    # single-category row when only one category was affected that period)
    # -- so group and sum rather than filtering on the Animal Category label.
    group_cols = ["Year", "Semester", "period_start", "Administrative Division",
                  "disease_short", "Serotype/Subtype/Genotype"]
    outbreaks = (
        df.groupby(group_cols, dropna=False)["New outbreaks"]
        .sum(min_count=1)
        .reset_index()
        .rename(columns={"Administrative Division": "division", "New outbreaks": "new_outbreaks",
                          "Serotype/Subtype/Genotype": "serotype"})
    )

    species = df[df["Species"].notna() & (df["Species"] != "")][[
        "Year", "Semester", "period_start", "Administrative Division", "disease_short",
        "Serotype/Subtype/Genotype", "Animal Category", "Species",
        "Susceptible", "Cases", "Killed and disposed of", "Slaughtered", "Deaths", "Vaccinated",
    ]].rename(columns={
        "Administrative Division": "division", "Serotype/Subtype/Genotype": "serotype",
        "Animal Category": "animal_category", "Species": "species",
        "Killed and disposed of": "killed_disposed",
    }).reset_index(drop=True)
    species.columns = [c.lower() for c in species.columns]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outbreaks.to_csv(OUT_DIR / "hpai_outbreaks_division_semester.csv", index=False)
    species.to_csv(OUT_DIR / "hpai_species_quantitative.csv", index=False)

    print(f"Outbreak-count rows: {len(outbreaks)} -> {OUT_DIR/'hpai_outbreaks_division_semester.csv'}")
    print(f"Species-quantitative rows: {len(species)} -> {OUT_DIR/'hpai_species_quantitative.csv'}")
    print("\nTotal new outbreaks by division:")
    print(outbreaks.groupby("division")["new_outbreaks"].sum().sort_values(ascending=False))
    print("\nWild/non-poultry species detected:", sorted(species[species["animal_category"] != "Domestic"]["species"].dropna().unique()))


if __name__ == "__main__":
    main()
