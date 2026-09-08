# Tableau / Power BI recreation guide

No proprietary workbook was created. Local curated Parquet tables are under artifacts/<mode>-v1/bi. Keep those customer records local unless publishing rights and owner instructions permit distribution.

Use customer_scores_<split>.parquet at one observed user + fixed cutoff, and metrics.csv at metric ID + dataset + split. Do not union snapshot counts as unique people. Never join Hillstrom row identities to cosmetics users. If combining score periods, retain cutoff and run ID as part of every relationship.

Overview: eligible buyer count, mature repurchase rate, candidate count. Customer health: primary segment count, recency histogram, purchasing-day frequency and historical-value proxy. Model: Brier, ROC-AUC, both class APs and calibration, fixed test window. Audience: capacity, policy, suppression and segment filters using the same sort/tie rule as retention.cohorts.audience. Experiment: independent arm means and treatment-control intervals per assigned Hillstrom customer.

Always show dataset, run mode, fixed scoring cutoff, interval, evidence type and units. Unknown future labels remain blank. Metrics.csv supplies aggregate values; per-customer probability is a model estimate. Scenario controls must be labeled assumptions and never overwrite observed metrics. Table filters must not silently redefine denominators of precomputed evaluation metrics.
