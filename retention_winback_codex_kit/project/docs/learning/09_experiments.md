# 9. How do we estimate what contact caused?

Random assignment makes treatment and control comparable on average. Use all assigned customers, including nonconverters.

## Inspect

src/retention/hillstrom.py:effect,analyze; docs/experiment_protocol.md

```bash
.venv/bin/python -c "from retention.common import run_dir,read; print(read(run_dir('full')/'hillstrom/experiment.json'))"
```

## Observed in full-v1

Read the computed hillstrom/experiment.json for this run; values are not hardcoded into this lesson.

## Common mistake

Conditioning spend on conversion and claiming a population effect. Guard: `tests/integration/test_real_run.py:test_hillstrom_separation`.

## Exercises

1. Do Mens creative labels imply customer gender?
2. Can the effect be reused as the cosmetics campaign effect?

Answers are in ANSWERS.md.
