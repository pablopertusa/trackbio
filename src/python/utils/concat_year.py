import xarray as xr
from pathlib import Path

directory = "data/copernicus/raw"
path = Path(directory)
dataset_concat = xr.open_dataset(f"{str(path)}/Global_Ocean_Physics_Reanalysis_year_1999.nc") # El archivo más antiguo sobre el que se va a concatenar

for file in path.iterdir():
    if file.name[-3:] == ".nc": # Solo vamos a trabajar con los .nc
        print(file)
        data = xr.open_dataset(file.absolute())
        dataset_concat = xr.combine_by_coords([dataset_concat, data])

dataset_concat.to_netcdf(f"{str(path)}dataset_concat.nc")