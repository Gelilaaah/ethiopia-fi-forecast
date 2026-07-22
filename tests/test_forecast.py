"""Tests for Task 4: forecasting logic (trend fitting, event augmentation, scenarios)."""
import os
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from impact_model import build_enriched_impact_links, apply_context_refinement
from forecast import fit_trend_with_ci, two_point_trend, event_augmented_forecast, build_scenarios

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed',
                          'ethiopia_fi_unified_data_enriched.csv')
FORECAST_YEARS = [2025, 2026, 2027]


@pytest.fixture(scope='module')
def dataset():
    df = pd.read_csv(DATA_PATH)
    df['observation_date'] = pd.to_datetime(df['observation_date'])
    return df


@pytest.fixture(scope='module')
def acc_ownership(dataset):
    obs = dataset[dataset['record_type'] == 'observation']
    return obs[(obs['indicator_code'] == 'ACC_OWNERSHIP') & (obs['gender'] == 'all')].sort_values('observation_date')


@pytest.fixture(scope='module')
def mm_account(dataset):
    obs = dataset[dataset['record_type'] == 'observation']
    return obs[obs['indicator_code'] == 'ACC_MM_ACCOUNT'].sort_values('observation_date')


@pytest.fixture(scope='module')
def enriched_links(dataset):
    impact_links = dataset[dataset['record_type'] == 'impact_link']
    events = dataset[dataset['record_type'] == 'event']
    return apply_context_refinement(build_enriched_impact_links(impact_links, events))


def test_trend_forecast_covers_all_years(acc_ownership):
    trend, _ = fit_trend_with_ci(acc_ownership['observation_date'], acc_ownership['value_numeric'], FORECAST_YEARS)
    assert list(trend['year']) == FORECAST_YEARS


def test_trend_forecast_is_increasing(acc_ownership):
    """Historical Access trend is upward; the extrapolation should continue that direction."""
    trend, _ = fit_trend_with_ci(acc_ownership['observation_date'], acc_ownership['value_numeric'], FORECAST_YEARS)
    assert trend['predicted'].is_monotonic_increasing


def test_ci_bounds_contain_predicted(acc_ownership):
    trend, _ = fit_trend_with_ci(acc_ownership['observation_date'], acc_ownership['value_numeric'], FORECAST_YEARS)
    assert (trend['ci_lower'] <= trend['predicted']).all()
    assert (trend['predicted'] <= trend['ci_upper']).all()


def test_two_point_trend_band_widens_with_horizon(mm_account):
    """Uncertainty band should widen for years further from the last observed data point."""
    trend = two_point_trend(mm_account['observation_date'], mm_account['value_numeric'], FORECAST_YEARS)
    band_widths = (trend['ci_upper'] - trend['ci_lower']).tolist()
    assert band_widths == sorted(band_widths)  # non-decreasing


def test_two_point_trend_continues_observed_direction(mm_account):
    trend = two_point_trend(mm_account['observation_date'], mm_account['value_numeric'], FORECAST_YEARS)
    last_observed = mm_account['value_numeric'].iloc[-1]
    assert trend['predicted'].iloc[0] > last_observed  # mobile money was growing


def test_event_augmented_never_decreases_below_trend_for_access(acc_ownership, enriched_links):
    """All impact_links on ACC_OWNERSHIP are 'increase' direction, so augmented should be >= trend."""
    trend, _ = fit_trend_with_ci(acc_ownership['observation_date'], acc_ownership['value_numeric'], FORECAST_YEARS)
    aug = event_augmented_forecast(trend, 'ACC_OWNERSHIP', enriched_links, '2024-11-29')
    assert (aug['event_augmented_predicted'] >= aug['trend_predicted']).all()


def test_mm_account_event_augmentation_is_near_zero(mm_account, enriched_links):
    """M-Pesa's only link to ACC_MM_ACCOUNT is already fully realized by 2024 -- marginal
    effect on 2025-2027 forecasts should be negligible."""
    trend = two_point_trend(mm_account['observation_date'], mm_account['value_numeric'], FORECAST_YEARS)
    aug = event_augmented_forecast(trend, 'ACC_MM_ACCOUNT', enriched_links, '2024-11-29')
    assert (aug['marginal_event_effect'].abs() < 0.1).all()


def test_scenarios_are_ordered(acc_ownership, enriched_links):
    """Optimistic >= base >= pessimistic must hold for every forecast year."""
    trend, _ = fit_trend_with_ci(acc_ownership['observation_date'], acc_ownership['value_numeric'], FORECAST_YEARS)
    scenarios = build_scenarios(trend, 'ACC_OWNERSHIP', enriched_links, '2024-11-29')
    assert (scenarios['optimistic'] >= scenarios['base']).all()
    assert (scenarios['base'] >= scenarios['pessimistic']).all()


def test_scenarios_never_negative(mm_account, enriched_links):
    trend = two_point_trend(mm_account['observation_date'], mm_account['value_numeric'], FORECAST_YEARS)
    scenarios = build_scenarios(trend, 'ACC_MM_ACCOUNT', enriched_links, '2024-11-29')
    assert (scenarios[['optimistic', 'base', 'pessimistic']] >= 0).all().all()


def test_nfis_target_not_met_under_base_scenario(acc_ownership, enriched_links):
    """Documents the headline Task 4 finding: base scenario misses the 70% NFIS-II target
    through 2027. This should fail loudly (not silently) if the underlying data/model changes
    enough to flip this conclusion, since it's the report's central claim."""
    trend, _ = fit_trend_with_ci(acc_ownership['observation_date'], acc_ownership['value_numeric'], FORECAST_YEARS)
    scenarios = build_scenarios(trend, 'ACC_OWNERSHIP', enriched_links, '2024-11-29')
    assert scenarios[scenarios['year'] == 2027]['base'].iloc[0] < 70
