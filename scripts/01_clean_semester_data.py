"""
Clean the WAHIS six-month country report (Disease situation export) for
Bangladesh avian influenza into a tidy, analysis-ready table.

Source: WOAH WAHIS "Disease situation" export (semester-level, national),
not outbreak-level event data. See ../README.md for the data-tier caveat.
"""
import pandas as pd
from pathlib import Path

RAW = Path(__file__).parent.parent / "data" / "raw" / "wahis_disease_situation_2026-08-04.csv"
OUT = Path(__file__).parent.parent / "data" / "processed" / "hpai_semester_status_bgd.csv"

STATUS_MAP = {
    "Present": 1,
    "Absent": 0,
    "No information": pd.NA,
}

DISEASE_SHORT = {
    "High pathogenicity avian influenza viruses (Inf. with) (poultry)": "HPAI_poultry",
    "Influenza A viruses of high pathogenicity (Inf. with) (non-poultry including wild birds) (2017-)": "HPAI_nonpoultry_wildbird",
}


def semester_start_date(year: int, semester: str) -> pd.Timestamp:
    return pd.Timestamp(year=year, month=1 if semester.startswith("Jan") else 7, day=1)


def main():
    df = pd.read_csv(RAW)
    df["disease_code"] = df["Disease"].map(DISEASE_SHORT)
    df["present"] = df["Disease status"].map(STATUS_MAP)
    df["period_start"] = df.apply(lambda r: semester_start_date(r["Year"], r["Semester"]), axis=1)
    df["half"] = df["Semester"].str.slice(0, 3).map({"Jan": "H1", "Jul": "H2"})

    df = df.rename(columns={"Animal category": "animal_category", "Occurence code": "occurrence_code"})
    tidy = df[[
        "Year", "half", "period_start", "disease_code", "animal_category",
        "occurrence_code", "Disease status", "present",
    ]].sort_values(["period_start", "disease_code", "animal_category"]).reset_index(drop=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    tidy.to_csv(OUT, index=False)
    print(f"Wrote {len(tidy)} rows -> {OUT}")
    print(tidy.groupby(["disease_code", "animal_category"])["present"].agg(["count", "sum"]))


if __name__ == "__main__":
    main()
