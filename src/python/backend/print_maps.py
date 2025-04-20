import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import ListedColormap

def save_world_map(y_pred_classes, lat_max, lat_min, lon_max, lon_min, output_image_path):

    arr_sum = np.sum(y_pred_classes, axis=0)

    num_lat, num_lon = arr_sum.shape

    # Crear bordes
    lat_edges = np.linspace(lat_max, lat_min, num_lat + 1)
    lon_edges = np.linspace(lon_min, lon_max, num_lon + 1)

    # === Crear colormap personalizado con escala roja y blanco para 0
    reds = plt.colormaps.get_cmap('OrRd')
    colors = reds(np.linspace(0, 1, 256))
    colors[0] = [1, 1, 1, 1]  # blanco puro para valor 0
    red_white_cmap = ListedColormap(colors)

    fig = plt.figure(figsize=(18, 9))
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray')

    # Mapa de calor
    mesh = ax.pcolormesh(lon_edges, lat_edges, arr_sum, cmap=red_white_cmap, shading='auto', transform=ccrs.PlateCarree())

    plt.colorbar(mesh, ax=ax, orientation='vertical', label='Valor sumado')
    plt.title('Mapa de calor (predicho)')
    plt.tight_layout()
    plt.savefig(output_image_path)
    print("imagen de las predicciones de distribución en el mundo en test guardada en ", output_image_path)


def save_distribution_image(data: np.ndarray, output_image_path: str) -> None:
    """
    La dimensión temporal debe ser la primera para que se pinten bien los resultados
    """
    arr_sum = np.sum(data, axis=0)

    plt.figure(figsize=(12, 6))
    plt.imshow(arr_sum, cmap='viridis', aspect='auto')
    plt.colorbar(label='Valor sumado')
    plt.title('Heatmap de la distribución')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    plt.savefig(output_image_path)
    print("imagen de las predicciones de distribución en test guardada en ", output_image_path)