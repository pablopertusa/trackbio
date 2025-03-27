import polars as pl
import xarray as xr

def get_data_by_location(data_tracking, data_climate):
    # Seleccionar la celda de la cuadrícula más cercana
    data_tracking = data_tracking.with_columns(
        pl.lit(data_climate["latitude_bins"].sel(latitude_bins=data_tracking["decimal_latitude"].to_numpy(), method="nearest").values).alias("lat_grid_lookup"),
        pl.lit(data_climate["longitude_bins"].sel(longitude_bins=data_tracking["decimal_longitude"].to_numpy(), method="nearest").values).alias("lon_grid_lookup")
    )

    # Extraer las variables climáticas de la celda más cercana
    climate_vars = data_climate.sel(latitude_bins=data_tracking["lat_grid_lookup"].to_numpy(), longitude_bins=data_tracking["lon_grid_lookup"].to_numpy(), time=data_tracking["date_format"].to_numpy(), method="nearest")

    # Convertir datos climáticos a Polars
    df_clima = pl.from_pandas(climate_vars.to_dataframe().reset_index()).unique()
    # Parsear las fechas
    data_tracking = data_tracking.with_columns(
        pl.col("date_format").str.to_datetime("%Y-%m-%dT%H:%M:%S", time_unit="ns")
    )

    # Unir tracking con clima en Polars
    df_merged = data_tracking.join(
        df_clima.rename({ # Se renombra para poder hacer el join bien
            "latitude_bins": "lat_grid_lookup",
            "longitude_bins": "lon_grid_lookup",
            "time": "date_format"
        }),
        on=["lat_grid_lookup", "lon_grid_lookup", "date_format"],
        how="left"
    )
    return df_merged


data_tracking = pl.read_csv("data/animals_processed.csv")
data_climate = xr.open_dataset("data/copernicus/processed/clean_data.nc")
resul = pl.DataFrame()

# Procesar de 100 en 100
batch_size = 200
for i in range(0, len(data_tracking), batch_size):
    print(f"Batch {i} procesado")
    batch = data_tracking.slice(i, batch_size)  # Seleccionar 100 filas
    processed = get_data_by_location(batch, data_climate)
    resul = pl.concat([resul, processed])  # Concatenar al resultado

print("Procesado terminado")
resul.write_csv("data/final_data.csv")