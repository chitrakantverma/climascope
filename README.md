# ClimaScope

A small Python dashboard for exploring climate data stored in NetCDF files. Built with Streamlit, Xarray, NumPy and Plotly.

## What it does

- Loads a bundled air-temperature sample or an uploaded `.nc` file.
- Shows a latitude/longitude heatmap for one date.
- Lists the dataset mean, minimum, maximum and largest change between time steps.
- Plots values over time at the nearest grid cell to a selected location.
- Subtracts one date from another to show a difference heatmap.

The interface uses standard Streamlit controls. Charts show the original grid values and observations without interpolation, smoothing or automatic resampling. Globe views, animation and repeated insight panels have been removed from the current dashboard to keep the project small.

## Run locally

Use Python 3.11:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

The sample loads automatically. Change a sidebar value, then click **Update location** or **Update date**. Open **Compare two dates** for the difference chart.

Classic NetCDF files work through SciPy. For the optional NetCDF4 backend, install `requirements-netcdf4.txt`; that backend has not been tested here.

## How the code fits together

| File | Job |
| --- | --- |
| `app.py` | Calls the sidebar and the four dashboard sections |
| `components/sidebar.py` | Loads files and reads the selected variable, location and date |
| `components/` | Displays the charts and summary |
| `modules/data_loader.py` | Opens files and selects coordinates |
| `modules/visualizations.py` | Builds the three chart types |
| `modules/variable_adapter.py` | Reads units and converts Kelvin to Celsius or Pa to hPa |
| `modules/analysis.py` | Calculates statistics |
| `modules/grid_math.py` | Checks the grid and calculates latitude weights |

To understand the project, start with `app.py`, follow `generate_heatmap`, then trace `get_spatial_slice` back to the selected date. The location chart uses Xarray's `sel(..., method="nearest")`. The comparison subtracts corresponding cells in two arrays. Streamlit reruns the script after an interaction; session state keeps loaded datasets and the committed selections.

## One calculation to understand

Latitude/longitude cells represent less area near the poles. The mean therefore uses `cos(latitude)` weights on a regular grid. Xarray applies the weights across latitude and longitude, then averages the time steps equally. This is a regional dataset average. It is not a global temperature estimate, and irregular time spacing is not duration-weighted.

## Sample data

The bundled file has 24 monthly means from 2013–2014, covering **15–75°N, 200–330°E**. It comes from the real NCEP tutorial subset maintained by [pydata/xarray-data](https://github.com/pydata/xarray-data). Data attribution: NCEP-NCAR Reanalysis 1, NOAA PSL, Boulder, Colorado, USA.

Its weighted mean is about **12.3206°C**. Each month receives equal weight, so this differs from averaging all four-daily source observations. Source links, processing notes and file hashes are in `data/provenance.json`.

To rebuild it from the original downloaded `air_temperature.nc`:

```sh
python scripts/prepare_demo.py /path/to/air_temperature.nc
```

## Checks and limits

```sh
python -m unittest test_grid_math.py
python -m unittest discover -s tests -v
```

The 13 test methods cover weighting, units, missing values, timestamps, original chart values, comparison and dataset switching. Runtime versions and results are recorded in `VALIDATION.json`.

Supported data has one-dimensional `lat`/`latitude` and `lon`/`longitude` coordinates, with optional `time`. Select a single level or ensemble member before uploading. Summary statistics require evenly spaced grids. Large files load into memory. Non-standard calendars and curvilinear grids need more work. This app does not predict weather; a two-date comparison does not establish long-term climate change.

## History and demo status

The original repository was first committed on **15 March 2026**. Fixes and this simpler interface were added on **25 October 2026**, keeping the original history. Older globe/animation versions can be found in that history.

The [existing hosted app](https://finalclimax-teygrdtzta6rrlgtm7sul7.streamlit.app/) uses the separate `supremeacc/finalclimax` repository. It is not a verified deployment of this repository's current code. Use the local instructions above until deployment is connected to this source.

[Showcase notes and screenshot](SHOWCASE.md).
