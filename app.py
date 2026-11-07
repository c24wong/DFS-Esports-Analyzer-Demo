"""Streamlit portfolio dashboard for sanitized esports projection results."""
from pathlib import Path

import pandas as pd
import streamlit as st

from src.metrics import edge_bucket_report, overall_metrics, signal_report


DATA_PATH = Path(__file__).parent / "sample_data" / "demo_predictions.csv"


@st.cache_data
def load_demo_data() -> pd.DataFrame:
    """Load the synthetic settled-prediction dataset."""
    return pd.read_csv(DATA_PATH)


st.set_page_config(
    page_title="DFS Esports Analytics",
    page_icon="🎯",
    layout="wide",
)

st.title("DFS Esports Analytics")
st.caption("Sanitized portfolio demo · synthetic data · not betting advice")

data = load_demo_data()
metrics = overall_metrics(data)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Settled predictions", f"{metrics['settled']:,}")
col2.metric("Mean absolute error", f"{metrics['mae']:.2f}")
col3.metric("Directional bias", f"{metrics['bias']:+.2f}")
col4.metric("Brier score", f"{metrics['brier']:.3f}")
col5.metric("Signal hit rate", f"{metrics['hit_rate']:.1%}")

overview, edges, architecture, data_tab = st.tabs(
    ["Overview", "Edge analysis", "System design", "Demo data"]
)

with overview:
    left, right = st.columns([3, 2])
    with left:
        st.subheader("Signal performance")
        signals = signal_report(data)
        st.dataframe(
            signals.style.format({"hit_rate": "{:.1%}"}),
            use_container_width=True,
            hide_index=True,
        )
    with right:
        st.subheader("What the metrics mean")
        st.markdown(
            """
            - **MAE** measures the typical size of a projection miss.
            - **Bias** shows systematic over- or under-projection.
            - **Brier score** evaluates probability calibration; lower is better.
            - **Hit rate** grades only non-push Over and Under signals.
            """
        )

    st.info(
        "A model can be nearly unbiased while still producing weak betting "
        "signals. Forecast accuracy, calibration, and market value must be "
        "evaluated separately."
    )

with edges:
    st.subheader("Performance by absolute model edge")
    buckets = edge_bucket_report(data)
    st.dataframe(
        buckets.style.format(
            {
                "mae": "{:.2f}",
                "bias": "{:+.2f}",
                "hit_rate": "{:.1%}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    chart = buckets.set_index("edge_bucket")[["hit_rate"]].dropna()
    st.bar_chart(chart, y_label="Hit rate", x_label="Absolute edge bucket")
    st.caption(
        "Larger model-to-line differences are hypotheses to test—not automatic "
        "evidence of stronger expected value."
    )

with architecture:
    st.subheader("Production workflow")
    st.graphviz_chart(
        """
        digraph {
          rankdir=LR;
          node [shape=box, style="rounded,filled", fillcolor="#EEF4FF"];
          market [label="Market snapshots"];
          normalize [label="Normalization"];
          history [label="Match history"];
          projection [label="Projection engine"];
          store [label="Immutable storage"];
          settle [label="Settlement"];
          evaluate [label="Evaluation"];
          market -> normalize -> projection;
          history -> projection;
          projection -> store -> settle -> evaluate;
        }
        """,
        use_container_width=True,
    )
    st.markdown(
        "The production system is private. This public repository exposes only "
        "the generic evaluation and presentation layer."
    )

with data_tab:
    st.subheader("Synthetic settled predictions")
    st.dataframe(data, use_container_width=True, hide_index=True)
    st.download_button(
        "Download demo CSV",
        data.to_csv(index=False),
        file_name="demo_predictions.csv",
        mime="text/csv",
    )
