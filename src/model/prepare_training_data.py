import xarray as xr
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler


def prepare_training_data(path_to_presence_grid: str, path_to_copernicus_grid: str, test_size: float = 0.1, random_state: int = 27) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    data_copernicus = xr.open_dataset(path_to_copernicus_grid)
    data_presence = xr.open_dataset(path_to_presence_grid)

    X = data_copernicus.to_array().transpose("time", "variable", "latitude_bins", "longitude_bins").values
    y = data_presence.presencia.values
    # Lo pasamos a binario
    y_binario = (y > 0).astype(float)

    X_train, X_test, y_train, y_test = train_test_split(X, y_binario, test_size=test_size, random_state=random_state)

    # Normalizar X
    scaler_X = MinMaxScaler()
    X_train = X_train.reshape(-1, X_train.shape[-1])
    X_test = X_test.reshape(-1, X_test.shape[-1])
    X_train = scaler_X.fit_transform(X_train)
    X_test = scaler_X.transform(X_test)

    # Reajustar las dimensiones después de la normalización
    X_train = X_train.reshape(-1, 35, 252, 15)
    X_test = X_test.reshape(-1, 35, 252, 15)

    # Normalizar y
    scaler_y = MinMaxScaler()
    y_train = y_train.reshape(-1, y_train.shape[-1])
    y_test = y_test.reshape(-1, y_test.shape[-1])
    y_train = scaler_y.fit_transform(y_train)
    y_test = scaler_y.transform(y_test)

    # Reajustar las dimensiones después de la normalización
    y_train = y_train.reshape(-1, 35, 252, 1)
    y_test = y_test.reshape(-1, 35, 252, 1)

    return X_train, X_test, y_train, y_test


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

