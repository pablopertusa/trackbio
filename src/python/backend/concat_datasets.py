# Esta función concatenado los ficheros que han pasado el proceso de binning en un 
# único fichero

from src.python.utils.concat_year import concat_year
import xarray as xr

def concat_datasets(dataset_list: list[str], input_directory: str, min_year: int, max_year: int) -> bool:
    try:
        for dataset in dataset_list:
            success = concat_year(input_directory, dataset, min_year, max_year)
            if not success:
                return False
        
        data_dict = {}
        for dataset in dataset_list:
            data = xr.open_dataset(f"{input_directory}/{dataset}_concat.nc")
            data = data.squeeze(dim='depth') # Quitamos la dimensión depth que no hace falta y solo tiene un valor
            data_dict[dataset] = data
        data_list = list(data_dict.values())
        data_combined = xr.merge(data_list)
        data_combined.to_netcdf(f"{input_directory}/data_combined.nc")

        return True

    except Exception as e:
        print("Error al concatenar:", e)
        return False
