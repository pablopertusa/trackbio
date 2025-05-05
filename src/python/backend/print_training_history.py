import matplotlib.pyplot as plt
import json

def save_training_history_plot(path_to_history: str, path_to_images_folder: str) -> None:
    try:
        with open(path_to_history, "r") as file:
            history = json.load(file)

        for k in history:
            values = history[k]
            plt.plot(values)
            plt.xlabel("Epoch")
            plt.ylabel(k)
            plt.title(f"Evolución de {k} en training")
            path = path_to_images_folder + f"{k}_training"
            plt.savefig(path)

    except Exception as e:
        print("Ha ocurrido un error creando los gráficos de las métricas: ", e)

