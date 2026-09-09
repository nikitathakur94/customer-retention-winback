"""Build ordered local lessons and executable notebooks from real project artifacts."""

import nbformat
from retention.common import ROOT, run_dir, read, connect
from retention.features import FEATURES, PURCHASE
from retention.snapshots import snapshot_sql

CHAPTERS = [
    (
        "business",
        "Which buyers should marketing investigate?",
        "The model estimates a future absence of purchase. It cannot say whether an email changes behavior.",
        "docs/business_brief.md; src/retention/cohorts.py:audience",
        "snapshots.json",
        "Confusing a high risk score with a campaign effect.",
        "tests/integration/test_real_run.py:test_hillstrom_separation",
        "Why is a high-risk customer not automatically a good incentive target?",
        "What additional data makes a candidate contactable?",
        "Risk is observational; a person may not respond to contact.",
        "Verified identity, permission and reachable contact details.",
    ),
    (
        "sources",
        "What can these datasets actually establish?",
        "The cosmetics files contain events. Hillstrom contains randomized assignments. No shared identity exists.",
        "src/retention/ingest.py:download; data/manifests/acquisition.json",
        "quality.json",
        "Calling the two sources one customer database.",
        "tests/integration/test_real_run.py:test_source_and_conservation",
        "Why retain the source file hash?",
        "Why avoid duplicate removal in Hillstrom?",
        "A checksum detects input changes and supports reproducibility.",
        "Identical aggregate attributes can belong to different randomly assigned customers.",
    ),
    (
        "cleaning",
        "Which rows count as valid behavior?",
        "A purchase can count even when its price is unusable. Source multiplicity remains visible.",
        "src/retention/profiling.py:profile; dbt/models/fct_purchase_occasions.sql",
        "quality.json",
        "Removing purchases because their value is missing.",
        "tests/unit/test_contracts.py:test_cutoff_purchase_presence_and_inactive_buyer",
        "What defines an inferred occasion?",
        "Why is it not an order?",
        "One observed user and identical purchase timestamp.",
        "No source order ID or quantity proves an actual order.",
    ),
    (
        "labels",
        "What exactly does a non-repurchase label mean?",
        "Features stop strictly before the cutoff. The following 28 days define a label only when coverage is complete.",
        "src/retention/snapshots.py:build; dbt/tests/maturity_contract.sql",
        "snapshots.json",
        "Treating an unknown future as no purchase.",
        "tests/integration/test_real_run.py:test_snapshot_labels_and_prediction_roundtrip",
        "Where does an event exactly at cutoff belong?",
        "What happens at the outcome end?",
        "Only in the outcome, not the features.",
        "The half-open outcome excludes the exact end timestamp.",
    ),
    (
        "sql_features",
        "How does a timeline become one model row?",
        "SQL groups the complete eligible history by observed user and cutoff. IDs remain keys rather than predictors.",
        "src/retention/snapshots.py:snapshot_sql; configs/features.yaml",
        "snapshots.json",
        "Using current activity to define the buyer universe.",
        "tests/unit/test_contracts.py:test_cutoff_purchase_presence_and_inactive_buyer",
        "Why keep a buyer with no recent views?",
        "What does a missing relative activity change mean?",
        "A prior buyer can still meet the 60-day eligibility window.",
        "The previous 14 days had zero activity, so no relative baseline exists.",
    ),
    (
        "models",
        "Does digital behavior add useful information?",
        "The ablation compares purchase-only and combined predictors on the same buyers. Simpler baselines can win.",
        "src/retention/modeling.py:train; src/retention/features.py",
        "validation_metrics.json",
        "Choosing features by looking at final test labels.",
        "tests/unit/test_contracts.py:test_allowlist_partition_and_ties",
        "Which partition fits the base estimator?",
        "Which partition selects the model?",
        "Only the training snapshot.",
        "The policy-selection half of validation after separate calibration.",
    ),
    (
        "evaluation",
        "Are the scores calibrated and useful for ranking?",
        "Brier score measures probability error. Top-K lift measures concentration of future non-repurchase against the same population prevalence.",
        "src/retention/evaluation.py:metrics; src/retention/calibration.py",
        "test_metrics.json",
        "Calling high accuracy strong evidence under high prevalence.",
        "tests/integration/test_real_run.py:test_snapshot_labels_and_prediction_roundtrip",
        "Why report AP for both classes?",
        "What happens when risk scores tie?",
        "Repurchase is rarer and its AP has a different prevalence reference.",
        "String user ID deterministically breaks ties.",
    ),
    (
        "audiences",
        "How do scores turn into a candidate list?",
        "Rules assign one primary segment. Recent purchases suppress selection. Capacity limits a local analytical export.",
        "src/retention/cohorts.py:segment,audience; src/retention/experiments.py",
        "audience_summary.json",
        "Treating unknown consent as permission.",
        "tests/unit/test_contracts.py:test_segment_precedence_and_audience",
        "Why do incentive costs include natural converters?",
        "Is risk times historical value expected profit?",
        "They also receive the incentive when they convert in treatment.",
        "No. It is a transparent prioritization heuristic without causal or margin identification.",
    ),
    (
        "experiments",
        "How do we estimate what contact caused?",
        "Random assignment makes treatment and control comparable on average. Use all assigned customers, including nonconverters.",
        "src/retention/hillstrom.py:effect,analyze; docs/experiment_protocol.md",
        "hillstrom/experiment.json",
        "Conditioning spend on conversion and claiming a population effect.",
        "tests/integration/test_real_run.py:test_hillstrom_separation",
        "Do Mens creative labels imply customer gender?",
        "Can the effect be reused as the cosmetics campaign effect?",
        "No. They describe merchandise creatives.",
        "No. The populations, intervention and follow-up differ.",
    ),
    (
        "dashboard",
        "What decision can the evidence support?",
        "The app reads precomputed artifacts. Its fixed model window is distinct from interactive candidate policy controls.",
        "app/Home.py; docs/BI_HANDOFF.md",
        "results_manifest.json",
        "Changing a visual filter and silently changing the evaluation denominator.",
        "tests/ui/test_app.py:test_pages",
        "Where are future outcomes revealed?",
        "What makes the recommendation defensible without strong uplift?",
        "Only in a clearly labeled retrospective explorer view.",
        "The recommendation can favor a simple policy or a prospective experiment when evidence is weak.",
    ),
]


def build(mode="dev"):
    p = run_dir(mode)
    dest = ROOT / "docs/learning"
    dest.mkdir(parents=True, exist_ok=True)
    links = []
    answers = []
    for i, (
        slug,
        question,
        concept,
        files,
        artifact,
        mistake,
        test,
        q1,
        q2,
        a1,
        a2,
    ) in enumerate(CHAPTERS, 1):
        name = f"{i:02}_{slug}.md"
        links.append(f"{i}. [{question}]({name})")
        observed = (
            "Read the computed "
            + artifact
            + " for this run; values are not hardcoded into this lesson."
        )
        if (p / artifact).exists():
            obj = read(p / artifact)
            if artifact == "snapshots.json":
                observed = (
                    "Observed eligible counts: "
                    + ", ".join(f"{r['split']}={r['n']:,}" for r in obj)
                    + ". Latest labels remain null."
                )
            elif artifact == "quality.json":
                observed = (
                    "Analytical source rows: "
                    + str(obj["analytical_waterfall"]["source_rows"])
                    + ". Duplicate sensitivity remains in quality.json."
                )
            elif artifact == "results_manifest.json":
                observed = (
                    "Frozen selected model: "
                    + obj["selected_model"]
                    + ". "
                    + obj["recommendation"]
                )
        command = f".venv/bin/python -c \"from retention.common import run_dir,read; print(read(run_dir('{mode}')/'{artifact}'))\""
        (dest / name).write_text(
            f"# {i}. {question}\n\n{concept}\n\n## Inspect\n\n{files}\n\n```bash\n{command}\n```\n\n## Observed in {mode}-v1\n\n{observed}\n\n## Common mistake\n\n{mistake} Guard: `{test}`.\n\n## Exercises\n\n1. {q1}\n2. {q2}\n\nAnswers are in ANSWERS.md.\n"
        )
        answers.append(f"## {i}. {slug}\n\n1. {a1}\n2. {a2}")
    (dest / "START_HERE.md").write_text(
        "# Learning order\n\nStart at the project directory with `make doctor`. Open the Overview dashboard after `make dashboard`. The results describe public-data reconstruction, not original employment outcomes.\n\n"
        + "\n".join(links)
        + "\n\nAfter chapter 4, open the local `artifacts/"
        + mode
        + "-v1/traces/worked_customer.md`. Those customer records stay out of Git.\n"
    )
    (dest / "ANSWERS.md").write_text("# Exercise answers\n\n" + "\n\n".join(answers))
    import yaml

    contracts = []
    for feature in FEATURES:
        contracts.append(
            {
                "name": feature,
                "family": "purchase" if feature in PURCHASE else "digital",
                "grain": "observed user and UTC cutoff",
                "window": "[cutoff-60d,cutoff); nested suffix windows end at cutoff",
                "definition_sql": "src/retention/snapshots.py:snapshot_sql; generated docs/snapshot_reference.sql",
                "null_behavior": "SQL NULL when no reference event or denominator; training-only median imputation. Counts/sums as specified in SQL.",
                "direction": "exploratory hypothesis; no causal interpretation",
                "leakage_guard": "feature_max_timestamp < as_of_timestamp; no metadata backfill",
            }
        )
    (ROOT / "configs/features.yaml").write_text(
        yaml.safe_dump({"version": "1.0", "features": contracts}, sort_keys=False)
    )
    (ROOT / "docs/snapshot_reference.sql").write_text(
        "-- Executed SQL formula reference, generated from the production function.\n"
        + snapshot_sql("2019-12-01")
    )
    # Five executable walkthroughs import production code and use local real results.
    for number, (title, code) in enumerate(
        [
            (
                "Source coverage",
                "from retention.common import run_dir,read\np=run_dir(MODE)\nread(p/'quality.json')['analytical_waterfall']",
            ),
            (
                "Snapshots and labels",
                "import pandas as pd\nfrom retention.common import run_dir\np=run_dir(MODE)\nx=pd.read_parquet(p/'features_test.parquet'); y=pd.read_parquet(p/'outcomes_test.parquet')\nassert (x.feature_max_timestamp<x.as_of_timestamp).all()\nassert pd.read_parquet(p/'outcomes_latest_unlabeled.parquet').non_repurchase_28d.isna().all()\nx[['purchase_recency','purchasing_days_60','value_60']].describe()",
            ),
            (
                "Model comparisons",
                "from retention.common import run_dir,read\nimport pandas as pd\nr=read(run_dir(MODE)/'test_metrics.json')\npd.DataFrame({k:{m:v[m] for m in ['roc_auc','brier','average_precision_repurchase']} for k,v in r.items()}).T",
            ),
            (
                "Candidates and economics",
                "import pandas as pd\nfrom retention.common import run_dir\nfrom retention.cohorts import audience\nfrom retention.experiments import economics\ns=pd.read_parquet(run_dir(MODE)/'scores_latest_unlabeled.parquet')\na=audience(s,10)\nassert a.consent_status.eq('unknown').all()\nprint(economics(.1,.01,100,.3,5,1,0,count=10))\na[['primary_segment','risk_probability']]",
            ),
            (
                "Randomized campaign evidence",
                "import pandas as pd\nfrom retention.common import run_dir,read\npd.DataFrame(read(run_dir(MODE)/'hillstrom/experiment.json')['effects'])",
            ),
        ],
        1,
    ):
        nb = nbformat.v4.new_notebook()
        nb.cells = [
            nbformat.v4.new_markdown_cell(
                f"# {title}\nReal project artifacts only. Public-data reconstruction, separate from original employment claims."
            ),
            nbformat.v4.new_code_cell(f"MODE='{mode}'\n" + code),
        ]
        for cell_number, cell in enumerate(nb.cells):
            cell.id = f"lesson-{number}-{cell_number}"
        nb.metadata = {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            }
        }
        nbformat.write(nb, ROOT / "notebooks" / f"{number:02}_walkthrough.ipynb")
    queries = [
        (
            "How many source events by month?",
            "SELECT source_file,count(*) n FROM source_events GROUP BY 1 ORDER BY 1",
        ),
        (
            "Which event types occur?",
            "SELECT event_type,count(*) n FROM int_behavior_events GROUP BY 1 ORDER BY 2 DESC",
        ),
        (
            "How much duplicate ambiguity exists?",
            "SELECT count(*)-count(DISTINCT content_hash) identical_excess FROM int_behavior_events",
        ),
        (
            "How many purchases have invalid price?",
            "SELECT count(*) n FROM int_behavior_events WHERE event_type='purchase' AND NOT valid_price",
        ),
        (
            "How many observed identifiers?",
            "SELECT count(*) observed_ids FROM analytics.dim_customer_observed",
        ),
        (
            "How many inferred purchase occasions?",
            "SELECT count(*) occasions FROM analytics.fct_purchase_occasions",
        ),
        (
            "How many eligible buyers by cutoff?",
            "SELECT split,count(*) n FROM mart_customer_snapshot GROUP BY 1 ORDER BY 1",
        ),
        (
            "What are mature return rates?",
            "SELECT * FROM analytics.mart_retention_cohort ORDER BY as_of_timestamp",
        ),
        (
            "How often are sessions missing?",
            "SELECT avg((user_session IS NULL)::INTEGER) missing_share FROM int_behavior_events",
        ),
        (
            "What does train recency look like?",
            "SELECT min(purchase_recency),median(purchase_recency),max(purchase_recency) FROM mart_customer_snapshot WHERE split='train'",
        ),
        (
            "Are inactive eligible buyers retained?",
            "SELECT count(*) n FROM mart_customer_snapshot WHERE split='train' AND active_days_14=0",
        ),
        (
            "Are immature labels null?",
            "SELECT count(*) n,count(non_repurchase_28d) known_labels FROM mart_customer_outcome WHERE split='latest_unlabeled'",
        ),
    ]
    con = connect(mode, True)
    text = (
        "# SQL business workbook\n\nRun "
        + p.name
        + '. Open `.venv/bin/python` and use `from retention.common import connect; con=connect("'
        + mode
        + '",True)` then `con.execute(sql).df()`.\n'
    )
    for title, sql in queries:
        text += (
            f"\n## {title}\n\n```sql\n{sql};\n```\n\n"
            + con.execute(sql).df().to_markdown(index=False)
            + "\n"
        )
    con.close()
    (p / "reports/sql_workbook.md").write_text(text)
    (ROOT / "docs/SQL_WORKBOOK.md").write_text(
        "# SQL workbook\n\nThe generator runs 12 real queries and writes results to `artifacts/<mode>-v1/reports/sql_workbook.md`. See `scripts/build_learning.py` for all query source. Source-row and customer data remain local.\n"
    )


if __name__ == "__main__":
    import sys

    build(sys.argv[1] if len(sys.argv) > 1 else "dev")
