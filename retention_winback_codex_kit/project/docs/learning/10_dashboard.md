# 10. What decision can the evidence support?

The app reads precomputed artifacts. Its fixed model window is distinct from interactive candidate policy controls.

## Inspect

app/Home.py; docs/BI_HANDOFF.md

```bash
.venv/bin/python -c "from retention.common import run_dir,read; print(read(run_dir('full')/'results_manifest.json'))"
```

## Observed in full-v1

Frozen selected model: tree_combined. Use the frozen score as a candidate-ranking aid. Verify contactability and consent, then run a randomized holdout before claiming incremental purchases or benefit.

## Common mistake

Changing a visual filter and silently changing the evaluation denominator. Guard: `tests/ui/test_app.py:test_pages`.

## Exercises

1. Where are future outcomes revealed?
2. What makes the recommendation defensible without strong uplift?

Answers are in ANSWERS.md.
