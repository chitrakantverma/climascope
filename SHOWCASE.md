# ClimaScope notes

Original repository: 15 March 2026. Current maintenance: 25 October 2026. History is preserved.

## Quick walkthrough

Run `streamlit run app.py` after installing `requirements.txt`. The sample loads automatically.

1. Inspect the heatmap. Its axes are longitude and latitude; the colours represent the selected variable's values.
2. Change the date in the sidebar and click **Update date**.
3. Change latitude/longitude and click **Update location**. The marker and trend use the nearest dataset grid cell.
4. Open **Compare two dates**, choose dates and click **Compare**. The result is the second slice minus the first.

## Explain the project

The app helps inspect a NetCDF file without writing selection and plotting code each time. Xarray opens the file and selects data by labelled coordinates. NumPy/Xarray calculate the summary, Plotly builds charts, and Streamlit provides the controls.

The area-weighted mean uses cosine-latitude weights because regular latitude/longitude cells get smaller near the poles. The supplied sample is regional. A difference between two dates is not evidence of long-term climate change.

This version deliberately uses a plain interface and original data values. The old globe, animation, smoothing and duplicate charts added complexity without helping the main task. They are available in repository history.

Before an interview, run the app yourself and trace the selection, conversion and plotting steps. Be able to explain any AI-assisted code you use; the appearance of the interface does not establish how the code was written.

## Case-study draft

I revisited ClimaScope, a climate-data viewer first uploaded in March 2026.

The current version focuses on four things: a heatmap, dataset statistics, a location trend and a comparison between two dates. The interface uses standard Streamlit controls, and charts show original values without smoothing.

The maintenance also fixes unit conversions, timestamp labels and stale selections when switching datasets. A real regional NCEP sample is bundled with source attribution and reproducible preparation steps. Thirteen test methods cover the calculations, charts and controls.

The next step is connecting the hosted app to this version. The current public URL still points to a separate repository.

Repository: https://github.com/chitrakantverma/climascope

## Browser evidence

Screenshots below are from the local app. The public Streamlit URL uses `supremeacc/finalclimax`; it has not been updated by these commits. No screen recording has been completed.


Plain dashboard, 25 October 2026:

<img width="1280" height="720" alt="clipboard" src="https://github.com/user-attachments/assets/e3e97b7b-bf12-4235-97b2-4721a2d986e8" />
