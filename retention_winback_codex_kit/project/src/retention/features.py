"""Explicit predictor allowlists: IDs and outcomes cannot enter training."""

PURCHASE = [
    "purchase_recency",
    "purchasing_days_7",
    "purchasing_days_14",
    "purchasing_days_28",
    "purchasing_days_60",
    "occasions_60",
    "value_28",
    "value_60",
    "valid_price_share",
    "median_purchase_event_value",
    "first_purchase_age",
    "repeat_buyer",
    "mean_purchase_gap",
]
DIGITAL = [
    "event_recency",
    "view_recency",
    "cart_recency",
    "active_days_7",
    "active_days_14",
    "active_days_28",
    "sessions_28",
    "views_28",
    "carts_28",
    "removals_28",
    "products_28",
    "categories_28",
    "cart_without_purchase_14",
    "activity_recent_14",
    "activity_previous_14",
    "activity_change",
    "activity_relative_change",
    "no_activity_baseline",
    "purchase_categories",
    "category_view_concentration",
    "missing_session_share",
]
FEATURES = PURCHASE + DIGITAL


def validate_features(features: list[str]) -> None:
    if (
        not features
        or not set(features).issubset(FEATURES)
        or len(set(features)) != len(features)
    ):
        raise ValueError(
            "Predictors must be unique members of the pre-cutoff feature allowlist"
        )
