# Execution status

Updated 2026-09-08. This is a public-data reconstruction, not historical employment results.

- Phase 1 COMPLETE: Python 3.12 environment and uv lock tested; real-source acquisition pinned and hashed. 16 GiB RAM, bounded 4 GiB DuckDB / four threads. Stable dbt 1.10 used after experimental parser package installation failed TLS validation.
- Phase 2 COMPLETE: real whole-customer dev sample ingestion, snapshots, model and initial dashboard rendered.
- Phase 3 COMPLETE: 20,692,840 full source events; five months present, 152 daily coverage dates. SQL/dbt build and 10 tests pass. Raw multiplicity retained, including 1,109,098 identical excess rows. Intraday tracking completeness cannot be proven.
- Phase 4 COMPLETE: six frozen full-data candidates, disjoint validation calibration/policy selection, final test, latest scoring, audience and dry-run assignment. Full test N=48,865; selected tree_combined ROC-AUC=0.783826, Brier=0.089854. Latest eligible N=49,473; analytical candidates=4,948. Consent/contactability unknown.
- Phase 5 COMPLETE: independent real Hillstrom N=64,000; ITT arm comparisons, fixed split T-learner, uncertainty and IPW policy comparisons. Visit Qini interval includes zero, so heterogeneous targeting advantage is not established.
- Phase 6 IN PROGRESS: seven pages render, initial unit/UI suite 12 passed; full integration suite 4 passed. Browser layout review underway. Ten learning chapters and five notebooks generated; notebook execution pending. Real customer features and source rows reconcile, future outcomes separate.
- Phase 7 IN PROGRESS: full computational stages executed and logged under artifacts/full-v1/execution. Reports and metrics manifest generated/reconciled. Editable slides/PDF and final visual review pending.

## Git checkpoints

- 02325f4: specification, contracts and environment setup (pushed).
- 8fea45d: real-data pipeline, modeling and campaign analysis (pushed).

Only source code, configuration, dependency lock, guidance and compact provenance/status documents belong in Git. Data, derived customer records, model binaries, figures/screenshots and presentation outputs remain local under ignored artifacts/data directories.

## Verification caveats

Read-only trace inspection initially used the host timezone; connection timezone is now UTC and trace totals pass. This changed display/reconciliation, not trained features or test design. Optional 14/42-day horizon and rolling-origin extensions were not run. No original-project results, deployed campaigns or causal retailer benefit are claimed.
