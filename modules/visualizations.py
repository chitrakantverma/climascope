"""Three basic charts using the dataset values without smoothing."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.data_loader import get_spatial_slice, get_location_timeseries
from modules.variable_adapter import get_variable_info, normalize_values


def _grid(data):
    """Put latitude on rows and longitude on columns."""
    lat = "lat" if "lat" in data.dims else "latitude"
    lon = "lon" if "lon" in data.dims else "longitude"
    if set(data.dims) != {lat, lon}:
        raise ValueError("Choose a variable with only latitude, longitude and optional time dimensions.")
    if data[lat].ndim != 1 or data[lon].ndim != 1:
        raise ValueError("This chart needs one-dimensional latitude and longitude coordinates.")
    return data.transpose(lat, lon), lat, lon


def _heatmap(data, values, lat, lon, units, difference=False):
    options = {"colorscale": "Viridis"}
    if difference:
        valid = np.asarray(values)[np.isfinite(values)]
        limit = float(np.max(np.abs(valid))) if valid.size else 1.0
        limit = limit or 1.0
        options = {"colorscale": "RdBu_r", "zmin": -limit, "zmax": limit, "zmid": 0}
    fig = go.Figure(go.Heatmap(
        x=data[lon].values, y=data[lat].values, z=values,
        colorbar={"title": units}, hoverongaps=False, **options,
        hovertemplate="Longitude: %{x}<br>Latitude: %{y}<br>Value: %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(xaxis_title="Longitude", yaxis_title="Latitude", height=400,
                      margin=dict(l=0, r=0, t=15, b=0))
    return fig


def generate_heatmap(dataset, variable, time_index=None, selected_lat=None, selected_lon=None):
    """Plot the selected time slice as a latitude/longitude grid."""
    try:
        data = get_spatial_slice(dataset, variable, time_index)
        if data is None:
            return None
        data, lat, lon = _grid(data)
        info = get_variable_info(dataset, variable)
        values = normalize_values(data.values, info)
        fig = _heatmap(data, values, lat, lon, info["display_units"])
        if selected_lat is not None and selected_lon is not None:
            # The trend uses the nearest grid cell, so mark that same cell.
            cell = data.sel({lat: selected_lat, lon: selected_lon}, method="nearest")
            fig.add_trace(go.Scatter(x=[float(cell[lon])], y=[float(cell[lat])],
                                     mode="markers", marker=dict(color="black", size=9, symbol="x"),
                                     name="Selected grid cell"))
        return fig
    except (ValueError, KeyError, TypeError) as error:
        st.error(f"Cannot draw heatmap: {error}")
        return None


def generate_time_series(dataset, variable, lat, lon):
    """Plot each observation at the nearest grid cell in time order."""
    data = get_location_timeseries(dataset, variable, lat, lon)
    if data is None:
        return None
    if data.dims != ("time",):
        st.warning("The time trend needs a single value per time step.")
        return None
    data = data.sortby("time")
    info = get_variable_info(dataset, variable)
    values = normalize_values(data.values, info)
    lat_name = "lat" if "lat" in data.coords else "latitude"
    lon_name = "lon" if "lon" in data.coords else "longitude"
    fig = go.Figure(go.Scatter(x=data.time.values, y=values, mode="lines+markers",
                              connectgaps=False, name=variable))
    fig.update_layout(
        title=f"Nearest grid cell: {float(data[lat_name]):.2f}, {float(data[lon_name]):.2f}",
        xaxis_title="Date", yaxis_title=f"{variable} ({info['display_units']})",
        height=300, margin=dict(l=0, r=0, t=45, b=0),
    )
    return fig


def generate_difference_heatmap(dataset, variable, time1, time2):
    """Subtract the first time slice from the second, cell by cell."""
    try:
        first = get_spatial_slice(dataset, variable, time1)
        second = get_spatial_slice(dataset, variable, time2)
        if first is None or second is None:
            return None
        first, lat, lon = _grid(first)
        second = second.transpose(lat, lon)
        info = get_variable_info(dataset, variable)
        # Convert both slices before subtraction; Kelvin offsets cancel out.
        difference = normalize_values(second.values, info) - normalize_values(first.values, info)
        fig = _heatmap(first, difference, lat, lon, info["display_units"], difference=True)
        fig.update_layout(title=f"{pd.Timestamp(time2):%Y-%m-%d %H:%M} minus {pd.Timestamp(time1):%Y-%m-%d %H:%M}",
                          margin=dict(l=0, r=0, t=45, b=0))
        return fig
    except (ValueError, KeyError, TypeError) as error:
        st.error(f"Cannot compare dates: {error}")
        return None
