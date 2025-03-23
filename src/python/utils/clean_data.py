import xarray as xr

data = xr.open_dataset("/home/pablo/Desktop/zird/2/proy/trackbio/data/copernicus/processed/dataset_concat.nc")
data = data.drop_vars(["siconc", "sithick"]) # Estas variables eran todo NaN
data = data.drop_duplicates(dim="time") # Había duplicados debido a cómo se hacían las requests
print("duplicados eliminados")
print("interpolando...")
data = data.interpolate_na(dim="time", method="linear") # Quitamos los NaN interpolando sobre la dimensión del tiempo

data.to_netcdf("/home/pablo/Desktop/zird/2/proy/trackbio/data/copernicus/processed/clean_data.nc")
print("dataset procesado")