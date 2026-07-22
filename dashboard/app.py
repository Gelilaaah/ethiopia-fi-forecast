"""
Ethiopia Financial Inclusion Forecast — Interactive Dashboard
10 Academy KAIM Week 11 Challenge — Selam Analytics

Run from the repo root:
    streamlit run dashboard/app.py
"""
import os
import sys
from datetime import date

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# --- Path setup: make this work regardless of the working directory it's launched from ---
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(DASHBOARD_DIR)
SRC_DIR = os.path.join(REPO_ROOT, 'src')
DATA_DIR = os.path.join(REPO_ROOT, 'data', 'processed')

sys.path.insert(0, SRC_DIR)
from impact_model import build_enriched_impact_links, apply_context_refinement, build_association_matrix  # noqa: E402
from forecast import fit_trend_with_ci, two_point_trend, build_scenarios  # noqa: E402

st.set_page_config(
    page_title="Ethiopia Financial Inclusion Forecast",
    page_icon="\U0001F4B8",
    layout="wide",
)

FORECAST_YEARS = [2025, 2026, 2027]
LAST_DATA_DATE = "2024-11-29"

COLORS = {
    'teal': '#2A9D8F', 'orange': '#F4A261', 'red': '#E76F51',
    'dark': '#264653', 'blue': '#457B9D', 'yellow': '#E9C46A',
}


# ---------------------------------------------------------------------------
# Data loading (cached)
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, 'ethiopia_fi_unified_data_enriched.csv'))
    df['observation_date'] = pd.to_datetime(df['observation_date'], errors='coerce')

    obs = df[df['record_type'] == 'observation'].copy()
    events = df[df['record_type'] == 'event'].copy()
    impact_links = df[df['record_type'] == 'impact_link'].copy()
    targets = df[df['record_type'] == 'target'].copy()

    enriched_links = apply_context_refinement(build_enriched_impact_links(impact_links, events))

    return df, obs, events, impact_links, targets, enriched_links


@st.cache_data
def compute_forecasts(_obs, _enriched_links):
    """Recompute forecasts live using the same src/forecast.py logic as the notebooks
    (single source of truth -- the dashboard is never out of sync with the analysis)."""
    acc = _obs[(_obs['indicator_code'] == 'ACC_OWNERSHIP') & (_obs['gender'] == 'all')].sort_values('observation_date')
    mm = _obs[_obs['indicator_code'] == 'ACC_MM_ACCOUNT'].sort_values('observation_date')

    acc_trend, acc_model = fit_trend_with_ci(acc['observation_date'], acc['value_numeric'], FORECAST_YEARS)
    mm_trend = two_point_trend(mm['observation_date'], mm['value_numeric'], FORECAST_YEARS)

    acc_scenarios = build_scenarios(acc_trend, 'ACC_OWNERSHIP', _enriched_links, LAST_DATA_DATE)
    mm_scenarios = build_scenarios(mm_trend, 'ACC_MM_ACCOUNT', _enriched_links, LAST_DATA_DATE)

    return {
        'acc_historical': acc, 'mm_historical': mm,
        'acc_trend': acc_trend, 'mm_trend': mm_trend,
        'acc_scenarios': acc_scenarios, 'mm_scenarios': mm_scenarios,
    }


df, obs, events, impact_links, targets, enriched_links = load_data()
forecasts = compute_forecasts(obs, enriched_links)


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
st.sidebar.title("\U0001F1EA\U0001F1F9 Ethiopia FI Forecast")
st.sidebar.caption("Selam Analytics — 10 Academy KAIM Week 11")
page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Trends", "Forecasts", "Inclusion Projections"],
    label_visibility="collapsed",
)
st.sidebar.divider()
st.sidebar.caption(
    "Data: enriched Ethiopia Financial Inclusion dataset (77 records) — Global Findex, "
    "NBE, GSMA, AfricaNenda SIIPS 2025, and 10 Academy starter data."
)


def metric_card(col, label, value, delta=None, help_text=None):
    col.metric(label, value, delta=delta, help=help_text)


# ---------------------------------------------------------------------------
# PAGE 1: Overview
# ---------------------------------------------------------------------------
if page == "Overview":
    st.title("Ethiopia Financial Inclusion — Overview")
    st.markdown(
        "Tracking Ethiopia's progress on the two Global Findex pillars of financial "
        "inclusion — **Access** (account ownership) and **Usage** (digital payments) — "
        "against the National Financial Inclusion Strategy II (NFIS-II) targets."
    )

    acc_latest = obs[(obs['indicator_code'] == 'ACC_OWNERSHIP') & (obs['gender'] == 'all')].sort_values('observation_date').iloc[-1]
    acc_prev = obs[(obs['indicator_code'] == 'ACC_OWNERSHIP') & (obs['gender'] == 'all')].sort_values('observation_date').iloc[-2]
    mm_latest = obs[obs['indicator_code'] == 'ACC_MM_ACCOUNT'].sort_values('observation_date').iloc[-1]
    mm_prev = obs[obs['indicator_code'] == 'ACC_MM_ACCOUNT'].sort_values('observation_date').iloc[-2]
    crossover = obs[obs['indicator_code'] == 'USG_CROSSOVER'].sort_values('observation_date').iloc[-1]
    smartphone = obs[(obs['indicator_code'] == 'ACC_SMARTPHONE_PEN') & (obs['gender'] == 'all')].iloc[-1]

    c1, c2, c3, c4 = st.columns(4)
    metric_card(c1, "Account Ownership (2024)", f"{acc_latest['value_numeric']:.0f}%",
                delta=f"+{acc_latest['value_numeric'] - acc_prev['value_numeric']:.0f}pp since 2021",
                help_text="Findex-defined: adults with an account at a financial institution or mobile money")
    metric_card(c2, "Mobile Money Accounts (2024)", f"{mm_latest['value_numeric']:.2f}%",
                delta=f"+{mm_latest['value_numeric'] - mm_prev['value_numeric']:.2f}pp since 2021",
                help_text="Subset of Access; Findex-defined mobile money account ownership")
    metric_card(c3, "P2P / ATM Crossover Ratio", f"{crossover['value_numeric']:.2f}",
                delta="P2P now exceeds ATM withdrawal value" if crossover['value_numeric'] > 1 else "ATM still dominant",
                help_text="Ratio of P2P mobile transaction value to ATM cash withdrawal value. >1.0 means digital transfers have overtaken cash withdrawals in value.")
    metric_card(c4, "Smartphone Penetration (2025)", f"{smartphone['value_numeric']:.0f}%",
                delta="vs. 70.8% 4G coverage — the adoption gap",
                help_text="Only 15% of adults own a smartphone despite far higher network coverage")

    st.divider()

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Growth per Findex survey wave")
        acc_hist = forecasts['acc_historical'].copy()
        acc_hist['year'] = acc_hist['observation_date'].dt.year
        acc_hist['pp_change'] = acc_hist['value_numeric'].diff()
        growth = acc_hist.dropna(subset=['pp_change'])
        growth_labels = [f"{int(r['year'] - (4 if i==0 else (3 if i==1 else 3)))}\u2013{int(r['year'])}"
                          for i, (_, r) in enumerate(growth.iterrows())]
        fig = go.Figure(go.Bar(
            x=growth_labels, y=growth['pp_change'],
            marker_color=[COLORS['teal'], COLORS['teal'], COLORS['red']],
            text=[f"+{v:.0f}pp" for v in growth['pp_change']], textposition='outside',
        ))
        fig.update_layout(yaxis_title="Percentage point change", height=350,
                           margin=dict(t=20, b=20))
        st.plotly_chart(fig, width='stretch')
        st.caption(
            "Growth slowed sharply in the most recent wave (2021\u20132024, +3pp) despite "
            "Telebirr, Safaricom, and M-Pesa all launching in that window \u2014 see the "
            "**Trends** page for why."
        )

    with col_right:
        st.subheader("Progress toward NFIS-II target")
        nfis_target = targets[targets['indicator_code'] == 'ACC_OWNERSHIP']['value_numeric'].iloc[0]
        progress_pct = acc_latest['value_numeric'] / nfis_target * 100
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=acc_latest['value_numeric'],
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': COLORS['teal']},
                'steps': [
                    {'range': [0, nfis_target], 'color': '#f0f0f0'},
                    {'range': [nfis_target, 100], 'color': '#e8f6f4'},
                ],
                'threshold': {'line': {'color': COLORS['red'], 'width': 4},
                              'thickness': 0.85, 'value': nfis_target},
            },
            title={'text': f"Account Ownership vs. {nfis_target:.0f}% NFIS-II target"},
        ))
        fig.update_layout(height=350, margin=dict(t=60, b=20))
        st.plotly_chart(fig, width='stretch')
        st.caption(f"Currently at {progress_pct:.0f}% of the target. See **Inclusion Projections** for the full 2025-2027 trajectory.")

    st.divider()
    st.subheader("Key business questions this dashboard answers")
    q1, q2, q3 = st.columns(3)
    q1.info("**What drives financial inclusion in Ethiopia?**\n\nSee the *Trends* page for the event timeline and the underlying data patterns.")
    q2.info("**How do policies and product launches affect outcomes?**\n\nSee the *Forecasts* page for the event-indicator association matrix and validated impact estimates.")
    q3.info("**How will Access and Usage look in 2026 and 2027?**\n\nSee the *Inclusion Projections* page for scenario-based forecasts.")


# ---------------------------------------------------------------------------
# PAGE 2: Trends
# ---------------------------------------------------------------------------
elif page == "Trends":
    st.title("Trends")
    st.markdown("Explore the historical time series behind Ethiopia's financial inclusion story, with events overlaid.")

    indicator_options = (
        obs[obs['gender'] == 'all']
        .groupby('indicator_code')
        .filter(lambda g: len(g) >= 1)['indicator_code']
        .unique()
    )
    indicator_labels = {
        code: obs[obs['indicator_code'] == code]['indicator'].iloc[0] for code in indicator_options
    }

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_indicators = st.multiselect(
            "Select indicator(s) to plot",
            options=sorted(indicator_options, key=lambda c: indicator_labels[c]),
            format_func=lambda c: f"{indicator_labels[c]} ({c})",
            default=['ACC_OWNERSHIP'] if 'ACC_OWNERSHIP' in indicator_options else list(indicator_options[:1]),
        )
    with col2:
        show_events = st.checkbox("Overlay events", value=True)

    min_year, max_year = int(obs['observation_date'].dt.year.min()), int(obs['observation_date'].dt.year.max())
    year_range = st.slider("Date range", min_year, max_year, (min_year, max_year))

    if selected_indicators:
        fig = go.Figure()
        palette = px.colors.qualitative.Set2
        for i, code in enumerate(selected_indicators):
            series = obs[(obs['indicator_code'] == code) & (obs['gender'] == 'all')].sort_values('observation_date')
            if series.empty:
                series = obs[obs['indicator_code'] == code].sort_values('observation_date')
            series = series[
                (series['observation_date'].dt.year >= year_range[0]) &
                (series['observation_date'].dt.year <= year_range[1])
            ]
            if series.empty:
                continue
            fig.add_trace(go.Scatter(
                x=series['observation_date'], y=series['value_numeric'],
                mode='lines+markers', name=indicator_labels[code],
                line=dict(width=3, color=palette[i % len(palette)]), marker=dict(size=9),
            ))

        if show_events:
            visible_events = events[
                (events['observation_date'].dt.year >= year_range[0]) &
                (events['observation_date'].dt.year <= year_range[1])
            ]
            for _, ev in visible_events.iterrows():
                fig.add_vline(x=ev['observation_date'].timestamp() * 1000, line_dash="dot",
                              line_color="gray", opacity=0.5)

        fig.update_layout(height=500, hovermode='x unified',
                           yaxis_title="Value", margin=dict(t=20))
        st.plotly_chart(fig, width='stretch')

        if show_events:
            st.caption("Dotted lines mark events (product launches, policy changes, infrastructure milestones) in the selected date range.")
    else:
        st.warning("Select at least one indicator above to see a chart.")

    st.divider()
    st.subheader("Channel comparison: registered users by provider")
    reg_data = obs[obs['indicator_code'].isin(['USG_TELEBIRR_USERS', 'USG_MPESA_USERS', 'USG_MPESA_ACTIVE'])]
    if not reg_data.empty:
        fig2 = px.bar(
            reg_data, x='indicator', y='value_numeric', color='indicator',
            labels={'value_numeric': 'Users', 'indicator': ''},
            color_discrete_sequence=[COLORS['teal'], COLORS['orange'], COLORS['red']],
        )
        fig2.update_layout(height=380, showlegend=False, margin=dict(t=20))
        st.plotly_chart(fig2, width='stretch')
        st.caption(
            "Registered users vastly overstate real Findex-comparable inclusion — see the "
            "M-Pesa registered-vs-active gap (10.8M \u2192 7.1M, 65.7% active rate)."
        )

    with st.expander("Download underlying data"):
        st.dataframe(obs[['record_id', 'pillar', 'indicator', 'indicator_code', 'value_numeric',
                           'unit', 'observation_date', 'gender', 'confidence']], width='stretch')
        csv = obs.to_csv(index=False).encode('utf-8')
        st.download_button("Download observations as CSV", csv, "observations.csv", "text/csv")


# ---------------------------------------------------------------------------
# PAGE 3: Forecasts
# ---------------------------------------------------------------------------
elif page == "Forecasts":
    st.title("Forecasts")
    st.markdown(
        "Two models are compared for each target: a **trend-only baseline** and an "
        "**event-augmented model** built on Task 3's validated event-impact estimates."
    )

    target_choice = st.selectbox(
        "Forecast target",
        ["Access — Account Ownership", "Usage proxy — Mobile Money Account Ownership"],
    )
    model_choice = st.radio("Model", ["Trend-only baseline", "Event-augmented"], horizontal=True)

    is_access = target_choice.startswith("Access")
    hist = forecasts['acc_historical'] if is_access else forecasts['mm_historical']
    trend = forecasts['acc_trend'] if is_access else forecasts['mm_trend']
    scenarios = forecasts['acc_scenarios'] if is_access else forecasts['mm_scenarios']
    indicator_code = 'ACC_OWNERSHIP' if is_access else 'ACC_MM_ACCOUNT'

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist['observation_date'].dt.year, y=hist['value_numeric'],
                              mode='lines+markers', name='Historical (Findex)',
                              line=dict(color=COLORS['dark'], width=3), marker=dict(size=10)))

    if model_choice == "Trend-only baseline":
        fig.add_trace(go.Scatter(x=trend['year'], y=trend['ci_upper'], mode='lines',
                                  line=dict(width=0), showlegend=False, hoverinfo='skip'))
        fig.add_trace(go.Scatter(x=trend['year'], y=trend['ci_lower'], mode='lines',
                                  fill='tonexty', fillcolor='rgba(231,111,81,0.15)',
                                  line=dict(width=0), name='Uncertainty band'))
        fig.add_trace(go.Scatter(x=trend['year'], y=trend['predicted'], mode='lines+markers',
                                  name='Trend forecast', line=dict(color=COLORS['red'], dash='dash', width=3),
                                  marker=dict(size=9)))
    else:
        fig.add_trace(go.Scatter(x=scenarios['year'], y=scenarios['optimistic'], mode='lines+markers',
                                  name='Optimistic', line=dict(color=COLORS['teal'], width=2)))
        fig.add_trace(go.Scatter(x=scenarios['year'], y=scenarios['base'], mode='lines+markers',
                                  name='Base (event-augmented)', line=dict(color=COLORS['orange'], width=3)))
        fig.add_trace(go.Scatter(x=scenarios['year'], y=scenarios['pessimistic'], mode='lines+markers',
                                  name='Pessimistic', line=dict(color=COLORS['red'], width=2)))

    if is_access:
        nfis_target = targets[targets['indicator_code'] == 'ACC_OWNERSHIP']['value_numeric'].iloc[0]
        fig.add_hline(y=nfis_target, line_dash="dot", line_color="gray",
                      annotation_text=f"NFIS-II target: {nfis_target:.0f}%")

    fig.update_layout(height=480, yaxis_title="%", margin=dict(t=20), hovermode='x unified')
    st.plotly_chart(fig, width='stretch')

    st.divider()
    st.subheader("Event \u2192 indicator association matrix")
    assoc_matrix = build_association_matrix(enriched_links)
    fig_heat = px.imshow(
        assoc_matrix, text_auto='.1f', color_continuous_scale='RdBu_r', color_continuous_midpoint=0,
        aspect='auto', labels=dict(color="Estimated effect"),
    )
    fig_heat.update_layout(height=450, margin=dict(t=20))
    st.plotly_chart(fig_heat, width='stretch')
    st.caption(
        "Rows = events, columns = indicators they're modeled to affect. Read column-by-column — "
        "values mix percentage-point (Access/Gender) and relative-fraction (Usage counts/ratios) "
        "scales. Full methodology in notebooks/03_event_impact_modeling.ipynb."
    )

    st.divider()
    st.subheader("Key projected milestones")
    m1, m2 = st.columns(2)
    with m1:
        acc_base = forecasts['acc_scenarios']
        year_reaches_target = acc_base[acc_base['optimistic'] >= 70]['year']
        if len(year_reaches_target):
            st.success(f"**Optimistic scenario** reaches the 70% NFIS-II target in **{int(year_reaches_target.iloc[0])}**")
        else:
            st.warning("**No scenario** reaches the 70% NFIS-II target within the 2025-2027 forecast window")
    with m2:
        base_2027 = acc_base[acc_base['year'] == 2027]['base'].iloc[0]
        st.info(f"**Base scenario, 2027:** {base_2027:.0f}% account ownership ({70 - base_2027:.0f}pp short of target)")


# ---------------------------------------------------------------------------
# PAGE 4: Inclusion Projections
# ---------------------------------------------------------------------------
elif page == "Inclusion Projections":
    st.title("Inclusion Projections")
    st.markdown("Full 2025-2027 outlook against Ethiopia's own policy targets, with scenario selection.")

    scenario = st.select_slider("Scenario", options=["Pessimistic", "Base", "Optimistic"], value="Base")
    scenario_col = scenario.lower()

    acc_scenarios = forecasts['acc_scenarios']
    mm_scenarios = forecasts['mm_scenarios']
    nfis_target = targets[targets['indicator_code'] == 'ACC_OWNERSHIP']['value_numeric'].iloc[0]

    c1, c2, c3 = st.columns(3)
    for col, year in zip([c1, c2, c3], FORECAST_YEARS):
        val = acc_scenarios[acc_scenarios['year'] == year][scenario_col].iloc[0]
        gap = nfis_target - val
        col.metric(f"Account Ownership, {year}", f"{val:.1f}%",
                   delta=f"{-gap:.1f}pp vs. NFIS-II target" if gap > 0 else f"+{-gap:.1f}pp above target",
                   delta_color="inverse" if gap > 0 else "normal")

    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Access: Account Ownership")
        acc_hist = forecasts['acc_historical']
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=acc_hist['observation_date'].dt.year, y=acc_hist['value_numeric'],
                                  mode='lines+markers', name='Historical', line=dict(color=COLORS['dark'], width=3)))
        fig.add_trace(go.Scatter(x=acc_scenarios['year'], y=acc_scenarios[scenario_col],
                                  mode='lines+markers', name=f'{scenario} forecast',
                                  line=dict(color=COLORS['teal'], width=3, dash='dash'), marker=dict(size=10)))
        fig.add_hline(y=nfis_target, line_dash="dot", line_color=COLORS['red'],
                      annotation_text=f"NFIS-II target ({nfis_target:.0f}%)")
        fig.update_layout(height=400, yaxis_title="%", margin=dict(t=20))
        st.plotly_chart(fig, width='stretch')

    with col_right:
        st.subheader("Usage proxy: Mobile Money Accounts")
        mm_hist = forecasts['mm_historical']
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mm_hist['observation_date'].dt.year, y=mm_hist['value_numeric'],
                                  mode='lines+markers', name='Historical', line=dict(color=COLORS['dark'], width=3)))
        fig.add_trace(go.Scatter(x=mm_scenarios['year'], y=mm_scenarios[scenario_col],
                                  mode='lines+markers', name=f'{scenario} forecast',
                                  line=dict(color=COLORS['orange'], width=3, dash='dash'), marker=dict(size=10)))
        fig.update_layout(height=400, yaxis_title="%", margin=dict(t=20))
        st.plotly_chart(fig, width='stretch')

    st.caption(
        "**Note on the Usage proxy:** the Findex-literal Usage indicator (adults who made/received "
        "a digital payment) has only one historical data point in the source dataset, insufficient "
        "for trend forecasting. Mobile Money Account ownership is used as a statistically-grounded "
        "proxy instead — see notebooks/04_forecasting.ipynb, Section 1, for the full explanation."
    )

    st.divider()
    st.subheader("Answers to the consortium's key questions")

    with st.expander("What drives financial inclusion in Ethiopia?", expanded=True):
        st.markdown(
            "- Mobile money product launches (Telebirr, M-Pesa) drive **Usage** far more than "
            "**Access** — most adoption sits on top of existing bank accounts rather than creating "
            "new Findex-measured account holders.\n"
            "- Infrastructure (4G, EthSwitch's Instant Payment System) enables transaction *volume* "
            "growth, but device access (smartphone penetration, only 15%) is now the binding "
            "constraint on further digital-payment usage.\n"
            "- Policy programs (NFIS-II, Fayda Digital ID) are the main identified levers for "
            "**Access** specifically, but both are still mid-implementation and carry real delivery risk."
        )

    with st.expander("How do events affect outcomes?"):
        st.markdown(
            "See the Event \u2192 Indicator Association Matrix on the **Forecasts** page. Validated "
            "against history: the model explains ~84% of Mobile Money Account growth (2021-2024) but "
            "initially over-predicted Account Ownership growth by >3x before a documented, evidence-"
            "based refinement (see notebooks/03_event_impact_modeling.ipynb)."
        )

    with st.expander("How will 2026 and 2027 look?"):
        st.markdown(
            f"Under the **{scenario}** scenario selected above: Account Ownership reaches "
            f"**{acc_scenarios[acc_scenarios['year']==2027][scenario_col].iloc[0]:.0f}%** by 2027 "
            f"and Mobile Money Account ownership reaches "
            f"**{mm_scenarios[mm_scenarios['year']==2027][scenario_col].iloc[0]:.0f}%**. "
            "Try the scenario selector above to compare outcomes."
        )

    st.divider()
    with st.expander("Download forecast data"):
        forecast_csv = pd.read_csv(os.path.join(DATA_DIR, 'forecast_2025_2027.csv'))
        st.dataframe(forecast_csv, width='stretch')
        csv = forecast_csv.to_csv(index=False).encode('utf-8')
        st.download_button("Download forecast table as CSV", csv, "forecast_2025_2027.csv", "text/csv")
