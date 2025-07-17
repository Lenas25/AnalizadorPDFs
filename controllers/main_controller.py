# Importar módulos necesarios de Flask y el servicio de procesamiento de PDF
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
from services.pdf_service import extraer_data_pdf
import os
import json
from controllers import shared_data

# Crear un blueprint para las rutas principales de la aplicación
main_bp = Blueprint('main', __name__)

# Ruta de la página principal (inicio)
@main_bp.route("/", methods=["GET", "POST"])
def home():
    try:
        shared_data.clear_uploaded_files()
        # Mostrar la página de inicio con los datos actuales (sin limpiar)
        return render_template("index.html", data_list=shared_data.get_data_extraida())
    except Exception as e:
        return render_template("index.html", error=f"Error al cargar la página: {str(e)}")

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
    return jsonify(data=shared_data.get_data_extraida())

# Ruta que busca archivos PDF en la carpeta local 'uploads' según el título ingresado por el usuario
@main_bp.route("/buscar", methods=["POST", "GET"])
def buscar_titulo():
    shared_data.clear_data_extraida()  # Reiniciar resultados anteriores

    if request.method == "POST":
        termino_busqueda = request.form.get("buscar_tema", "").lower()

        if termino_busqueda:
            try:
                # Recorrer todos los archivos PDF en la carpeta de subidas
                for nombrearchivo in os.listdir(current_app.config['UPLOAD_FOLDER']):
                    if nombrearchivo.endswith(".pdf"):
                        urlarchivo = os.path.join(current_app.config['UPLOAD_FOLDER'], nombrearchivo)
                        try:
                            data = extraer_data_pdf(urlarchivo)

                            # Comparar el término de búsqueda con el título del PDF
                            if data and "titulo" in data and termino_busqueda in data["titulo"].lower():
                                shared_data.add_data_extraida(data)
                        except Exception as e:
                            print(f"Error procesando {nombrearchivo}: {str(e)}")
                            continue

                # Mostrar resultados en la misma plantilla de inicio
                return render_template("index.html", data_list=shared_data.get_data_extraida())
            except ImportError:
                return render_template("index.html", error="Error: No se pudo importar el servicio de PDF")
            except FileNotFoundError:
                return render_template("index.html", error="Carpeta de archivos no encontrada.")
            except Exception as e:
                return render_template("index.html", error=f"Error durante la búsqueda: {str(e)}")

    # Si no se envió un término de búsqueda válido, redirige a inicio con error
    return redirect(url_for("main.home", error="Por favor, ingresa un término de búsqueda."))

# Ruta para subir archivos PDF, extraer datos de cada uno y mostrarlos en la interfaz (compatibilidad)
@main_bp.route("/extract", methods=["POST", "GET"])
def extract():
    if request.method == "POST":
        # Obtener los archivos PDF enviados desde el formulario
        files = request.files.getlist("pdf")

        # Validar que todos los archivos sean PDFs
        if not files or any(not file.filename or not file.filename.endswith('.pdf') for file in files):
            return render_template("index.html", error="Por favor, sube solo archivos válidos en formato PDF.")

        # Limpiar listas anteriores
        shared_data.clear_data_extraida()
        shared_data.clear_uploaded_files()

        # Guardar y procesar cada archivo PDF
        for file in files:
            if file.filename:
                print(file.filename)  # Opcional: imprimir el nombre en consola para seguimiento
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)  # Guardar archivo en carpeta temporal (uploads)

                # Agregar a la lista de archivos subidos
                shared_data.add_uploaded_file({
                    'filename': file.filename,
                    'filepath': filepath
                })

                data = extraer_data_pdf(filepath)  # Extraer metadatos, resumen, país, etc.

                if data:
                    shared_data.add_data_extraida(data)

        # Renderizar los resultados extraídos en la plantilla de inicio
        return render_template("index.html", data_list=shared_data.get_data_extraida())

    # Si se accede por GET o sin archivos, redirige a inicio con error
    return redirect(url_for("main.home", error="Por favor, adjunta archivos."))

# Ruta para subir archivos individuales y agregarlos a la lista
@main_bp.route("/upload_file", methods=["POST"])
def upload_file():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400

    file = request.files['pdf']

    if file.filename == '' or file.filename is None:
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Solo se permiten archivos PDF'}), 400

    # Verificar si el archivo ya existe en la lista
    uploaded_files = shared_data.get_uploaded_files()
    if any(f['filename'] == file.filename for f in uploaded_files):
        return jsonify({'error': 'El archivo ya existe en la lista'}), 400

    # Guardar el archivo
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Agregar a la lista de archivos subidos
    shared_data.add_uploaded_file({
        'filename': file.filename,
        'filepath': filepath
    })

    return jsonify({
        'success': True,
        'filename': file.filename,
        'files': shared_data.get_uploaded_files()
    })

# Ruta para eliminar un archivo de la lista
@main_bp.route("/delete_file/<filename>", methods=["DELETE"])
def delete_file(filename):
    uploaded_files = shared_data.get_uploaded_files()

    # Buscar el archivo en la lista
    file_to_remove = None
    for i, file_info in enumerate(uploaded_files):
        if file_info['filename'] == filename:
            file_to_remove = i
            break

    if file_to_remove is None:
        return jsonify({'error': 'Archivo no encontrado'}), 404

    # Eliminar el archivo físico
    filepath = uploaded_files[file_to_remove]['filepath']
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        return jsonify({'error': f'Error al eliminar el archivo: {str(e)}'}), 500

    # Eliminar de la lista
    shared_data.remove_uploaded_file(filename)

    return jsonify({
        'success': True,
        'message': 'Archivo eliminado correctamente',
        'files': shared_data.get_uploaded_files()
    })

# Ruta para obtener la lista de archivos subidos
@main_bp.route("/get_files", methods=["GET"])
def get_files():
    return jsonify({'files': shared_data.get_uploaded_files()})

# Ruta para extraer datos de los archivos en la lista
@main_bp.route("/extract_from_list", methods=["POST"])
def extract_from_list():
    uploaded_files = shared_data.get_uploaded_files()

    if not uploaded_files:
        return jsonify({'error': 'No hay archivos en la lista para procesar'}), 400

    shared_data.clear_data_extraida()  # Reiniciar datos anteriores

    # Procesar cada archivo en la lista
    for file_info in uploaded_files:
        try:
            data = extraer_data_pdf(file_info['filepath'])
            if data:
                shared_data.add_data_extraida(data)
        except Exception as e:
            print(f"Error procesando {file_info['filename']}: {str(e)}")
            continue

    return jsonify({
        'success': True,
        'data_count': len(shared_data.get_data_extraida()),
        'redirect_url': url_for('main.home')
    })
