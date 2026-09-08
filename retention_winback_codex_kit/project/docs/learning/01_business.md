# 1. Which buyers should marketing investigate?

The model estimates a future absence of purchase. It cannot say whether an email changes behavior.

## Inspect

docs/business_brief.md; src/retention/cohorts.py:audience

```bash
.venv/bin/python -c "from retention.common import run_dir,read; print(read(run_dir('full')/'snapshots.json'))"
```

## Observed in full-v1

Observed eligible counts: train=51,828, validation=53,074, test=48,865, latest_unlabeled=49,473. Latest labels remain null.

## Common mistake

Confusing a high risk score with a campaign effect. Guard: `tests/integration/test_real_run.py:test_hillstrom_separation`.

## Exercises

1. Why is a high-risk customer not automatically a good incentive target?
2. What additional data makes a candidate contactable?

Answers are in ANSWERS.md.
