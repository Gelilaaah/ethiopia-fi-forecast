# Data Enrichment Log — Task 1

**Collected by:** Gelila
**Collection date:** 2026-07-17
**Base dataset:** `data/raw/ethiopia_fi_unified_data.csv` (57 records: 30 observations, 10 events, 3 targets, 14 impact_links)
**Enriched dataset:** `data/processed/ethiopia_fi_unified_data_enriched.csv` (77 records)

All additions are generated programmatically by `src/enrich_data.py` so the enrichment is reproducible. This log explains **why** each addition was made and links it back to the Data Enrichment Guide (`data/raw/additional_data_points_guide.xlsx`).

---

## Summary of additions

| Type | Count | Record IDs |
|---|---|---|
| Observations | 12 | REC_0034 – REC_0045 |
| Events | 3 | EVT_0011 – EVT_0013 |
| Impact links | 5 | IMP_0015 – IMP_0019 |
| **Total new records** | **20** | |

---

## New Observations

### Enablers / indirect correlation (Sheet C)

| ID | Indicator | Value | Date | Source | Confidence |
|---|---|---|---|---|---|
| REC_0034 | Smartphone penetration (all) | 15% | 2025-05-14 | GSMA Mobile Gender Gap Report 2025 | medium |
| REC_0035 | Smartphone penetration (male) | 18% | 2025-05-14 | GSMA Mobile Gender Gap Report 2025 | medium |
| REC_0036 | Smartphone penetration (female) | 6% | 2025-05-14 | GSMA Mobile Gender Gap Report 2025 | medium |
| REC_0040 | Adult literacy rate | 71.04% | 2022-12-31 | UNESCO Institute for Statistics | medium |
| REC_0041 | Electricity access rate | 54% | 2025-08-18 | Ethiopian Ministry of Water and Energy | **high** |

**Why:** Sheet C flags smartphone penetration, literacy, and electricity access as enabler/proxy variables. These matter directly for our forecasting question: Ethiopia has strong 4G coverage (existing REC_0009, 70.8%) but only 15% smartphone penetration — this gap is a plausible explanation for usage lagging behind infrastructure, and a leading indicator worth tracking into the forecast period.

**Data quality note:** REC_0040 (literacy) is flagged `medium` confidence because two respectable secondary sources disagree materially on the same year (71.04% vs. 60.5% for 2022) — this discrepancy itself is documented as an EDA data-quality limitation rather than silently resolved.

### Gender disaggregation (Sheet A/D)

| ID | Indicator | Value | Date | Source | Confidence |
|---|---|---|---|---|---|
| REC_0037 | Smartphone ownership gender gap | 43pp | 2025-05-14 | GSMA | medium |
| REC_0038 | Mobile phone ownership (male) | 86% | 2024-12-31 | GSMA | medium |
| REC_0039 | Mobile phone ownership (female) | 65% | 2024-12-31 | GSMA | medium |
| REC_0042 | Digital payment adoption (male) | 24% | 2021-12-31 | World Bank Global Findex 2021 | **high** |
| REC_0043 | Digital payment adoption (female) | 15% | 2021-12-31 | World Bank Global Findex 2021 | **high** |

**Why:** The challenge brief explicitly calls for gender-gap analysis in Task 2 ("Analyze the gender gap"). The base dataset had only one gender-gap observation (REC_0030, mobile phone gap). REC_0042/REC_0043 give a genuine 2021 Findex-sourced usage baseline pre-dating Telebirr's full maturity, which is valuable for isolating how much of the 2021→2024 usage growth is gender-differentiated. Notably: the smartphone gender gap (43pp) is nearly double the basic mobile phone gender gap (24pp, existing REC_0030) — device *type*, not basic connectivity, looks like the more binding gender constraint today.

### Usage / infrastructure (Sheet B, direct correlation)

| ID | Indicator | Value | Date | Source | Confidence |
|---|---|---|---|---|---|
| REC_0044 | EthSwitch IPS transaction count (cumulative) | ~79.4M | 2024-12-31 | AfricaNenda SIIPS 2025 | **high** |
| REC_0045 | IPS cost reduction vs. pre-IPS | 47% | 2025-11-12 | AfricaNenda SIIPS 2025 (EthSwitch self-reported) | medium |

**Why:** Sheet B lists transaction volumes and cost/affordability data as directly correlated indicators. The AfricaNenda "State of Inclusive Instant Payment Systems" 2025 case study on EthSwitch is an independent, dated, detailed source with real figures — a rare find given how sparse Ethiopia-specific payment-system data usually is. REC_0045 is marked `medium` (not `high`) because the cost-reduction figure is self-reported by EthSwitch to AfricaNenda rather than independently audited.

---

## New Events

| ID | Category | Event | Date | Source |
|---|---|---|---|---|
| EVT_0011 | infrastructure | EthSwitch Instant Payment System (IPS) go-live | 2024-02-01 | AfricaNenda SIIPS 2025 |
| EVT_0012 | regulation | NBE approves interoperable QR standard (ETHQR) | 2024-04-01 | AfricaNenda SIIPS 2025 |
| EVT_0013 | regulation | NBE mandates ETHQR standard adoption | 2024-11-01 | AfricaNenda SIIPS 2025 |

**Why:** None of the original 10 events captured Ethiopia's shift to real-time interoperable payments — arguably as structurally important as Telebirr's 2021 launch, since it changes *how* every existing provider's transactions clear, not just adding a new provider. All three follow the schema convention: `category` is filled, `pillar` is left empty (effects captured via impact_links, per the "no pre-assigned pillar" design principle in the README).

---

## New Impact Links

| ID | Event | → Indicator | Direction | Magnitude | Lag | Evidence |
|---|---|---|---|---|---|---|
| IMP_0015 | EVT_0011 (IPS go-live) | USG_P2P_COUNT | increase | high | 6mo | empirical |
| IMP_0016 | EVT_0011 (IPS go-live) | USG_CROSSOVER | increase | medium | 8mo | empirical |
| IMP_0017 | EVT_0012 (ETHQR standard) | USG_P2P_COUNT | increase | medium | 9mo | literature (India UPI) |
| IMP_0018 | EVT_0013 (ETHQR mandate) | ACC_OWNERSHIP | increase | low | 18mo | theoretical |
| IMP_0019 | EVT_0009 (NFIS-II) | ACC_OWNERSHIP | increase | medium | 36mo | expert |

**Why:**
- **IMP_0015/IMP_0016** connect the new IPS event to observed outcomes already in the dataset — P2P transaction count roughly doubled (REC_0015 → REC_0016) and the P2P/ATM crossover ratio passed 1.0 (REC_0020) in the months following IPS launch. This is exactly the kind of "test your model against historical data" check Task 3 asks for.
- **IMP_0017** borrows from India's UPI QR-standardization experience (comparable-country evidence, as Task 3 instructs when Ethiopian pre/post data is insufficient).
- **IMP_0019** fills a real gap: **EVT_0009 (NFIS-II) had zero impact_links in the original 14**, despite NFIS-II being the policy source of the 70%-by-2025 target (REC_0031). Without this link, the association matrix in Task 3 would have no modeled channel from the strategy that sets the headline target to the indicator it targets.

---

## Data limitations acknowledged

1. **Literacy rate discrepancy** (REC_0040) — two credible secondary compilations of UNESCO data disagree by ~10pp for the same year; neither is the primary UNESCO source directly.
2. **EthSwitch IPS transaction volumes/values by individual year** were present in the source PDF's table but rendered ambiguously after text extraction — only the clearly-stated cumulative 2024 figures (~79.4M transactions, ~$5B) were used; year-by-year breakdowns were not added to avoid misattributing garbled numbers.
3. **Self-reported metrics** (REC_0045, cost reduction) are marked `medium` confidence rather than `high` since they come from the operator itself, not an independent audit.
4. New impact_link magnitudes for EVT_0012/EVT_0013/EVT_0009 are judgment calls (`theoretical`/`expert` evidence basis) since Ethiopia has under a year of post-event data for the QR standard and NFIS-II's effects are necessarily long-horizon — these should be treated as hypotheses to revisit in Task 3, not settled estimates.
