import polars as pl
import numpy as np
import xarray as xr
import pandas as pd  # solo para fechas (xarray no acepta directamente Series de Polars)
import os

def encontrar_bin(valor, bins):
    idx = np.digitize(valor, bins) - 1  # Restamos 1 para que el índice sea coherente con el bin izquierdo
    if idx < 0:
        idx = 0
    if idx >= len(bins):
        return None  # El valor está fuera del rango de bins
    return bins[idx]

# Esta función es necesaria porque al agrupar por mes con la API de xarray, se pone como fecha del grupo
# el último día de cada mes, por lo que es necesario para mantener la consistencia del grid.
def ultimo_dia_del_mes(fecha):
    """
    Devuelve un string con el último día del mes de la fecha dada,
    en formato 'YYYY-MM-DDT00:00:00.000000000'.
    
    Parámetros:
        fecha (str o pd.Timestamp): Fecha de entrada, como string o Timestamp.
        
    Retorna:
        str: Último día del mes en formato especificado.
    """

    fecha = pd.to_datetime(fecha)
    ultimo_dia = fecha + pd.offsets.MonthEnd(0)
    return pd.Timestamp(ultimo_dia).strftime('%Y-%m-%dT00:00:00.000000000')


def tracking_to_netCDF(animal_data: str, copernicus_data: str, output_file: str, debug: bool = False) -> bool:
    if os.path.exists(output_file):
        print("presence_grid.nc cacheado, no se inicia el proceso de transformación")
        return True

    try:
        print("Convirtiendo los datos de tracking a grid...")
        df = pl.read_csv(animal_data)
        copernicus_data = xr.open_dataset(copernicus_data) # Es data_clean.nc

        # Encontramos en qué celda del grid de los datos de copernicus caería cada observación
        df = df.with_columns([
            (pl.col("latitude").map_elements(lambda x: encontrar_bin(x, copernicus_data["latitude_bins"].values), return_dtype=pl.Float64)).alias("lat_bin"),
            (pl.col("longitude").map_elements(lambda x: encontrar_bin(x, copernicus_data["longitude_bins"].values), return_dtype=pl.Float64)).alias("lon_bin"),
            (pl.col("date").map_elements(lambda x: ultimo_dia_del_mes(x), return_dtype=str)).alias("mes")  # Redondeo a mes
        ])

        if debug:
            print(df)

        # Extraer coordenadas únicas
        lat_vals = copernicus_data["latitude_bins"].values
        lon_vals = copernicus_data["longitude_bins"].values

        # Obtener tiempos únicos
        unique_times = copernicus_data["time"].values

        time_to_idx = {t: i for i, t in enumerate(unique_times)}

        # Crear índice de lat y lon
        lat_to_idx = {lat: i for i, lat in enumerate(lat_vals)}
        lon_to_idx = {lon: i for i, lon in enumerate(lon_vals)}

        # Crear array de ceros (esto es el grid que se irá rellenando con las observaciones)
        data = np.zeros((len(unique_times), len(lat_vals), len(lon_vals)), dtype=np.int64)
        if debug: 
            print(time_to_idx)
            print(lat_to_idx)
            print(lon_to_idx)

        # Iterar y marcar presencia
        not_found = 0
        for row in df.iter_rows(named=True):
            t = row["mes"]
            t_parsed = np.datetime64(t)
            lat = row["lat_bin"]
            lon = row["lon_bin"]

            if lat in lat_to_idx and lon in lon_to_idx and t_parsed in time_to_idx:
                i = time_to_idx[t_parsed]
                j = lat_to_idx[lat]
                k = lon_to_idx[lon]
                data[i, j, k] += 1
            else:
                not_found += 1

        print("INFO: Observaciones no encontradas en el grid de datos:", not_found)

        # Crear dataset xarray
        ds = xr.Dataset(
            {
                "presencia": (["time", "latitude", "longitude"], data)
            },
            coords={
                "time": pd.to_datetime(unique_times),
                "latitude": lat_vals,
                "longitude": lon_vals
            }
        )

        # Guardar como NetCDF
        ds.to_netcdf(output_file)
        return True

    except Exception as e:
        print(f"Ha ocurrido un error pasando los datos de tracking a grid: {e}")
        return False
