# Project handoff

Completed 2026-09-09. Root: `/Users/nik/Documents/GitHub/customer-retention-winback/retention_winback_codex_kit/project`.

## Start here

1. Read `docs/learning/START_HERE.md`, then the ten chapters in order.
2. Open the dashboard with `make dashboard` and visit Overview, Risk model, Customer explorer and Win-back studio.
3. Read `artifacts/full-v1/traces/worked_customer.md` and `artifacts/full-v1/reports/sql_workbook.md`; run the five notebooks in `notebooks/`.
4. Review `artifacts/full-v1/reports/executive_memo.md`, the model card and experiment protocol.
5. Present `artifacts/full-v1/slides/deck.pptx` or `deck.pdf`. Both are local, generated deliverables; the PPTX contains editable charts.

## Verified commands

Run from the project root:

```sh
make setup
make doctor
make reproduce MODE=full
make test-fast
make test-integration MODE=full
make dashboard
```

Setup and full reproduction completed successfully. Reproduction checks source/feature contracts, reuses frozen computational stages and rebuilds downstream outputs; its receipt distinguishes reused and executed stages. The original full computational run is also logged. All five notebooks executed with the project kernel. Final verification: 13 unit/UI tests, five full-data integration tests, four dbt models and ten dbt tests, and Ruff undefined-name checks passed. Minor local CPU-detection and NumPy deprecation warnings remain.

Dashboard address: http://127.0.0.1:8501. If the process has stopped, `make dashboard` restarts it.

## Measured results and evidence

Full source: 20,692,840 events. Held-out cosmetics test: 48,865 eligible buyers. Frozen tree_combined ROC-AUC 0.783826 and Brier 0.089854 (constant Brier 0.107707). Latest candidates: 4,948 of 49,473 eligible buyers, with unknown consent/contactability. Independent Hillstrom experiment: 64,000 assigned customers; visit Qini 95% interval approximately [-0.0296, 0.0360], so targeting advantage remains uncertain.

Local evidence root: `artifacts/full-v1/`. Consult `results_manifest.json`, `execution/reproduce.json`, `slides/delivery.json`, screenshots and model freeze records. Source provenance is tracked under `data/manifests/`. `ACCEPTANCE_EVIDENCE.md` maps checks to evidence.

## Limits and operational next steps

This is a public-data reconstruction, not original Macy's data, implementation or impact. Risk scores do not estimate incremental campaign benefit. No outreach occurred; proposed assignments are dry runs. Real activation needs verified consent/contactability, campaign overlap checks, economic inputs and a prospective randomized holdout. Intraday source completeness and true order/currency semantics cannot be established. Optional horizon/rolling extensions were not run. BI guidance and exports are supplied, not proprietary BI workbooks. PDF was visually inspected after bundled rendering; Microsoft PowerPoint itself was not opened.

Raw downloads, warehouse, generated customer exports, models and presentation outputs remain local and ignored, along with `.venv`, caches and credentials. Recreate them using the documented pipeline; source downloads require network access and their source terms apply. Presentation generation additionally uses the Codex artifact runtime described in README.md.
