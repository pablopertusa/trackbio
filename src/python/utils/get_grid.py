import get_data
import polars as pl
from datetime import datetime

temp = pl.read_csv("data/temporal_subset.csv")
box = pl.read_csv("data/world_box.csv")

day = temp.filter(pl.col("mas_actual") == 0)["day"].to_list()[0]
month = temp.filter(pl.col("mas_actual") == 0)["month"].to_list()[0]
year = temp.filter(pl.col("mas_actual") == 0)["year"].to_list()[0]
min_time = f"{day}-{month}-{year}"
day = temp.filter(pl.col("mas_actual") == 1)["day"].to_list()[0]
month = temp.filter(pl.col("mas_actual") == 1)["month"].to_list()[0]
year = temp.filter(pl.col("mas_actual") == 1)["year"].to_list()[0]
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
    if y == 1999:
        fin = datetime.strptime("31-12-1999", "%d-%m-%Y")
        fin_format = fin.strftime("%Y-%m-%dT%H:%M:%S")
        get_data.make_request_copernicus("cmems_mod_glo_phy_my_0.083deg_P1D-m", f"Global_Ocean_Physics_Reanalysis_year_{y}.nc",
                                                fecha_min_format, fin_format, max_latitude, min_latitude, max_longitude, min_longitude)
    elif y == fecha_max.year:
        inicio = datetime.strptime(f"1-1-{y}", "%d-%m-%Y")
        inicio_format = fin.strftime("%Y-%m-%dT%H:%M:%S")
        get_data.make_request_copernicus("cmems_mod_glo_phy_my_0.083deg_P1D-m", f"Global_Ocean_Physics_Reanalysis_year_{y}.nc",
                                                inicio_format, fecha_max_format, max_latitude, min_latitude, max_longitude, min_longitude)
    else:
        inicio = datetime.strptime(f"1-1-{y}", "%d-%m-%Y")
        fin = datetime.strptime(f"31-12-{y}", "%d-%m-%Y")
        inicio_format = inicio.strftime("%Y-%m-%dT%H:%M:%S")
        fin_format = fin.strftime("%Y-%m-%dT%H:%M:%S")
        get_data.make_request_copernicus("cmems_mod_glo_phy_my_0.083deg_P1D-m", f"Global_Ocean_Physics_Reanalysis_year_{y}.nc",
                                                inicio_format, fin_format, max_latitude, min_latitude, max_longitude, min_longitude)
    print(f"AÑO: {y} FINALIZADO")
print("Fin de descarga de datos")