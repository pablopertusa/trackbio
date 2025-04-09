# Esta función descarga los datos necesarios de la API de copernicus
from ..utils import get_data

def download_data(dataset_list: list[str], box_path: str, temp_path: str, output_directory: str) -> bool:
    """
    Para ejecutar correctamente esta función se necesita tener un archivo .env la carpeta raíz
    del proyecto con los campos `USERNAME_COPERNICUS` y `PASSWORD_COPERNICUS`. Por ejemplo en `trackbio/.env`
    """
    for dataset in dataset_list:
        success = get_data(dataset, temp_path, box_path, dataset, output_directory)
        if not success:
            print("Error en la descarga")
            return False
