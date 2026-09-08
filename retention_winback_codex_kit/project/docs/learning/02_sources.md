# 2. What can these datasets actually establish?

The cosmetics files contain events. Hillstrom contains randomized assignments. No shared identity exists.

## Inspect

src/retention/ingest.py:download; data/manifests/acquisition.json

```bash
.venv/bin/python -c "from retention.common import run_dir,read; print(read(run_dir('full')/'quality.json'))"
```

## Observed in full-v1

Analytical source rows: 20692840. Duplicate sensitivity remains in quality.json.

## Common mistake

Calling the two sources one customer database. Guard: `tests/integration/test_real_run.py:test_source_and_conservation`.

## Exercises

1. Why retain the source file hash?
2. Why avoid duplicate removal in Hillstrom?

Answers are in ANSWERS.md.
