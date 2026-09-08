# 8. How do scores turn into a candidate list?

Rules assign one primary segment. Recent purchases suppress selection. Capacity limits a local analytical export.

## Inspect

src/retention/cohorts.py:segment,audience; src/retention/experiments.py

```bash
.venv/bin/python -c "from retention.common import run_dir,read; print(read(run_dir('full')/'audience_summary.json'))"
```

## Observed in full-v1

Read the computed audience_summary.json for this run; values are not hardcoded into this lesson.

## Common mistake

Treating unknown consent as permission. Guard: `tests/unit/test_contracts.py:test_segment_precedence_and_audience`.

## Exercises

1. Why do incentive costs include natural converters?
2. Is risk times historical value expected profit?

Answers are in ANSWERS.md.
