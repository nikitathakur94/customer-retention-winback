# Model card and scoring runbook

Purpose: estimate 28-day non-repurchase among observed users with a valid purchase in the preceding 60 days. This is a non-contractual retail proxy; later return is possible. Public-data reconstruction, not original employment implementation.

Train cutoff 2019-12-01; validation 2019-12-30; final test 2020-01-28; latest scoring 2020-03-01 (unknown outcome). Base estimators and preprocessing fit train only. A salted MD5 partition separates validation calibration from policy/model selection. Constant, recency, purchase-only and combined logistic/tree models use fixed hyperparameters. Sigmoid calibration uses only calibration-half validation. Minimum Brier on policy-half validation selects a frozen artifact. No refit on validation.

Predictors: allowlist in configs/features.yaml. Missing values use training-fitted median imputation. The feature named median_purchase_event_value is an event-value proxy, not median order value. First purchase age is within the 60-day observed window. Provided sessions are scoped to a user; missingness is explicit. All metadata comes from the same pre-cutoff events. No identifiers, future outcomes, campaign assignment, inferred contact details or protected traits enter the retention model.

Read actual model name, parameters/hashes and test metrics in artifacts/<mode>-v1/freeze.json and test_metrics.json. Train refuses to overwrite an unblinded run. A model redesign requires a new run version and explicit post-test disclosure. The saved estimator bundle includes feature order and calibrator; integration tests reproduce its predictions.

Monitoring: verify source hashes/schema, daily coverage and behavioral event vocabulary first. Stop supervised evaluation on immature or materially incomplete follow-up. Compare per-feature missingness and score distributions across cutoffs in audience_summary.json. Reconcile source inclusion/exclusion, primary segment counts, capacity and suppression. Review calibration only when labels mature. Set production alert thresholds after business review; five months do not establish seasonal baselines.

Operating steps: make doctor; make download; make reproduce MODE=full; make test-integration MODE=full; make dashboard. Resume individual CLI stages when their prerequisites exist. `make reproduce` reuses frozen models for an existing run; it does not authorize model changes. Data and model artifacts remain local.

Limits: anonymous observed identifiers are not verified customers across devices; no true orders, quantity, currency verification, refunds, campaign exposures, consent, margin or contactability. Risk and heuristic priority do not estimate incremental profit. Logistic coefficients and validation permutation importance are explanations, not causal drivers.
