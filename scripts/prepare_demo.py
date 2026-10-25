"""Derive the bundled monthly sample from Xarray's real NCEP tutorial file."""
from pathlib import Path
import argparse
import hashlib
import json
import xarray as xr

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = 'https://github.com/pydata/xarray-data/blob/master/air_temperature.nc'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    with xr.open_dataset(args.source) as original:
        monthly = original.resample(time='MS').mean(keep_attrs=True).load()
        monthly['air'] = monthly.air.astype('float32')
        monthly.air.attrs.update(long_name='Monthly mean air temperature at sigma level 995', statistic='Monthly mean of four-daily observations')
        monthly.attrs.update(source=SOURCE_URL, processing='Monthly arithmetic means derived from the NCEP tutorial subset; regional, not global.')
        target = ROOT / 'data/ncep_air_monthly_2013_2014.nc'
        monthly.to_netcdf(target, engine='scipy')
        provenance = {
            'source_url': SOURCE_URL,
            'source_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(),
            'derived_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'source_time_steps': original.sizes['time'],
            'derived_time_steps': monthly.sizes['time'],
            'latitude_extent': [float(original.lat.min()), float(original.lat.max())],
            'longitude_extent_native': [float(original.lon.min()), float(original.lon.max())],
            'processing': monthly.attrs['processing'],
            'units': monthly.air.attrs['units'],
            'attribution': 'NCEP-NCAR Reanalysis 1 data provided by NOAA PSL, Boulder, Colorado, USA; tutorial subset maintained by pydata/xarray-data.',
            'source_documentation': 'https://tutorial.xarray.dev/fundamentals/01_datastructures.html',
        }
        (ROOT/'data/provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
        print(json.dumps(provenance, indent=2))

if __name__ == '__main__': main()
