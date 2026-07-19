"""
Task 1: Data Enrichment
Adds new, sourced observations, events, and impact_links to the starter
Ethiopia Financial Inclusion unified dataset.

Every added record is backed by a real, cited source found via web research
on 2026-07-17. Sources are documented in data/data_enrichment_log.md.
"""
import pandas as pd

COLLECTED_BY = "Keneni"
COLLECTION_DATE = "2026-07-17"

COLUMNS = [
    'record_id', 'parent_id', 'record_type', 'category', 'pillar', 'indicator',
    'indicator_code', 'indicator_direction', 'value_numeric', 'value_text',
    'value_type', 'unit', 'observation_date', 'period_start', 'period_end',
    'fiscal_year', 'gender', 'location', 'region', 'source_name', 'source_type',
    'source_url', 'confidence', 'related_indicator', 'relationship_type',
    'impact_direction', 'impact_magnitude', 'impact_estimate', 'lag_months',
    'evidence_basis', 'comparable_country', 'collected_by', 'collection_date',
    'original_text', 'notes'
]


def blank_row():
    return {c: pd.NA for c in COLUMNS}


def make_observation(record_id, pillar, indicator, indicator_code, value_numeric,
                      unit, value_type, observation_date, source_name, source_url,
                      confidence, indicator_direction='higher_better', gender='all',
                      location='national', original_text='', notes=''):
    r = blank_row()
    r.update(dict(
        record_id=record_id, record_type='observation', pillar=pillar,
        indicator=indicator, indicator_code=indicator_code,
        indicator_direction=indicator_direction, value_numeric=value_numeric,
        value_type=value_type, unit=unit, observation_date=observation_date,
        gender=gender, location=location, source_name=source_name,
        source_type='research', source_url=source_url, confidence=confidence,
        collected_by=COLLECTED_BY, collection_date=COLLECTION_DATE,
        original_text=original_text, notes=notes
    ))
    return r


def make_event(record_id, category, indicator, observation_date, source_name,
               source_url, confidence, original_text='', notes=''):
    r = blank_row()
    r.update(dict(
        record_id=record_id, record_type='event', category=category,
        indicator=indicator, observation_date=observation_date,
        source_name=source_name, source_type='research', source_url=source_url,
        confidence=confidence, collected_by=COLLECTED_BY,
        collection_date=COLLECTION_DATE, original_text=original_text, notes=notes
    ))
    return r


def make_impact_link(record_id, parent_id, pillar, related_indicator,
                      relationship_type, impact_direction, impact_magnitude,
                      lag_months, evidence_basis, comparable_country=pd.NA,
                      impact_estimate=pd.NA, notes=''):
    r = blank_row()
    r.update(dict(
        record_id=record_id, parent_id=parent_id, record_type='impact_link',
        pillar=pillar, related_indicator=related_indicator,
        relationship_type=relationship_type, impact_direction=impact_direction,
        impact_magnitude=impact_magnitude, impact_estimate=impact_estimate,
        lag_months=lag_months, evidence_basis=evidence_basis,
        comparable_country=comparable_country, collected_by=COLLECTED_BY,
        collection_date=COLLECTION_DATE, notes=notes
    ))
    return r


def build_new_records():
    rows = []

    # ---------------- NEW OBSERVATIONS ----------------

    # Smartphone penetration (enabler, ACCESS) -- GSMA Mobile Gender Gap Report 2025
    rows.append(make_observation(
        'REC_0034', 'ACCESS', 'Smartphone Penetration Rate', 'ACC_SMARTPHONE_PEN',
        15.0, '%', 'percentage', '2025-05-14',
        'GSMA Mobile Gender Gap Report 2025', 'https://www.gsma.com/', 'medium',
        gender='all',
        original_text='Only 15 percent of people own a smartphone.',
        notes='Enabler/proxy variable (Sheet C). Explains why 4G coverage (70.8%) has not translated into commensurate digital service usage -- device penetration is the binding constraint.'
    ))
    rows.append(make_observation(
        'REC_0035', 'ACCESS', 'Smartphone Penetration Rate', 'ACC_SMARTPHONE_PEN',
        18.0, '%', 'percentage', '2025-05-14',
        'GSMA Mobile Gender Gap Report 2025', 'https://www.gsma.com/', 'medium',
        gender='male',
        original_text='...only 6 percent of women own a smartphone, compared to 18 percent of men.',
        notes='Male smartphone ownership, gender-disaggregated.'
    ))
    rows.append(make_observation(
        'REC_0036', 'ACCESS', 'Smartphone Penetration Rate', 'ACC_SMARTPHONE_PEN',
        6.0, '%', 'percentage', '2025-05-14',
        'GSMA Mobile Gender Gap Report 2025', 'https://www.gsma.com/', 'medium',
        gender='female',
        original_text='...only 6 percent of women own a smartphone.',
        notes='Female smartphone ownership, gender-disaggregated.'
    ))
    rows.append(make_observation(
        'REC_0037', 'GENDER', 'Smartphone Ownership Gender Gap', 'GEN_GAP_SMARTPHONE',
        43.0, 'pp', 'gap_pp', '2025-05-14',
        'GSMA Mobile Gender Gap Report 2025', 'https://www.gsma.com/', 'medium',
        indicator_direction='lower_better',
        original_text='...a 43 percent gap.',
        notes='Smartphone gender gap is far wider than the overall mobile phone gender gap (24pp, REC_0030), suggesting device cost/type -- not basic connectivity -- is now the primary gender-differentiated barrier.'
    ))
    rows.append(make_observation(
        'REC_0038', 'ACCESS', 'Mobile Phone Ownership Rate', 'ACC_MOBILE_OWNERSHIP',
        86.0, '%', 'percentage', '2024-12-31',
        'GSMA Mobile Gender Gap Report 2025', 'https://www.gsma.com/', 'medium',
        gender='male',
        original_text='In 2024, 86 percent of Ethiopian men...owned a mobile phone.',
        notes='Gender-disaggregated basic mobile ownership, complements GEN_GAP_MOBILE (REC_0030).'
    ))
    rows.append(make_observation(
        'REC_0039', 'ACCESS', 'Mobile Phone Ownership Rate', 'ACC_MOBILE_OWNERSHIP',
        65.0, '%', 'percentage', '2024-12-31',
        'GSMA Mobile Gender Gap Report 2025', 'https://www.gsma.com/', 'medium',
        gender='female',
        original_text='...65 percent of...women owned a mobile phone.',
        notes='Gender-disaggregated basic mobile ownership.'
    ))
    rows.append(make_observation(
        'REC_0040', 'ACCESS', 'Adult Literacy Rate', 'ENB_LITERACY',
        71.04, '%', 'percentage', '2022-12-31',
        'UNESCO Institute for Statistics (via statbase.org)',
        'https://statbase.org/data/eth-literacy-rate/', 'medium',
        original_text='Ethiopia - 71.04% (2022).',
        notes='CAUTION: secondary sources disagree on this figure -- Knoema cites 60.5% for the same year (2022) from a different compilation. Flagged as a data-quality limitation in the EDA. Included as an enabler/proxy variable (Sheet C) since low literacy constrains onboarding and product understanding.'
    ))
    rows.append(make_observation(
        'REC_0041', 'ACCESS', 'Electricity Access Rate', 'ENB_ELECTRICITY',
        54.0, '%', 'percentage', '2025-08-18',
        "Ethiopian Ministry of Water and Energy (via Ethiopian News Agency)",
        'https://www.ena.et/web/eng/w/eng_7157130', 'high',
        original_text="Ethiopia's Ministry of Water and Energy announced that the country's national electricity coverage has reached 54 percent of the population.",
        notes='Enabler/proxy variable (Sheet C) -- non-negotiable infrastructure input for digital and agent-based financial services, especially rural.'
    ))
    rows.append(make_observation(
        'REC_0042', 'USAGE', 'Digital Payment Adoption Rate', 'USG_DIGITAL_PAYMENT',
        24.0, '%', 'percentage', '2021-12-31',
        'World Bank Global Findex 2021 (via AfricaNenda SIIPS 2025 case study)',
        'https://www.africanenda.org/uploads/files/siips2025/siips_2025_EthSwitch-Ethiopia_CaseStudy_en.pdf',
        'high', gender='male',
        original_text='...only 24% of men...had done so [made or received a digital payment].',
        notes='2021 gender-disaggregated baseline for digital payment adoption, useful pre-Telebirr-maturity anchor point and for gender-gap-in-usage analysis (Sheet C item 3).'
    ))
    rows.append(make_observation(
        'REC_0043', 'USAGE', 'Digital Payment Adoption Rate', 'USG_DIGITAL_PAYMENT',
        15.0, '%', 'percentage', '2021-12-31',
        'World Bank Global Findex 2021 (via AfricaNenda SIIPS 2025 case study)',
        'https://www.africanenda.org/uploads/files/siips2025/siips_2025_EthSwitch-Ethiopia_CaseStudy_en.pdf',
        'high', gender='female',
        original_text='...15% of women had done so.',
        notes='2021 female digital payment baseline -- 9pp gender gap in usage at that point.'
    ))
    rows.append(make_observation(
        'REC_0044', 'USAGE', 'P2P Transaction Count via EthSwitch IPS', 'USG_IPS_TXN_COUNT',
        79369833, 'transactions', 'count', '2024-12-31',
        'AfricaNenda SIIPS 2025 -- EthSwitch Ethiopia Case Study',
        'https://www.africanenda.org/uploads/files/siips2025/siips_2025_EthSwitch-Ethiopia_CaseStudy_en.pdf',
        'high',
        original_text='...the IPS processing approximately 79 million transactions, valuing a total of $5 billion.',
        notes='Cumulative EthSwitch switch volume (ATM/POS/IPS combined) through 2024, showing the 2024 inflection after IPS go-live in February 2024.'
    ))
    rows.append(make_observation(
        'REC_0045', 'AFFORDABILITY', 'Instant Payment System Cost Reduction', 'AFF_IPS_COST_REDUCTION',
        47.0, '%', 'percentage', '2025-11-12',
        'AfricaNenda SIIPS 2025 -- EthSwitch Ethiopia Case Study',
        'https://www.africanenda.org/uploads/files/siips2025/siips_2025_EthSwitch-Ethiopia_CaseStudy_en.pdf',
        'medium',
        original_text='Transfer costs on the EthSwitch IPS are approximately 47% lower per transaction for end users compared to the cost of digital payments before its introduction.',
        notes='Self-reported by EthSwitch (via AfricaNenda), hence medium not high confidence. Directly relevant to AFFORDABILITY pillar and to explaining any usage acceleration post-Feb 2024.'
    ))

    # ---------------- NEW EVENTS ----------------
    rows.append(make_event(
        'EVT_0011', 'infrastructure', 'EthSwitch Instant Payment System (IPS) Go-Live',
        '2024-02-01', 'EthSwitch / AfricaNenda SIIPS 2025',
        'https://www.africanenda.org/uploads/files/siips2025/siips_2025_EthSwitch-Ethiopia_CaseStudy_en.pdf',
        'high',
        original_text='The system went live in February 2024 with the P2P use cases and two participating banks: Awash Bank and Amhara Bank.',
        notes='First cross-domain (bank + non-bank) real-time interoperable payment rail in Ethiopia. Not pre-assigned to a pillar per schema convention -- see impact_links.'
    ))
    rows.append(make_event(
        'EVT_0012', 'regulation', 'NBE Approves Interoperable QR Standard (ETHQR)',
        '2024-04-01', 'National Bank of Ethiopia / AfricaNenda SIIPS 2025',
        'https://www.africanenda.org/uploads/files/siips2025/siips_2025_EthSwitch-Ethiopia_CaseStudy_en.pdf',
        'high',
        original_text='In April 2024, the NBE had approved a standardized QR scheme and QR brand, ETHQR, creating a single standard for all participants.',
        notes='Standardization event enabling merchant-side (P2B) QR acceptance across banks and non-banks.'
    ))
    rows.append(make_event(
        'EVT_0013', 'regulation', 'NBE Mandates ETHQR Standard Adoption',
        '2024-11-01', 'National Bank of Ethiopia / AfricaNenda SIIPS 2025',
        'https://www.africanenda.org/uploads/files/siips2025/siips_2025_EthSwitch-Ethiopia_CaseStudy_en.pdf',
        'high',
        original_text='In November 2024, the NBE mandated that payment providers adopt the standard to promote public trust and interoperability and minimize consumer confusion.',
        notes='Regulatory mandate following the April 2024 voluntary standard -- a forcing function likely to accelerate merchant QR acceptance.'
    ))

    # ---------------- NEW IMPACT LINKS ----------------
    rows.append(make_impact_link(
        'IMP_0015', 'EVT_0011', 'USAGE', 'USG_P2P_COUNT', 'direct', 'increase',
        'high', lag_months=6, evidence_basis='empirical',
        notes='P2P transaction count roughly doubled between mid-2024 and mid-2025 (REC_0015 to REC_0016), coinciding with IPS ramp-up.'
    ))
    rows.append(make_impact_link(
        'IMP_0016', 'EVT_0011', 'USAGE', 'USG_CROSSOVER', 'indirect', 'increase',
        'medium', lag_months=8, evidence_basis='empirical',
        notes='Cheaper, faster P2P rails plausibly contributed to the P2P/ATM crossover ratio exceeding 1.0 (REC_0020) shortly after IPS launch and the Oct-2024 milestone event (EVT_0006).'
    ))
    rows.append(make_impact_link(
        'IMP_0017', 'EVT_0012', 'USAGE', 'USG_P2P_COUNT', 'indirect', 'increase',
        'medium', lag_months=9, evidence_basis='literature',
        comparable_country='India',
        notes="India's UPI QR standardization is widely credited with accelerating merchant-side digital payment adoption; ETHQR is a structurally similar single-QR-standard intervention."
    ))
    rows.append(make_impact_link(
        'IMP_0018', 'EVT_0013', 'ACCESS', 'ACC_OWNERSHIP', 'enabling', 'increase',
        'low', lag_months=18, evidence_basis='theoretical',
        notes='Mandatory standardization reduces consumer confusion and fraud risk, which the literature links to modest gains in trust and first-time account formation, though the channel is indirect and slow.'
    ))
    rows.append(make_impact_link(
        'IMP_0019', 'EVT_0009', 'ACCESS', 'ACC_OWNERSHIP', 'enabling', 'increase',
        'medium', lag_months=36, evidence_basis='expert',
        notes='NFIS-II (EVT_0009) sets the 70% account ownership target (see target REC_0031) but had no modeled impact_link in the original 14 -- added to make the policy-to-outcome channel explicit for Task 3/4 modeling. Effect assumed to operate through coordinated agent-banking and digital ID rollout rather than a single mechanism, hence long lag and expert-judgment basis.'
    ))

    return pd.DataFrame(rows, columns=COLUMNS)


if __name__ == '__main__':
    base = pd.read_csv('data/raw/ethiopia_fi_unified_data.csv')
    new = build_new_records()
    enriched = pd.concat([base, new], ignore_index=True)
    enriched.to_csv('data/processed/ethiopia_fi_unified_data_enriched.csv', index=False)
    print(f"Base records: {len(base)}")
    print(f"New records added: {len(new)}")
    print(f"Enriched total: {len(enriched)}")
    print(enriched['record_type'].value_counts())
