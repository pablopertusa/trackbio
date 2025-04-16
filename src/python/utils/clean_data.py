import xarray as xr
import os

def clean_data(filename_input: str, filename_output: str, method: str = "linear") -> bool:
    if os.path.exists(filename_output):
        print("data_clean.nc cacheado, no se inicia el proceso de limpieza")
        return True

    try:
        data = xr.open_dataset(filename_input)
        data = data.drop_vars(["siconc", "sithick"]) # Estas variables eran todo NaN
        data = data.drop_duplicates(dim="time") # Había duplicados debido a cómo se hacían las requests
        print("Duplicados eliminados")

        print("Interpolando...")
        data_inter = (
            data
            .interpolate_na(dim="time", method=method)
            .interpolate_na(dim="latitude_bins", method=method)
            .interpolate_na(dim="longitude_bins", method=method)
            .ffill("time").bfill("time")
            .ffill("latitude_bins").bfill("latitude_bins")
            .ffill("longitude_bins").bfill("longitude_bins")
        )

        data_inter.to_netcdf(filename_output)
        print("Dataset procesado")
        return True

    except Exception as e:
        print("Ha ocurrido un error:")
        print(e)
        return False


if __name__== "__main":
    filename_input = ["/home/pablo/Desktop/zird/2/proy/trackbio/data/copernicus/processed/Global_Ocean_Physics_Reanalysis_concat.nc"]
    filename_output = ["/home/pablo/Desktop/zird/2/proy/trackbio/data/copernicus/processed/Global_Ocean_Physics_Reanalysis_clean.nc"]
    for fi, fo in zip(filename_input, filename_output):
        clean_data(fi, fo, method="nearest")