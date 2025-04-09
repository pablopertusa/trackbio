# Esta función toma los datos en crudo del animal sobre el que se tienen las observaciones, preferiblemente observaciones de tracking,
# y obtiene el subconjunto temporal y espacial que abarcan estos datos. Es importante para el proceso de descarga de datos, en el que 
# no se quieren descargar datos innecesarios.

import polars as pl

def get_subset(path_to_csv: str, output_directory: str) -> bool:
    """
    Toma como input el CSV donde están los datos del animal y devuelve True si todo se ha podido realizar correctamente. False
    de lo contrario.
    **Importante**: En el CSV se espera que estén presentes las columnas "latitude", "longitude" y "date" con formato "Y-%m-%dT%H:%M:%S".
    """
    try:
        tracking = pl.read_csv(path_to_csv)
        tracking = (
            tracking
            .with_columns(
                pl.col("date").str.strptime(pl.Datetime, format="%Y-%m-%dT%H:%M:%S")
            )
        )
        max_latitude = tracking["latitude"].max()
        max_longitude = tracking["longitude"].max()
        min_latitude = tracking["latitude"].min()
        min_longitude = tracking["longitude"].min()

        box = pl.DataFrame({"max_latitude": max_latitude, "min_latitude": min_latitude, "max_longitude": max_longitude, "min_longitude": min_longitude})
        box.write_csv(f"{output_directory}/data/world_box.csv")

        temp = pl.DataFrame({"first": [1, 0], "day": [tracking.head(1)["date"].to_list()[0].day, tracking.tail(1)["date"].to_list()[0].day], 
                                                    "month": [tracking.head(1)["date"].to_list()[0].month, tracking.tail(1)["date"].to_list()[0].month], 
                                                                "year": [tracking.head(1)["date"].to_list()[0].year, tracking.tail(1)["date"].to_list()[0].year]})
        temp.write_csv(f"{output_directory}/temporal_subset.csv")
        return True

    except Exception as e:
        print("Error durante get_subset:")
        print(e)
        return False
