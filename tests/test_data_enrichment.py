"""Tests for Task 1: data loading and enrichment integrity."""
import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from enrich_data import build_new_records, COLUMNS

RAW_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'ethiopia_fi_unified_data.csv')
REF_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'reference_codes.csv')


@pytest.fixture(scope='module')
def base_df():
    return pd.read_csv(RAW_PATH)


@pytest.fixture(scope='module')
def ref_df():
    return pd.read_csv(REF_PATH)


@pytest.fixture(scope='module')
def new_records():
    return build_new_records()


def test_raw_files_load(base_df, ref_df):
    assert len(base_df) == 57
    assert len(ref_df) > 0


def test_base_record_type_counts(base_df):
    counts = base_df['record_type'].value_counts()
    assert counts['observation'] == 30
    assert counts['event'] == 10
    assert counts['target'] == 3
    assert counts['impact_link'] == 14


def test_new_records_have_all_columns(new_records):
    assert list(new_records.columns) == COLUMNS


def test_new_records_no_duplicate_ids(new_records):
    assert new_records['record_id'].duplicated().sum() == 0


def test_enriched_dataset_no_duplicate_ids(base_df, new_records):
    enriched = pd.concat([base_df, new_records], ignore_index=True)
    assert enriched['record_id'].duplicated().sum() == 0


def test_all_impact_link_parents_resolve(base_df, new_records):
    enriched = pd.concat([base_df, new_records], ignore_index=True)
    event_ids = set(enriched[enriched['record_type'] == 'event']['record_id'])
    impact_links = enriched[enriched['record_type'] == 'impact_link']
    orphans = impact_links[~impact_links['parent_id'].isin(event_ids)]
    assert len(orphans) == 0, f"Orphaned impact_links: {orphans['record_id'].tolist()}"


def test_new_events_have_no_pillar(new_records):
    """Per schema design: events must not have a pre-assigned pillar."""
    new_events = new_records[new_records['record_type'] == 'event']
    assert new_events['pillar'].isna().all()


def test_new_events_have_category(new_records):
    new_events = new_records[new_records['record_type'] == 'event']
    assert new_events['category'].notna().all()


def test_confidence_values_are_valid(new_records, ref_df):
    valid_confidence = set(ref_df[ref_df['field'] == 'confidence']['code'])
    used = new_records['confidence'].dropna().unique()
    for c in used:
        assert c in valid_confidence, f"Invalid confidence value: {c}"


def test_pillar_values_are_valid(new_records, ref_df):
    valid_pillars = set(ref_df[ref_df['field'] == 'pillar']['code'])
    used = new_records['pillar'].dropna().unique()
    for p in used:
        assert p in valid_pillars, f"Invalid pillar value: {p}"


def test_event_category_values_are_valid(new_records, ref_df):
    valid_categories = set(ref_df[(ref_df['field'] == 'category')]['code'])
    used = new_records[new_records['record_type'] == 'event']['category'].dropna().unique()
    for c in used:
        assert c in valid_categories, f"Invalid event category: {c}"


def test_nfis_ii_now_has_impact_link(base_df, new_records):
    """EVT_0009 (NFIS-II) had zero impact_links in the base dataset; enrichment should add one."""
    enriched = pd.concat([base_df, new_records], ignore_index=True)
    links = enriched[(enriched['record_type'] == 'impact_link') & (enriched['parent_id'] == 'EVT_0009')]
    assert len(links) >= 1
