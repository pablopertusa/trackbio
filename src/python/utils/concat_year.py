import xarray as xr
import polars as pl

def concat_year(directory: str, filename: str, min_year: int, max_year: int) -> bool:
    try:
        dataset_concat = xr.open_dataset(f"{directory}/{filename}_{min_year}_binned.nc") # El archivo más antiguo sobre el que se va a concatenar
        # Nos quedamos con la media de cada mes
        dataset_concat_mensual = dataset_concat.resample(time="1ME").mean()

        for y in range(min_year+1, max_year+1):
            print(f"{directory}/{filename}_{y}_binned.nc")
            data = xr.open_dataset(f"{directory}/{filename}_{y}_binned.nc")
            # Nos quedamos con la media de cada mes
            data_mensual = data.resample(time="1ME").mean()
            # Lo concatenamos con el primero
            dataset_concat = xr.combine_by_coords([dataset_concat_mensual, data_mensual])
            print(f"{directory}/{filename}_{y}_binned.nc", "concatenado")

        dataset_concat.to_netcdf(f"{directory}/{filename}_concat.nc")
        print("dataset concatenado en:", f"{directory}/{filename}_concat.nc")
        return True

    except Exception as e:
        print("Ha ocurrido un error:")
        print(e)
        return False

if __name__ == "__main__":
    directory = "data/copernicus/processed"
    filename = ["Global_Ocean_Physics_Reanalysis"]
    temp = pl.read_csv("/home/pablo/Desktop/zird/2/proy/trackbio/data/temporal_subset.csv")
    min_year = temp.filter(pl.col("first") == 1)["year"].to_list()[0]
    max_year = temp.filter(pl.col("first") == 0)["year"].to_list()[0]

    for f in filename:
        concat_year(directory, f, min_year, max_year)