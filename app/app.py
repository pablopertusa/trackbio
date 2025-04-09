import json
from src.python.backend.download_data import download_data
from src.python.backend.get_subset import get_subset
from src.python.utils.get_grid import make_grid_files
from src.python.utils.concat_year import concat_year
import polars as pl

try:
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
except Exception as e:
    print("Necesitas un config.json para que funcione correctamente")

try:
    animal_data = config["animal_data"]
    copernicus_datasets = config["copernicus_datasets"]
    data_folder = config["data_folder"]
    grid_size = config["grid_size"]
except KeyError:
    print("Tu archivo config.json no tiene los campos necesarios")

# Cogemos el subconjunto espacial y temporal
success_subset = get_subset(animal_data, data_folder)

if success_subset:
    box_path = data_folder + "world_box.csv"
    temp_path = data_folder + "temporal_subset.csv"
    output_directory = data_folder + "copernicus/raw"
    # Descargamos los datos
    success_download = download_data(copernicus_datasets, box_path, temp_path, output_directory)
else:
    print("Error en subset, no continuamos")

if success_download:
    input_directory = data_folder + "copernicus/raw"
    output_directory = data_folder + "copernicus/processed"
    df_world_box = pl.read_csv(box_path)
    lat_max = df_world_box["max_latitude"].to_list()[0]
    lat_min = df_world_box["min_latitude"].to_list()[0]
    lon_max = df_world_box["max_longitude"].to_list()[0]
    lon_min = df_world_box["min_longitude"].to_list()[0]
    # Hacemos el grid de los archivos más grande para que todos coincidan y sean manejables
    success_binning = make_grid_files(input_directory, output_directory, grid_size, lat_min, lat_max, lon_min, lon_max)
else:
    print("Error en download, no continuamos")

if success_binning:
    input_directory = data_folder + "copernicus/processed"
    df_temp = pl.read_csv(temp_path)
    min_year = df_temp.filter(pl.col("first") == 1)["year"].to_list()[0]
    max_year = df_temp.filter(pl.col("first") == 0)["year"].to_list()[0]
    success_concat_list = []
    for dataset in copernicus_datasets:
        # Concatenamos todos los años de cada dataset
        success_aux = concat_year(input_directory, dataset, min_year, max_year)
        success_concat_list.append(success_aux)
    success_concat = all(success_concat_list)
else:
    print("Error en binning, no continuamos")

if success_concat:
    print("Hemos llegado al final")

