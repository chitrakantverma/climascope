import streamlit as st

from components.sidebar import render_sidebar
from components.heatmap_panel import render_heatmap_panel
from components.timeseries_panel import render_timeseries_panel
from components.comparison_panel import render_comparison_panel
from components.insights_panel import render_insights_panel

st.set_page_config(page_title="ClimaScope", layout="wide")
st.title("ClimaScope")
st.write("Explore a climate dataset by location and date.")

if "dataset" not in st.session_state:
    st.session_state.dataset = None

variable, time, lat, lon = render_sidebar()
dataset = st.session_state.dataset

if dataset is None or variable is None:
    st.info("Upload a NetCDF (.nc) file using the sidebar to begin.")
    st.stop()

if "pydata/xarray-data" in str(dataset.attrs.get("source", "")):
    st.caption("Sample: NCEP monthly air temperature, 2013–2014. Covers 15–75°N and 200–330°E.")

render_heatmap_panel(dataset, variable, time, lat, lon)
render_insights_panel(dataset, variable)
render_timeseries_panel(dataset, variable, lat, lon)

with st.expander("Compare two dates"):
    render_comparison_panel(dataset, variable)
