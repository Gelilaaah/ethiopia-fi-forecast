# Data Quality Assessment — Task 2

Companion document to `notebooks/02_eda.ipynb`, Section 8.

## Coverage summary

- 42 observations across 21 distinct indicator codes, spanning 2011-2025.
- Only **6 indicators** (`ACC_OWNERSHIP`, `ACC_FAYDA`, `ACC_MM_ACCOUNT`, `ACC_4G_COV`,
  `USG_P2P_COUNT`, `GEN_GAP_ACC`) have 3+ observations — enough to describe any trend.
- The remaining 15 indicators have only 1-2 observations each (single snapshots or two-point
  "before/after" pairs).

## Confidence distribution

| Confidence | Share |
|---|---|
| High | majority — mostly primary NBE/operator/Findex-sourced figures |
| Medium | secondary-source or self-reported figures (flagged explicitly at collection time) |
| Low | none currently in the dataset |

## Known limitations

1. **Sparse core time series.** The two indicators we're actually forecasting (Account Ownership,
   Digital Payment Adoption) have only 4-5 Findex survey points across 13 years. This constrains
   every downstream regression/forecast in Task 3-4 to wide uncertainty bands by necessity.
2. **No urban/rural or regional disaggregation** exists anywhere in the dataset. The challenge brief
   explicitly invites this analysis "if available" — it is not available, and should be flagged to
   the consortium as a priority gap rather than approximated.
3. **Literacy rate has conflicting secondary sources** for the same year (71.04% vs. 60.5%, 2022).
   Neither is the primary UNESCO source directly; both are third-party compilations. Kept at
   `medium` confidence.
4. **Self-reported operator metrics** (e.g., EthSwitch's 47% IPS cost-reduction figure) are not
   independently audited — marked `medium`, not `high`.
5. **Gender disaggregation is inconsistent across years.** Male/female account ownership exists for
   2021 but not 2024 (only the aggregate gap, 18pp, is reported for 2024) — growth-rate-by-gender
   for the most recent period cannot be directly computed.
6. **Correlation analysis (Section 6) is illustrative, not statistical.** With 4-7 data points per
   indicator, no correlation coefficient in this dataset meets a reasonable bar for statistical
   significance. Relationships are reported as directionally consistent with a plausible mechanism,
   never as proven effects.
7. **Registered-user metrics (Telebirr, M-Pesa) are not directly comparable to Findex-measured
   ownership/usage.** They measure different things (cumulative sign-ups vs. survey-reported active
   use in the past 12 months) — conflating them would overstate real inclusion. See EDA Section 2.1/3.2.

## Implication for forecasting (Task 4)

Given the sparsity above, Task 4 should treat any point forecast as provisional and lead with
explicit confidence intervals / scenario ranges rather than a single number — the brief's own
guidance ("wide uncertainty ranges are appropriate") is not just a suggestion here, it's the only
honest way to represent 4-5 data points spread over 13 years.
