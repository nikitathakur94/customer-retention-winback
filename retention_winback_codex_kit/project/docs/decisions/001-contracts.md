# Initial analytical decisions — before any outcomes are inspected

Use the kit's four UTC cutoffs and half-open 60-day feature / 28-day outcome windows. Preserve source multiplicity; measure exact-duplicate sensitivity. Purchase presence is independent of price validity. Use only event-time metadata and customer-scoped provided sessions, with missing-session flags rather than fabricated sessions.

Development selects whole user histories using MD5(user_id), first eight hexadecimal digits modulo 10 = 0. Validation calibration/policy use the parity of a separate salted MD5("calibration:" + user_id) digest, avoiding correlation with the development sample bucket. Full and dev are separate runs.

Use one fixed logistic specification (C=1) and one fixed histogram tree specification (100 iterations, 15 leaves, minimum leaf 50, L2=1); no hyperparameter search. Select model on validation-policy Brier score. Fit sigmoid calibration on the other half of validation. Choose classification threshold 0.5 and audience capacity 10% as planning assumptions before inspecting test. Compare equal-capacity recency, risk, value, and risk-times-value heuristic policies. Recent-purchase suppression is seven days. Use training 75th percentile historical value for high value and negative 14-day activity change for decline.

Two datasets never join. Hillstrom uplift target is visit (engagement), with Mens E-Mail versus No E-Mail fixed in advance, 60/20/20 stratified partitions and 20% targeting capacity. These choices are teaching assumptions; revisit only with a new evaluation design.

Source terms: cosmetics card label reported by supplied kit is Data files © Original Authors; dynamic card text could not be extracted by browser research. Publisher link verified. Hillstrom author explicitly provides the CSV for the analysis challenge; no blanket redistribution license established. Keep both datasets and customer traces local.
