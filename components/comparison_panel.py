import pandas as pd
import streamlit as st
from modules.data_loader import get_time_range
from modules.visualizations import generate_difference_heatmap


def render_comparison_panel(ds, selected_var):
    times = get_time_range(ds)
    if len(times) < 2:
        st.info("At least two dates are needed for comparison.")
        return
    # Store indices in the controls, then select the matching dataset timestamps.
    left, right = st.columns(2)
    def label(index):
        return str(pd.Timestamp(times[index]))
    first = left.selectbox("First date", range(len(times)), format_func=label)
    second = right.selectbox("Second date", range(len(times)), index=len(times)-1, format_func=label)
    if st.button("Compare", key="compare_btn"):
        fig = generate_difference_heatmap(ds, selected_var, times[first], times[second])
        if fig is not None:
            st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
        st.caption("Second date minus first date. A two-date difference does not establish a climate trend.")
