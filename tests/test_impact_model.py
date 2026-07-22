"""Tests for Task 3: event impact modeling logic and historical validation results."""
import os
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from impact_model import (
    build_enriched_impact_links, build_association_matrix, predict_indicator_change,
    apply_context_refinement, effect_realized_fraction, indicator_scale, months_between
)

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed',
                          'ethiopia_fi_unified_data_enriched.csv')


@pytest.fixture(scope='module')
def enriched():
    df = pd.read_csv(DATA_PATH)
    impact_links = df[df['record_type'] == 'impact_link']
    events = df[df['record_type'] == 'event']
    return build_enriched_impact_links(impact_links, events)


def test_effect_realized_fraction_is_zero_before_event():
    assert effect_realized_fraction(-5, 12) == 0.0
    assert effect_realized_fraction(0, 12) == 0.0


def test_effect_realized_fraction_is_monotonic_increasing():
    fractions = [effect_realized_fraction(m, 12) for m in [1, 6, 12, 24, 48]]
    assert fractions == sorted(fractions)


def test_effect_realized_fraction_near_full_at_lag_months():
    frac = effect_realized_fraction(12, 12)
    assert frac > 0.9


def test_effect_realized_fraction_half_at_midpoint():
    frac = effect_realized_fraction(6, 12)
    assert 0.45 < frac < 0.55


def test_indicator_scale_classification():
    assert indicator_scale('ACC_OWNERSHIP') == 'pp'
    assert indicator_scale('GEN_GAP_ACC') == 'pp'
    assert indicator_scale('USG_P2P_COUNT') == 'relative'


def test_months_between():
    assert abs(months_between('2021-05-17', '2022-05-17') - 12) < 0.5


def test_enriched_links_have_no_orphaned_events(enriched):
    assert enriched['event_name'].isna().sum() == 0


def test_association_matrix_shape(enriched):
    matrix = build_association_matrix(enriched)
    assert matrix.shape[0] == enriched['event_name'].nunique()
    assert matrix.shape[1] == enriched['related_indicator'].nunique()


def test_acc_mm_account_validation_close_to_actual(enriched):
    """M-Pesa's link to ACC_MM_ACCOUNT should predict within 2pp of the actual +4.75pp change."""
    result = predict_indicator_change('ACC_MM_ACCOUNT', '2024-11-29', enriched)
    assert abs(result['combined_effect'] - 4.75) < 2.0


def test_acc_ownership_raw_model_overshoots(enriched):
    """Documents the known validation gap: raw model should over-predict actual +3pp change."""
    result = predict_indicator_change('ACC_OWNERSHIP', '2024-11-29', enriched)
    assert result['combined_effect'] > 3.0 * 2  # more than double the actual


def test_refinement_reduces_acc_ownership_overshoot(enriched):
    """The context refinement should bring the ACC_OWNERSHIP prediction closer to actual (+3pp)
    without eliminating it entirely (avoid overfitting to n=1)."""
    raw = predict_indicator_change('ACC_OWNERSHIP', '2024-11-29', enriched, effect_column='full_effect')
    refined_links = apply_context_refinement(enriched)
    refined = predict_indicator_change('ACC_OWNERSHIP', '2024-11-29', refined_links, effect_column='refined_effect')

    assert refined['combined_effect'] < raw['combined_effect']
    assert refined['combined_effect'] > 3.0  # still not a perfect (overfit) match


def test_refinement_does_not_affect_acc_mm_account(enriched):
    """The refinement is scoped to ACC_OWNERSHIP only -- ACC_MM_ACCOUNT should be unchanged."""
    refined_links = apply_context_refinement(enriched)
    raw_mm = predict_indicator_change('ACC_MM_ACCOUNT', '2024-11-29', enriched, effect_column='full_effect')
    refined_mm = predict_indicator_change('ACC_MM_ACCOUNT', '2024-11-29', refined_links, effect_column='refined_effect')
    assert abs(raw_mm['combined_effect'] - refined_mm['combined_effect']) < 1e-6
