# 5. How does a timeline become one model row?

SQL groups the complete eligible history by observed user and cutoff. IDs remain keys rather than predictors.

## Inspect

src/retention/snapshots.py:snapshot_sql; configs/features.yaml

```bash
.venv/bin/python -c "from retention.common import run_dir,read; print(read(run_dir('full')/'snapshots.json'))"
```

## Observed in full-v1

Observed eligible counts: train=51,828, validation=53,074, test=48,865, latest_unlabeled=49,473. Latest labels remain null.

## Common mistake

Using current activity to define the buyer universe. Guard: `tests/unit/test_contracts.py:test_cutoff_purchase_presence_and_inactive_buyer`.

## Exercises

1. Why keep a buyer with no recent views?
2. What does a missing relative activity change mean?

Answers are in ANSWERS.md.
