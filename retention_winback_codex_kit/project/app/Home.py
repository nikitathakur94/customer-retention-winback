"""Seven decision and learning pages sharing immutable run artifacts."""

import os
import math
import numpy as np
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from retention.common import ROOT, read, DISCLOSURE
from retention.cohorts import audience
from retention.experiments import economics, power

st.set_page_config(page_title="Retention & Win-Back", page_icon="↻", layout="wide")
st.markdown(
    '<style>.block-container{max-width:1280px;padding:2rem}h1{letter-spacing:-.04em}div[data-testid="stMetric"]{background:#eef5f2;border-radius:12px;padding:18px}section[data-testid="stSidebar"]{background:#eaf1ee}div[data-testid="stMetricValue"]{font-size:1.8rem;white-space:normal}div[data-testid="stMetricLabel"] p{white-space:normal}</style>',
    unsafe_allow_html=True,
)
BASE = Path(os.environ.get("RETENTION_ARTIFACTS_DIR", ROOT / "artifacts"))
PAGES = [
    "Overview",
    "Customer health",
    "Risk model",
    "Customer explorer",
    "Win-back studio",
    "Campaign lab",
    "Data quality and learning",
]
st.sidebar.markdown("## Retention / Studio")
st.sidebar.caption("Customer decisions grounded in observed history")
mode = st.sidebar.selectbox("Run mode", ["full", "dev"])
page = st.sidebar.radio("Workspace", PAGES)
p = BASE / f"{mode}-v1"
split = st.sidebar.selectbox(
    "Fixed scoring snapshot",
    ["latest_unlabeled", "test", "validation", "train"],
    disabled=page in ["Risk model", "Customer explorer", "Campaign lab"],
)
effective_split = "test" if page in ["Risk model", "Customer explorer"] else split
st.sidebar.info("No outreach is authorized. Consent and contactability are unknown.")
st.title(page)
st.caption(DISCLOSURE)
is_hill = page == "Campaign lab"
st.caption(
    "Hillstrom randomized email experiment — independent dataset • Full 64,000 assignments • 14-day outcomes • OBSERVED / MODEL_ESTIMATE"
    if is_hill
    else f"REES46 cosmetics • {mode}-v1 • Coverage: Oct 2019–Feb 2020 • Snapshot: {effective_split} • OBSERVED / MODEL_ESTIMATE"
)


@st.cache_data(show_spinner=False)
def load_frame(path, mtime):
    return pd.read_parquet(path)


def frame(name):
    f = p / name
    return load_frame(str(f), f.stat().st_mtime_ns) if f.exists() else pd.DataFrame()


def get(name):
    return read(p / name) if (p / name).exists() else None


def missing(message="Run make reproduce MODE=" + mode + " to build this page."):
    st.info(message)


def show_table(df):
    labels = {
        "non_repurchase_prevalence": "No-return prevalence",
        "average_precision_non_repurchase": "AP no return",
        "average_precision_repurchase": "AP return",
        "roc_auc": "ROC-AUC",
        "brier": "Brier",
        "log_loss": "Log loss",
        "n": "N",
        "model": "Model",
    }
    st.dataframe(df.rename(columns=labels), width="stretch", hide_index=True)


def manifest_value(key):
    manifest = get("results_manifest.json")
    if manifest is None:
        return None
    return next(
        (r["value"] for r in manifest["metrics"] if r["metric_id"] == key), None
    )


scores = frame(f"scores_{effective_split}.parquet")
if not scores.empty and not is_hill:
    st.caption(
        "Scoring cutoff (UTC): "
        + str(scores.as_of_timestamp.iloc[0])
        + " • Features use the preceding 60 days"
    )
if page == "Overview":
    st.subheader("Which previous buyers should enter a win-back test?")
    manifest = get("results_manifest.json")
    if manifest is None:
        missing()
    else:
        cols = st.columns(3)
        cols[0].metric(
            "Eligible observed buyers",
            f"{manifest_value('eligible_buyers_' + split):,}",
        )
        rate = manifest_value("non_repurchase_prevalence_" + split)
        cols[1].metric(
            "Observed 28-day repurchase",
            "Unknown future" if rate is None else f"{1 - rate:.1%}",
        )
        cols[2].metric(
            "Analytical candidates", f"{manifest_value('candidate_count_' + split):,}"
        )
        st.info(manifest["recommendation"])
        st.subheader("The model predicts a 28-day absence of purchase")
        st.write(
            "A later return remains possible. Risk estimates describe historical purchase patterns; a randomized campaign is needed to establish whether contact changes outcomes."
        )
        show_table(pd.DataFrame(get("snapshots.json")))
        st.caption(
            "Each row has its own eligible population. Do not sum snapshots as unique people."
        )
        if not scores.empty:
            st.plotly_chart(
                px.histogram(
                    scores,
                    x="risk_probability",
                    nbins=35,
                    labels={
                        "risk_probability": "Predicted 28-day non-repurchase probability"
                    },
                    color_discrete_sequence=["#167264"],
                ),
                width="stretch",
            )
elif page == "Customer health":
    if scores.empty:
        missing()
    else:
        counts = (
            scores.groupby("primary_segment").size().rename("customers").reset_index()
        )
        st.plotly_chart(
            px.bar(
                counts,
                x="customers",
                y="primary_segment",
                orientation="h",
                labels={"primary_segment": "Primary segment"},
                color_discrete_sequence=["#167264"],
            ),
            width="stretch",
        )
        st.caption(
            "Precedence: recent purchase, quality hold, high value decline, lapsed engaged, one-time buyer, inactive lower value, other. Thresholds were frozen before test."
        )
        c1, c2 = st.columns(2)
        c1.plotly_chart(
            px.histogram(
                scores,
                x="purchase_recency",
                nbins=30,
                labels={"purchase_recency": "Days since purchase"},
            ),
            width="stretch",
        )
        c2.plotly_chart(
            px.histogram(
                scores,
                x="activity_change",
                range_x=[-100, 100],
                nbins=40,
                labels={
                    "activity_change": "Recent 14-day activity minus prior 14 days"
                },
            ),
            width="stretch",
        )
        st.caption(
            "Activity chart displays −100 to +100 for legibility; observations outside that range remain in calculations."
        )
        show_table(
            scores.groupby("repeat_buyer")
            .agg(
                customers=("user_id", "size"),
                median_value_proxy=("value_60", "median"),
                median_observed_gap=("mean_purchase_gap", "median"),
            )
            .reset_index()
        )
        st.write(
            "Purchase-gap averages exist only for observed repeat occasions. Single-occasion buyers are censored or have no identifiable gap; these histories are not omitted from scoring."
        )
elif page == "Risk model":
    result = get("test_metrics.json")
    freeze = get("freeze.json")
    if result is None:
        missing()
    else:
        st.caption(
            "Fixed final-test evaluation: cutoff 2020-01-28; outcomes [2020-01-28, 2020-02-25). Sidebar snapshot does not change evaluation denominators."
        )
        st.success(
            "Frozen selection: "
            + freeze["selected_model"]
            + " • validation-policy Brier score"
        )
        show_table(
            pd.DataFrame(
                [
                    {
                        "model": name,
                        **{
                            k: r[k]
                            for k in [
                                "n",
                                "non_repurchase_prevalence",
                                "roc_auc",
                                "average_precision_non_repurchase",
                                "average_precision_repurchase",
                                "brier",
                                "log_loss",
                            ]
                        },
                    }
                    for name, r in result.items()
                ]
            )
        )
        name = st.selectbox(
            "Inspect model",
            list(result),
            index=list(result).index(freeze["selected_model"]),
        )
        show_table(pd.DataFrame(result[name]["top_k"]))
        chart = pd.DataFrame(result[name]["reliability"])
        fig = px.line(
            chart,
            x="predicted",
            y="observed",
            markers=True,
            range_x=[0, 1],
            range_y=[0, 1],
            labels={
                "predicted": "Mean predicted non-repurchase",
                "observed": "Observed non-repurchase",
            },
        )
        fig.add_scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="Perfect calibration",
            line={"dash": "dash", "color": "gray"},
        )
        st.plotly_chart(fig, width="stretch")
        st.json(result[name]["uncertainty"])
        st.caption(
            "Risk-ranking lift is not campaign uplift. High class prevalence makes accuracy and non-repurchase AP easy to misread."
        )
elif page == "Customer explorer":
    index = get("traces/index.json")
    if index is None:
        missing(
            "Generate local source traces using .venv/bin/python -m retention.cli trace --mode "
            + mode
        )
    else:
        st.caption(
            "Fixed historical test snapshot. A reproducible set of source-reconciled buyers is available; all raw histories remain local."
        )
        entry = st.selectbox(
            "Anonymous observed buyer",
            list(range(len(index))),
            format_func=lambda i: index[i]["kind"] + " · " + index[i]["user_id"],
        )
        row = index[entry]
        uid = row["user_id"]
        st.metric("Predicted non-repurchase", f"{row['risk']:.1%}")
        st.write("Primary segment: " + row["segment"])
        st.json(row["manual_reconciliation"])
        events = frame(f"traces/{uid}.parquet")
        show_table(events)
        st.download_button(
            "Download pre-cutoff source trace",
            events.to_csv(index=False).encode(),
            "source_trace.csv",
            "text/csv",
        )
        if st.checkbox("Reveal retrospective future outcomes", value=False):
            st.warning(
                "Retrospective diagnostics only. These events never enter features or audience exports."
            )
            st.write(
                "Observed non-repurchase label: "
                + str(row["retrospective_non_repurchase"])
            )
            show_table(frame(f"traces/{uid}_retrospective.parquet"))
elif page == "Win-back studio":
    if scores.empty:
        missing()
    else:
        tab1, tab2 = st.tabs(["Candidate audience", "Hypothetical economics"])
        with tab1:
            capacity = st.number_input(
                "Maximum candidate count",
                min_value=0,
                max_value=len(scores),
                value=min(len(scores), math.ceil(len(scores) * 0.1)),
                step=1,
            )
            policy = st.selectbox(
                "Priority policy", ["risk", "recency", "value", "risk_value"]
            )
            segments = st.multiselect(
                "Included primary segments",
                sorted(scores.primary_segment.unique()),
                default=sorted(scores.primary_segment.unique()),
            )
            selected = audience(scores, int(capacity), policy, segments)
            st.metric("Selected candidates", len(selected))
            st.caption(
                "Interactive policy scenario. Default published totals use the frozen capacity and risk policy."
            )
            st.download_button(
                "Download candidate CSV",
                selected.to_csv(index=False).encode(),
                "winback_candidates.csv",
                "text/csv",
            )
            show_table(selected)
            st.info(
                "Consent: unknown. Contactability: unknown. This analytical export cannot authorize sending."
            )
            st.write(
                "Proposed brief: acknowledge recent category interest for lapsed engaged buyers, test useful content for one-time buyers, and reserve incentives for a randomized arm. Never promise unavailable inventory."
            )
        with tab2:
            st.caption("ASSUMPTION_SCENARIO • no defaults represent business facts")
            st.write(
                "Incentive costs apply to natural converters too: δ × V × m − (p₀ + δ) × r × D − c."
            )
            if st.button("Load explicitly hypothetical example"):
                for key, value in {
                    "p0": 0.1,
                    "delta": 0.01,
                    "V": 100.0,
                    "m": 0.3,
                    "D": 5.0,
                    "r": 1.0,
                    "c": 0.0,
                }.items():
                    st.session_state["econ_" + key] = value
            values = {}
            for key, label in [
                ("p0", "Assumed no-contact conversion probability"),
                ("delta", "Assumed absolute effect"),
                ("V", "Assumed basket value"),
                ("m", "Assumed contribution margin fraction"),
                ("D", "Incentive cost"),
                ("r", "Assumed redemption fraction"),
                ("c", "Contact cost"),
            ]:
                values[key] = st.number_input(label, value=None, key="econ_" + key)
            try:
                scenario = economics(**values, count=int(capacity))
                st.json(scenario)
                if scenario.get("evidence_type") == "ASSUMPTION_SCENARIO":
                    points = [
                        {
                            "assumed_absolute_effect": float(d),
                            "contribution_per_contact": economics(
                                **{**values, "delta": float(d)}
                            )["per_contact"],
                        }
                        for d in np.linspace(0, min(0.1, 1 - values["p0"]), 30)
                    ]
                    st.plotly_chart(
                        px.line(
                            pd.DataFrame(points),
                            x="assumed_absolute_effect",
                            y="contribution_per_contact",
                            title="Hypothetical effect sensitivity",
                        ),
                        width="stretch",
                    )
            except ValueError as exc:
                st.error(str(exc))
elif page == "Campaign lab":
    result = get("hillstrom/experiment.json")
    uplift = get("hillstrom/uplift.json")
    if result is None:
        missing()
    else:
        st.subheader("Randomized email outcomes per assigned customer")
        show_table(pd.DataFrame(result["arm_summary"]))
        effect_frame = pd.DataFrame(
            [r for r in result["effects"] if r["outcome"] == "conversion"]
        )
        effect_frame["ci_halfwidth"] = effect_frame.apply(
            lambda r: r["ci95_unadjusted"][1] - r["difference"], axis=1
        )
        st.plotly_chart(
            px.scatter(
                effect_frame,
                x="difference",
                y="arm",
                error_x="ci_halfwidth",
                title="14-day conversion difference vs control, 95% unadjusted CI",
            ),
            width="stretch",
        )
        show_table(pd.DataFrame(result["effects"]))
        st.caption(result["interval_method"])
        st.subheader("Response versus engagement uplift")
        show_table(pd.DataFrame(uplift["policies"]).T.reset_index(names="policy"))
        st.write(
            f"Test Qini: {uplift['qini_auc']:.5f}; 95% interval: {uplift['qini_ci95']}. Target: visits, not retained customers."
        )
        st.divider()
        st.subheader("Proposed cosmetics experiment — dry run only")
        st.write(
            "Separate 28-day repurchase trial: no-contact control, reminder/content and incentive arms. No cosmetics treatment outcomes exist."
        )
        p0 = st.number_input(
            "Assumed control repurchase rate", value=None, key="power_p0"
        )
        delta = st.number_input(
            "Desired absolute effect", value=None, key="power_delta"
        )
        if p0 is not None and delta is not None:
            try:
                st.json(power(p0, delta))
            except ValueError as exc:
                st.error(str(exc))
        else:
            st.info(
                "Enter planning assumptions to calculate sample size. Two comparisons use Bonferroni alpha."
            )
else:
    quality = get("quality.json")
    if quality is None:
        missing()
    else:
        show_table(
            pd.DataFrame(quality["monthly_full_source"]).drop(columns="event_counts")
        )
        st.json(quality["analytical_waterfall"])
        st.json(quality["duplicate_sensitivity"])
        st.write(quality["coverage_basis"])
        st.write("Unavailable: " + ", ".join(quality["missing_capabilities"]))
    st.subheader("Learning path")
    chapters = sorted((ROOT / "docs/learning").glob("*.md"))
    if chapters:
        selected = st.selectbox("Chapter", [x.name for x in chapters])
        st.markdown((ROOT / "docs/learning" / selected).read_text())
    else:
        st.info("Learning chapters are being generated.")
    with st.expander("About and source provenance"):
        st.write(DISCLOSURE)
        st.markdown(
            "[REES46 publisher](https://rees46.com/en/datasets) · [Cosmetics dataset](https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-cosmetics-shop) · [Hillstrom original study](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html)"
        )
