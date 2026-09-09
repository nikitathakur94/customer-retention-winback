"""Mutually exclusive segments and local analytical candidate exports."""

import numpy as np
import pandas as pd


def segment(df: pd.DataFrame, high_value: float) -> pd.DataFrame:
    out = df.copy()
    conditions = [
        out.purchase_recency < 7,
        out.valid_price_share.isna(),
        (out.value_60 >= high_value) & (out.activity_change < 0),
        (out.views_28 + out.carts_28 > 0) & (out.purchase_recency >= 14),
        ~out.repeat_buyer.astype(bool),
        (out.event_recency >= 28) & (out.value_60 < high_value),
    ]
    names = [
        "recent_purchase_suppressed",
        "quality_withheld",
        "high_value_declining",
        "lapsed_engaged",
        "observed_one_time",
        "inactive_lower_value",
    ]
    out["primary_segment"] = np.select(conditions, names, default="other_eligible")
    out["suppression_reason"] = np.select(
        conditions[:2],
        ["purchase_within_7_days", "insufficient_purchase_quality"],
        default="",
    )
    out["reason_codes"] = out.primary_segment
    out["eligibility_status"] = np.where(
        out.suppression_reason.eq(""), "analytically_eligible", "suppressed"
    )
    return out


def audience(
    scores: pd.DataFrame,
    capacity: int,
    policy: str = "risk",
    segments: list[str] | None = None,
) -> pd.DataFrame:
    if not isinstance(capacity, int) or capacity < 0:
        raise ValueError("Capacity must be a nonnegative integer")
    if policy not in ["risk", "recency", "value", "risk_value"]:
        raise ValueError("Unknown policy")
    df = scores[scores.suppression_reason.eq("")].copy()
    if segments is not None:
        df = df[df.primary_segment.isin(segments)]
    col = {
        "risk": "risk_probability",
        "recency": "purchase_recency",
        "value": "historical_value_proxy",
        "risk_value": "risk_value_priority",
    }[policy]
    df = df.sort_values([col, "user_id"], ascending=[False, True]).head(capacity).copy()
    df["priority_policy"] = policy
    allowed = [
        "dataset_id",
        "run_id",
        "as_of_date",
        "user_id",
        "model_version",
        "feature_contract_version",
        "risk_probability",
        "risk_rank",
        "primary_segment",
        "historical_value_proxy",
        "priority_policy",
        "reason_codes",
        "eligibility_status",
        "suppression_reason",
        "contactability_status",
        "consent_status",
    ]
    result = df[allowed]
    assert not result.user_id.duplicated().any()
    assert result.consent_status.eq("unknown").all()
    return result
