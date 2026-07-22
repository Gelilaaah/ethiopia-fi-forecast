"""Tests for Task 5: Streamlit dashboard smoke tests.

Uses streamlit.testing.v1.AppTest to load the real app and drive its widgets
without a browser -- catches import errors, runtime exceptions, and broken
widget wiring across all 4 pages.
"""
import os
import pytest

streamlit_testing = pytest.importorskip("streamlit.testing.v1")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP_PATH = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'app.py')


def get_by_label(widgets, label):
    for w in widgets:
        if w.label == label:
            return w
    raise ValueError(f"No widget with label {label!r} found")


def navigate(at, page_name):
    get_by_label(at.radio, "Navigate").set_value(page_name).run(timeout=30)
    return at


def test_app_loads_without_exception():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=30)
    assert not at.exception


def test_overview_page_has_metrics():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=30)
    assert len(at.metric) >= 4  # at least 4 key metric cards


@pytest.mark.parametrize("page_name", ["Overview", "Trends", "Forecasts", "Inclusion Projections"])
def test_each_page_loads_without_exception(page_name):
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=30)
    navigate(at, page_name)
    assert not at.exception


def test_trends_page_multiselect_interaction():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=30)
    navigate(at, "Trends")
    ms = get_by_label(at.multiselect, "Select indicator(s) to plot")
    assert len(ms.options) > 0
    ms.set_value(['ACC_OWNERSHIP', 'ACC_MM_ACCOUNT']).run(timeout=30)
    assert not at.exception


def test_trends_page_empty_selection_shows_warning_not_error():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=30)
    navigate(at, "Trends")
    get_by_label(at.multiselect, "Select indicator(s) to plot").set_value([]).run(timeout=30)
    assert not at.exception
    assert len(at.warning) >= 1


def test_forecasts_page_target_and_model_switch():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=30)
    navigate(at, "Forecasts")
    get_by_label(at.selectbox, "Forecast target").set_value(
        "Usage proxy \u2014 Mobile Money Account Ownership"
    ).run(timeout=30)
    assert not at.exception
    get_by_label(at.radio, "Model").set_value("Event-augmented").run(timeout=30)
    assert not at.exception


def test_inclusion_projections_scenario_slider():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=30)
    navigate(at, "Inclusion Projections")
    slider = get_by_label(at.select_slider, "Scenario")
    for value in ["Pessimistic", "Base", "Optimistic"]:
        slider.set_value(value).run(timeout=30)
        assert not at.exception


def test_download_buttons_present_on_trends_and_projections():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=30)
    navigate(at, "Trends")
    assert len(at.get('download_button')) >= 1

    at2 = AppTest.from_file(APP_PATH)
    at2.run(timeout=30)
    navigate(at2, "Inclusion Projections")
    assert len(at2.get('download_button')) >= 1


def test_at_least_four_interactive_charts_across_dashboard():
    """Technical requirement: at least 4 interactive visualizations."""
    total_charts = 0
    for page_name in ["Overview", "Trends", "Forecasts", "Inclusion Projections"]:
        at = AppTest.from_file(APP_PATH)
        at.run(timeout=30)
        navigate(at, page_name)
        charts = at.get('plotly_chart')
        total_charts += len(charts) if charts else 0
    assert total_charts >= 4
