# Highly Pathogenic Avian Influenza in Bangladesh — One Health Data & Analysis

Working repository for a One Health analysis of HPAI in Bangladesh —
poultry, wild birds, and (planned) environmental/climate covariates —
built entirely from official WOAH WAHIS surveillance data.

> Khalilur Rahman Ridoy Khan

---

## Key Findings

| Metric | Value |
|--------|-------|
| Study period | 2007–2025 (WAHIS records) |
| Total reported HPAI outbreaks (event-level) | 564 |
| Divisions affected | 8 of 8 |
| Highest-burden division | Dhaka (266 outbreaks) |
| Epidemic wave with finest resolution | 2007–2013 (event 192, 46 follow-up reports) |
| Peak single-report outbreak count | 156 new outbreaks (April 2008) |
| Second wave peak | 67 new outbreaks (March 2011) |
| Wild-species detections | House Crow, Phasianidae, and a captive Serval (2025) |
| Most recent record | H5N1 in a captive Serval, Narayanganj, April 2025 |
| Seasonality | 525 of 563 outbreaks (93%) in Jan-Jun (dry/cool) semesters vs. 38 in Jul-Dec (monsoon) |
| Outbreaks vs. humidity | Pearson r = -0.21; outbreaks concentrate below ~75% mean relative humidity |

---

## Data tiers

WAHIS (WOAH) publishes **two different products** and it is easy to grab
the wrong one:

| Tier | WAHIS product | Granularity | What it contains |
|------|----------------|-------------|-------------------|
| **Tier 1** | "Disease situation" / six-month country report | National, per 6-month semester | Present / Absent / No-information per disease per semester. No location, no case counts. |
| **Tier 2 (in hand)** | "Quantitative data" dashboard (event-level export) | Administrative division, per semester, per species/serotype | New outbreaks, susceptible, cases, killed/disposed, slaughtered, deaths, vaccinated |

Both files are in `data/raw/`:
- `wahis_disease_situation_2026-08-04.csv` — Tier 1, 84 rows. Supports the
  national reporting-status timeline (Figure 1) only.
- `wahis_quantitative_data_2026-08-04.csv` — Tier 2, 179 rows for Bangladesh
  across **11 diseases** (not just HPAI — also FMD, ASF, lumpy skin disease,
  rabies, anthrax, etc.; useful for other One Health papers in this
  series). Filtered to the 2 HPAI-related listings: 105 rows, 2007–2025,
  covering 8 administrative divisions/localities.

**Known gaps / caveats:**
- Tier 1 export has no rows at all for 2021 or 2022 (not "no information" —
  the years are simply absent). Tier 2 shows the same silence (2014–2015
  and 2020–2024 have no HPAI rows), consistent with a real reporting gap
  rather than an export artifact, but not proven.
- Tier 2 gives **administrative division** (mostly the old 7 greater
  divisions, occasionally an upazila like "Narayanganj Sadar"), not exact
  GPS coordinates. Fine for division-level choropleth maps and regression;
  not fine enough for point-pattern/kernel-density analysis.
- "-" in the raw export means *not reported*, not zero — kept as `NaN`
  throughout `scripts/03_clean_quantitative_outbreaks.py`, never coerced to 0.
- A single 2025 record: H5N1 in a **Serval** (wild cat) in Narayanganj —
  a mammalian spillover event, notable for the One Health framing.

### Event-level layer (WAHIS → Reports → Animal disease events)

Bangladesh has exactly **9 distinct HPAI "events"** in WAHIS's tracking
(an event = one outbreak wave/investigation, followed over time by
"follow-up reports" — WAHIS does not open a new event per case). See
`data/processed/hpai_event_reference.csv`.

Opening an individual event's **Outbreaks** tab confirmed WAHIS *does*
store exact outbreak-level coordinates (e.g. the 2025 event: a **captive**
Serval, H5N1-positive, at 23.64696, 90.512087, Siddirgonj Thana,
Narayanganj — labelled "WILD Captive", i.e. a captive-wildlife biosecurity
case, not confirmed free-ranging transmission). But there is no bulk
export of this outbreak-coordinate layer, and the largest event (192, the
2007–2013 wave) has **549 individual outbreaks** — infeasible to extract
by hand. Point-level spatial analysis is therefore out of scope for this
paper; division-level is the practical ceiling.

What **is** bulk-exportable per event is the **report history** (WAHIS →
event → Historical Reports tab → Export), which gives report-by-report
dates and new/cumulative outbreak counts — much finer than the semester
bins. Used for event 192 → `hpai_event192_report_history.csv` → Figure 4,
which reveals **two distinct peaks** inside the "2007–2013" semester-level
wave (April 2008: 156 new outbreaks in one report; March 2011: 67) with a
quiet 2009–2010 gap between them, invisible in the semester-level data.
The other 8 HPAI events have only 1–2 reports each, so this doesn't add
meaningful resolution for them.

### Climate and poultry-density covariates

Added to move toward the risk-mapping/regression stage of the original plan:

- **Climate** (`scripts/10_fetch_climate_covariates.py`): daily temperature,
  relative humidity, and precipitation from the [NASA POWER](https://power.larc.nasa.gov/)
  point API (public, no auth), one query per division centroid, 2007-2025,
  aggregated to WAHIS semesters. Division-centroid average, not
  village-level.
- **Poultry density** (`scripts/11_fetch_poultry_density.py`): chicken
  density (head/km²) from [FAO GLW4](https://data.apps.fao.org/catalog//iso/9d1e149b-d63f-4213-978b-317a8eb42d02)
  (2020, 10 km, CC BY 4.0), zonal-averaged per division against the
  dissolved 7-division boundary (`data/external/bgd_adm1_wahis7.geojson`,
  built from [geoBoundaries](https://www.geoboundaries.org) ADM1, with
  Mymensingh merged back into Dhaka to match WAHIS's older 7-division
  scheme). This is a **single 2020 snapshot** applied to all years as a
  relative-exposure covariate, not a year-matched population — Bangladesh's
  poultry sector grew substantially over 2007-2025, so absolute headcounts
  from this layer should not be read as historical population estimates.
- **Merged dataset** (`scripts/12_build_modeling_dataset.py`): 266
  division-semester rows (7 divisions × 38 semesters, 2007-2025) combining
  outbreak counts + climate + poultry density, with explicit zero rows for
  semesters with no reported outbreaks (needed for count modeling, not just
  absent from the data) → `data/processed/hpai_modeling_dataset.csv`.

**Finding:** outbreaks are strongly seasonal, not primarily explained by
poultry density. 525 of 563 outbreaks (93%) fall in Jan-Jun (dry/cool)
semesters vs. 38 in Jul-Dec (monsoon/warm) — see Table 2
(`data/table2b_seasonal_split.csv`) and Figure 5. Correlation with chicken
density is negligible (r = 0.02); humidity (r = -0.21) and precipitation
(r = -0.19) are the stronger (still modest) associations, consistent with
the seasonal split rather than a separate climate effect — see
`data/table2_covariate_correlation.csv`.

**Modeling caveat:** `statsmodels` is broken in this environment (a scipy
version mismatch unrelated to this project — `ImportError: cannot import
name '_lazywhere' from 'scipy._lib._util'`), so Table 2 is Pearson
correlation on raw counts, not a fitted negative-binomial/zero-inflated
regression with division fixed effects as originally planned. Fix the
environment (`pip install -U scipy statsmodels`) or move modeling to R
(`MASS::glm.nb`) to take this further.

### If we need finer resolution than this later

Both WAHIS's and FAO EMPRES-i+'s public APIs are hardened against scripted
access (confirmed while building this repo — WAHIS sits behind Cloudflare
bot protection, EMPRES-i+ is a Flutter app with no discoverable open
endpoint), so pulling more requires the browser UI: WAHIS → **Analytics →
Quantitative data → Export data** (division/semester/species detail, as
above) or WAHIS → **Reports → Animal disease events** → open an event →
**Outbreaks** tab (exact coordinates, one outbreak at a time).

---

## Repository Structure

```
avian-influenza/
├── data/
│   ├── raw/                                        # Untouched source exports
│   ├── external/                                   # Downloaded boundaries + climate
│   │   ├── bgd_adm1_wahis7.geojson                 # 7-division boundary (Mymensingh merged into Dhaka)
│   │   ├── climate_daily_by_division.csv           # NASA POWER daily, pre-aggregation
│   │   └── glw4_2020_chicken_density_global.tif    # gitignored; re-downloaded by script 11
│   ├── processed/
│   │   ├── hpai_semester_status_bgd.csv            # Tier-1 semester table
│   │   ├── hpai_outbreaks_division_semester.csv     # Tier-2 outbreak counts
│   │   ├── hpai_species_quantitative.csv            # Tier-2 species-level counts
│   │   ├── hpai_event_reference.csv                 # 9 HPAI event/report IDs (provenance)
│   │   ├── hpai_event192_report_history.csv         # Event 192, near-monthly resolution
│   │   ├── climate_semester_by_division.csv         # NASA POWER climate, division x semester
│   │   ├── poultry_density_by_division.csv          # FAO GLW4 chicken density, per division
│   │   └── hpai_modeling_dataset.csv                # Merged outbreaks + climate + poultry
│   ├── table1_division_summary.csv                 # Table 1: division burden
│   ├── table2_covariate_correlation.csv            # Table 2: covariate correlations
│   └── table2b_seasonal_split.csv                  # Table 2b: dry vs. monsoon split
├── scripts/
│   ├── 01_clean_semester_data.py                   # Tier-1 export -> tidy CSV
│   ├── 02_semester_status_timeline.py              # Figure 1
│   ├── 03_clean_quantitative_outbreaks.py          # Tier-2 export -> tidy CSVs
│   ├── 04_division_outbreak_burden.py              # Figure 2
│   ├── 05_species_spillover_timeline.py            # Figure 3
│   ├── 06_table1_division_summary.py               # Table 1
│   ├── 07_clean_event_list.py                      # Event/report ID reference table
│   ├── 08_clean_event192_report_history.py         # Event 192 report history -> tidy CSV
│   ├── 09_event192_epidemic_curve.py               # Figure 4
│   ├── 10_fetch_climate_covariates.py              # NASA POWER climate by division
│   ├── 11_fetch_poultry_density.py                 # FAO GLW4 poultry density by division
│   ├── 12_build_modeling_dataset.py                # Merge outbreaks + covariates
│   ├── 13_table2_covariate_associations.py         # Table 2 + 2b
│   └── 14_climate_seasonality_figure.py            # Figure 5
├── figures/
│   ├── fig1_semester_status_timeline.png
│   ├── fig2_division_outbreak_burden.png
│   ├── fig3_species_spillover_timeline.png
│   ├── fig4_event192_epidemic_curve.png
│   └── fig5_climate_seasonality.png
└── paper/                                           # Manuscript files
```

## How to Reproduce

```bash
pip install -r requirements.txt
python scripts/01_clean_semester_data.py
python scripts/02_semester_status_timeline.py
python scripts/03_clean_quantitative_outbreaks.py
python scripts/04_division_outbreak_burden.py
python scripts/05_species_spillover_timeline.py
python scripts/06_table1_division_summary.py
python scripts/07_clean_event_list.py
python scripts/08_clean_event192_report_history.py
python scripts/09_event192_epidemic_curve.py
python scripts/10_fetch_climate_covariates.py     # network call, ~10-15s
python scripts/11_fetch_poultry_density.py        # downloads ~12 MB raster on first run
python scripts/12_build_modeling_dataset.py
python scripts/13_table2_covariate_associations.py
python scripts/14_climate_seasonality_figure.py
```

## License

Data: Public domain (WOAH WAHIS)
Code: MIT License
