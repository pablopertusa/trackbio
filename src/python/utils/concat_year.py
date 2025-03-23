import xarray as xr
from pathlib import Path

directory = "data/copernicus/processed"
filename = "Global_Ocean_Physics_Reanalysis_year"
dataset_concat = xr.open_dataset(f"{directory}/{filename}_1999_binned.nc") # El archivo más antiguo sobre el que se va a concatenar

for y in range(2000, 2014):
    print(f"{directory}/{filename}_{y}_binned.nc")
    data = xr.open_dataset(f"{directory}/{filename}_{y}_binned.nc")
    dataset_concat = xr.combine_by_coords([dataset_concat, data])
    print(f"{directory}/{filename}_{y}_binned.nc", "concatenado")

dataset_concat.to_netcdf(f"{directory}/{filename}_concat.nc")
print("dataset concatenado en:", f"{directory}/{filename}_concat.nc")