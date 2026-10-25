import numpy as np
import pandas as pd
import streamlit as st
import xarray as xr
from modules.grid_math import latitude_weights


def compute_climate_insights(dataset, variable):
    """
    Compute summary statistics for a climate variable across the entire dataset.
    
    Returns a dictionary with:
      - global_avg: Area-weighted dataset mean, with equal weight per time step.
      - max_value: The maximum value.
      - max_location: (lat, lon, time) of the maximum value.
      - min_value: The minimum value.
      - min_location: (lat, lon, time) of the minimum value.
      - largest_change: Signed change with the largest magnitude between consecutive time steps.
      - largest_change_times: (time_from, time_to) of the largest change.
    """
    if dataset is None or variable not in dataset:
        return None
        
    data = dataset[variable].where(np.isfinite(dataset[variable]))
    
    lat_name = 'lat' if 'lat' in dataset.coords else 'latitude' if 'latitude' in dataset.coords else None
    lon_name = 'lon' if 'lon' in dataset.coords else 'longitude' if 'longitude' in dataset.coords else None
    
    if not lat_name or not lon_name:
        return None
        
    try:
        extra_dims = set(data.dims) - {lat_name, lon_name, 'time'}
        if extra_dims:
            raise ValueError("Select a single level/member before computing statistics.")
        if data[lat_name].ndim != 1 or data[lon_name].ndim != 1:
            raise ValueError("Statistics require a regular rectilinear latitude/longitude grid.")
        # Validate longitude spacing; cosine latitude weights assume equal-width cells.
        longitudes = np.asarray(data[lon_name].values, dtype=float)
        if not np.isfinite(longitudes).all() or len(np.unique(longitudes)) != len(longitudes):
            raise ValueError("Longitude coordinates must be finite and unique.")
        if len(longitudes) > 2 and not np.allclose(np.diff(longitudes), np.diff(longitudes)[0], rtol=1e-4, atol=1e-6):
            raise ValueError("Statistics require evenly spaced longitude coordinates.")
        if not bool(data.notnull().any()):
            raise ValueError("The selected variable contains no valid observations.")
        if 'time' in data.dims:
            data = data.sortby('time')
            if len(np.unique(data.time.values)) != len(data.time):
                raise ValueError("Duplicate timestamps must be resolved before comparing time steps.")
        weights = xr.DataArray(latitude_weights(data[lat_name].values), coords={lat_name: data[lat_name]}, dims=[lat_name])
        spatial_mean = data.weighted(weights).mean(dim=[lat_name, lon_name], skipna=True)
        insights = {}
        
        # 1. Global average value
        insights['global_avg'] = float(spatial_mean.mean(skipna=True).values)
        
        # 2. Maximum value and location
        max_idx = data.fillna(-np.inf).argmax(dim=...)
        insights['max_value'] = float(data.max().values)
        max_lat = float(data[lat_name].values[max_idx[lat_name].values])
        max_lon = float(data[lon_name].values[max_idx[lon_name].values])
        if 'time' in max_idx:
            try:
                max_time = pd.to_datetime(data['time'].values[max_idx['time'].values]).strftime('%Y-%m-%d %H:%M')
            except:
                max_time = str(data['time'].values[max_idx['time'].values])
            insights['max_location'] = f"{max_lat:.2f}°, {max_lon:.2f}° on {max_time}"
        else:
            insights['max_location'] = f"{max_lat:.2f}°, {max_lon:.2f}°"
        
        # 3. Minimum value and location
        min_idx = data.fillna(np.inf).argmin(dim=...)
        insights['min_value'] = float(data.min().values)
        min_lat = float(data[lat_name].values[min_idx[lat_name].values])
        min_lon = float(data[lon_name].values[min_idx[lon_name].values])
        if 'time' in min_idx:
            try:
                min_time = pd.to_datetime(data['time'].values[min_idx['time'].values]).strftime('%Y-%m-%d %H:%M')
            except:
                min_time = str(data['time'].values[min_idx['time'].values])
            insights['min_location'] = f"{min_lat:.2f}°, {min_lon:.2f}° on {min_time}"
        else:
            insights['min_location'] = f"{min_lat:.2f}°, {min_lon:.2f}°"
        
        # 4. Largest change between consecutive time steps
        if 'time' in data.dims and len(data.time) > 1:
            # Compute the mean across space for each time step, then diff
            # Use the same area weighting as the dataset mean.
            diffs = spatial_mean.diff(dim='time')
            abs_diffs = np.abs(diffs)
            
            if not bool(abs_diffs.notnull().any()):
                raise ValueError('No valid consecutive time steps are available for comparison.')
            max_change_idx = int(abs_diffs.fillna(-np.inf).argmax(dim='time').values)
            max_change_time = diffs.time.values[max_change_idx]
            insights['largest_change'] = float(diffs.sel(time=max_change_time, method='nearest').values)
            
            try:
                t_from = pd.to_datetime(data.time.values[max_change_idx]).strftime('%Y-%m-%d %H:%M')
                t_to = pd.to_datetime(data.time.values[max_change_idx + 1]).strftime('%Y-%m-%d %H:%M')
            except:
                t_from = str(data.time.values[max_change_idx])
                t_to = str(data.time.values[max_change_idx + 1])
                
            insights['largest_change_times'] = f"{t_from} → {t_to}"
        else:
            insights['largest_change'] = None
            insights['largest_change_times'] = None
        
        return insights
        
    except Exception as e:
        st.error(f"Error computing climate insights: {e}")
        return None
