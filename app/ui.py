import subprocess
import time
import os
import gradio as gr
import shutil


def run_app(uploaded_file):
    """
    Runs the app as a subprocess and processes its output.

    Args:
        uploaded_file: The uploaded file object from Gradio.

    Returns:
        A list of paths to the generated image files, or an error message.
    """
    try:
        if uploaded_file:
            input_filename = os.path.basename(uploaded_file.name)
            current_directory = os.getcwd()
            data_directory = current_directory + "/data"
            destination_path = os.path.join(data_directory, input_filename)
            shutil.move(uploaded_file.name, destination_path)
            print(f"Archivo guardado en: {destination_path}")

            process = subprocess.Popen(
                ["python3", "-m", "app.app"],
                cwd=current_directory
            )
            process.wait()

            if process.returncode != 0:
                raise RuntimeError(f"El proceso terminó con código de error {process.returncode}")
        else:
            return ["No file uploaded."]

    except Exception as e:
        print(f"Error executing command: {e}")
        return [f"Error processing: {e}"]  # Return an error message to Gradio

    images_directory = "images"
    generated_images = []
    if os.path.exists(images_directory):
        for filename in os.listdir(images_directory):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                full_path = os.path.join(images_directory, filename)
                generated_images.append(full_path)
    else:
        print(f"Warning: The images directory '{images_directory}' does not exist.")

    if not generated_images:
        print("Warning: No generated images found.")
        return ["No generated images found. Ensure the Python script generates them."]

    generated_images.sort()
    return generated_images


def gradio_interface():
    """
    Function defining the Gradio interface.
    """
    with gr.Blocks(title="Trackbio") as interface:
        gr.Markdown("<div align='center'><h1>TRACKBIO</h1></div>")
        file_input = gr.File(label="Upload File")
        process_button = gr.Button("Start App", variant="primary")
        image_gallery = gr.Gallery(format="png", columns=1)
        process_button.click(
            fn=run_app,
            inputs=file_input,
            outputs=image_gallery
        )
    return interface

if __name__ == "__main__":
    interface = gradio_interface()
    interface.launch()