"""Transparent evaluation metrics for settled prop projections."""
from __future__ import annotations

import math

import pandas as pd


REQUIRED_COLUMNS = {
    "prediction_id",
    "projection",
    "line",
    "actual",
    "edge",
    "over_probability",
    "signal",
}


def prepare_predictions(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate settled rows and derive reusable evaluation fields."""
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    prepared = frame.copy()
    numeric = ["projection", "line", "actual", "edge", "over_probability"]
    for column in numeric:
        prepared[column] = pd.to_numeric(prepared[column], errors="raise")

    if not prepared["signal"].isin({"over", "under", "pass"}).all():
        raise ValueError("signal must be over, under, or pass")
    if not prepared["over_probability"].between(0, 1).all():
        raise ValueError("over_probability must be between 0 and 1")

    prepared["absolute_error"] = (
        prepared["projection"] - prepared["actual"]
    ).abs()
    prepared["bias"] = prepared["projection"] - prepared["actual"]
    prepared["push"] = prepared["actual"] == prepared["line"]
    prepared["actual_over"] = (prepared["actual"] > prepared["line"]).astype(float)
    prepared["correct"] = pd.NA

    over = (~prepared["push"]) & (prepared["signal"] == "over")
    under = (~prepared["push"]) & (prepared["signal"] == "under")
    prepared.loc[over, "correct"] = prepared.loc[over, "actual_over"] == 1
    prepared.loc[under, "correct"] = prepared.loc[under, "actual_over"] == 0
    return prepared


def overall_metrics(frame: pd.DataFrame) -> dict[str, float | int]:
    """Calculate portfolio-level error, calibration, and signal metrics."""
    prepared = prepare_predictions(frame)
    non_push = prepared[~prepared["push"]]
    graded = non_push[non_push["signal"].isin({"over", "under"})]
    brier = ((non_push["over_probability"] - non_push["actual_over"]) ** 2).mean()
    hit_rate = graded["correct"].astype(float).mean() if len(graded) else math.nan
    return {
        "settled": int(len(prepared)),
        "mae": float(prepared["absolute_error"].mean()),
        "bias": float(prepared["bias"].mean()),
        "brier": float(brier),
        "graded_picks": int(len(graded)),
        "hit_rate": float(hit_rate),
    }


def signal_report(frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize graded performance by Over and Under recommendation."""
    prepared = prepare_predictions(frame)
    graded = prepared[
        (~prepared["push"]) & prepared["signal"].isin({"over", "under"})
    ].copy()
    if graded.empty:
        return pd.DataFrame(columns=["signal", "graded_picks", "correct", "hit_rate"])
    report = (
        graded.groupby("signal", sort=False)["correct"]
        .agg(graded_picks="count", correct="sum", hit_rate="mean")
        .reset_index()
    )
    report["correct"] = report["correct"].astype(int)
    return report


def edge_bucket_report(frame: pd.DataFrame) -> pd.DataFrame:
    """Measure whether larger absolute edges correspond to better outcomes."""
    prepared = prepare_predictions(frame)
    prepared["edge_bucket"] = pd.cut(
        prepared["edge"].abs(),
        bins=[0, 1, 2, 3, math.inf],
        labels=["0–1", "1–2", "2–3", "3+"],
        include_lowest=True,
    )

    error = (
        prepared.groupby("edge_bucket", observed=False)
        .agg(
            settled=("prediction_id", "count"),
            mae=("absolute_error", "mean"),
            bias=("bias", "mean"),
        )
        .reset_index()
    )
    graded = prepared[
        (~prepared["push"]) & prepared["signal"].isin({"over", "under"})
    ]
    hits = (
        graded.groupby("edge_bucket", observed=False)["correct"]
        .agg(graded_picks="count", hit_rate="mean")
        .reset_index()
    )
    return error.merge(hits, on="edge_bucket", how="left")
