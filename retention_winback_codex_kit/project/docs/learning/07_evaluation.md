# 7. Are the scores calibrated and useful for ranking?

Brier score measures probability error. Top-K lift measures concentration of future non-repurchase against the same population prevalence.

## Inspect

src/retention/evaluation.py:metrics; src/retention/calibration.py

```bash
.venv/bin/python -c "from retention.common import run_dir,read; print(read(run_dir('full')/'test_metrics.json'))"
```

## Observed in full-v1

Read the computed test_metrics.json for this run; values are not hardcoded into this lesson.

## Common mistake

Calling high accuracy strong evidence under high prevalence. Guard: `tests/integration/test_real_run.py:test_snapshot_labels_and_prediction_roundtrip`.

## Exercises

1. Why report AP for both classes?
2. What happens when risk scores tie?

Answers are in ANSWERS.md.
