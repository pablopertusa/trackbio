import polars as pl
import numpy as np
import xarray as xr
import pandas as pd  # solo para fechas (xarray no acepta directamente Series de Polars)

def encontrar_bin(valor, bins):
    idx = np.digitize(valor, bins) - 1  # Restamos 1 para que el índice sea coherente con el bin izquierdo
    if idx < 0:
        idx = 0
    if idx >= len(bins) - 1:
        return None  # El valor está fuera del rango de bins
    return bins[idx]

def tracking_to_netCDF(animal_data: str, copernicus_data: str, output_file: str, apply_trackbio_pipeline: bool = False) -> bool:
    try:

        if apply_trackbio_pipeline:
            schema = {
                "individual_id": pl.String,
                "date": pl.Datetime,
                "decimal_longitude": pl.Float64,
                "decimal_latitude": pl.Float64,
                "year": pl.Int32,
                "month": pl.Int8,
                "day": pl.Int8,
                "hour": pl.Int8,
            }

            df = pl.read_csv(animal_data, schema=schema)
            # Aplicamos el mismo filtrado que se hizo para sacar el subconjunto de datos espacial y temporal en data_subset.ipynb
            df = df.filter(pl.col("year") >= 2005) # Quitar algunos años para que el dataset se pueda tratar en local
            df = df.filter(pl.col("decimal_longitude") >= -90).filter(pl.col("decimal_longitude") <= 90) # Quitar outliers
            copernicus_data = xr.open_dataset(copernicus_data) # Es data_clean.nc
            df.rename({"decimal_latitude":"latitude", "decimal_longitude": "longitude"})
        else:
            df = pl.read_csv(animal_data)
            copernicus_data = xr.open_dataset(copernicus_data) # Es data_clean.nc

        # Encontramos en qué celda del grid de los datos de copernicus caería cada observación
        df = df.with_columns([
            (pl.col("latitude").map_elements(lambda x: encontrar_bin(x, copernicus_data["latitude_bins"].values), return_dtype=pl.Float64)).alias("lat_bin"),
            (pl.col("longitude").map_elements(lambda x: encontrar_bin(x, copernicus_data["longitude_bins"].values), return_dtype=pl.Float64)).alias("lon_bin"),
            (pl.col("date").dt.truncate("1d")).alias("datetime_day")  # Redondeo a día
        ])

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
        data = np.zeros((len(unique_times), len(lat_vals), len(lon_vals)), dtype=np.uint8)

        # Iterar y marcar presencia
        not_found = 0
        for row in df.iter_rows(named=True):
            t = row["datetime_day"]
            t_parsed = np.datetime64(t)
            lat = row["lat_bin"]
            lon = row["lon_bin"]

            if lat in lat_to_idx and lon in lon_to_idx and t_parsed in time_to_idx:
                i = time_to_idx[t_parsed]
                j = lat_to_idx[lat]
                k = lon_to_idx[lon]
                data[i, j, k] = 1
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
