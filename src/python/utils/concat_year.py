import xarray as xr
from pathlib import Path

directory = "data/copernicus/processed"
dataset_concat = xr.open_dataset(f"{directory}/Global_Ocean_Physics_Reanalysis_year_1999_binned.nc") # El archivo más antiguo sobre el que se va a concatenar

for y in range(2000, 2014):
    print(f"{directory}/Global_Ocean_Physics_Reanalysis_year_{y}_binned.nc")
    data = xr.open_dataset(f"{directory}/Global_Ocean_Physics_Reanalysis_year_{y}_binned.nc")
    dataset_concat = xr.combine_by_coords([dataset_concat, data])
    print(f"{directory}/Global_Ocean_Physics_Reanalysis_year_{y}_binned.nc", "concatenado")

dataset_concat.to_netcdf(f"{directory}/dataset_concat.nc")
print("dataset concatenado en:", f"{directory}/dataset_concat.nc")