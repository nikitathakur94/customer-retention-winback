# Acceptance checklist

Initial status: **NOT RUN**. This checklist describes what the local implementation must verify. A checked item must link to a real test, command log, or inspected artifact. Do not check items merely because code or a planned test exists.

## Sources and identity

- [ ] Both selected sources have provenance, terms, retrieval/version information, and actual file hashes.
- [ ] All five cosmetics months are present for the final run, or a coverage blocker is explicitly disclosed.
- [ ] Actual schema, counts, dates, event vocabulary, and missingness are profiled.
- [ ] Real-data dev sampling selects whole customer histories consistently across months.
- [ ] Raw data, credentials, fixture data, and analytical results cannot be confused.
- [ ] Dataset-specific IDs and outputs cannot be joined or pooled across the two tracks.
- [ ] No contact information from the resume is included in project data.

## Data semantics

- [ ] ID precision is preserved and UTC parsing is verified.
- [ ] Every important table has a documented grain and uniqueness checks.
- [ ] Source rows, excluded rows, and canonical analytical rows reconcile under the stated policy.
- [ ] Exact-duplicate ambiguity is measured, not erased without disclosure.
- [ ] Inferred purchase occasions are not labeled true orders.
- [ ] Purchase-event value is labeled a proxy and currency is not invented.
- [ ] Missing/invalid price does not erase otherwise valid purchase presence.
- [ ] Cart removal is not treated as a refund.
- [ ] Missing or reconstructed sessions are disclosed and do not use future events.
- [ ] Product metadata cannot be backfilled from the future.
- [ ] A previously purchasing but recently inactive user remains in the snapshot universe.

## Labels and validation

- [ ] Feature, eligibility, outcome, and maturity intervals are implemented exactly.
- [ ] Events precisely at feature cutoff and outcome end behave correctly.
- [ ] Incomplete labels are null, not negatives/non-repurchase assumptions.
- [ ] Actual source coverage supports every evaluated outcome window.
- [ ] Training labels mature before validation scoring; validation labels mature before test scoring.
- [ ] IDs and all future-derived fields are excluded from the model allowlist.
- [ ] Preprocessors and feature-selection operations fit only on permitted training data.
- [ ] Validation calibration and policy-selection subsets are disjoint.
- [ ] The final model, calibrator, and policy are frozen before test evaluation.
- [ ] Any post-test changes are disclosed as such.
- [ ] Latest-period scoring does not pretend unknown future outcomes are observed.

## Models and audiences

- [ ] Constant, simple-rule/recency, logistic, and tree-challenger outputs are actually computed.
- [ ] Purchase-only versus purchase-plus-digital ablation uses matching cohorts.
- [ ] Reported metrics identify label prevalence, class, split, run mode, and actual population size.
- [ ] Calibration and ranking metrics include baselines and appropriate uncertainty.
- [ ] Top-K metrics use deterministic tie-breaking, matching denominators, and actual K.
- [ ] Saved models reproduce predictions with the saved feature schema and calibrator.
- [ ] Marketing segments have explicit precedence and reconcile to the eligible population.
- [ ] Candidate exports are unique, capacity-limited, and consistent with dashboard totals.
- [ ] Unknown consent/contactability remains unknown; no actual outreach is performed.
- [ ] Audience exports contain no future outcomes.
- [ ] Heuristic priority and risk-weighted historical value are not called incremental revenue.

## Experiments and assumptions

- [ ] Scenario inputs are distinguished from observations and absent values remain missing.
- [ ] Incentive costs include natural converters and are not double-counted.
- [ ] Invalid probabilities, negative costs, and infeasible break-even results are handled.
- [ ] Proposed cosmetics assignment is labeled a dry run, with no simulated causal success claim.
- [ ] Power/MDE assumptions and multiplicity choices are stated.
- [ ] Hillstrom assignment and pre-treatment/outcome fields remain intact.
- [ ] Hillstrom customers with identical aggregate attributes are not incorrectly deduplicated.
- [ ] Actual campaign comparisons use assigned-customer denominators and confidence intervals.
- [ ] Uplift-model features exclude every post-treatment outcome.
- [ ] Uplift rankings are evaluated out of sample, with support and uncertainty reported.
- [ ] Visits, conversion, and spend are never interchangeably called retention.
- [ ] No Hillstrom effect is presented as an achieved cosmetics or Macy’s result.

## Application and deliverables

- [ ] The dashboard actually launches using the documented command.
- [ ] All seven pages render with actual artifacts or honest unavailable states.
- [ ] Dataset/run/window/evidence labels are visible and consistent.
- [ ] Real customer timelines reconcile to feature values without future leakage.
- [ ] Filters, exports, invalid inputs, empty cohorts, and missing artifacts are tested.
- [ ] Browser screenshots are captured and inspected for clipped text/controls.
- [ ] The learning guide and notebooks execute against real project modules.
- [ ] At least one full-data end-to-end run is logged, or a precise blocker is disclosed.
- [ ] Results manifest, dashboard, reports, and slide values reconcile.
- [ ] PPTX and PDF are generated, opened/rendered, and visually inspected, or missing formats are disclosed.
- [ ] Final recommendation is supported even if the model or uplift policy fails to outperform a baseline.
- [ ] Resume/interview notes distinguish historical facts from reconstruction results.
- [ ] HANDOFF.md includes verified commands, actual paths, measured results, blockers, and a learning order.
