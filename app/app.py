import json
import polars as pl
from src.python.backend.download_data import download_data
from src.python.backend.get_subset import get_subset
from src.python.utils.get_grid import make_grid_files
from src.python.utils.concat_year import concat_year

def run_pipeline(config_path="config.json"):
    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
    except Exception:
        print("Necesitas un config.json para que funcione correctamente")
        return

    try:
        animal_data = config["animal_data"]
        copernicus_datasets = config["copernicus_datasets"]
        data_folder = config["data_folder"]
        grid_size = config["grid_size"]
    except KeyError:
        print("Tu archivo config.json no tiene los campos necesarios")
        return

    # Paso 1: Obtener subset
    success_subset = get_subset(animal_data, data_folder)
    if not success_subset:
        print("Error en subset, no continuamos")
        return

    # Paso 2: Descargar datos
    box_path = data_folder + "world_box.csv"
    temp_path = data_folder + "temporal_subset.csv"
    output_directory_raw = data_folder + "copernicus/raw"
    success_download = download_data(copernicus_datasets, box_path, temp_path, output_directory_raw)
    if not success_download:
        print("Error en download, no continuamos")
        return

    # Paso 3: Binning (crear grid)
    input_directory = output_directory_raw
    output_directory_processed = data_folder + "copernicus/processed"
    df_world_box = pl.read_csv(box_path)
    lat_max = df_world_box["max_latitude"].to_list()[0]
    lat_min = df_world_box["min_latitude"].to_list()[0]
    lon_max = df_world_box["max_longitude"].to_list()[0]
    lon_min = df_world_box["min_longitude"].to_list()[0]

    success_binning = make_grid_files(
        input_directory,
        output_directory_processed,
        grid_size,
        lat_min, lat_max,
        lon_min, lon_max
    )
    if not success_binning:
        print("Error en binning, no continuamos")
        return

    # Paso 4: Concatenar por año
    input_directory = output_directory_processed
    df_temp = pl.read_csv(temp_path)
    min_year = df_temp.filter(pl.col("first") == 1)["year"].to_list()[0]
    max_year = df_temp.filter(pl.col("first") == 0)["year"].to_list()[0]

    success_concat_list = []
    for dataset in copernicus_datasets:
        success_aux = concat_year(input_directory, dataset, min_year, max_year)
        if not success_aux:
            print(f"Error al concatenar dataset {dataset}, no continuamos")
            return
        success_concat_list.append(success_aux)

    success_concat = all(success_concat_list)
    if success_concat:
        print("Hemos llegado al final")
    else:
        print("No hemos completado la ejecución")

if __name__ == "__main__":
    run_pipeline()
