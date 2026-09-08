# 3. Which rows count as valid behavior?

A purchase can count even when its price is unusable. Source multiplicity remains visible.

## Inspect

src/retention/profiling.py:profile; dbt/models/fct_purchase_occasions.sql

```bash
.venv/bin/python -c "from retention.common import run_dir,read; print(read(run_dir('full')/'quality.json'))"
```

## Observed in full-v1

Analytical source rows: 20692840. Duplicate sensitivity remains in quality.json.

## Common mistake

Removing purchases because their value is missing. Guard: `tests/unit/test_contracts.py:test_cutoff_purchase_presence_and_inactive_buyer`.

## Exercises

1. What defines an inferred occasion?
2. Why is it not an order?

Answers are in ANSWERS.md.
