"""Runtime checks against a real NCEP-derived NetCDF and controlled edge cases."""
from pathlib import Path
import sys
import unittest
import hashlib
import json
import numpy as np
import pandas as pd
import xarray as xr
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from modules.analysis import compute_climate_insights
from modules.data_loader import load_dataset
from modules.variable_adapter import get_variable_info, normalize_values
from modules.visualizations import generate_heatmap, generate_time_series, generate_difference_heatmap

SAMPLE = ROOT / 'data/ncep_air_monthly_2013_2014.nc'

def synthetic(values=None, times=None):
    if values is None:
        values = np.array([[[10., 10.], [30., 30.]], [[12., 12.], [32., 32.]]])
    if times is None:
        times = pd.to_datetime(['2020-01-01 00:00', '2020-01-01 06:00'])
    return xr.Dataset({'air': (('time', 'lat', 'lon'), values, {'units': 'degK'})}, coords={'time': times, 'lat': [0., 60.], 'lon': [10., 20.]})

class RuntimeChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds = load_dataset(str(SAMPLE))

    def test_real_sample_integrity_and_dimensions(self):
        provenance = json.loads((ROOT/'data/provenance.json').read_text())
        self.assertEqual(hashlib.sha256(SAMPLE.read_bytes()).hexdigest(), provenance['derived_sha256'])
        self.assertEqual(dict(self.ds.sizes), {'time': 24, 'lat': 25, 'lon': 53})
        self.assertTrue(self.ds.air.attrs['units'] == 'degK')

    def test_weighted_mean_matches_independent_numpy_reference(self):
        values = self.ds.air.values.astype(float)
        weights = np.cos(np.deg2rad(self.ds.lat.values.astype(float)))[:, None]
        expected = np.average(values.mean(axis=0), weights=np.broadcast_to(weights, values.shape[1:]))
        result = compute_climate_insights(self.ds, 'air')
        self.assertAlmostEqual(result['global_avg'], expected, places=10)
        self.assertAlmostEqual(result['max_value'], float(np.nanmax(values)))
        self.assertAlmostEqual(result['min_value'], float(np.nanmin(values)))

    def test_kelvin_alias_and_missing_units(self):
        info = get_variable_info(self.ds, 'air')
        np.testing.assert_allclose(normalize_values(np.array([273.15, 283.15]), info), [0., 10.])
        unknown = self.ds.copy(deep=True)
        unknown.air.attrs.pop('units')
        self.assertEqual(get_variable_info(unknown, 'air')['display_units'], 'units not supplied')

    def test_missing_values_and_subdaily_timestamps(self):
        ds = synthetic()
        ds.air.values[0, 0, 0] = np.nan
        result = compute_climate_insights(ds, 'air')
        self.assertIsNotNone(result)
        self.assertIn('00:00 → 2020-01-01 06:00', result['largest_change_times'])
        self.assertEqual(result['min_value'], 10.)

    def test_unsorted_times_keep_extrema_dates_aligned(self):
        ds = synthetic().isel(time=[1, 0])
        result = compute_climate_insights(ds, 'air')
        self.assertIn('2020-01-01 06:00', result['max_location'])
        self.assertEqual(result['largest_change'], 2.)

    def test_invalid_grids_and_duplicate_times_fail_cleanly(self):
        bad_time = synthetic(times=pd.to_datetime(['2020-01-01', '2020-01-01']))
        self.assertIsNone(compute_climate_insights(bad_time, 'air'))
        empty = synthetic(np.full((2, 2, 2), np.nan))
        self.assertIsNone(compute_climate_insights(empty, 'air'))
        extra = synthetic().expand_dims(level=[1000, 850])
        self.assertIsNone(compute_climate_insights(extra, 'air'))

    def test_charts_preserve_original_cells_and_observations(self):
        first, last = self.ds.time.values[[0, -1]]
        heatmap = generate_heatmap(self.ds, 'air', first)
        trend = generate_time_series(self.ds, 'air', 45, 265)
        difference = generate_difference_heatmap(self.ds, 'air', first, last)
        np.testing.assert_allclose(heatmap.data[0].z, self.ds.air.isel(time=0).values - 273.15)
        np.testing.assert_allclose(trend.data[0].y, self.ds.air.sel(lat=45, lon=265, method='nearest').values - 273.15)
        self.assertEqual(len(trend.data[0].x), 24)
        np.testing.assert_allclose(difference.data[0].z, self.ds.air.isel(time=-1).values - self.ds.air.isel(time=0).values)
        for fig in [heatmap, trend, difference]:
            self.assertIn('data', fig.to_json())
        missing = self.ds.copy(deep=True)
        missing.air.values[0, 0, 0] = np.nan
        self.assertTrue(np.isnan(generate_heatmap(missing, 'air', first).data[0].z[0, 0]))

    def test_streamlit_controls_and_dataset_switch(self):
        at = AppTest.from_file(str(ROOT/'app.py'), default_timeout=45).run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(len(at.error), 0)
        self.assertGreaterEqual(len(at.get('plotly_chart')), 2)
        before = len(at.get('plotly_chart'))
        at.button(key='compare_btn').click().run()
        self.assertEqual(len(at.get('plotly_chart')), before + 1)
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(len(at.error), 0)
        shifted = self.ds.assign_coords(lat=np.linspace(-45, -15, 25), lon=np.linspace(10, 40, 53), time=pd.date_range('2020-01-01', periods=24, freq='MS'))
        at.session_state['datasets'] = {'demo': self.ds, 'shifted': shifted}
        at.run()
        box = next(e for e in at.selectbox if e.label == 'Select Dataset')
        box.set_value('shifted').run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(len(at.error), 0)
        self.assertTrue(-45 <= at.session_state['selected_lat'] <= -15)
        self.assertTrue(10 <= at.session_state['selected_lon'] <= 40)
        self.assertEqual(pd.Timestamp(at.session_state['active_time']).year, 2020)

if __name__ == '__main__': unittest.main()
