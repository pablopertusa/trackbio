import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import ListedColormap
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import contextily as cx
import matplotlib as mpl
import warnings


def save_world_map(y_pred_classes, lat_max, lat_min, lon_max, lon_min, output_image_path, is_test=False):
    if is_test:
        y_pred_classes = np.squeeze(y_pred_classes)

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
    if is_test:
        plt.title('Mapa de calor (real)')
    else:
        plt.title('Mapa de calor (predicho)')
    plt.tight_layout()
    plt.savefig(output_image_path)
    plt.close(fig)

    if is_test:
        print("imagen de la distribución en el mundo de test guardada en", output_image_path)
    else:
        print("imagen de las predicciones de distribución en el mundo en test guardada en", output_image_path)


def save_world_map_pretty(y_pred_classes, lat_max, lat_min, lon_max, lon_min, output_image_path, is_test=False):
    if is_test:
        y_pred_classes = np.squeeze(y_pred_classes)

    arr_sum = np.sum(y_pred_classes, axis=0)

    # === Coordenadas geográficas del grid original
    nlat_count, nlon_count = arr_sum.shape

    # === Bordes del grid
    lat_edges = np.linspace(lat_max, lat_min, nlat_count + 1)
    lon_edges = np.linspace(lon_min, lon_max, nlon_count + 1)

    # === Construcción de polígonos de cada celda y valores
    polygons, values = [], []
    for i in range(nlat_count):
        for j in range(nlon_count):
            polygons.append(
                Polygon([
                    (lon_edges[j],     lat_edges[i]),
                    (lon_edges[j + 1], lat_edges[i]),
                    (lon_edges[j + 1], lat_edges[i + 1]),
                    (lon_edges[j],     lat_edges[i + 1]),
                ])
            )
            values.append(arr_sum[i, j])

    # GeoDataFrame WGS84 → Web-Mercator
    gdf = gpd.GeoDataFrame({"value": values, "geometry": polygons}, crs="EPSG:4326").to_crs(epsg=3857)

    # Filtrar valores > 0 para que las celdas con 0 no se muestren
    gdf_pos = gdf[gdf["value"] > 0]

    # === Configuración de la figura más horizontal
    fig, ax = plt.subplots(figsize=(16, 8))  # ancho aumentado, altura reducida
    ax.set_facecolor("#ffffff")  # fondo blanco para áreas sin datos

    # === Definir extensión longitudinal amplia (–80° a 160°)
    R = 6378137.0  # radio terrestre en EPSG:3857
    lon_min_vis, lon_max_vis = -80.0, 160.0
    x_min_vis = R * np.radians(lon_min_vis)
    x_max_vis = R * np.radians(lon_max_vis)
    # Límites de latitud basados en datos + buffer vertical (200 km)
    _, y_min_data, _, y_max_data = gdf.total_bounds
    buffer_y = 2e5
    ax.set_xlim(x_min_vis, x_max_vis)
    ax.set_ylim(y_min_data - buffer_y, y_max_data + buffer_y)

    # === Añadir mapa base con proveedores de teselas (fallback)
    for provider in [
        cx.providers.CartoDB.Voyager,
        cx.providers.OpenStreetMap.Mapnik,
        cx.providers.Esri.WorldGrayCanvas
    ]:
        try:
            cx.add_basemap(ax, source=provider, attribution_size=6, reset_extent=False)
            break
        except Exception as exc:
            warnings.warn(f"Proveedor {provider} no disponible: {exc}")
    else:
        warnings.warn("Sin mapa base; se mostrará solo la capa de calor.")

    # === Crear colormap de amarillo-anaranjado (tipo yema)
    base_cmap = plt.cm.get_cmap("YlOrRd", 256)
    # Usar entre 20% y 100% del degradado original
    new_colors = base_cmap(np.linspace(0.2, 1.0, 256))
    cmap_yema = mpl.colors.ListedColormap(new_colors)

    # === Pintar heatmap con el nuevo colormap
    gdf_pos.plot(
        ax=ax,
        column="value",
        cmap=cmap_yema,
        linewidth=0,
        edgecolor="none",
        alpha=0.9,
        zorder=10,
    )

    # === Colorbar ajustada a shrink=0.66 y aspect=25
    norm = mpl.colors.Normalize(vmin=gdf_pos["value"].min(), vmax=gdf_pos["value"].max())
    sm = mpl.cm.ScalarMappable(cmap=cmap_yema, norm=norm)
    sm._A = []  # necesario para la colorbar
    cb = fig.colorbar(
        sm,
        ax=ax,
        orientation='vertical',
        pad=0.01,
        shrink=1,
        aspect=25
    )
    cb.set_label("Valor sumado")

    # === Título y detalles finales
    if is_test:
        ax.set_title('Mapa de calor (real)')
    else:
        ax.set_title('Mapa de calor (predicho)')
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(output_image_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    if is_test:
        print("imagen de la distribución en el mundo de test guardada en", output_image_path)
    else:
        print("imagen de las predicciones de distribución en el mundo en test guardada en", output_image_path)


def save_world_map_probs(y_pred_probs, lat_max, lat_min, lon_max, lon_min, output_image_path, month, is_test=False):

    num_lat, num_lon = y_pred_probs.shape

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
    mesh = ax.pcolormesh(lon_edges, lat_edges, y_pred_probs, cmap=red_white_cmap, shading='auto', transform=ccrs.PlateCarree())

    plt.colorbar(mesh, ax=ax, orientation='vertical', label='Valor sumado')
    if is_test:
        plt.title(f'Mapa de calor {month} (real)')
    else:
        plt.title(f'Mapa de calor {month} (predicho)')
    plt.tight_layout()
    plt.savefig(output_image_path)
    plt.close(fig)

    if is_test:
        print("imagen de la distribución en el mundo de test guardada en", output_image_path)
    else:
        print("imagen de las predicciones de distribución en el mundo en test guardada en", output_image_path)

def save_distribution_image(data: np.ndarray, output_image_path: str, is_test=False) -> None:
    """
    La dimensión temporal debe ser la primera para que se pinten bien los resultados
    """
    if is_test:
        data = np.squeeze(data)

    arr_sum = np.sum(data, axis=0)

    plt.figure(figsize=(12, 6))
    plt.imshow(arr_sum, cmap='viridis', aspect='auto')
    plt.colorbar(label='Valor sumado')
    if is_test:
        plt.title('Heatmap de la distribución (real)')
    else:
        plt.title('Heatmap de la distribución (predicho)')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    plt.savefig(output_image_path)

    if is_test:
        print("imagen de la distribución en test guardada en", output_image_path)
    else:
        print("imagen de las predicciones de distribución en test guardada en", output_image_path)


def save_world_map_probs_pretty(y_pred_probs, lat_max, lat_min, lon_max, lon_min, output_image_path, month, is_test=False):

    nlat_count, nlon_count = y_pred_probs.shape

    lat_edges = np.linspace(lat_max, lat_min, nlat_count + 1)
    lon_edges = np.linspace(lon_min, lon_max, nlon_count + 1)

    # === Construcción de polígonos de cada celda y valores
    polygons, values = [], []
    for i in range(nlat_count):
        for j in range(nlon_count):
            polygons.append(
                Polygon([
                    (lon_edges[j],     lat_edges[i]),
                    (lon_edges[j + 1], lat_edges[i]),
                    (lon_edges[j + 1], lat_edges[i + 1]),
                    (lon_edges[j],     lat_edges[i + 1]),
                ])
            )
            values.append(y_pred_probs[i, j])

    # GeoDataFrame WGS84 → Web-Mercator
    gdf = gpd.GeoDataFrame({"value": values, "geometry": polygons}, crs="EPSG:4326").to_crs(epsg=3857)

    # Filtrar valores > 0 para que las celdas con 0 no se muestren
    media = gdf["value"].mean()
    gdf_pos = gdf[gdf["value"] > 7*media]

    # === Configuración de la figura más horizontal
    fig, ax = plt.subplots(figsize=(16, 8))  # ancho aumentado, altura reducida
    ax.set_facecolor("#ffffff")  # fondo blanco para áreas sin datos

    # === Definir extensión longitudinal amplia (–80° a 160°)
    R = 6378137.0  # radio terrestre en EPSG:3857
    lon_min_vis, lon_max_vis = -80.0, 160.0
    x_min_vis = R * np.radians(lon_min_vis)
    x_max_vis = R * np.radians(lon_max_vis)
    # Límites de latitud basados en datos + buffer vertical (200 km)
    _, y_min_data, _, y_max_data = gdf.total_bounds
    buffer_y = 2e5
    ax.set_xlim(x_min_vis, x_max_vis)
    ax.set_ylim(y_min_data - buffer_y, y_max_data + buffer_y)

    # === Añadir mapa base con proveedores de teselas (fallback)
    for provider in [
        cx.providers.CartoDB.Voyager,
        cx.providers.OpenStreetMap.Mapnik,
        cx.providers.Esri.WorldGrayCanvas
    ]:
        try:
            cx.add_basemap(ax, source=provider, attribution_size=6, reset_extent=False)
            break
        except Exception as exc:
            warnings.warn(f"Proveedor {provider} no disponible: {exc}")
    else:
        warnings.warn("Sin mapa base; se mostrará solo la capa de calor.")

    # === Crear colormap de amarillo-anaranjado (tipo yema)
    base_cmap = plt.cm.get_cmap("YlOrRd", 256)
    # Usar entre 20% y 100% del degradado original
    new_colors = base_cmap(np.linspace(0.2, 1.0, 256))
    cmap_yema = mpl.colors.ListedColormap(new_colors)

    # === Pintar heatmap con el nuevo colormap
    gdf_pos.plot(
        ax=ax,
        column="value",
        cmap=cmap_yema,
        linewidth=0,
        edgecolor="none",
        alpha=0.9,
        zorder=10,
    )

    # === Colorbar ajustada a shrink=0.66 y aspect=25
    norm = mpl.colors.Normalize(vmin=gdf_pos["value"].min(), vmax=gdf_pos["value"].max())
    sm = mpl.cm.ScalarMappable(cmap=cmap_yema, norm=norm)
    sm._A = []  # necesario para la colorbar
    cb = fig.colorbar(
        sm,
        ax=ax,
        orientation='vertical',
        pad=0.01,
        shrink=1,
        aspect=25
    )
    cb.set_label("Valor sumado")
    if is_test:
        plt.title(f'Mapa de calor {month} (real)')
    else:
        plt.title(f'Mapa de calor {month} (predicho)')
    plt.tight_layout()
    plt.savefig(output_image_path)
    plt.close(fig)

    if is_test:
        print("imagen de la distribución en el mundo de test guardada en", output_image_path)
    else:
        print("imagen de las predicciones de distribución en el mundo en test guardada en", output_image_path)

def save_distribution_image(data: np.ndarray, output_image_path: str, is_test=False) -> None:
    """
    La dimensión temporal debe ser la primera para que se pinten bien los resultados
    """
    if is_test:
        data = np.squeeze(data)

    arr_sum = np.sum(data, axis=0)

    plt.figure(figsize=(12, 6))
    plt.imshow(arr_sum, cmap='viridis', aspect='auto')
    plt.colorbar(label='Valor sumado')
    if is_test:
        plt.title('Heatmap de la distribución (real)')
    else:
        plt.title('Heatmap de la distribución (predicho)')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    plt.savefig(output_image_path)

    if is_test:
        print("imagen de la distribución en test guardada en", output_image_path)
    else:
        print("imagen de las predicciones de distribución en test guardada en", output_image_path)