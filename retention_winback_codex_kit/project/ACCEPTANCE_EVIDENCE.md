# Acceptance evidence

Verified 2026-09-09. This records execution evidence for the kit checklist; it does not mark optional extensions as executed. Paths below are relative to the project root. Ignored artifacts are available locally and reproduced by documented commands.

| Area | Evidence and result |
|---|---|
| Sources, provenance and identity | `data/manifests/acquisition.json`; `artifacts/full-v1` quality outputs. Five monthly source counts total 20,692,840, with 152 daily dates. Hillstrom remains a separate 64,000-row track. |
| Stable whole-customer development sampling | `tests/integration/test_real_run.py`: source-file sampled counts reconcile to the full source using the customer hash bucket. |
| UTC, identifiers, windows and missing labels | `tests/unit/test_contracts.py`, `tests/integration/test_real_run.py`, `configs/features.yaml`, snapshot SQL and feature contracts. Boundary checks and latest null labels pass. |
| Data semantics and marts | Four dbt models plus ten passing dbt tests; profiling measures exact duplicates without deleting them. Purchase occasions and event-value proxies are explicitly labeled. |
| Model isolation and reproducibility | Saved feature allowlist, frozen model records, disjoint validation calibration/selection; integration prediction roundtrip passes. Source and feature contract validation precedes reuse. |
| Metrics and audience reconciliation | `artifacts/full-v1/results_manifest.json`, model metrics and audience summary. Test N=48,865; latest eligible 49,473; candidate capacity 4,948. Export and dashboard count test passes. |
| Experiment assumptions | Unit checks cover economics and assignment behavior; Hillstrom reports use assigned denominators and independent out-of-sample evaluation. Unknown operational inputs remain missing. |
| Seven-page dashboard | `tests/ui/test_app.py`; browser screenshots in `artifacts/full-v1/screenshots/`. Pages rendered with real artifacts. Empty cohorts, fixed test explorer, future reveal and default capacity exercised. |
| Learning and notebooks | Ten chapters in `docs/learning/`; five executed notebooks under `artifacts/full-v1/executed_notebooks/`; SQL workbook and source-reconciled worked trace. |
| Full execution | `artifacts/full-v1/execution/`: original full stages and successful `reproduce.json`, explicitly distinguishing frozen-stage reuse. |
| Slides and PDF | `artifacts/full-v1/slides/deck.pptx`, `deck.pdf`, `delivery.json`; editable chart validation and all 14 PDF pages visually reviewed. Bundled renderer, not Microsoft PowerPoint. |
| Final code checks | `make test-fast`: 13 passed. `make test-integration MODE=full`: five passed. Ruff F checks passed. |
| Git hygiene | `.gitignore` excludes environments, data, warehouse, generated artifacts, caches and credentials. Notebook source outputs are empty. |

Limitations and unrun optional extensions are stated in STATUS.md and HANDOFF.md. Neither the model ranking nor the independent email experiment establishes an achieved cosmetics or Macy's campaign benefit.
