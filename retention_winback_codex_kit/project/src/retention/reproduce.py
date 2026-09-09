"""Resume a frozen run without silently retraining after test inspection."""

import subprocess, sys, time
from .common import ROOT, run_dir, read, save, digest, now


def reproduce(mode):
    """Run missing stages, verify immutable artifacts, then rebuild communication outputs."""
    p = run_dir(mode)
    started = now()
    steps = []
    contract_path = p / "input_contract.json"
    from .snapshots import snapshot_sql
    import hashlib

    def current_contract():
        acquisition = read(ROOT / "data/manifests/acquisition.json")
        if any(v.get("status") != "acquired" for v in acquisition.values()):
            raise RuntimeError("Both real sources must be acquired before reproduction")
        return {
            "source_hashes": {
                dataset: [f["sha256"] for f in metadata["files"]]
                for dataset, metadata in acquisition.items()
            },
            "snapshot_sql_sha256": hashlib.sha256(
                snapshot_sql("2019-12-01").encode()
            ).hexdigest(),
        }

    # Acquisition verifies original files and pins the saved version; network only if absent.
    for step in [
        "doctor",
        "download",
        "profile",
        "build",
        "dbt",
        "train",
        "evaluate",
        "score",
        "cohorts",
        "hillstrom",
        "reports",
        "trace",
        "supplement",
        "learning",
        "notebooks",
        "presentation",
    ]:
        if step == "profile":
            contract = current_contract()
            if contract_path.exists() and read(contract_path) != contract:
                raise ValueError(
                    "Source or feature contract changed. Existing frozen run cannot be silently reused."
                )
            if not contract_path.exists():
                save(contract_path, contract)
        outputs = {
            "profile": "quality.json",
            "build": "snapshots.json",
            "train": "freeze.json",
            "evaluate": "test_metrics.json",
            "score": "audience_summary.json",
            "hillstrom": "hillstrom/uplift.json",
        }
        if step in outputs and (p / outputs[step]).exists():
            if step == "train":
                frozen = read(p / "freeze.json")
                for name, h in frozen["model_hashes"].items():
                    if digest(p / "models" / f"{name}.joblib") != h:
                        raise ValueError("Frozen model was modified")
            steps.append(
                {
                    "step": step,
                    "status": "reused_existing_verified_run_artifact",
                    "artifact": outputs[step],
                }
            )
            print("REUSE", step, flush=True)
            continue
        t = time.perf_counter()
        subprocess.run(
            [sys.executable, "-m", "retention.cli", step, "--mode", mode],
            cwd=ROOT,
            check=True,
        )
        steps.append(
            {"step": step, "status": "executed", "seconds": time.perf_counter() - t}
        )
    save(
        p / "execution/reproduce.json",
        {
            "started": started,
            "completed": now(),
            "mode": mode,
            "steps": steps,
            "note": "Existing frozen run artifacts reused. To change source/feature specification, create a separately versioned run and disclose the new evaluation design.",
        },
    )
