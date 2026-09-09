# Customer Retention & Win-Back Analytics

A working, local-first public-data reconstruction of the business problem behind Nikita Thakur's retention analytics resume statement. It is **not original Macy's data, implementation, or measured company impact**. The REES46 2019–2020 event data and the independent 2008 Hillstrom randomized experiment never share identities or results.

## Start locally

Run these commands from `retention_winback_codex_kit/project`:

```bash
make setup
make doctor
make download
make demo                      # Real whole-customer development sample
make reproduce MODE=full       # Full population; resumes existing frozen artifacts
make test-fast
make test-integration MODE=full
make dashboard                 # http://127.0.0.1:8501
```

`make setup` uses the Python 3.11–3.13 interpreter on your PATH, creates `.venv`, installs a local uv executable, and syncs `uv.lock`. The tested machine uses Python 3.12.8. The latest successful `make reproduce` receipt lists executed and reused stages separately. Existing model/test artifacts remain frozen; a redesign requires a new run version and evaluation disclosure.

Downloading uses the official KaggleHub API, caches cosmetics version 6, and records every file hash. An optional `COSMETICS_DATA_DIR` can point to the five original monthly CSVs. Supported Kaggle authentication is `kagglehub.login()` or the documented local token file. Never put tokens in this repository. Hillstrom acquisition used the documented scikit-uplift fallback after the original author URL failed.

The analytics and dashboard need no paid/cloud service. Slide generation uses the Codex bundled Node artifact runtime and bundled headless LibreOffice/Poppler. On another installation set `CODEX_ARTIFACT_RUNTIME` to its dependency root, `CODEX_PRESENTATION_SKILL` to its installed presentation skill, and `RETENTION_NODE` to its Node executable. Without that runtime, the analysis/dashboard still run; the editable deck stage has an explicit local-tool dependency.

## What was actually run

Full cosmetics run: **20,692,840 events** in all five monthly archives. Final test: **48,865 eligible buyers**. Validation selected the combined tree model; test **ROC-AUC 0.7838**, **Brier 0.08985** against **0.10771** for the constant baseline. Latest scoring: **49,473 eligible buyers** and **4,948 analytical candidates**. These values are a compact record of `artifacts/full-v1/results_manifest.json`, not original employment results.

The independent Hillstrom analysis retains **64,000 original assignments**. Its held-out visit Qini interval includes zero, so the run does not establish a reliable uplift-targeting advantage. No cosmetics campaign has run and no incremental revenue is claimed.

## Read and inspect

- [Learning start](docs/learning/START_HERE.md): ten chapters, exercises and glossary.
- [Status](STATUS.md) and [handoff](HANDOFF.md): executed checks and limitations.
- [Business brief](docs/business_brief.md), [model card](docs/model_card.md), [experiment protocol](docs/experiment_protocol.md).
- [BI recreation guide](docs/BI_HANDOFF.md), [demo](docs/DEMO.md), [interview boundary](docs/interview_notes.md).
- Local `artifacts/full-v1/reports/analytical_report.md`, `executive_memo.md`, `hillstrom_readout.md`, and `sql_workbook.md`.
- Local `artifacts/full-v1/traces/worked_customer.md`: real event/feature reconciliation with future outcomes in separate files.
- Local `artifacts/full-v1/slides/deck.pptx` and `deck.pdf`: editable deck and matching rendering.

## Reusable entry points

Use `.venv/bin/python -m retention.cli STEP --mode full` for `profile`, `build`, `dbt`, `train`, `evaluate`, `score`, `cohorts`, `hillstrom`, `reports`, `trace`, `supplement`, `learning`, `notebooks`, or `presentation`. `train` refuses to overwrite an unblinded run. Do not manually combine `dev` and `full` outputs. `retention.common.run_dir` enforces their separate artifact roots.

## Data and Git policy

Track code, SQL/dbt tests, configuration, lockfiles, source manifests and learning/documentation source. Ignore `.venv`, `venv`, caches, IDE/OS files, credentials, original/processed records, DuckDB warehouses, trained models, customer exports, screenshots and generated presentations. Executed notebooks live under ignored artifacts; notebook source in Git has no execution outputs.

Raw multiplicity is preserved. **1,109,098 identical excess rows** are disclosed rather than assumed erroneous. Purchasing-day frequency and binary outcomes are robust to exact duplicates; historical value sensitivity is reported separately. Missing or invalid price never erases purchase presence. Provided sessions remain customer scoped. Daily event presence supports coverage but cannot prove no intraday tracking outages.

Consent/contactability, true order IDs, quantity, refunds, verified currency, margin, campaign exposure and cross-device CRM identity are unavailable. First observed purchase age is bounded to the 60-day feature window. Prices are event-value proxies in source monetary units. Candidate exports authorize no outreach. Original-project facts must be verified separately from memory.
