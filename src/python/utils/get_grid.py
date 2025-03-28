import xarray as xr
from pathlib import Path
import numpy as np

directory = "data/copernicus/raw"
path = Path(directory)
output = "data/copernicus/processed"
grid_size = 1

for file in path.iterdir():
    if file.name[-3:] == ".nc":
        print("binning", file)
        data = xr.open_dataset(file.absolute())
        lat_bins = np.arange(data.latitude.min(), data.latitude.max() + grid_size, grid_size)
        lon_bins = np.arange(data.longitude.min(), data.longitude.max() + grid_size, grid_size)

        lat_labels = (lat_bins[:-1] + lat_bins[1:]) / 2
        lon_labels = (lon_bins[:-1] + lon_bins[1:]) / 2

        data_binned = data.groupby_bins("latitude", lat_bins, labels=lat_labels).mean()
        data_binned = data_binned.groupby_bins("longitude", lon_bins, labels=lon_labels).mean()

        data_binned.to_netcdf(f"{output}/{file.name[:-3]}_binned.nc")
        print(file, "terminado")