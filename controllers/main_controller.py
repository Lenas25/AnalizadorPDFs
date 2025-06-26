# Importar módulos necesarios de Flask y el servicio de procesamiento de PDF
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
from services.pdf_service import extraer_data_pdf
import os

# Crear un blueprint para las rutas principales de la aplicación
main_bp = Blueprint('main', __name__)

# Lista global para almacenar los datos extraídos de los archivos PDF
data_extraida = []

# Ruta de la página principal (inicio)
@main_bp.route("/", methods=["GET", "POST"])
def home():
    global data_extraida
    # Reinicia la lista cada vez que se entra a la página de inicio
    data_extraida = []
    return render_template("index.html")

# Ruta para mostrar la página de estadísticas
@main_bp.route("/estadisticas", methods=["GET", "POST"])
def estadisticas():
    if request.method == "GET":
        return render_template("estadisticas.html")
    # Si es POST, redirige a inicio
    return redirect(url_for("main.home"))

# Ruta para obtener los datos estadísticos extraídos en formato JSON (usado por JavaScript)
@main_bp.route("/dataestadistica", methods=["GET"])
def data_estadistica():
    global data_extraida
    return jsonify(data=data_extraida)

# Ruta que busca archivos PDF en la carpeta local 'uploads' según el título ingresado por el usuario
@main_bp.route("/buscar", methods=["POST", "GET"])
def buscar_titulo():
    global data_extraida
    data_extraida = []  # Reiniciar resultados anteriores

    if request.method == "POST":
        termino_busqueda = request.form.get("buscar_tema", "").lower()

        if termino_busqueda:
            # Recorrer todos los archivos PDF en la carpeta de subidas
            for nombrearchivo in os.listdir(current_app.config['UPLOAD_FOLDER']):
                if nombrearchivo.endswith(".pdf"):
                    urlarchivo = os.path.join(current_app.config['UPLOAD_FOLDER'], nombrearchivo)
                    data = extraer_data_pdf(urlarchivo)

                    # Comparar el término de búsqueda con el título del PDF
                    if data and termino_busqueda in data["titulo"].lower():
                        data_extraida.append(data)

            # Mostrar resultados en la misma plantilla de inicio
            return render_template("index.html", data_list=data_extraida)

    # Si no se envió un término de búsqueda válido, redirige a inicio con error
    return redirect(url_for("main.home", error="Por favor, ingresa un término de búsqueda."))

# Ruta para subir archivos PDF, extraer datos de cada uno y mostrarlos en la interfaz
@main_bp.route("/extract", methods=["POST", "GET"])
def extract():
    global data_extraida

    if request.method == "POST":
        # Obtener los archivos PDF enviados desde el formulario
        files = request.files.getlist("pdf")

        # Validar que todos los archivos sean PDFs
        if not files or any(not file.filename.endswith('.pdf') for file in files):
            return render_template("index.html", error="Por favor, sube solo archivos válidos en formato PDF.")

        # Guardar y procesar cada archivo PDF
        for file in files:
            print(file.filename)  # Opcional: imprimir el nombre en consola para seguimiento
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)  # Guardar archivo en carpeta temporal (uploads)
            data = extraer_data_pdf(filepath)  # Extraer metadatos, resumen, país, etc.

            if data:
                data_extraida.append(data)

        # Renderizar los resultados extraídos en la plantilla de inicio
        return render_template("index.html", data_list=data_extraida)

    # Si se accede por GET o sin archivos, redirige a inicio con error
    return redirect(url_for("main.home", error="Por favor, adjunta archivos."))
