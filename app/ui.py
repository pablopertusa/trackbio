import gradio as gr
import subprocess
import time
import os

def run_app(archivo):
    try:
        proceso = subprocess.Popen(
            ["python3", "-m", "app.app"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        # No usamos process.wait() aquí para no bloquear la interfaz de Gradio.

        while proceso.poll() is None:
            print("Procesando en segundo plano...")
            time.sleep(2)

        stdout, stderr = proceso.communicate()
        print("Salida del proceso:", stdout.decode())
        if stderr:
            print("Error del proceso:", stderr.decode())
            raise RuntimeError(f"Error al ejecutar el proceso: {stderr.decode()}")

        if proceso.returncode != 0:
             raise RuntimeError(f"El proceso terminó con código de error {proceso.returncode}")

    except Exception as e:
        print(f"Error al ejecutar el comando: {e}")
        return [f"Error al procesar: {e}"]  # Devolver un mensaje de error a Gradio

    directorio_imagenes = "images"
    imagenes_generadas = []
    if os.path.exists(directorio_imagenes):
        for nombre_archivo in os.listdir(directorio_imagenes):
            if nombre_archivo.lower().endswith((".png", ".jpg", ".jpeg")):
                ruta_completa = os.path.join(directorio_imagenes, nombre_archivo)
                imagenes_generadas.append(ruta_completa)
    else:
        print(f"Advertencia: El directorio de imágenes '{directorio_imagenes}' no existe.")

    if not imagenes_generadas:
        print("Advertencia: No se encontraron imágenes generadas.")
        return ["No se encontraron imágenes generadas.  Asegúrese de que el script de Python las genera."]

    return imagenes_generadas


def interfaz_gradio():
    """
    Función que define la interfaz de Gradio.
    """
    with gr.Blocks() as interfaz:
        gr.Markdown("# Trackbio")
        boton_procesar = gr.Button("Iniciar app")
        archivo_input = gr.File(label="Subir Archivo")
        galeria_imagenes = gr.Gallery()
        boton_procesar.click(
            fn=run_app,
            inputs=archivo_input,
            outputs=galeria_imagenes
        )
    return interfaz

if __name__ == "__main__":
    interfaz = interfaz_gradio()
    interfaz.launch()