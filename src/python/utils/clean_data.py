import xarray as xr

data = xr.open_dataset("/home/pablo/Desktop/zird/2/proy/trackbio/data/copernicus/processed/dataset_concat.nc")
data = data.drop_vars(["siconc", "sithick"])
data = data.drop_duplicates(dim="time")
print("duplicados eliminados")
print("interpolando...")
data = data.interpolate_na(dim="time", method="nearest")

data.to_netcdf("/home/pablo/Desktop/zird/2/proy/trackbio/data/copernicus/processed/clean_data.nc")
print("dataset procesado")