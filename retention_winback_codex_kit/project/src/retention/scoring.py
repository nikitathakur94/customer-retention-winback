"""Score feature-only snapshots with frozen artifact and export no future outcomes."""

import joblib
import numpy as np
import pandas as pd
from .common import run_dir, read, save, digest
from .modeling import predict
from .cohorts import segment, audience


def score(mode="dev"):
    p = run_dir(mode)
    frozen = read(p / "freeze.json")
    name = frozen["selected_model"]
    path = p / "models" / f"{name}.joblib"
    if digest(path) != frozen["model_hashes"][name]:
        raise ValueError("Frozen model changed")
    model = joblib.load(path)
    counts = []
    for split in ["train", "validation", "test", "latest_unlabeled"]:
        df = pd.read_parquet(p / f"features_{split}.parquet")
        df["risk_probability"] = predict(model, df)
        df = segment(df, frozen["high_value_threshold"])
        df["dataset_id"] = "rees46_cosmetics"
        df["run_id"] = p.name
        df["as_of_date"] = df.as_of_timestamp.astype(str)
        df["model_version"] = name
        df["feature_contract_version"] = "1.0"
        df["historical_value_proxy"] = df.value_60
        df["risk_value_priority"] = df.risk_probability * df.value_60
        df = df.sort_values(["risk_probability", "user_id"], ascending=[False, True])
        df["risk_rank"] = np.arange(1, len(df) + 1)
        df["contactability_status"] = "unknown"
        df["consent_status"] = "unknown"
        df.to_parquet(p / f"scores_{split}.parquet", index=False)
        capacity = int(np.ceil(len(df) * frozen["capacity_fraction"]))
        candidates = audience(df, capacity)
        directory = p / "audiences"
        directory.mkdir(exist_ok=True)
        candidates.to_csv(directory / f"{split}.csv", index=False)
        candidates.to_parquet(directory / f"{split}.parquet", index=False)
        df[df.suppression_reason.ne("")][["user_id", "suppression_reason"]].to_csv(
            directory / f"{split}_suppression.csv", index=False
        )
        counts.append(
            {
                "split": split,
                "eligible": len(df),
                "capacity": capacity,
                "selected": len(candidates),
                "suppressed": int(df.suppression_reason.ne("").sum()),
                "segments": df.primary_segment.value_counts().to_dict(),
                "score_mean": float(df.risk_probability.mean()),
                "missingness": df[model["features"]].isna().mean().to_dict(),
            }
        )
    save(p / "audience_summary.json", counts)
    return counts
