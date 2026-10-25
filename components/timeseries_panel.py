import streamlit as st
from modules.visualizations import generate_time_series


def render_timeseries_panel(ds, selected_var, lat, lon):
    st.subheader("Location trend")
    if lat is None or lon is None:
        st.info("Select latitude and longitude in the sidebar.")
        return
    fig = generate_time_series(ds, selected_var, lat, lon)
    if fig is not None:
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
    else:
        st.caption("A time dimension is needed for this chart.")
