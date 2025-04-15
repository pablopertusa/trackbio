import json
import polars as pl
from src.python.backend.download_data import download_data
from src.python.backend.get_subset import get_subset
from src.python.utils.get_grid import make_grid_files
from src.python.backend.concat_datasets import concat_datasets
from src.python.utils.clean_data import clean_data
from src.python.utils.tracking_to_netCDF import tracking_to_netCDF
from src.model.prepare_training_data import prepare_training_data, save_distribution_image
from src.model.train import train_model, predict_model

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
        training_verbosity = config["training_verbosity"]
        image_folder = config["distribution_image_folder"]
        if data_folder[-1] != "/": # Para que todos los path sean consistentes
            data_folder += "/"
        if image_folder[-1] != "/": # Para que todos los path sean consistentes
            image_folder += "/"
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

    success_concat = concat_datasets(copernicus_datasets, input_directory, min_year, max_year)

    if not success_concat:
        print("Error en concat, no continuamos")
        return

    # Paso 5: Limpiamos los datos
    input_file = input_directory + "/data_combined.nc"
    output_file = input_directory + "/data_clean.nc"
    success_clean = clean_data(input_file, output_file, method="linear")

    if not success_clean:
        print("Error limpiando los datos, no continuamos") 
        return

    # Paso 6: Creamos el grid con los datos de tracking
    input_file = output_file
    output_file = data_folder + "presence_grid.nc"
    success_grid = tracking_to_netCDF(animal_data, input_file, output_file, debug=False)
    
    if not success_grid:
        print("Error al crear el grid de presencia")
        return

    # Paso 7: Entrenamos el modelo
    presence_grid_file = data_folder + "presence_grid.nc"
    copernicus_grid_file = data_folder + "copernicus/processed/data_clean.nc"
    X_train, X_test, y_train, y_test = prepare_training_data(presence_grid_file, copernicus_grid_file, test_size=0.1, random_state=27)
    batch_size = 16
    model, history = train_model(X_train, X_test, y_train, y_test, batch_size, print_model_summary=training_verbosity)
    y_pred_classes = predict_model(X_test, model)
    output_image_path = image_folder + "test_distribution.png"
    save_distribution_image(y_pred_classes, output_image_path)
    


if __name__ == "__main__":
    run_pipeline()
