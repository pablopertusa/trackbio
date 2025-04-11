import xarray as xr

def clean_data(filename_input: str, filename_output: str, method: str = "linear") -> bool:
    try:
        data = xr.open_dataset(filename_input)
        data = data.drop_vars(["siconc", "sithick"]) # Estas variables eran todo NaN
        data = data.drop_duplicates(dim="time") # Había duplicados debido a cómo se hacían las requests
        print("Duplicados eliminados")

        print("Interpolando...")
        data = data.interpolate_na(dim="time", method=method) # Quitamos los NaN interpolando sobre la dimensión del tiempo

        data.to_netcdf(filename_output)
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