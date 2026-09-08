# 4. What exactly does a non-repurchase label mean?

Features stop strictly before the cutoff. The following 28 days define a label only when coverage is complete.

## Inspect

src/retention/snapshots.py:build; dbt/tests/maturity_contract.sql

```bash
.venv/bin/python -c "from retention.common import run_dir,read; print(read(run_dir('full')/'snapshots.json'))"
```

## Observed in full-v1

Observed eligible counts: train=51,828, validation=53,074, test=48,865, latest_unlabeled=49,473. Latest labels remain null.

## Common mistake

Treating an unknown future as no purchase. Guard: `tests/integration/test_real_run.py:test_snapshot_labels_and_prediction_roundtrip`.

## Exercises

1. Where does an event exactly at cutoff belong?
2. What happens at the outcome end?

Answers are in ANSWERS.md.
