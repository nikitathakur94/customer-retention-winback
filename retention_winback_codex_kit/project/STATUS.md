# Execution status

Updated 2026-09-09. The seven core implementation phases are complete. This is a public-data reconstruction, not historical employment results.

1. Environment and source contracts: complete. Python 3.12, tested uv lock, pinned downloads with hashes and source terms. DuckDB limited to 4 GiB and four threads.
2. Real-data development pipeline: complete. Stable whole-customer sampling across monthly files; separate calibration membership.
3. Full data and marts: complete. 20,692,840 events across five months and 152 dates; 1,109,098 identical excess rows retained and measured. Four dbt models and ten dbt tests pass.
4. Risk and audience: complete. Six frozen candidates, separate validation calibration/selection, final test and latest scoring. Selected tree_combined: test N=48,865, ROC-AUC 0.783826, Brier 0.089854. Latest eligible N=49,473; candidates=4,948. Consent/contactability unknown.
5. Independent experiment analysis: complete. Hillstrom N=64,000; assigned-customer comparisons, out-of-sample uplift and uncertainty. Visit Qini interval includes zero; heterogeneous targeting advantage is not established.
6. Dashboard and learning: complete. Seven pages reviewed in browser, 13 unit/UI tests and five full-data integration tests pass. Ten learning chapters and five successfully executed notebooks; source-reconciled customer traces.
7. Reproduction and handoff: complete. Full computational stages logged; `make reproduce MODE=full` passes with explicit reuse of frozen stages. Reports, editable 14-slide PPTX and rendered PDF produced; all 14 PDF pages visually inspected. Font configuration fixed the PDF fallback font. See HANDOFF.md and ACCEPTANCE_EVIDENCE.md.

## Git checkpoints

- 02325f4: specification, contracts and environment setup.
- 8fea45d: pipeline, modeling and campaign analysis.
- b8e8902: dashboard, full reports and learning.
- Final completion checkpoint: see Git history for this document's commit.

Data, derived customer records, models, screenshots and generated presentations stay in ignored local directories. Source code, dependency locks, notebooks without outputs, documentation and compact provenance are tracked.

## Scope and limitations

Optional 14/42-day and rolling-origin extensions were not run. Native Tableau/Power BI workbooks are not supplied; BI exports and handoff instructions are supplied. Source daily coverage cannot prove absence of intraday outages. Stable dbt was pinned after experimental parser installation failed TLS validation. The deck was rendered with bundled LibreOffice, not inspected in Microsoft PowerPoint. Post-test changes addressed display, UTC trace reads, documentation and export formatting; the frozen model and test design were preserved. No outreach or measured cosmetics campaign effect is claimed.
