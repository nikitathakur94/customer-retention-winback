# Sources and implementation references

Research date: **7 September 2026**. These are source/documentation references, not a claim that dataset archives were downloaded, code was run, or results were independently reproduced. Resolve redirects and recheck current APIs before implementation. Record the actual downloaded version and checksums locally.

## Selected data

### A. REES46 cosmetics events — main retention workflow

**Publisher’s dataset index:** https://rees46.com/en/datasets

The publisher lists cosmetics behavior events covering October 2019–February 2020. This is the primary source for the retail-event reconstruction.

**Dataset card and acquisition entry:** https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-cosmetics-shop

**Handle:** `mkechinov/ecommerce-events-history-in-cosmetics-shop`

Use linked customer purchase and digital-event history. Expect a multi-month, multi-million-event dataset; calculate exact counts and available event types from the files. Do not assume the data contains real order IDs, campaign assignment, margin, consent, or verified CRM identities. Inspect the actual schema and documentation.

The surfaced card uses the license label **“Data files © Original Authors.”** Capture the current terms and keep raw data out of the repository/distribution bundle unless redistribution is clearly permitted. Public accessibility is not a substitute for checking terms.

**Acquisition API:** https://github.com/Kaggle/kagglehub

Consult the official examples for `dataset_download`, version handles, `output_dir`, caching, and supported authentication. This reference supports direct download to a local project or use of a cache. Some public resources require consent/authentication; handle that explicitly rather than inventing data or silently changing datasets.

### B. Hillstrom / MineThatData — independent campaign lab

**Original study and linked CSV:** https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html

The author describes a randomized, three-arm email test among 64,000 customers with a two-week outcome period. Use it for actual campaign incrementality analysis, not for reconstructing cosmetics browsing history.

**Maintained loader and schema reference:** https://www.uplift-modeling.com/en/latest/api/datasets/fetch_hillstrom.html

The loader supports all three outcomes through `target_col="all"`. Keep assignment and pre/post-treatment fields separate. Preserve the original schema and all outcomes in the raw layer.

**Additional official catalog:** https://www.tensorflow.org/datasets/catalog/hillstrom

Useful as a corroborating schema/source reference; there is no need to install TensorFlow merely to obtain this dataset.

**Non-negotiable separation:** no shared customer mapping exists between these selected sources. Keep separate data namespaces, models, dashboard badges, results, and inference claims.

## Engineering references

**DuckDB CSV ingestion**
https://duckdb.org/docs/current/data/csv/overview

Use explicit types and scalable ingestion rather than loading every raw CSV into pandas. Follow any official redirect.

**DuckDB Parquet handling**
https://duckdb.org/docs/current/data/parquet/overview

Use for persisted, queryable analytical data and efficient repeated reads. Confirm supported options for the installed version.

**DuckDB dbt adapter**
https://github.com/duckdb/dbt-duckdb

Use the maintained adapter’s profile and compatibility documentation. Implement a genuine dbt project with executable models/tests, not just a folder named dbt.

**uv project workflow**
https://docs.astral.sh/uv/guides/projects/

Reference for local environments, dependency management, and reproducible project execution. Generate and test the lockfile on the actual target machine.

**Streamlit AppTest**
https://docs.streamlit.io/develop/api-reference/app-testing

Use for fast application logic/state checks. Complement it with actual browser screenshots for layout review; a headless logic test alone does not establish visual correctness.

## Modeling and experiment references

**scikit-learn: leakage and preprocessing pitfalls**
https://scikit-learn.org/stable/common_pitfalls.html

Supports separating training from evaluation and fitting transformations only on permitted data. The project’s explicit timestamp rules remain necessary; a pipeline object alone does not prevent temporal leakage.

**scikit-learn: probability calibration**
https://scikit-learn.org/stable/modules/calibration.html

Reference for calibration curves and held-out calibration. Verify the current estimator API rather than using deprecated prefit examples from an old tutorial.

**scikit-learn: average precision**
https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html

Name and compute this metric consistently. Do not substitute a differently calculated area under a precision-recall curve without labeling it.

**statsmodels: power calculation**
https://www.statsmodels.org/stable/generated/statsmodels.stats.power.NormalIndPower.solve_power.html

Use with a correctly defined two-proportion effect size and documented alpha, power, allocation, and baseline-rate assumptions. The primary project’s 28-day outcome and Hillstrom’s two-week outcome remain distinct.

**scikit-uplift: Qini AUC**
https://www.uplift-modeling.com/en/latest/api/metrics/qini_auc_score.html

Use a stated, tested uplift-ranking metric implementation. Report uncertainty and support; a visually attractive curve is not proof of a reliable policy.

## Source-use rules for generated reports

Cite dataset owners for dataset facts, software documentation for implementation methods, and this project’s own versioned outputs for its measured results. Separate an outside source’s reported facts from measurements actually calculated locally.

Do not reuse published notebook accuracy, campaign-lift numbers, sample findings, or charts as project outputs. Do not copy the original challenge winner’s answer and present it as a fresh result. Do not attach third-party raw data or copyrighted articles merely because a URL is accessible.

Source terms, verified access date, file hashes, code commit, run mode, and metric definitions should travel with the generated artifacts.
