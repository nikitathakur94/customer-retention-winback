"""Acquire original data without publishing it; preserve immutable files and hashes."""

import os, platform, shutil
from pathlib import Path
import pandas as pd
import psutil
from .common import ROOT, save, read, digest, now

MONTHS = [
    "2019-Oct.csv",
    "2019-Nov.csv",
    "2019-Dec.csv",
    "2020-Jan.csv",
    "2020-Feb.csv",
]
HANDLE = "mkechinov/ecommerce-events-history-in-cosmetics-shop"
HILL_URL = "https://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv"


def doctor():
    info = {
        "time": now(),
        "python": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "ram_bytes": psutil.virtual_memory().total,
        "available_ram_bytes": psutil.virtual_memory().available,
        "free_disk_bytes": shutil.disk_usage(ROOT).free,
        "duckdb_memory": "4GB",
        "duckdb_threads": 4,
    }
    save(ROOT / "data/manifests/environment.json", info)
    print(info)
    return info


def download():
    manifest = ROOT / "data/manifests/acquisition.json"
    out = read(manifest) if manifest.exists() else {}
    os.environ.setdefault("KAGGLEHUB_CACHE", str(ROOT / "data/raw/cosmetics/cache"))
    try:
        if os.environ.get("COSMETICS_DATA_DIR"):
            base = Path(os.environ["COSMETICS_DATA_DIR"])
            version = "user-local-unversioned"
        else:
            import kagglehub

            prior = out.get("cosmetics", {}).get("version")
            handle = (
                f"{HANDLE}/versions/{prior}"
                if prior and str(prior).isdigit()
                else HANDLE
            )
            base = Path(kagglehub.dataset_download(handle))
            version = base.name
        files = []
        for name in MONTHS:
            matches = list(base.rglob(name))
            if len(matches) != 1:
                raise ValueError(
                    f"Expected exactly one {name}; found {len(matches)} in {base}"
                )
            p = matches[0]
            files.append(
                {
                    "name": name,
                    "path": str(p.resolve()),
                    "bytes": p.stat().st_size,
                    "sha256": digest(p),
                }
            )
        out["cosmetics"] = {
            "status": "acquired",
            "version": version,
            "time": now(),
            "source": f"https://www.kaggle.com/datasets/{HANDLE}",
            "terms": "Data files © Original Authors (kit card transcription); no redistribution assumed",
            "files": files,
        }
    except Exception as exc:
        out["cosmetics"] = {
            "status": "blocked",
            "error": str(exc),
            "resume": "Set COSMETICS_DATA_DIR to all five original CSVs, or configure Kaggle using kagglehub.login(), then make download.",
        }
    save(manifest, out)
    try:
        p = ROOT / "data/raw/hillstrom/hillstrom.csv"
        p.parent.mkdir(parents=True, exist_ok=True)
        method = out.get("hillstrom", {}).get("method", "original author CSV")
        source = out.get("hillstrom", {}).get("source", HILL_URL)
        if not p.exists():
            import requests

            try:
                response = requests.get(HILL_URL, timeout=45)
                response.raise_for_status()
                if not response.text.lower().startswith("recency"):
                    raise ValueError("Original link did not return expected CSV")
                p.write_bytes(response.content)
            except Exception:
                from sklift.datasets import fetch_hillstrom

                d = fetch_hillstrom(
                    target_col="all", data_home=str(ROOT / "data/raw/hillstrom/cache")
                )
                frame = d.data.copy()
                frame["segment"] = d.treatment
                for c in ["visit", "conversion", "spend"]:
                    frame[c] = d.target[c]
                frame.to_csv(p, index=False)
                method = "documented sklift fetch_hillstrom fallback"
                source = "https://www.uplift-modeling.com/en/latest/api/datasets/fetch_hillstrom.html"
        df = pd.read_csv(p)
        if len(df) != 64000 or not {"segment", "visit", "conversion", "spend"}.issubset(
            df.columns
        ):
            raise ValueError("Hillstrom schema/count mismatch")
        out["hillstrom"] = {
            "status": "acquired",
            "time": now(),
            "source": source,
            "method": method,
            "terms": "Author supplies for public analysis challenge; redistribution rights not assumed",
            "files": [
                {
                    "name": p.name,
                    "path": str(p),
                    "bytes": p.stat().st_size,
                    "sha256": digest(p),
                }
            ],
            "rows": len(df),
        }
    except Exception as exc:
        out["hillstrom"] = {
            "status": "blocked",
            "error": str(exc),
            "resume": "make download",
        }
    save(manifest, out)
    print({k: v["status"] for k, v in out.items()})
    return out
