import xarray as xr
from pathlib import Path
import numpy as np

def make_grid_files(input_directory: str, output_directory: str, grid_size: int, latitude_min: float,
                       latitude_max: float, longitude_min: float, longitude_max: float) -> bool:
    try:
        path = Path(input_directory)
        for file in path.iterdir():
            if file.name[-3:] == ".nc":
                print("binning", file)
                data = xr.open_dataset(file.absolute())
                lat_bins = np.arange(latitude_min, latitude_max + grid_size, grid_size)
                lon_bins = np.arange(longitude_min, longitude_max + grid_size, grid_size)

                lat_labels = (lat_bins[:-1] + lat_bins[1:]) / 2
                lon_labels = (lon_bins[:-1] + lon_bins[1:]) / 2

                data_binned = data.groupby_bins("latitude", lat_bins, labels=lat_labels).mean()
                data_binned = data_binned.groupby_bins("longitude", lon_bins, labels=lon_labels).mean()

                data_binned.to_netcdf(f"{output_directory}/{file.name[:-3]}_binned.nc")
                print(file, "terminado")
        return True

    except Exception as e:
        print("Error en binning:", e)
        return False



if __name__ == "__main__":
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