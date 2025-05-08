import numpy as np
from src.python.utils.calculate_month import calculate_month
from src.python.backend.print_maps import save_world_map_probs

def save_distribution_maps_per_month(elapsed_months: int, start_month: int, predicted_data: np.ndarray,
                                     lat_max, lat_min, lon_max, lon_min, output_image_path) -> None:

    n_months = predicted_data.shape[0]

    months = ["january", "february", "march", "april", "may", "june",
              "july", "august", "september", "october", "november", "december"]
    d = {}
    for m in months:
        d[m] = np.zeros(shape=(predicted_data.shape[1], predicted_data.shape[2]))

    for i in range(n_months):
        month_data = predicted_data[i]
        month = calculate_month(elapsed_months + i + 1, start_month)
        d[month] += month_data

    for m in months:
        d[m] /= n_months # Hacer la media 
    
    for m in months:
        aux_pos_image = months.index(m) + 5 # Esto es para que las imágenes salgan en un orden concreto en la UI
        save_world_map_probs(d[m], lat_max, lat_min, lon_max, lon_min, output_image_path + f"{aux_pos_image}_predicted_distribution_{m}", m)

