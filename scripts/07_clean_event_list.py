"""
Tidy the WAHIS "Events management" export into a reference table of the
distinct HPAI event/report IDs for Bangladesh -- used for methods-section
provenance (each event/report ID is independently verifiable on WAHIS) and
as a checklist for opening individual reports to look for finer-than-
division location detail.
"""
import pandas as pd
from pathlib import Path

RAW = Path(__file__).parent.parent / "data" / "raw" / "wahis_event_list_2026-08-04.csv"
OUT = Path(__file__).parent.parent / "data" / "processed" / "hpai_event_reference.csv"

HPAI_DISEASES = [
    "High pathogenicity avian influenza viruses (Inf. with) (poultry)",
    "Influenza A viruses of high pathogenicity (Inf. with) (non-poultry including wild birds) (2017-)",
]


def main():
    df = pd.read_csv(RAW, sep=";", encoding="utf-8-sig")
    df["disease"] = df["disease"].str.strip()
    hpai = df[df["disease"].isin(HPAI_DISEASES)].copy()
    hpai["eventStartDate"] = pd.to_datetime(hpai["eventStartDate"], format="%d/%m/%Y")
    hpai["submissionDate"] = pd.to_datetime(hpai["submissionDate"], format="%d/%m/%Y")
    hpai = hpai.sort_values("eventStartDate").reset_index(drop=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    hpai.to_csv(OUT, index=False)
    print(f"Saved {len(hpai)} HPAI events -> {OUT}")
    print(hpai[["eventId", "reportId", "disease", "subType", "eventStartDate", "reason", "reportNumber"]])


if __name__ == "__main__":
    main()
