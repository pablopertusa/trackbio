import src.python.utils.make_requests as make_requests
import polars as pl
from datetime import datetime
import copernicusmarine as cm
from dotenv import load_dotenv
import os

def get_data(dataset_id: str, temp_path: str, box_path: str, output_file: str, output_directory: str = "/home/pablo/Desktop/zird/2/proy/trackbio/data/copernicus/raw") -> bool:
    """
    Descarga el dataset de la API de Copernicus con el id `dataset_id`
    Devuelve True si la descarga se realiza correctamente, False en otro caso.
    """
    try: 
        # Cargamos desde .env
        load_dotenv()

        username = os.getenv("USERNAME_COPERNICUS")
        password = os.getenv("PASSWORD_COPERNICUS")

        # Nos logeamos en la API de Copernicusmarine
        cm.login(username=username, password=password, force_overwrite=True)

        # Cogemos el subconjunto de los datos que necesitamos
        temp = pl.read_csv(temp_path)
        box = pl.read_csv(box_path)

        day = temp.filter(pl.col("first") == 1)["day"].to_list()[0]
        month = temp.filter(pl.col("first") == 1)["month"].to_list()[0]
        year = temp.filter(pl.col("first") == 1)["year"].to_list()[0]
        min_time = f"{day}-{month}-{year}"
        day = temp.filter(pl.col("first") == 0)["day"].to_list()[0]
        month = temp.filter(pl.col("first") == 0)["month"].to_list()[0]
        year = temp.filter(pl.col("first") == 0)["year"].to_list()[0]
        max_time = f"{day}-{month}-{year}"
        fecha_min = datetime.strptime(min_time, "%d-%m-%Y")
        fecha_min_format = fecha_min.strftime("%Y-%m-%dT%H:%M:%S")
        fecha_max = datetime.strptime(max_time, "%d-%m-%Y")
        fecha_max_format = fecha_max.strftime("%Y-%m-%dT%H:%M:%S")

        max_latitude = box["max_latitude"].to_list()[0]
        min_latitude = box["min_latitude"].to_list()[0]
        max_longitude = box["max_longitude"].to_list()[0]
        min_longitude = box["min_longitude"].to_list()[0]

        print("empezamos")
        for y in range(fecha_min.year, fecha_max.year+1):
            print("---------------------------")
            print(f"AÑO: {y}")
            if y == fecha_min.year:
                fin = datetime.strptime(f"31-12-{y}", "%d-%m-%Y")
                fin_format = fin.strftime("%Y-%m-%dT%H:%M:%S")
                make_requests.make_request_copernicus(dataset_id, f"{output_file}_{y}.nc",
                                                        fecha_min_format, fin_format, max_latitude, min_latitude, max_longitude, min_longitude, output_directory)
            elif y == fecha_max.year:
                inicio = datetime.strptime(f"1-1-{y}", "%d-%m-%Y")
                inicio_format = fin.strftime("%Y-%m-%dT%H:%M:%S")
                make_requests.make_request_copernicus(dataset_id, f"{output_file}_{y}.nc",
                                                        inicio_format, fecha_max_format, max_latitude, min_latitude, max_longitude, min_longitude, output_directory)
            else:
                inicio = datetime.strptime(f"1-1-{y}", "%d-%m-%Y")
                fin = datetime.strptime(f"31-12-{y}", "%d-%m-%Y")
                inicio_format = inicio.strftime("%Y-%m-%dT%H:%M:%S")
                fin_format = fin.strftime("%Y-%m-%dT%H:%M:%S")
                make_requests.make_request_copernicus(dataset_id, f"{output_file}_{y}.nc",
                                                        inicio_format, fin_format, max_latitude, min_latitude, max_longitude, min_longitude, output_directory)
            print(f"AÑO: {y} FINALIZADO")
        print("Fin de descarga de datos")
        return True

    except Exception as e:
        print("Ha ocurrido un error, la descarga no se ha completado:")
        print(e)
        return False



if __name__ == "__main__":
    dataset_id = ["cmems_mod_glo_phy_my_0.083deg_P1D-m"] 
    output_file_name = ["Global_Ocean_Physics_Reanalysis_year"] # La extensión .nc se pone automáticamente en la función get_data

    for d, o in zip(dataset_id, output_file_name):
        get_data(d, o)