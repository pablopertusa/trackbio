import json
import polars as pl
from src.python.backend.download_data import download_data
from src.python.backend.get_subset import get_subset
from src.python.utils.get_grid import make_grid_files
from src.python.backend.concat_datasets import concat_datasets
from src.python.utils.clean_data import clean_data
from src.python.utils.tracking_to_netCDF import tracking_to_netCDF
from src.model.prepare_training_data import prepare_training_data
from src.model.train import train_model, predict_model, predict_model_probs
from src.python.backend.print_maps import save_world_map, save_distribution_image, save_world_map_pretty
from src.python.backend.set_seed import set_seed
from src.python.backend.print_training_history import save_training_history_plot
from src.python.backend.monthly_maps import save_distribution_maps_per_month

def run_pipeline(config_path="config.json", debug=False):
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
    set_seed(10)
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
    # Esto lo usaremos para los mapas
    temp_df = pl.read_csv(temp_path)
    start_month = temp_df.filter(pl.col("first") == 1)["month"].to_list()[0]

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
    test_size = 0.1
    X_train, X_test, y_train, y_test = prepare_training_data(presence_grid_file, copernicus_grid_file, test_size=test_size, random_state=27)
    batch_size = 16
    model = train_model(X_train, X_test, y_train, y_test, batch_size, print_model_summary=training_verbosity, save_history=True, history_path="./training_history.json", debug=debug)
    y_pred_classes = predict_model(X_test, model)
    y_pred_probs = predict_model_probs(X_test, model)
    print(y_pred_probs.shape)

    # Paso 8: Guardamos los mapas y más imágenes
    output_image_path_distribution_real = image_folder + "1_test_distribution_real.png"
    output_image_path_world_real = image_folder + "3_test_distribution_map_real.png"
    output_image_path_distribution_predicted = image_folder + "2_test_distribution_predicted.png"
    output_image_path_world_predicted = image_folder + "4_test_distribution_map_predicted.png"
    #save_distribution_image(y_test, output_image_path_distribution_real, is_test=True)
    save_world_map_pretty(y_test,lat_max, lat_min, lon_max, lon_min, output_image_path_world_real, is_test=True)
    #save_distribution_image(y_pred_classes, output_image_path_distribution_predicted)
    save_world_map_pretty(y_pred_classes,lat_max, lat_min, lon_max, lon_min, output_image_path_world_predicted)
    path_to_history = "./training_history.json"
    save_training_history_plot(path_to_history, image_folder)

    n_months_train = X_train.shape[0]
    save_distribution_maps_per_month(n_months_train, start_month, y_pred_probs, lat_max, lat_min, lon_max, lon_min, image_folder)


if __name__ == "__main__":
    run_pipeline()
