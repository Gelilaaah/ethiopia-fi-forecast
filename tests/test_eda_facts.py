"""Tests for Task 2: sanity checks on key EDA facts derived from the enriched dataset."""
import os
import pandas as pd
import pytest

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed',
                          'ethiopia_fi_unified_data_enriched.csv')


@pytest.fixture(scope='module')
def obs():
    df = pd.read_csv(DATA_PATH)
    df['observation_date'] = pd.to_datetime(df['observation_date'])
    return df[df['record_type'] == 'observation']


def test_account_ownership_has_four_national_waves(obs):
    acc = obs[(obs['indicator_code'] == 'ACC_OWNERSHIP') & (obs['gender'] == 'all')]
    assert len(acc) == 4  # 2014, 2017, 2021, 2024


def test_account_ownership_growth_slowdown(obs):
    """The 2021-2024 wave-on-wave growth must be smaller than the 2017-2021 wave-on-wave growth --
    this is the central EDA finding and should not silently break if the dataset changes."""
    acc = obs[(obs['indicator_code'] == 'ACC_OWNERSHIP') & (obs['gender'] == 'all')].sort_values('observation_date')
    values = acc['value_numeric'].tolist()
    growth_2017_2021 = values[2] - values[1]
    growth_2021_2024 = values[3] - values[2]
    assert growth_2021_2024 < growth_2017_2021


def test_mobile_money_account_penetration_doubled(obs):
    mm = obs[obs['indicator_code'] == 'ACC_MM_ACCOUNT'].sort_values('observation_date')
    assert len(mm) == 2
    ratio = mm['value_numeric'].iloc[-1] / mm['value_numeric'].iloc[0]
    assert ratio > 1.5  # 4.7% -> 9.45% is roughly 2x


def test_gender_gap_narrowed(obs):
    gap = obs[obs['indicator_code'] == 'GEN_GAP_ACC'].sort_values('observation_date')
    assert gap['value_numeric'].iloc[-1] <= gap['value_numeric'].iloc[0]


def test_smartphone_gap_wider_than_account_gap(obs):
    """Central Section 2.2 finding: smartphone gender gap should exceed the account ownership gap."""
    smartphone_gap = obs[obs['indicator_code'] == 'GEN_GAP_SMARTPHONE']['value_numeric'].iloc[0]
    account_gap = obs[obs['indicator_code'] == 'GEN_GAP_ACC']['value_numeric'].iloc[-1]
    assert smartphone_gap > account_gap


def test_4g_coverage_exceeds_smartphone_penetration(obs):
    """Central Section 4 finding: infrastructure has outpaced device access."""
    coverage_4g = obs[obs['indicator_code'] == 'ACC_4G_COV']['value_numeric'].max()
    smartphone = obs[(obs['indicator_code'] == 'ACC_SMARTPHONE_PEN') & (obs['gender'] == 'all')]['value_numeric'].iloc[0]
    assert coverage_4g > smartphone


def test_p2p_transaction_count_grew(obs):
    p2p = obs[obs['indicator_code'] == 'USG_P2P_COUNT'].sort_values('observation_date')
    assert len(p2p) == 2
    assert p2p['value_numeric'].iloc[-1] > p2p['value_numeric'].iloc[0]


def test_mpesa_active_rate_consistent_with_sector_rate(obs):
    """M-Pesa's own registered/active ratio should roughly match the sector-wide activity rate --
    used in the EDA as a cross-validation check."""
    registered = obs[obs['indicator_code'] == 'USG_MPESA_USERS']['value_numeric'].iloc[0]
    active = obs[obs['indicator_code'] == 'USG_MPESA_ACTIVE']['value_numeric'].iloc[0]
    mpesa_rate = active / registered * 100

    sector_rate = obs[obs['indicator_code'] == 'USG_ACTIVE_RATE']['value_numeric'].iloc[0]
    assert abs(mpesa_rate - sector_rate) < 10  # within 10pp of each other
