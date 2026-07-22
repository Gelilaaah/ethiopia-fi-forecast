"""
Task 4: Forecasting Access and Usage

FORECAST TARGETS AND A DATA-DRIVEN SCOPING DECISION
----------------------------------------------------
- ACCESS  -> ACC_OWNERSHIP: 4 Findex-sourced points (2014, 2017, 2021, 2024). Enough for a
  real (if wide) trend regression.
- USAGE   -> the brief's literal target, USG_DIGITAL_PAYMENT (Findex "made or received a
  digital payment"), has only ONE historical point in this dataset (2021, split by gender,
  no 'all' value, no 2024 update) -- mathematically impossible to fit any trend to a single
  point. Rather than silently forecasting off one number, we forecast ACC_MM_ACCOUNT
  (mobile money account ownership) as the primary Usage proxy instead:
    (a) it has two clean Findex-sourced points (2021, 2024), just enough for a trend line,
    (b) it's the Usage-adjacent indicator most tightly connected to Ethiopia's actual
        digital-payment behavior, per the Market Nuances guide (P2P dominance, mobile-
        money-only users are rare -- most Usage IS mobile money usage here).
  This substitution is documented prominently in the forecasting notebook, not hidden.

METHODOLOGY
-----------
Two models are built and compared for each target, per the challenge brief:

1. BASELINE (trend-only): OLS regression of value ~ year, extrapolated to 2025-2027.
   With only 2-4 historical points, prediction intervals are wide by construction --
   this is treated as correct (appropriately wide uncertainty), not a bug to fix.
   ACC_MM_ACCOUNT has only 2 points (0 residual degrees of freedom), so no statistical
   CI is possible there; a judgment-based scenario band is used instead (see below).

2. EVENT-AUGMENTED: baseline trend + the MARGINAL (not-yet-realized-as-of-last-data-point)
   portion of each relevant impact_link's effect. Already-realized effects (as of the last
   Findex survey date) are treated as already "baked into" the historical trend -- adding
   their full effect again would double-count. Only the incremental realization between the
   last data point and each forecast year is added on top of the trend line.

SCENARIOS
---------
- Optimistic: event-driven effects reach 100% of their modeled magnitude on schedule.
- Base:       event-driven effects reach 100% of their modeled magnitude (using the
              Task-3-refined, historically-validated magnitudes).
- Pessimistic: enabling-relationship effects (the least-validated category -- see Task 3)
              only reach 50% of their modeled magnitude, reflecting implementation risk
              (e.g. NFIS-II / Fayda rollout delays).
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm


def fit_trend_with_ci(dates: pd.Series, values: pd.Series, forecast_years: list, alpha: float = 0.2):
    """
    OLS linear trend (value ~ year), extrapolated to forecast_years with prediction intervals.
    Returns a DataFrame with columns: year, predicted, ci_lower, ci_upper.
    alpha=0.2 -> 80% prediction interval (chosen deliberately wide given tiny n; see module docstring).
    """
    years = pd.to_datetime(dates).dt.year.values.astype(float)
    y = values.values.astype(float)

    X = sm.add_constant(years)
    model = sm.OLS(y, X).fit()

    X_future = sm.add_constant(np.array(forecast_years, dtype=float), has_constant='add')
    pred = model.get_prediction(X_future)
    summary = pred.summary_frame(alpha=alpha)

    return pd.DataFrame({
        'year': forecast_years,
        'predicted': summary['mean'].values,
        'ci_lower': summary['obs_ci_lower'].values,
        'ci_upper': summary['obs_ci_upper'].values,
    }), model


def two_point_trend(dates: pd.Series, values: pd.Series, forecast_years: list, judgment_band_pct: float = 0.35):
    """
    For indicators with only 2 historical points (0 residual df -- no statistical CI possible).
    Fits the line through both points exactly, extrapolates, and applies a judgment-based
    +/- percentage band that WIDENS with distance from the last observed point (more distant
    forecasts are more uncertain). This is explicitly a heuristic, not a statistical interval.
    """
    years = pd.to_datetime(dates).dt.year.values.astype(float)
    y = values.values.astype(float)
    last_year, last_value = years[-1], y[-1]

    slope = (y[-1] - y[0]) / (years[-1] - years[0])

    rows = []
    for i, fy in enumerate(forecast_years, start=1):
        predicted = last_value + slope * (fy - last_year)
        band = predicted * judgment_band_pct * (1 + 0.15 * (i - 1))  # widen ~15% per additional year out
        rows.append({'year': fy, 'predicted': predicted,
                      'ci_lower': max(0, predicted - band), 'ci_upper': predicted + band})
    return pd.DataFrame(rows)


def event_augmented_forecast(trend_df: pd.DataFrame, indicator_code: str, enriched_links: pd.DataFrame,
                              last_data_date: str, realization_multiplier: float = 1.0,
                              enabling_multiplier: float = 1.0, effect_column: str = 'refined_effect') -> pd.DataFrame:
    """
    Add the marginal (not-yet-realized-as-of-last_data_date) portion of each relevant
    impact_link's effect on top of a trend forecast, for each forecast year.

    realization_multiplier scales ALL effects (used for optimistic/pessimistic scenarios).
    enabling_multiplier scales only 'enabling' relationship_type effects (the least-validated
    category), used to model implementation risk independently of direct/indirect effects.
    """
    from impact_model import effect_realized_fraction, months_between

    relevant = enriched_links[enriched_links['related_indicator'] == indicator_code].copy()
    if effect_column not in relevant.columns:
        effect_column = 'full_effect'

    out_rows = []
    for _, trow in trend_df.iterrows():
        forecast_date = f"{int(trow['year'])}-12-31"
        marginal_total = 0.0

        for _, erow in relevant.iterrows():
            t_last = months_between(erow['event_date'], last_data_date)
            t_future = months_between(erow['event_date'], forecast_date)

            frac_last = effect_realized_fraction(t_last, erow['lag_months'])
            frac_future = effect_realized_fraction(t_future, erow['lag_months'])
            marginal_frac = max(0.0, frac_future - frac_last)  # only the NEW realization since last data point

            scale = realization_multiplier
            if erow['relationship_type'] == 'enabling':
                scale *= enabling_multiplier

            marginal_total += erow[effect_column] * marginal_frac * scale

        out_rows.append({
            'year': trow['year'],
            'trend_predicted': trow['predicted'],
            'marginal_event_effect': marginal_total,
            'event_augmented_predicted': trow['predicted'] + marginal_total,
        })

    return pd.DataFrame(out_rows)


def build_scenarios(trend_df: pd.DataFrame, indicator_code: str, enriched_links: pd.DataFrame,
                     last_data_date: str, effect_column: str = 'refined_effect') -> pd.DataFrame:
    """
    Combine trend uncertainty (CI bounds) with event-realization risk (enabling-effect multiplier)
    into three named scenarios per forecast year:
      - Optimistic:  trend's upper CI bound + full (100%) event effect realization
      - Base:        trend's point estimate + full (100%) event effect realization
      - Pessimistic: trend's lower CI bound + enabling-relationship effects only 50% realized
                     (reflecting implementation risk -- policy/ID rollouts slipping)
    """
    from impact_model import effect_realized_fraction, months_between

    relevant = enriched_links[enriched_links['related_indicator'] == indicator_code].copy()
    if effect_column not in relevant.columns:
        effect_column = 'full_effect'

    def marginal_effect(forecast_date, enabling_mult):
        total = 0.0
        for _, erow in relevant.iterrows():
            t_last = months_between(erow['event_date'], last_data_date)
            t_future = months_between(erow['event_date'], forecast_date)
            frac_last = effect_realized_fraction(t_last, erow['lag_months'])
            frac_future = effect_realized_fraction(t_future, erow['lag_months'])
            marginal_frac = max(0.0, frac_future - frac_last)
            mult = enabling_mult if erow['relationship_type'] == 'enabling' else 1.0
            total += erow[effect_column] * marginal_frac * mult
        return total

    rows = []
    for _, trow in trend_df.iterrows():
        forecast_date = f"{int(trow['year'])}-12-31"
        full_effect = marginal_effect(forecast_date, enabling_mult=1.0)
        half_enabling_effect = marginal_effect(forecast_date, enabling_mult=0.5)

        rows.append({
            'year': trow['year'],
            'optimistic': trow['ci_upper'] + full_effect,
            'base': trow['predicted'] + full_effect,
            'pessimistic': max(0, trow['ci_lower'] + half_enabling_effect),
        })
    return pd.DataFrame(rows)
