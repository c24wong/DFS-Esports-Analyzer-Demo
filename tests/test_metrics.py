import math

import pandas as pd
import pytest

from src.metrics import edge_bucket_report, overall_metrics, prepare_predictions


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "prediction_id": 1,
                "projection": 32.0,
                "line": 29.5,
                "actual": 34.0,
                "edge": 2.5,
                "over_probability": 0.65,
                "signal": "over",
            },
            {
                "prediction_id": 2,
                "projection": 28.0,
                "line": 30.5,
                "actual": 32.0,
                "edge": -2.5,
                "over_probability": 0.35,
                "signal": "under",
            },
            {
                "prediction_id": 3,
                "projection": 29.0,
                "line": 29.5,
                "actual": 29.5,
                "edge": -0.5,
                "over_probability": 0.47,
                "signal": "pass",
            },
        ]
    )


def test_overall_metrics_exclude_push_from_brier_and_hit_rate():
    result = overall_metrics(sample_frame())
    assert result["settled"] == 3
    assert result["graded_picks"] == 2
    assert result["hit_rate"] == 0.5
    assert result["mae"] == pytest.approx((2.0 + 4.0 + 0.5) / 3)
    assert result["bias"] == pytest.approx((-2.0 - 4.0 - 0.5) / 3)
    expected_brier = ((0.65 - 1.0) ** 2 + (0.35 - 1.0) ** 2) / 2
    assert result["brier"] == pytest.approx(expected_brier)


def test_edge_bucket_report_counts_rows_and_graded_picks():
    report = edge_bucket_report(sample_frame())
    bucket = report[report["edge_bucket"] == "2–3"].iloc[0]
    assert bucket["settled"] == 2
    assert bucket["graded_picks"] == 2
    assert bucket["hit_rate"] == 0.5


def test_validation_rejects_invalid_probability():
    frame = sample_frame()
    frame.loc[0, "over_probability"] = 1.2
    with pytest.raises(ValueError, match="between 0 and 1"):
        prepare_predictions(frame)
