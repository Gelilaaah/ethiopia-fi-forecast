"""
Task 3: Event Impact Modeling

Translates qualitative impact_link records (direction, magnitude, lag, relationship_type)
into a quantitative model that can predict how an indicator changes in response to one or
more events over time.

Modeling choices (documented, not "ground truth"):

1. INDICATOR SCALE — every indicator is classified as either:
   - 'pp'       : effects are additive, in percentage points (Access/Gender pillar
                  percentages, and USAGE percentage-type indicators like digital payment
                  adoption).
   - 'relative' : effects are multiplicative, as a fractional change on the baseline
                  (USAGE count/value/ratio indicators like P2P transaction counts, where
                  "high impact" means "grew a lot in relative terms", not "+8 percentage
                  points" which is meaningless for a raw count).

2. MAGNITUDE MAPPING — impact_magnitude (low/medium/high) is mapped to a numeric value per
   scale. These are judgment calls calibrated loosely against the historical validation in
   this notebook, not independently derived.

3. RELATIONSHIP DAMPING — 'direct' relationships apply the full magnitude; 'indirect' and
   'enabling' relationships are dampened, since they represent a weaker/less certain causal
   channel per the evidence_basis field.

4. TIME CURVE — an event's effect does not appear instantly. We model it as a logistic
   ("S-curve") ramp that reaches ~50% of its full effect at lag_months/2 and ~95% by
   lag_months, i.e. lag_months represents the point by which the effect is "mostly realized"
   rather than a hard cutoff. This reflects gradual adoption dynamics (awareness -> trial ->
   habitual use) rather than a step-function effect on launch day.

5. COMBINING EFFECTS — multiple events affecting the same 'pp'-scale indicator are summed.
   Multiple events affecting the same 'relative'-scale indicator are compounded
   (multiplicatively), not summed, to avoid effects exceeding 100% in an unrealistic way.
"""
import numpy as np
import pandas as pd

PP_MAGNITUDE = {'low': 1.5, 'medium': 4.0, 'high': 8.0}
REL_MAGNITUDE = {'low': 0.15, 'medium': 0.35, 'high': 0.70}

RELATIONSHIP_DAMPING = {'direct': 1.0, 'indirect': 0.55, 'enabling': 0.40}

DIRECTION_SIGN = {'increase': 1, 'decrease': -1}

# Indicators whose effects should be modeled additively in percentage points
PP_SCALE_INDICATORS = {
    'ACC_OWNERSHIP', 'ACC_MM_ACCOUNT', 'ACC_4G_COV', 'ACC_MOBILE_PEN',
    'ACC_SMARTPHONE_PEN', 'ACC_MOBILE_OWNERSHIP', 'GEN_GAP_ACC', 'GEN_GAP_MOBILE',
    'GEN_GAP_SMARTPHONE', 'GEN_MM_SHARE', 'USG_DIGITAL_PAYMENT', 'USG_ACTIVE_RATE',
    'AFF_DATA_INCOME',
}

# Everything else (counts, values, ratios) is modeled as a relative/multiplicative effect
RELATIVE_SCALE_FALLBACK = 'relative'


def indicator_scale(indicator_code: str) -> str:
    return 'pp' if indicator_code in PP_SCALE_INDICATORS else RELATIVE_SCALE_FALLBACK


def magnitude_to_numeric(impact_magnitude: str, relationship_type: str, impact_direction: str,
                          scale: str) -> float:
    """Convert a qualitative impact_link row into a signed numeric 'full effect' value."""
    base = PP_MAGNITUDE.get(impact_magnitude, 0.0) if scale == 'pp' else REL_MAGNITUDE.get(impact_magnitude, 0.0)
    damping = RELATIONSHIP_DAMPING.get(relationship_type, 0.5)
    sign = DIRECTION_SIGN.get(impact_direction, 0)
    return sign * base * damping


def effect_realized_fraction(months_since_event: float, lag_months: float, k: float = 6.0) -> float:
    """
    Logistic ramp: fraction of the full effect realized at a given number of months
    since the event occurred. Reaches 0.5 at lag_months/2, ~0.95 by lag_months.
    Returns 0 for months_since_event <= 0 (event hasn't happened yet).
    """
    if months_since_event <= 0:
        return 0.0
    if lag_months <= 0:
        return 1.0
    midpoint = lag_months / 2
    # k controls steepness; scaled so the curve naturally reaches ~0.95 by lag_months
    steepness = k / max(lag_months, 1e-6)
    x = steepness * (months_since_event - midpoint)
    return float(1 / (1 + np.exp(-x)))


def months_between(start, end) -> float:
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    return (end - start).days / 30.44


def build_enriched_impact_links(impact_links: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Join impact_links to their parent event and attach the numeric full-effect value."""
    events_idx = events.set_index('record_id')
    out = impact_links.copy()
    out['event_name'] = out['parent_id'].map(events_idx['indicator'])
    out['event_date'] = pd.to_datetime(out['parent_id'].map(events_idx['observation_date']))
    out['event_category'] = out['parent_id'].map(events_idx['category'])
    out['scale'] = out['related_indicator'].map(indicator_scale)
    out['full_effect'] = out.apply(
        lambda r: magnitude_to_numeric(r['impact_magnitude'], r['relationship_type'],
                                        r['impact_direction'], r['scale']),
        axis=1
    )
    return out


def build_association_matrix(enriched_links: pd.DataFrame) -> pd.DataFrame:
    """Rows = events, columns = indicators, values = full (fully-realized) estimated effect."""
    matrix = enriched_links.pivot_table(
        index='event_name', columns='related_indicator', values='full_effect', aggfunc='sum', fill_value=0.0
    )
    return matrix



# --- Refinement layer (see notebooks/03_event_impact_modeling.ipynb, Section 5) ---
#
# Historical validation shows the raw model overshoots ACC_OWNERSHIP growth by >3x
# (predicts +10.3pp vs. actual +3pp, 2021-2024), driven almost entirely by Telebirr's
# "high/direct" link. This is not a bug in the ramp-up math -- it's a real overstatement
# of causal strength, and it's the same phenomenon Task 2's EDA already surfaced: most
# Telebirr adoption sits on top of an *existing* bank account (mobile-money-only users are
# ~0.5% of adults per the Market Nuances guide) rather than creating a new Findex-measured
# account holder. The Kenya comparable-country evidence behind IMP_0001's "high" magnitude
# doesn't transfer cleanly, because Kenya's M-Pesa (2007) launched into a much lower banking
# baseline than Ethiopia's already-growing bank sector had reached by 2021 (46% account
# ownership, itself the product of a decade of branch expansion under NFIS-I).
#
# Refinement: dampen the ACCOUNT-OWNERSHIP-pillar effect of product_launch/market_entry
# events whose evidence_basis is comparable-country 'literature' (i.e. imported evidence,
# not Ethiopia-specific empirical data) by a context factor. USAGE-pillar effects from the
# same events are left untouched, since Validation 1 (ACC_MM_ACCOUNT, M-Pesa) showed those
# hold up well against actuals (predicted +4.0pp vs. actual +4.75pp).
CONTEXT_DAMPING_ACCESS_LAUNCH = 0.35  # applied to product_launch/market_entry -> ACC_OWNERSHIP links
                                       # sourced from comparable-country literature evidence


def apply_context_refinement(enriched_links: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of enriched_links with a 'refined_effect' column applying the
    documented context-damping adjustment above. Does not mutate the source dataset."""
    out = enriched_links.copy()
    out['refined_effect'] = out['full_effect']

    mask = (
        (out['related_indicator'] == 'ACC_OWNERSHIP')
        & (out['event_category'].isin(['product_launch', 'market_entry']))
        & (out['evidence_basis'] == 'literature')
    )
    out.loc[mask, 'refined_effect'] = out.loc[mask, 'full_effect'] * CONTEXT_DAMPING_ACCESS_LAUNCH
    return out


def predict_indicator_change(indicator_code: str, as_of_date, enriched_links: pd.DataFrame,
                              effect_column: str = 'full_effect') -> dict:
    """
    Predict the model-implied change in `indicator_code` by `as_of_date`, combining all
    impact_links that target it. Returns a dict with the combined effect and a breakdown
    of each contributing event's realized (time-adjusted) contribution.
    """
    scale = indicator_scale(indicator_code)
    relevant = enriched_links[enriched_links['related_indicator'] == indicator_code].copy()

    contributions = []
    for _, row in relevant.iterrows():
        t = months_between(row['event_date'], as_of_date)
        frac = effect_realized_fraction(t, row['lag_months'])
        full_effect = row[effect_column]
        realized = full_effect * frac
        contributions.append({
            'event_name': row['event_name'], 'event_date': row['event_date'].date(),
            'full_effect': full_effect, 'months_elapsed': round(t, 1),
            'lag_months': row['lag_months'], 'fraction_realized': round(frac, 2),
            'realized_effect': realized
        })

    contrib_df = pd.DataFrame(contributions)

    if scale == 'pp':
        combined = contrib_df['realized_effect'].sum() if len(contrib_df) else 0.0
    else:
        # compound relative effects multiplicatively: total = product(1 + e_i) - 1
        combined = 1.0
        for e in contrib_df['realized_effect']:
            combined *= (1 + e)
        combined = combined - 1.0 if len(contrib_df) else 0.0

    return {'indicator_code': indicator_code, 'scale': scale, 'combined_effect': combined,
            'contributions': contrib_df}
