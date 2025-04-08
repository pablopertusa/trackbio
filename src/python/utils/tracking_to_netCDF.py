import polars as pl
import numpy as np
import xarray as xr
import pandas as pd  # solo para fechas (xarray no acepta directamente Series de Polars)

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

df = pl.read_csv("data/foca_procesado.csv", schema=schema)
copernicus_data = xr.open_dataset("data/copernicus/processed/Global_Ocean_Physics_Reanalysis_clean.nc")

# Redondear coordenadas a la grid de 1°
df = df.with_columns([
    (pl.col("decimal_latitude").floor()).cast(pl.Int32).alias("lat_bin"),
    (pl.col("decimal_longitude").floor()).cast(pl.Int32).alias("lon_bin"),
    (pl.col("date").dt.truncate("1d")).alias("datetime_day")  # Redondeo a hora
])

# Extraer coordenadas únicas
lat_vals = np.arange(-70, -29)  # -70 a -30 inclusive
lon_vals = np.arange(-70, -29)

# Obtener tiempos únicos
unique_times = df.select("datetime_day").unique().sort("datetime_day").to_series().to_list()
time_to_idx = {t: i for i, t in enumerate(unique_times)}

# 5. Crear índice de lat y lon
lat_to_idx = {lat: i for i, lat in enumerate(lat_vals)}
lon_to_idx = {lon: i for i, lon in enumerate(lon_vals)}

# 6. Crear array de ceros
data = np.zeros((len(unique_times), len(lat_vals), len(lon_vals)), dtype=np.uint8)

# 7. Iterar y marcar presencia
for row in df.iter_rows(named=True):
    t = row["datetime_hour"]
    lat = row["lat_bin"]
    lon = row["lon_bin"]
    if lat in lat_to_idx and lon in lon_to_idx and t in time_to_idx:
        i = time_to_idx[t]
        j = lat_to_idx[lat]
        k = lon_to_idx[lon]
        data[i, j, k] = 1

# 8. Crear dataset xarray
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

# 9. Guardar como NetCDF
ds.to_netcdf("salida_polars.nc")
