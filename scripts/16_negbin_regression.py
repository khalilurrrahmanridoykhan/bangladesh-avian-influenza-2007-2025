"""
Table 3: Negative-binomial regression of HPAI outbreak counts on climate
covariates, with division fixed effects.

new_outbreaks ~ temp_mean_c + humidity_mean_pct + precip_total_mm + C(division)

Division fixed effects absorb any division-level confound (Dhaka's much
higher raw burden, for instance) so the climate coefficients reflect
within-division variation over time (i.e. seasonality), not cross-division
differences. Precipitation is rescaled per 100mm so its coefficient is on
an interpretable scale; temperature and humidity are left in their natural
(degC, %) units.

Chicken density is deliberately NOT included here: it is a single static
2020 value per division (see script 11), so it is perfectly collinear with
the division fixed effects -- a first attempt at
`... + chicken_density_per_1000 + C(division)` failed to converge with
implausible coefficients (e.g. exp(9.1) ~= 9,000x per 1000 head/km^2) for
exactly this reason. Its association with outbreak burden can only be
tested as a between-division comparison (7 units, no fixed effects) --
already reported descriptively in Table 2 (r = 0.02, negligible) and
Table 1 (division ranking); it is not re-estimated in this regression.
"""
import pandas as pd
import statsmodels.formula.api as smf
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "processed" / "hpai_modeling_dataset.csv"
OUT = Path(__file__).parent.parent / "data" / "table3_negbin_regression.csv"
OUT_SUMMARY = Path(__file__).parent.parent / "data" / "table3_negbin_regression_summary.txt"


def main():
    df = pd.read_csv(DATA, parse_dates=["period_start"])
    # pandas >=3.0 defaults to an Arrow-backed StringDtype for text columns,
    # which the installed patsy's categorical sniffer doesn't recognize --
    # cast back to plain object dtype for the formula API.
    df["division"] = df["division"].astype(object)
    df["precip_per_100mm"] = df["precip_total_mm"] / 100

    model = smf.negativebinomial(
        "new_outbreaks ~ temp_mean_c + humidity_mean_pct + precip_per_100mm + C(division)",
        data=df,
    )
    result = model.fit(method="bfgs", maxiter=500, disp=False)
    if not result.mle_retvals["converged"]:
        print("BFGS did not converge either; falling back to Newton with more iterations...")
        result = model.fit(method="newton", maxiter=200, disp=False)

    OUT_SUMMARY.write_text(str(result.summary()))
    print(result.summary())

    table = pd.DataFrame({
        "term": result.params.index,
        "coef": result.params.values,
        "irr": result.params.apply(lambda x: pd.NA).values,  # placeholder, filled below
        "std_err": result.bse.values,
        "p_value": result.pvalues.values,
        "ci_low": result.conf_int()[0].values,
        "ci_high": result.conf_int()[1].values,
    })
    import numpy as np
    table["irr"] = np.exp(table["coef"])
    # alpha is the NB dispersion parameter, not a log-rate coefficient --
    # exponentiating it as an "incidence rate ratio" would be meaningless.
    table.loc[table["term"] == "alpha", "irr"] = pd.NA
    table.to_csv(OUT, index=False)
    print(f"\nSaved -> {OUT}")
    print(f"Saved full summary -> {OUT_SUMMARY}")
    print(f"\nPseudo R-squared: {result.prsquared:.4f}")
    print(f"Log-likelihood: {result.llf:.2f}")
    print(f"AIC: {result.aic:.2f}")


if __name__ == "__main__":
    main()
