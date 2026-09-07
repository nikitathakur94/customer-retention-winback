# Codex build brief: Customer Retention & Win-Back Analytics

## Your assignment

Build and actually run an end-to-end, local-first analytics project called **Customer Retention & Win-Back Analytics**. Deliver functioning code, real-data analyses, a trained and evaluated model, a usable dashboard, marketing audience exports, an independent real campaign experiment analysis, presentations, and a guided learning journey.

This is an implementation assignment, not a request for another proposal. Do not stop after creating a scaffold, a notebook, an architecture diagram, or a list of future tasks. Work through the phases below, execute the pipeline, inspect the outputs, repair failures, and provide an honest completion report. If credentials, network access, data permissions, or local resources block execution, build everything that can be built, identify the exact blocker, and leave a precise resume command. Never present unexecuted stages as complete.

The owner is **Nikita Thakur**. The career context is her **Business Analyst at Factspan, working on Macy’s Customer Intelligence, May 2016–June 2019** experience. The resume statement motivating this reconstruction is:

> Customer Retention & Win-Back Analytics: Partnered with marketing to identify disengagement signals, built a churn-propensity model from purchase and digital behaviour, and converted scores into targeted win-back cohorts.

Translate each part of this statement into something the owner can inspect, run, understand, and explain. Keep the central story about customer analytics and marketing decisions, rather than turning it into a platform-engineering showcase.

### Historical honesty

This is a **public-data reconstruction inspired by the business problem**, not a recreation of confidential Macy’s data or proof of the original project’s specific implementation. Do not invent original algorithms, stakeholder conversations, company results, production adoption, or personal contributions. Do not imply Macy’s supplied or endorsed these datasets. Do not backdate public data or modern tooling to the original role. The primary dataset is from 2019–2020; the separate campaign dataset is from 2008.

Put this disclosure in the README, dashboard About section, report, presentation, and interview notes. Do not copy personal contact details from the resume into fixtures, code, or marketing exports. Use neutral project branding and no Macy’s logo.

## 1. Business problem and success criteria

Use the planning scenario of a retailer’s online beauty/cosmetics business. This is a practical public-data analogue for one department in a larger retailer, not a claim about Macy’s operating practices.

The marketing team needs to answer:

1. Which previously purchasing customers appear to be disengaging?
2. Which are unlikely to purchase in the next 28 days?
3. Does browsing/cart behaviour add useful information beyond purchase recency and frequency?
4. Which customers should enter a budget-constrained win-back **candidate** audience, and why?
5. What experiment would establish whether contacting those customers causes incremental purchases?

Build two clearly separated analytical tracks:

- **Track A — Retention operations:** real event histories → reliable customer features → forward-looking non-repurchase propensity → understandable marketing cohorts and a proposed experiment.
- **Track B — Campaign incrementality lab:** an independent randomized email dataset → actual treatment-versus-control estimates → an introductory uplift-modeling comparison.

They share teaching concepts and application navigation, not customer identities, model training rows, or business results. Never join, pool, or transport individual predictions between them. Hillstrom campaign effects must never appear as achieved effects for the cosmetics retailer.

Project success means a reproducible, defensible analysis and a useful decision tool. It does **not** require a particular model score, a positive campaign effect, or proof that ML beats a simple baseline. A well-supported “use the simple rule” or “run an experiment before deployment” is a valid recommendation.

## 2. Data sources: use these, not synthetic substitutes

### Track A: REES46 eCommerce Events History in Cosmetics Shop

Publisher index:
https://rees46.com/en/datasets

Dataset:
https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-cosmetics-shop

Kaggle handle:
`mkechinov/ecommerce-events-history-in-cosmetics-shop`

The publisher lists October 2019–February 2020 coverage. Expect a large event dataset, on the order of 20 million rows, rather than a tiny pre-aggregated churn table. Verify actual counts, files, dates, and event types after acquisition; approximate source descriptions are not validation results.

Expected fields to validate:
`event_time, event_type, product_id, category_id, category_code, brand, price, user_id, user_session`.

Expected event vocabulary includes product views, cart additions, cart removals, and purchases. Inspect the files rather than trusting potentially generic dataset-card wording about event types. Preserve any source/documentation discrepancy in the data-quality report.

Use all five months for the final run. Expected monthly filenames are `2019-Oct.csv`, `2019-Nov.csv`, `2019-Dec.csv`, `2020-Jan.csv`, and `2020-Feb.csv`; discover and validate the actual archive structure rather than assuming it.

Acquisition requirements:

- Prefer the official `kagglehub.dataset_download` interface. Check current API details in https://github.com/Kaggle/kagglehub before implementing it.
- Support a user-provided local data directory as an alternative to downloading.
- Resolve and record the downloaded dataset version, file sizes, retrieval time, source URLs, and SHA-256 checksums. Pin subsequent reproductions to that version.
- Cache downloads and avoid duplicated multi-gigabyte copies. Do not force redownloads by default.
- On authentication or consent failure, provide the exact supported local action required. Do not print tokens or put them in repository files. Do not silently switch datasets.
- Inspect and record applicable source terms. The publicly surfaced cosmetics card uses “Data files © Original Authors”; do not assume CC0 or blanket redistribution rights. Keep raw records out of Git and distribution bundles unless permissions clearly allow redistribution. The project code’s license is separate from the data’s terms.
- Do not fetch random third-party “cleaned” copies as an undocumented shortcut.

These events provide an observed identifier, not a verified cross-device CRM person. They do not establish contactability, consent, in-store purchases, refunds, margin, true order quantity, or campaign exposure. Verify available fields, and explicitly list absent capabilities.

### Track B: Kevin Hillstrom / MineThatData email experiment

Original study description and original data link:
https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html

Maintained dataset-loading reference:
https://www.uplift-modeling.com/en/latest/api/datasets/fetch_hillstrom.html

Independent dataset catalog:
https://www.tensorflow.org/datasets/catalog/hillstrom

Use the original linked CSV where accessible. An explicitly documented fallback is `sklift.datasets.fetch_hillstrom(target_col="all")`; preserve all outcomes and the treatment column. Do not install TensorFlow solely to download a small CSV. Record provenance, terms, actual schema, row counts, and checksums here too.

This dataset describes 64,000 customers assigned among two email creatives and a no-email control, with subsequent two-week outcomes. The campaign names refer to merchandise/creative, **not customer gender**. Keep this dataset in its own directory and warehouse schema.

Never synthesize treatment assignments or outcomes and call them this real experiment. Small artificial fixtures are allowed only in clearly identified unit tests, never in main results or portfolio screenshots.

## 3. Working style, local environment, and execution safety

Create the implementation under `project/` when this brief is inside a guidance kit. If running the brief standalone in an empty working directory, create `customer-retention-winback/`. Inspect the workspace first and do not overwrite unrelated work.

Use a compact stack:

- A supported local Python version, preferably 3.11 or 3.12 if compatible with current dependencies; use a project virtual environment and a tested lockfile.
- `uv` for dependency management when available, with a documented equivalent environment setup otherwise.
- DuckDB and Parquet for local storage and efficient SQL processing.
- dbt-core with the DuckDB adapter for staging, reusable analytical models, documentation, and tests.
- Python, scikit-learn, and statsmodels for models, evaluation, and experiment calculations.
- Streamlit and Plotly for the main dashboard.
- pytest, concise SQL/dbt tests, and Streamlit AppTest. Use a small browser smoke-test set for actual layout checks where browser automation is available.
- Local JSON/Parquet experiment artifacts; no hosted tracking service is necessary.

Do not require Snowflake, BigQuery, Databricks, paid BI tools, Docker, a GPU, Kubernetes, Airflow, Kafka, an LLM API, or cloud credentials. Provide BI-friendly exports and a Tableau/Power BI recreation guide instead of claiming an uncreated proprietary workbook exists.

Inspect RAM, CPU, free disk, Python, dependency compatibility, network access, and browser/PDF rendering tools. Choose bounded DuckDB memory and thread settings with a spill directory. Record measured runtime and peak resource usage rather than promising runtimes in advance. Stream large CSVs or process them with DuckDB; do not concatenate all raw events into a pandas DataFrame.

Create two data modes:

- `dev`: a deterministic hash sample of whole `user_id` histories across every month, initially approximately 10% of users. This is real data, not fabricated data.
- `full`: all available source records. All headline conclusions, final charts, presentation figures, and audience outputs must identify whether they use full or dev data. Prefer the full run for final delivery.

Do not take a random sample of event rows, the first N rows, only buyers, or a single convenient month and treat it as the full lifecycle dataset. Keep user sampling stable across months. Store separate run IDs and output directories for dev, full, and test fixtures.

Write typed, modular Python with useful docstrings and comments. Write readable SQL with CTEs and grain comments. Keep business logic in reusable source modules and SQL models, not duplicated across dashboard pages and notebooks. Make commands idempotent. Log validation failures visibly.

Parallel agents may help only if supported. Lock shared schemas and metric contracts first, assign disjoint files, and avoid concurrent DuckDB writers. The lead agent remains responsible for integration and actual execution. Do not repeatedly run the full dataset for cosmetic changes.

## 4. Repository and runnable entry points

Create an equivalent of this structure, keeping modules small enough to inspect:

```text
project/
  README.md
  pyproject.toml
  uv.lock
  Makefile
  .gitignore
  .env.example
  configs/
    project.yaml
    features.yaml
    cohorts.yaml
    experiment.yaml
  data/
    raw/cosmetics/
    raw/hillstrom/
    processed/
    manifests/
  warehouse/
  dbt/
    dbt_project.yml
    profiles.example.yml
    models/staging/
    models/intermediate/
    models/marts/
    tests/
  src/retention/
    cli.py
    ingest.py
    profiling.py
    snapshots.py
    features.py
    modeling.py
    calibration.py
    evaluation.py
    scoring.py
    cohorts.py
    experiments.py
    hillstrom.py
    reporting.py
    provenance.py
  app/
    Home.py
    pages/
    components/
  notebooks/
  tests/
    unit/
    integration/
    ui/
  docs/
    learning/
    decisions/
  artifacts/<run_id>/
    metrics/
    models/
    predictions/
    audiences/
    figures/
    reports/
    slides/
    screenshots/
  STATUS.md
  HANDOFF.md
```

Expose and verify simple commands such as:

```text
make setup
make doctor
make download
make demo
make reproduce MODE=full
make dashboard
make test-fast
make test-integration
make presentation
```

Also expose individual CLI steps for profile, build, train, evaluate, score, cohort generation, Hillstrom analysis, reports, and a single-customer trace. `make reproduce` must run noninteractively after authorized data access has been configured. The dashboard command must serve the built application; do not leave the app dependent on an open notebook.

## 5. Business and metric contracts before modeling

Write a brief business document with the intended decision, audience, constraints, metric tree, and explicit assumptions. Include a reconstructed marketing requirements sheet and stakeholder questions, labeled as proposed requirements rather than actual historical conversations.

Create a data dictionary and a metric contract defining grain, numerator, denominator, window, unit, eligibility, missing-value handling, and limitations. Use exact names such as:

- observed customer / observed buyer;
- purchasing day;
- inferred purchase occasion;
- historical purchase-event value proxy;
- 28-day observed repurchase rate;
- 28-day non-repurchase risk;
- eligible candidate population;
- selected audience and suppression counts;
- historical risk-ranking lift;
- campaign treatment effect, only for a real randomized comparison;
- assumed incremental contribution, only in a scenario calculation.

Do not call every event a session or order. Do not call a first appearance “acquisition” without an observed-history qualification. Do not label purchase-event value as audited revenue, profit, customer lifetime value, or money saved.

Distinguish these four evidence categories throughout the app and reports:

`OBSERVED`, `MODEL_ESTIMATE`, `ASSUMPTION_SCENARIO`, `NOT_AVAILABLE`.

Add dataset and run identifiers. A screenshot must remain understandable without its surrounding notebook narrative.

## 6. Ingestion, cleaning, and the analytical data model

Preserve immutable raw input and implement a documented canonical analytical view.

Inspect missingness by month and event type, duplicate patterns, timestamp parsing, coverage gaps, unusually active identifiers, invalid prices, and inconsistent product/session identifiers. Produce an exclusion waterfall with counts and percentages. Source problems are part of the learning material, not something to hide.

### Critical semantics

- Treat identifiers as strings or explicitly safe integer identifiers, never floating point. Preserve category IDs exactly.
- Parse timestamps into UTC and use half-open intervals consistently.
- Preserve source file and row provenance. Distinguish a source-row identity from a content hash used to detect identical records.
- There is no verified order identifier in the expected cosmetics schema. For a useful proxy, group same-user purchase events at the same timestamp into an **inferred purchase occasion**. Compare this with purchasing-day and user/session-based counts. Never relabel the proxy as a true order count.
- Identical purchase rows could be duplicated instrumentation or multiple identical units when quantity is absent. Preserve raw multiplicity, document the default analytical policy, and show sensitivity of monetary and occasion metrics to exact deduplication. Do not confidently “fix” ambiguity away.
- Use purchasing days for robust frequency features and binary purchase existence for the target. A valid purchase event still counts behaviorally even if its price is missing or invalid.
- Treat price-derived totals as purchase-event value proxies. Check currency documentation; until verified, use source monetary units, not an invented currency symbol. Exclude or separately flag invalid prices for value calculations without erasing valid behavioral purchases.
- Cart removals are not refunds. Missing cart records do not prove a customer abandoned checkout. Define any cart-without-purchase signal using only observed events and clearly state its meaning.
- Scope session keys to the customer. Inspect whether provided sessions are reliable. If missing or clearly broken, optionally infer sessions from a configurable 30-minute inactivity gap and disclose this derivation. Do not reconstruct past session features using events that occurred after the scoring cutoff.
- Do not fill missing product attributes from later events. If product attributes change, use event-time values or an as-of dimension with no future backfill.
- Do not inner-join current activity to define the customer universe: a previously purchasing customer with no recent events must remain eligible if they meet the historical eligibility rule.

Build tables with documented grains, for example:

- `stg_cosmetics_events`: one standardized source event, with quality flags and duplicate metadata.
- `int_behavior_events`: documented canonical activity events.
- `fct_purchase_occasions`: inferred purchase occasions, explicitly labeled.
- `fct_customer_day`: one customer and calendar day, including behavioral aggregates.
- `dim_customer_observed`: observed identity and history metadata; calculate time-sensitive values as of each cutoff.
- `mart_customer_snapshot`: one customer and scoring cutoff, features and eligibility only.
- `mart_customer_outcome`: separately stored future-window outcomes and maturity flags.
- `mart_customer_scores`: one scored customer, cutoff, model version, and run ID.
- `mart_winback_audience`: candidate policy, priority, suppression status, and reason codes.
- `mart_retention_cohort`: mature cohort metrics with explicit denominators.
- separate `hillstrom_*` tables, with no cross-dataset joins.

Validate uniqueness, join cardinality, aggregate reconciliation, and conservation of included/excluded records. Avoid a full customer-by-day cross join when a sparse event aggregation plus a compact customer-by-cutoff grid is sufficient.

## 7. Define the prediction task correctly

This is non-contractual retail: use a forward-looking **non-repurchase proxy**, not a claim that the customer permanently churned.

For scoring timestamp `t`:

- Historical feature window: `[t - 60 days, t)`.
- Eligible model population: observed customers with at least one valid purchase event in that same historical window.
- Outcome window: `[t, t + 28 days)`.
- `repurchase_28d = 1` when at least one valid purchase event occurs in the outcome window.
- `non_repurchase_28d = 1 - repurchase_28d`.
- A label is usable only when the whole outcome window is covered by the source observation period and passes coverage checks. Otherwise, labels are null and excluded from supervised evaluation.

For this project, the published “churn propensity” is `P(non_repurchase_28d = 1 | information available before t)`. The dashboard must explain this definition in plain English. A customer purchasing on day 29 is not evidence that the 28-day label was miscomputed; it is a limitation of the chosen horizon.

Do not build a contemporaneous “no purchase in the last 28 days” label and predict it from the same recency used to define it. That would be a tautology, not a forward-looking model.

Use this initial chronological plan, subject to actual source-coverage validation:

| Purpose | Feature cutoff, UTC | Outcome interval, UTC |
|---|---|---|
| Train | 2019-12-01 00:00 | [2019-12-01, 2019-12-29) |
| Validation | 2019-12-30 00:00 | [2019-12-30, 2020-01-27) |
| Final test | 2020-01-28 00:00 | [2020-01-28, 2020-02-25) |
| Latest observed-period scoring | 2020-03-01 00:00 | Unknown future; no observed label |

The latest scoring cutoff assumes the February archive covers the full month, including leap day. Validate that assumption; do not infer guaranteed complete coverage solely from the last recorded event timestamp. If dates must change, preserve feature history, outcome maturity, and chronological isolation, and write a decision record before comparing models.

Enforce that all training labels mature before the validation scoring cutoff and all validation labels mature before the test scoring cutoff. Feature histories may overlap in calendar time; that is not by itself leakage. It is legitimate for the same real customer to appear at successive cutoffs because the intended use is repeated scoring of existing customers. Do not include customer identity as a predictor. Explain that this evaluation does not establish performance on an entirely new customer population.

Default to one row per customer per cutoff. Do not create many overlapping weekly snapshots just to inflate sample size. Add rolling-origin analysis only after the core version works, with outcome-window purging, availability checks, and customer-clustered uncertainty estimates.

For a 14- or 42-day horizon sensitivity, construct a separately valid temporal plan; do not reuse invalid overlapping splits or treat immature outcomes as negatives. Do not choose the horizon that makes the final test look best.

## 8. Exploratory analysis and feature engineering

Perform early feature exploration on training-period data. Keep final-test outcomes out of model selection and narrative cherry-picking. A source-wide data-quality inspection is acceptable; using test outcome relationships to design features is not.

Answer and visualize:

- How many identifiers become observed buyers, and how many return within observable follow-up windows?
- What do observed purchase gaps look like, with right-censoring acknowledged rather than studying only repeat purchasers and assuming they represent everyone?
- Are customers with reduced recent activity less likely to repurchase?
- Are recent browsers/cart users behaviorally different from fully inactive previous buyers?
- Do new-to-observation and repeat-buyer groups behave differently?
- How much does monetary-proxy concentration influence a marketing priority list?
- Are apparent changes associated with tracking coverage or holiday-period composition rather than a behavioral shift?

Create a manageable, documented feature set of roughly 25–40 features, not thousands of opaque encodings. Include:

**Purchase history:** days since last purchase; purchasing days over 7/14/28/60 days; inferred occasions; historical purchase-event value proxy over 28/60 days; positive-value share/missingness; median historical occasion value proxy; first-observed-purchase age; observed repeat-buyer indicator; historical purchase-gap summaries where identifiable.

**Digital engagement:** days since last observed event; days since last view/cart; active days and reliable/inferred sessions over 7/14/28 days; view and cart counts; cart-removal counts; unique products/categories viewed; observed cart-without-purchase indicators.

**Change and preference:** activity over the most recent 14 days versus the preceding 14 days; absolute change and a safe relative change; number of distinct purchasing categories; purchase/view concentration in a category; missing-history and insufficient-baseline flags.

All first/last events and global encodings must be calculated as of the cutoff. “First observed” is not true customer tenure. Never calculate interpurchase gaps from future transactions. Never use future-session totals, next purchase date, target-window activity, a later product mapping, or full-dataset target encodings as predictors.

For each feature, store its name, business interpretation, source grain, precise SQL formula/window, null behavior, expected direction as a hypothesis, and leakage risks. Relative decline with no prior baseline must be null or separately flagged, not infinite or automatically “100% decline.” Fit imputation/scaling/capping and feature selection only on the appropriate training partition.

Include observed-history RFM-style segmentation for interpretability. Derive data-dependent cut points from training data and freeze them for validation/test; label monetary inputs as proxies. RFM is a baseline, not a substitute for a churn label or proof of true lifetime value.

## 9. Modeling, evaluation, and what counts as improvement

Train and compare:

1. A constant-prevalence baseline.
2. A simple recency/RFM rule or recency-only probabilistic baseline.
3. Regularized logistic regression.
4. One restrained tree-based challenger, preferably scikit-learn histogram gradient boosting to avoid unnecessary platform dependencies.

Run the crucial ablation: purchase-only features versus purchase plus digital behavior, using the same cohorts and evaluation rules. This directly tests the resume’s purchase-and-digital-behavior story. Report a null or negative incremental contribution honestly.

Use a small declared tuning budget. A customer-disjoint internal split within the training snapshot may be used to choose base-model hyperparameters; label it as internal development, not the final out-of-time evaluation. Train the chosen base model on the training snapshot only.

Use validation customers, split deterministically into calibration and policy-selection subsets, for probability calibration and choosing operating rules. No customer belongs to both validation subsets. The base model can have seen the same identity at an earlier legitimate training cutoff; the validation feature/outcome records themselves remain held out. Evaluate uncalibrated and calibrated probabilities and use a conservative calibration method supported by sample size.

Freeze the base model, calibrator, feature contract, cutoffs, and selected operating policy before final-test evaluation. Do not refit the base model on validation labels and reuse a now-mismatched calibrator without a new, properly separated calibration design. Record freeze timestamps and artifact hashes. After test unblinding, fixes affecting the specification must be disclosed as post-test changes rather than silently preserving a “pristine” test claim.

Required outputs:

- Cohort counts and label prevalence for every split.
- ROC-AUC; average precision explicitly named and implemented, not ambiguously conflated with trapezoidal PR-AUC.
- Average precision for both the non-repurchase class and the complementary repurchase class, each with the relevant prevalence reference.
- Brier score, log loss, and reliability diagrams against the constant baseline.
- Precision, recall, gain/capture, and risk-ranking lift for fixed top 5%, 10%, and 20% audiences, with deterministic tie-breaking and actual K shown.
- Confusion matrix at an operating threshold chosen before test inspection, not an arbitrary accuracy-maximizing test threshold.
- Performance by observed one-time/repeat buyer and historical value bands, with group sizes and uncertainty cautions.
- Confidence intervals using customer-level resampling for the single-snapshot test; resample customer clusters if multiple snapshots are later pooled.
- Stability summaries across cutoffs: feature missingness, score distribution, calibration, and mature-label quality. Do not pretend five historical months establish long-term production stability.

High accuracy or high AP can be uninformative when non-repurchase is very common. Explain the prevalence baseline and show whether ranking adds practical value at the chosen capacity. Do not oversample or undersample before splitting. Avoid SMOTE as a default; if any imbalance handling is used, preserve evaluation prevalence and verify calibration.

Use logistic coefficients and held-out permutation importance for explanations. Optional SHAP is permitted if installation/runtime is reasonable, but not required. Separate **model explanation** from **business reason codes**. Neither establishes a causal reason for disengagement.

Create a model card with intended use, feature/label definition, training coverage, evaluation limits, identity limitations, proxy limitations, and deployment caveats. Persist model artifacts, preprocessing, calibration, feature order, environment versions, and every evaluation result.

## 10. Convert scores into defensible win-back candidates

Create behavioral flags and a deterministic, mutually exclusive primary segment using documented precedence. Suggested segments to operationalize and refine using training/validation evidence:

- high-historical-value customers with a meaningful observed activity decline;
- lapsed purchasers still browsing or adding products to carts;
- observed one-time purchasers whose second purchase has not yet occurred;
- longer-inactive, lower-historical-value customers for a low-cost reactivation test;
- recent/active purchasers to suppress from this win-back policy;
- insufficient-quality or insufficient-history cases to withhold from model-driven action.

Use a configurable recent-purchase suppression window, initially seven days as a **business assumption**, not a discovered fact. Define all other thresholds explicitly and lock them before final-test use. Permit overlapping explanatory flags, but reconcile the primary segment counts to the eligible population. Do not silently force every buyer into an at-risk segment.

Recent browsing is evidence of engagement, not proof that someone is persuadable. Do not call people “sure things,” “lost causes,” or “persuadables” as known individual facts from the observational churn model.

Implement and compare equal-capacity candidate policies: recency-only, risk-only, historical-value-only, and a transparent risk-plus-value heuristic. Label the last one a prioritization heuristic, not expected incremental profit or optimal treatment policy. Never calculate “revenue saved” by multiplying risk by historical spend.

For each segment, provide a short proposed marketing brief: observed signal, hypothesis, proposed message/offer type, why a holdout is needed, success metric, and relevant safeguards. Message templates are proposed examples, not records of actual campaigns. Missing inventory means recommendations are category-interest suggestions, not promises that products are available.

Build a candidate export including:

`dataset_id, run_id, as_of_date, user_id, model_version, feature_contract_version, risk_probability, risk_rank, primary_segment, historical_value_proxy, priority_policy, reason_codes, eligibility_status, suppression_reason, contactability_status, consent_status`.

Use `unknown` for missing contactability and consent. Distinguish **analytically eligible** from **operationally contactable**. The export is a local analytical handoff; no emails, advertising uploads, CRM writes, or outreach are authorized. Do not generate fake email addresses or silently convert unknown consent into permission.

Keep future outcomes out of scoring and audience schemas. For retrospective diagnostics, join mature labels only into a separate evaluation table. An observed spontaneous return among selected customers is not a campaign win.

## 11. Campaign economics and a proposed experiment

### Scenario calculator, not fabricated ROI

Provide a clearly separated what-if calculator. Inputs must be marked as user assumptions unless directly measured and appropriately usable. Missing inputs stay missing; do not replace them with apparently factual defaults.

Let:

- `p0` be the assumed no-contact conversion probability;
- `delta` be the assumed absolute campaign effect;
- `p1 = p0 + delta`;
- `V` be assumed gross basket value per conversion;
- `m` be contribution margin fraction before the modeled incentive;
- `D` be incentive cost per redeemed conversion;
- `r` be the redemption fraction among treated conversions;
- `c` be contact cost per assigned treatment customer.

Under explicit simplifying assumptions of equal basket value/margin across potential conversion outcomes:

`incremental_contribution_per_contact = delta * V * m - p1 * r * D - c`

`scenario_total = selected_contact_count * incremental_contribution_per_contact`

The incentive cost applies to natural converters too, not only incremental converters. Avoid double-counting the discount inside both V/m and D. Enforce valid probability and cost ranges. Show break-even conditions and flag infeasible break-even scenarios. Do not interpret an observational repurchase prediction as an identified untreated counterfactual. Do not use Hillstrom effects as estimates for this retailer.

A blank-input state, an explicitly loaded hypothetical example, and sensitivity curves are appropriate. “Assumed +1 percentage point effect” and “observed +1% relative lift” are different and must never be mixed.

### Proposed future experiment for Track A

Write a campaign experiment protocol with a no-contact control, a reminder/content arm, and an incentive arm, subject to available audience size and the actual business question. Reduce to one treatment versus control if a three-arm design is infeasible; document why.

Specify eligibility at assignment, exclusions, stable customer-level assignment, treatment proportions, an assignment registry to avoid accidental reassignment, overlapping-campaign contamination controls, observation windows, and intention-to-treat analysis. Assignment files are a **dry run**, not an executed intervention.

Primary outcome: 28-day observed repurchase. Secondary outcomes can include purchase-event value proxy and engagement, with limitations. Production guardrails such as unsubscribes, complaints, returns, and margin require additional data and must be listed as unavailable here.

Implement a power/MDE calculator for a two-proportion comparison. Require or explicitly label the assumed control rate and desired absolute effect. Show sensitivity to those assumptions, alpha, power, and allocation. Account for two primary treatment-versus-control comparisons when planning a three-arm test; use a stated multiplicity approach. Produce an analysis template with confidence intervals, sample-ratio checks, ITT denominators, and an analysis-freeze record.

Do not randomize historical cosmetics customers after the fact and call their pre-existing outcomes evidence of a real treatment effect.

## 12. Independent Hillstrom campaign incrementality lab

Build this after the main retention pipeline works. It is a required companion module, but it must not distract from finishing Track A.

Inspect arm counts, missing values, pre-treatment balance, and outcome consistency. Preserve the original random assignment. Do not deduplicate different customers merely because their aggregate attributes happen to be identical. If no customer key is present, create a stable source-row identifier for local record tracking, not a cross-dataset identity.

Produce real observed summaries for all three arms: sample size, website visit rate, conversion rate, and mean spend **per assigned customer**. Estimate email-versus-control absolute differences, relative differences where defined, and confidence intervals. Use conversion as the primary purchase-related endpoint, with visits/spend secondary; distinguish unadjusted intervals from multiplicity-adjusted tests for the two email-versus-control comparisons. Do not condition spend comparisons on conversion and then call them population treatment effects.

For an introductory uplift comparison:

- Restrict the first model to `Mens E-Mail` versus `No E-Mail`; do not choose the treatment after comparing which looks best.
- Use a fixed customer/row-disjoint train/validation/test split, stratified by treatment. This dataset does not contain a comparable longitudinal event timeline; do not invent a chronological split.
- Use only pre-treatment attributes. Exclude all post-treatment outcomes—`visit`, `conversion`, and `spend`—from the feature matrix, along with record identifiers. Treatment is handled explicitly by the modeling method, not accidentally treated as a customer characteristic.
- Compare response targeting with a simple two-model/T-learner uplift estimate `P(Y=1|T=1,X) - P(Y=1|T=0,X)`, using the known randomized treatment mechanism.
- Use `visit` as a clearly labeled engagement-uplift learning target when purchase events are too sparse for stable heterogeneous-effect modeling. Keep actual conversion and spend effect estimates in the experiment readout. Do not quietly redefine visits as retained customers or purchases.
- Evaluate frozen ranking policies on the untouched test partition with gain/Qini or uplift-at-K, arm counts, uncertainty, and explicit metric definitions. Use an implementation/reference such as scikit-uplift, rather than inventing a convenient curve formula.
- Compare treat-all, treat-none, random-capacity selection, response-based selection, and uplift-based selection on a consistent two-arm population. If implementing off-policy values, use the actual randomized assignment probability with a documented IPW estimator and its limitations. Do not score hypothetical observed outcomes for actions that did not occur.
- Low support, noisy rankings, or no robust advantage must be reported, not polished away. These are estimates of heterogeneous effects, not ground-truth labels for individual customer types.

Keep all charts marked “Hillstrom randomized email experiment — independent dataset.” Its 14-day outcomes must not be pooled with Track A’s 28-day outcomes. Add a one-page explanation of the three different concepts: churn risk, response probability, and treatment uplift.

## 13. Dashboard: a decision tool and a teaching tool

Build a polished Streamlit application, not a collection of unconnected charts. Use consistent typography, spacing, numerical formatting, chart titles, axis labels, and compact contextual help. Support a typical laptop viewport without horizontal overflow or clipped controls. Choose an accessible restrained theme; do not mimic confidential company branding.

Every page must show source dataset, run mode, data coverage, scoring cutoff where relevant, and whether displayed values are observed, predicted, or hypothetical. Separate global date filters from fixed model-cutoff filters; do not let a visual filter silently change a metric’s denominator or the model’s target definition.

Required pages:

1. **Overview:** business question, observed population and mature retention metrics, candidate audience size, key supported findings, and the current recommendation.
2. **Customer health:** RFM-style segments, observed purchase-gap/cohort views, activity changes, value-proxy concentration, and cohort-size/maturity labels.
3. **Risk model:** baseline comparison, purchase-only versus combined-feature results, calibration, capacity-based ranking metrics, and clear limitations.
4. **Customer explorer:** a real anonymous buyer’s pre-cutoff timeline, derived feature values, predicted risk, primary segment, reason codes, and a click-through source trace. Only reveal future outcomes in a separate retrospective mode.
5. **Win-back studio:** audience policy/capacity controls, segment breakdowns, exclusions, candidate CSV export, proposed message brief, and a visibly separate assumption-based economics tab.
6. **Campaign lab:** Hillstrom’s actual arm comparisons, uncertainty, response versus uplift targeting, and the proposed cosmetics experiment protocol in a separate section.
7. **Data quality and learning:** coverage/exclusion reports, feature/metric definitions, pipeline status, source provenance, limitations, and the guided chapter links.

Use shared metric/query functions and precomputed marts. Do not retrain models or scan all raw data on a widget rerun. Implement loading states, informative missing-data states, empty filters, invalid inputs, and CSV export reconciliation. Never show hardcoded placeholder KPIs as actual results.

Test filters, selected-user changes, cohort thresholds, download contents, zero-size audiences, missing artifacts, and both historical and latest-unlabeled scoring views. Capture actual application screenshots after tests; generated mock screenshots do not satisfy this requirement.

## 14. The learning journey is a first-class deliverable

The owner should understand the project, not merely possess its artifacts. Create `docs/learning/START_HERE.md` and approximately ten short, ordered chapters, supported by four to six executable walkthrough notebooks that import the real project modules.

Suggested progression: business framing; source inspection; cleaning and grains; label design and time windows; SQL feature construction; baselines and the ML model; evaluation and calibration; marketing cohorts; randomized campaign measurement; dashboard and final recommendation.

For each chapter include:

- the business question;
- the concept in plain English;
- exact files/functions/SQL models to inspect;
- a small runnable command or query;
- what was actually observed in this run;
- one common mistake and a test that catches it;
- two learning exercises, with answers in a separate file.

Use concise decision rationales and evidence, not private chain-of-thought transcripts or an enormous unstructured reasoning dump.

Generate a worked **one-customer walkthrough** from actual source data. Choose a reproducible example, display its exact pre-cutoff events, manually reconcile several feature values, show its score/segment, and separately show a mature future outcome. Add an actual false positive and false negative where the data supports them; do not invent representative people or guaranteed examples. Explain that model reason codes are not proof of why that person did not purchase.

Include a SQL workbook with around 12 focused business questions, model SQL answers, and real result excerpts. Provide a roughly 10-minute demo script and a 30-minute technical walkthrough. Include a glossary of RFM, observation window, label window, censoring, leakage, calibration, lift, MDE, ITT, and uplift, with the project’s concrete examples.

## 15. Final written outputs and presentation

Generate artifacts from the actual run, not a hand-entered parallel set of results:

- A concise business brief and proposed marketing requirements.
- Source/data dictionary, quality report, exclusion waterfall, metric/feature contracts, and reproducible data manifest.
- An analytical report with EDA, model results, ablation, customer examples, cohort policy comparison, limitations, and a supported recommendation.
- A model card and scoring/monitoring runbook.
- Candidate audience CSV/Parquet, suppression audit, campaign briefs, economics scenarios, and the proposed randomized experiment protocol.
- A separate Hillstrom experiment readout and uplift-learning results.
- A one- to two-page executive memo with a clear decision and no fabricated achieved benefit.
- A BI handoff: curated CSV/Parquet tables and a Tableau/Power BI dashboard specification with grains, relationships, measures, filters, and chart mappings. Do not pretend a native workbook exists unless actually created and opened.
- A learning guide, SQL workbook, demo script, and interview notes.

Create an editable **12–14-slide PPTX**, a matching PDF, and the generation source. Use available local presentation/rendering tools; inspect what is installed before selecting a pipeline. A slide HTML source is welcome as a portable fallback, but disclose any format that cannot actually be produced. Render and visually inspect the slides for clipping, unreadable charts, broken fonts, and inconsistent numbers.

Suggested slide narrative:

1. Business decision and reconstruction disclosure.
2. Source datasets and why their identities/results remain separate.
3. Data coverage and quality limitations.
4. Forward-looking retention definition and time-window diagram.
5. Observed disengagement patterns.
6. Features and purchase-versus-digital ablation.
7. Out-of-time model/baseline performance.
8. An actual customer trace.
9. Candidate cohorts and proposed actions.
10. Economics sensitivity, clearly hypothetical.
11. Proposed retailer experiment.
12. Actual Hillstrom campaign evidence, clearly independent.
13. Recommendation, uncertainties, and next data needed.
14. Sources and methodological appendix, if needed.

Use decision-oriented slide titles only when supported by computed results. Add speaker notes explaining evidence and caveats. No invented accuracy, saved revenue, deployed campaigns, or company-scale impact. No anonymous stock charts or copied other people’s project results.

Create `results_manifest.json` as the source of truth for reportable numbers. For every metric store value, unit, numerator/denominator when relevant, dataset, run mode, as-of/outcome windows, split, method, uncertainty if computed, and artifact/query provenance. Reports, dashboard KPIs, and slides must load these outputs rather than independently retype totals. Automated reconciliation should detect inconsistencies.

## 16. Tests and acceptance gates

Use tiny, explicitly artificial fixtures only for edge-case tests. Use real whole-customer samples for integration and actual final data for release verification. Keep the fast suite small; do not rerun downloads/training for documentation or layout changes.

Mandatory checks include:

- Exact-cutoff event is excluded from features and included in the outcome; exact outcome-end event is excluded from that outcome.
- Incomplete future windows produce null labels, never assumed non-repurchase.
- A prior buyer with no current events is retained in the snapshot universe.
- A purchase with missing price still counts for purchase presence; value flags remain correct.
- Duplicate policy, inferred occasion logic, and source-row conservation are tested.
- Session and product mappings cannot use post-cutoff events.
- Feature maxima are strictly before cutoffs; train/validation label maturity precedes the next evaluation origin.
- No ID or target-derived column can enter the model feature allowlist.
- Preprocessing and calibration use only authorized partitions.
- Partition, run-mode, and dataset separation cannot be bypassed silently.
- Scores survive save/load with matching feature order and appropriate numerical tolerance.
- Segment precedence, recent-purchase suppression, audience uniqueness/capacity, and empty audiences work.
- Unknown consent/contactability never becomes a sendable status.
- Export rows/aggregates reconcile to the dashboard.
- Scenario mathematics charges incentives for natural converters too and rejects invalid assumptions.
- Hillstrom post-treatment columns cannot enter features; arm labels remain intact; no row deduplication based only on equal attributes.
- Real experiment metrics and hypothetical retailer metrics have distinct names/dataset provenance.
- UI renders, filters work, and downloaded files contain the displayed audience.
- At least one full-data end-to-end run completes, or its precise blocker is prominently disclosed.
- Final documents/presentation load, render, and reconcile to the metrics manifest.

Never delete a failing correctness test merely to finish. Repair the implementation or explain a defensible change to the contract. Thresholds for “good enough ML performance” are not test assertions; correct evaluation and honest reporting are.

## 17. Phased implementation and handoff

Keep `STATUS.md` updated with completed, in-progress, blocked, and not-run stages, exact commands, and artifact locations. Maintain short decision records with the question, options, choice, evidence, limitations, and reversal trigger.

Execute in this order:

**Phase 1 — Preflight and contracts.** Inspect the machine, establish the repository/environment, validate sources/access, record assumptions, and lock initial grains, labels, and dates.

**Phase 2 — Real-data vertical slice.** Acquire both sources as permitted; build the dev-mode ingestion → snapshot → baseline → one dashboard page path. Verify end-to-end behavior before creating an elaborate UI.

**Phase 3 — Core data and analytics.** Complete quality profiling, dbt models, features, EDA, and leakage/boundary tests.

**Phase 4 — Models and candidate policies.** Train comparisons, calibrate, freeze policies, run final evaluation, generate latest-period scores, and create audience/experiment outputs.

**Phase 5 — Independent incrementality lab.** Implement Hillstrom arm comparisons and a restrained response-versus-uplift comparison.

**Phase 6 — Product and learning.** Complete dashboard pages, customer traces, learning materials, BI exports, and UI tests.

**Phase 7 — Full run and communication.** Execute the full-data pipeline, generate coherent reports and PPTX/PDF, inspect rendering, reconcile metrics, and prepare the final handoff.

Do not ask for approval after every routine stage. Ask only when a genuinely blocking access, permission, resource, or material ambiguity cannot be resolved safely from the brief. Do not install system-wide tools, create accounts, spend money, publish data, or send communications without permission.

At handoff, provide:

1. Exact setup/reproduction/dashboard commands that were verified.
2. A concise artifact index with real paths.
3. Actual source counts, completed run IDs, important measured results, and the main business recommendation.
4. Clearly separated limitations, unavailable fields, unexecuted stages, and optional extensions.
5. A reading order: the first chapter, first SQL query, first real-customer trace, and dashboard page to open.
6. An evidence matrix mapping the original resume sentence to reconstruction artifacts, without turning reconstruction results into historical employment claims.

For interview preparation, provide a 90-second reconstruction explanation and a deeper technical walkthrough. Keep a separate list of original-project details the owner would need to verify from memory. Do not write fabricated first-person statements about what was delivered at Macy’s.

Begin by inspecting the workspace and local environment, then implement Phase 1 and continue through the build. The end state should be something the owner can run, inspect, and learn from—not another prompt describing what someone else should build.
