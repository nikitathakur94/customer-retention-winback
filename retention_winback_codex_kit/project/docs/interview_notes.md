# Reconstruction explanation and historical boundary

Public-data reconstruction inspired by the business problem, not original Macy's data, implementation or measured impact. REES46 events are from 2019–2020, after the motivating role; Hillstrom is an independent 2008 experiment. Modern tooling is not backdated to the employment period.

## A 90-second explanation of this reconstruction

This project examines which observed previous buyers will not purchase in the next 28 days. It preserves anonymous shopping histories, builds purchase and digital features strictly before each scoring date, and uses later purchases only as mature outcomes. A chronological evaluation compares recency, logistic and tree models, including purchase-only versus combined inputs. Calibration and policy selection use disjoint validation customers. The frozen score feeds local candidate cohorts with capacity and recent-purchase suppression; consent stays unknown. An independent randomized email dataset demonstrates treatment effects and the distinction between response and uplift. The final recommendation requires a future holdout before claiming incremental benefit.

## Evidence mapping

- Identify disengagement signals: training_eda.csv, feature contracts, source-reconciled traces, dashboard Customer health.
- Build churn-propensity model: snapshots.py, frozen model bundles, test_metrics.json, purchase/digital ablation.
- Convert scores to win-back cohorts: cohorts.py, suppression audit, local candidate exports, proposed experiment protocol.
- Partner with marketing: proposed business requirements and questions only. This reconstruction does not prove a historical collaboration occurred or identify its participants.

## Original-project facts to verify from memory

Confirm actual data sources, observation windows, algorithm, role boundaries, stakeholder names, operational adoption, experiment design, achieved results and timelines before making employment claims. Do not replace unknown historical facts with reconstruction results.
