"""Independent randomized email ITT and held-out engagement-uplift analysis."""

import hashlib, math
import joblib
import numpy as np
import pandas as pd
from scipy.stats import norm, chisquare
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklift.metrics import qini_auc_score, uplift_at_k
from .common import ROOT, run_dir, save, now, digest

PRE = [
    "recency",
    "history_segment",
    "history",
    "mens",
    "womens",
    "zip_code",
    "newbie",
    "channel",
]
TREAT = "Mens E-Mail"
CONTROL = "No E-Mail"


def validate_hillstrom(df):
    if not set(PRE + ["segment", "visit", "conversion", "spend"]).issubset(df.columns):
        raise ValueError("Hillstrom schema mismatch")
    if df[PRE + ["segment", "visit", "conversion", "spend"]].isna().any().any():
        raise ValueError("Unresolved missing Hillstrom data")
    if set(df.segment) != {TREAT, CONTROL, "Womens E-Mail"}:
        raise ValueError("Assignment labels changed")
    if not df.visit.isin([0, 1]).all() or not df.conversion.isin([0, 1]).all():
        raise ValueError("Nonbinary outcomes")
    if (df.conversion > df.visit).any() or (df.spend < 0).any():
        raise ValueError("Inconsistent outcomes")


def estimator():
    cats = ["history_segment", "zip_code", "channel"]
    nums = [x for x in PRE if x not in cats]
    prep = ColumnTransformer(
        [
            ("categorical", OneHotEncoder(handle_unknown="ignore"), cats),
            ("numeric", StandardScaler(), nums),
        ]
    )
    return make_pipeline(prep, LogisticRegression(C=1, max_iter=1000))


def effect(t, c):
    difference = float(t.mean() - c.mean())
    se = math.sqrt(t.var(ddof=1) / len(t) + c.var(ddof=1) / len(c))
    z = difference / se if se else 0
    return {
        "difference": difference,
        "relative_difference": difference / float(c.mean()) if c.mean() else None,
        "ci95_unadjusted": [difference - 1.96 * se, difference + 1.96 * se],
        "p_unadjusted": float(2 * norm.sf(abs(z))),
        "p_bonferroni_two_comparisons": float(min(1, 4 * norm.sf(abs(z)))),
    }


def analyze(mode="dev"):
    p = run_dir(mode) / "hillstrom"
    p.mkdir(exist_ok=True)
    df = pd.read_csv(ROOT / "data/raw/hillstrom/hillstrom.csv")
    validate_hillstrom(df)
    df["source_row_id"] = np.arange(1, len(df) + 1)  # Not shared with retail user IDs.
    arms = []
    effects = []
    for arm, g in df.groupby("segment"):
        arms.append(
            {
                "arm": arm,
                "n": len(g),
                "visit_rate": float(g.visit.mean()),
                "conversion_rate": float(g.conversion.mean()),
                "mean_spend_per_assigned": float(g.spend.mean()),
            }
        )
        if arm != CONTROL:
            for outcome in ["conversion", "visit", "spend"]:
                effects.append(
                    {
                        "arm": arm,
                        "outcome": outcome,
                        "n_treatment": len(g),
                        "n_control": int(df.segment.eq(CONTROL).sum()),
                        **effect(g[outcome], df.loc[df.segment.eq(CONTROL), outcome]),
                    }
                )
    balance = (
        df.groupby("segment")[["recency", "history", "mens", "womens", "newbie"]]
        .agg(["mean", "std"])
        .round(5)
    )
    balance.to_csv(p / "pretreatment_balance.csv")
    counts = df.segment.value_counts()
    srm = chisquare(counts.to_numpy())
    save(
        p / "experiment.json",
        {
            "dataset_id": "hillstrom_email",
            "evidence_type": "OBSERVED",
            "followup_days": 14,
            "rows": len(df),
            "arm_summary": arms,
            "effects": effects,
            "sample_ratio_p": float(srm.pvalue),
            "duplicates_policy": "No aggregate-feature deduplication; preserve every original assignment",
            "interval_method": "Independent-arm mean difference; normal large-sample 95% intervals. Two conversion comparisons Bonferroni adjusted; visits/spend secondary.",
        },
    )
    two = df[df.segment.isin([TREAT, CONTROL])].copy()
    tr, hold = train_test_split(
        two, test_size=0.4, random_state=2801, stratify=two.segment
    )
    va, te = train_test_split(
        hold, test_size=0.5, random_state=2801, stratify=hold.segment
    )
    assert set(tr.source_row_id).isdisjoint(te.source_row_id) and set(
        va.source_row_id
    ).isdisjoint(te.source_row_id)
    models = {}
    for arm in [TREAT, CONTROL]:
        subset = tr[tr.segment.eq(arm)]
        models[arm] = estimator().fit(subset[PRE], subset.visit)
    joblib.dump(models, p / "visit_models.joblib")
    save(
        p / "freeze.json",
        {
            "time": now(),
            "model_sha256": digest(p / "visit_models.joblib"),
            "features": PRE,
            "target": "visit",
            "capacity": 0.2,
            "split_counts": {"train": len(tr), "validation": len(va), "test": len(te)},
            "selection": "Fixed logistic T-learner, no outcome-driven treatment or capacity selection",
        },
    )
    for name, g in [("train", tr), ("validation", va), ("test", te)]:
        g[["source_row_id", "segment"]].to_csv(p / f"{name}_ids.csv", index=False)
    response = models[TREAT].predict_proba(te[PRE])[:, 1]
    no_contact = models[CONTROL].predict_proba(te[PRE])[:, 1]
    uplift = response - no_contact
    treated = te.segment.eq(TREAT).astype(int).to_numpy()
    y = te.visit.to_numpy()
    ids = te.source_row_id.to_numpy()
    qini = float(qini_auc_score(y, uplift, treated))
    at_k = float(uplift_at_k(y, uplift, treated, strategy="overall", k=0.2))
    policies = {}
    n = len(te)
    k = math.ceil(n * 0.2)
    random_order = np.argsort(
        [hashlib.sha256(f"random:{x}".encode()).hexdigest() for x in ids]
    )
    for name, order in [
        ("treat_all", np.arange(n)),
        ("treat_none", np.array([], dtype=int)),
        ("random_capacity", random_order),
        ("response", np.lexsort((ids, -response))),
        ("uplift", np.lexsort((ids, -uplift))),
    ]:
        take = n if name == "treat_all" else 0 if name == "treat_none" else k
        chosen = np.zeros(n, dtype=bool)
        chosen[order[:take]] = True
        # Known assignment probability conditional on these two equally randomized arms is 1/2.
        contribution = np.where(chosen, treated * y / 0.5, (1 - treated) * y / 0.5)
        value = float(contribution.mean())
        se = float(contribution.std(ddof=1) / np.sqrt(n))
        policies[name] = {
            "selected": int(chosen.sum()),
            "treated_support": int(treated[chosen].sum()),
            "control_support": int((1 - treated[chosen]).sum()),
            "ipw_visit_policy_value": value,
            "ci95": [value - 1.96 * se, value + 1.96 * se],
        }
    rng = np.random.default_rng(2801)
    draws = []
    for _ in range(200):
        ix = rng.integers(0, n, n)
        draws.append(qini_auc_score(y[ix], uplift[ix], treated[ix]))
    save(
        p / "uplift.json",
        {
            "dataset_id": "hillstrom_email",
            "target": "14-day visit, engagement not purchase retention",
            "qini_auc": qini,
            "qini_ci95": np.quantile(draws, [0.025, 0.975]).tolist(),
            "uplift_at_top_20pct": at_k,
            "n_test": n,
            "policies": policies,
            "assignment_probability": 0.5,
            "policy_method": "IPW mean of observed outcome for matching policy/assignment divided by known assignment probability. Normal SE; no observed counterfactuals fabricated.",
            "uncertainty": "Qini 200 row bootstrap; no individual causal types identified.",
        },
    )
    return {"arm_summary": arms, "qini_auc": qini}
