# ClimaScope showcase package

Status: prepared from the actual project and a real NCEP tutorial subset on 25 October 2026. This is maintenance of a repository first committed on 15 March 2026.

## Run the demo

```sh
python -m pip install -r requirements.txt
streamlit run app.py
```

The regional NCEP monthly sample loads automatically. Start with Map View, switch to Globe View, choose two time slices and press Compare, then generate the temporal animation. Change the sidebar coordinates and press Locate on Map to inspect a local time trend. The image/video evidence below is captured from the local app, not a claim about the public cloud deployment.

Public cloud: the existing URL is listed in the README. Its current source/version must be checked before sharing it as the updated build.

## What to explain in an interview

**Problem:** NetCDF data is difficult to inspect without writing analysis code. The dashboard lets a user select a variable, location and time and inspect spatial patterns and temporal differences.

**Flow:** Xarray decodes labelled dimensions and units. The loader loads the data and closes the file handle. The sidebar stores the selected dataset, time and location. NumPy/Xarray compute summaries, SciPy interpolates/smooths map displays, and Plotly renders the figures through Streamlit.

**Why area weights?** Equal latitude/longitude cells cover less physical area near the poles. Cosine-latitude weights approximate those areas on a regular grid. The summary is over the supplied region and uses equal weight per time step. It is not a universal global mean estimator.

**Why two means differ:** The raw four-daily source yields about 12.3598°C. The bundled monthly means yield about 12.3206°C when every month is weighted equally. That difference comes from temporal aggregation and unequal month lengths.

**Bugs discovered during actual validation:** Default Streamlit hashing rejected the Xarray input; NOAA's `degK` alias was missed; subdaily timestamps were truncated; extrema dates could misalign after sorting; dataset switches retained stale location/time state. The current fixes and tests target those failures.

**Limits:** This is an exploratory visualization tool. Smoothing is for display. Comparing two dates does not establish long-term climate change. It does not forecast. Irregular/curvilinear grids, non-standard calendars and additional file backends need more work.

Before an interview, run the demo yourself and explain the above flow from the source. Verification done by this maintenance session should not be presented as your personal testing until you have repeated it.

## LinkedIn case study — draft, not published

ClimaScope now opens with a real NCEP climate sample instead of an empty upload screen.

The project was first uploaded in March 2026. This update focused on checking what happens when real data goes through it.

That exposed a few useful problems: the dataset could not pass through the summary cache, `degK` metadata was not being converted to Celsius, and six-hourly readings were displayed with date-only labels.

The updated version has a documented monthly sample, area-weighted regional summaries, consistent units and tests covering the data and Streamlit controls. Thirteen test methods pass.

One result needs context: the sample covers a region, so its average should never be described as a global temperature. A difference between two dates also says very little about long-term climate change.

Repository: https://github.com/chitrakantverma/climascope

## Evidence

Browser captures and the demo walkthrough are recorded below after UI verification.
