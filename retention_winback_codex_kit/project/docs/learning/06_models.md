# 6. Does digital behavior add useful information?

The ablation compares purchase-only and combined predictors on the same buyers. Simpler baselines can win.

## Inspect

src/retention/modeling.py:train; src/retention/features.py

```bash
.venv/bin/python -c "from retention.common import run_dir,read; print(read(run_dir('full')/'validation_metrics.json'))"
```

## Observed in full-v1

Read the computed validation_metrics.json for this run; values are not hardcoded into this lesson.

## Common mistake

Choosing features by looking at final test labels. Guard: `tests/unit/test_contracts.py:test_allowlist_partition_and_ties`.

## Exercises

1. Which partition fits the base estimator?
2. Which partition selects the model?

Answers are in ANSWERS.md.
