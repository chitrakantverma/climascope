import pandas as pd
import streamlit as st
from modules.visualizations import generate_heatmap


def render_heatmap_panel(ds, selected_var, selected_time, lat=None, lon=None):
    st.subheader("Heatmap")
    date = str(pd.Timestamp(selected_time)) if selected_time is not None else "No time dimension"
    st.caption(f"Variable: {selected_var} · Date: {date}")
    fig = generate_heatmap(ds, selected_var, selected_time, lat, lon)
    if fig is not None:
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
    st.caption("Each coloured cell shows one dataset value. Use the sidebar to change location.")
