# Importar módulos necesarios de Flask y el servicio de procesamiento de PDF
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
from services.pdf_service import extraer_datos_pdf # Servicio para extraer información de PDFs
import os
import json
from controllers import shared_data as datos_compartidos # Importa los datos compartidos de la aplicación

# Crear un blueprint para las rutas principales de la aplicación
main_bp = Blueprint('main', __name__)

# Ruta de la página principal (inicio)
@main_bp.route("/", methods=["GET", "POST"])
def inicio():
    try:
        # Limpia la lista de archivos subidos al cargar la página principal
        datos_compartidos.clear_archivos_subidos()
        # Muestra la página de inicio con la lista de datos extraídos (si existen)
        return render_template("index.html", lista_datos=datos_compartidos.get_datos_extraidos())
    except Exception as e:
        # En caso de error, muestra la página de inicio con un mensaje de error
        return render_template("index.html", error=f"Error al cargar la página: {str(e)}")

# Ruta para mostrar la página de estadísticas
@main_bp.route("/estadisticas", methods=["GET", "POST"])
def estadisticas():
    # Si la petición es GET, muestra la página de estadísticas
    if request.method == "GET":
        return render_template("estadisticas.html")
    # Si es POST, redirige a la página de inicio
    return redirect(url_for("main.inicio"))

# Ruta para obtener los datos estadísticos extraídos en formato JSON (usado por JavaScript)
@main_bp.route("/datos_estadistica", methods=["GET"])
def datos_estadistica():
    # Devuelve los datos extraídos en formato JSON para ser consumidos por el frontend
    return jsonify(datos=datos_compartidos.get_datos_extraidos())

# Ruta que busca archivos PDF en la carpeta local 'uploads' según el título ingresado por el usuario
@main_bp.route("/buscar", methods=["POST", "GET"])
def buscar_titulo():
    # Limpia los resultados de búsquedas anteriores
    datos_compartidos.clear_datos_extraidos()

    # Si la petición es POST, procesa la búsqueda
    if request.method == "POST":
        termino_busqueda = request.form.get("buscar_tema", "").lower()

        # Verifica que se haya ingresado un término de búsqueda
        if termino_busqueda:
            try:
                # Recorre todos los archivos en la carpeta de subidas
                for nombre_archivo in os.listdir(current_app.config['UPLOAD_FOLDER']):
                    if nombre_archivo.endswith(".pdf"):
                        ruta_archivo = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_archivo)
                        try:
                            # Extrae los datos del PDF
                            datos = extraer_datos_pdf(ruta_archivo)

                            # Compara el término de búsqueda con el título del PDF (en minúsculas)
                            if datos and "titulo" in datos and termino_busqueda in datos["titulo"].lower():
                                datos_compartidos.add_datos_extraidos(datos)
                        except Exception as e:
                            # Si hay un error procesando un archivo, lo imprime y continúa
                            print(f"Error procesando {nombre_archivo}: {str(e)}")
                            continue

                # Muestra los resultados en la plantilla de inicio
                return render_template("index.html", lista_datos=datos_compartidos.get_datos_extraidos())
            except ImportError:
                return render_template("index.html", error="Error: No se pudo importar el servicio de PDF")
            except FileNotFoundError:
                return render_template("index.html", error="Carpeta de archivos no encontrada.")
            except Exception as e:
                return render_template("index.html", error=f"Error durante la búsqueda: {str(e)}")

    # Si no se envió un término de búsqueda, redirige a inicio con un error
    return redirect(url_for("main.inicio", error="Por favor, ingresa un término de búsqueda."))

# Ruta para subir archivos PDF, extraer datos de cada uno y mostrarlos en la interfaz
@main_bp.route("/extraer", methods=["POST", "GET"])
def extraer():
    # Si la petición es POST, procesa los archivos subidos
    if request.method == "POST":
        # Obtiene la lista de archivos PDF enviados desde el formulario
        archivos = request.files.getlist("pdf")

        # Valida que todos los archivos sean PDF válidos
        if not archivos or any(not archivo.filename or not archivo.filename.endswith('.pdf') for archivo in archivos):
            return render_template("index.html", error="Por favor, sube solo archivos válidos en formato PDF.")

        # Limpia las listas de datos y archivos de sesiones anteriores
        datos_compartidos.clear_datos_extraidos()
        datos_compartidos.clear_archivos_subidos()

        # Procesa cada archivo PDF subido
        for archivo in archivos:
            if archivo.filename:
                # Guarda el archivo en la carpeta de subidas
                ruta_archivo = os.path.join(current_app.config['UPLOAD_FOLDER'], archivo.filename)
                archivo.save(ruta_archivo)

                # Agrega la información del archivo a la lista de archivos subidos
                datos_compartidos.add_archivo_subido({
                    'filename': archivo.filename,
                    'filepath': ruta_archivo
                })

                # Extrae los datos del archivo PDF
                datos = extraer_datos_pdf(ruta_archivo)

                # Si se extrajeron datos, los agrega a la lista de datos
                if datos:
                    datos_compartidos.add_datos_extraidos(datos)

        # Muestra los resultados extraídos en la plantilla de inicio
        return render_template("index.html", lista_datos=datos_compartidos.get_datos_extraidos())

    # Si se accede por GET, redirige a inicio con un error
    return redirect(url_for("main.inicio", error="Por favor, adjunta archivos."))

# Ruta para subir archivos individuales y agregarlos a la lista
@main_bp.route("/subir_archivo", methods=["POST"])
def subir_archivo():
    # Verifica si se incluyó un archivo en la petición
    if 'pdf' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400

    archivo = request.files['pdf']

    # Verifica si se seleccionó un archivo
    if archivo.filename == '' or archivo.filename is None:
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    # Verifica que el archivo sea un PDF
    if not archivo.filename.endswith('.pdf'):
        return jsonify({'error': 'Solo se permiten archivos PDF'}), 400

    # Verifica si el archivo ya existe en la lista de subidos
    archivos_subidos = datos_compartidos.get_archivos_subidos()
    if any(f['filename'] == archivo.filename for f in archivos_subidos):
        return jsonify({'error': 'El archivo ya existe en la lista'}), 400

    # Guarda el archivo en el servidor
    ruta_archivo = os.path.join(current_app.config['UPLOAD_FOLDER'], archivo.filename)
    archivo.save(ruta_archivo)

    # Agrega el archivo a la lista de archivos subidos
    datos_compartidos.add_archivo_subido({
        'filename': archivo.filename,
        'filepath': ruta_archivo
    })

    # Devuelve una respuesta JSON confirmando la subida
    return jsonify({
        'success': True,
        'filename': archivo.filename,
        'files': datos_compartidos.get_archivos_subidos()
    })

# Ruta para eliminar un archivo de la lista
@main_bp.route("/eliminar_archivo/<nombre_archivo>", methods=["DELETE"])
def eliminar_archivo(nombre_archivo):
    archivos_subidos = datos_compartidos.get_archivos_subidos()

    # Busca el archivo en la lista para obtener su información
    indice_a_eliminar = None
    for i, info_archivo in enumerate(archivos_subidos):
        if info_archivo['filename'] == nombre_archivo:
            indice_a_eliminar = i
            break

    # Si no se encuentra el archivo, devuelve un error
    if indice_a_eliminar is None:
        return jsonify({'error': 'Archivo no encontrado'}), 404

    # Elimina el archivo físico del servidor
    ruta_archivo = archivos_subidos[indice_a_eliminar]['filepath']
    try:
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
    except Exception as e:
        return jsonify({'error': f'Error al eliminar el archivo: {str(e)}'}), 500

    # Elimina el archivo de la lista de archivos subidos
    datos_compartidos.remove_archivo_subido(nombre_archivo)

    # Devuelve una respuesta JSON confirmando la eliminación
    return jsonify({
        'success': True,
        'message': 'Archivo eliminado correctamente',
        'files': datos_compartidos.get_archivos_subidos()
    })

# Ruta para obtener la lista actual de archivos subidos
@main_bp.route("/get_archivos", methods=["GET"])
def get_archivos():
    return jsonify({'files': datos_compartidos.get_archivos_subidos()})

# Ruta para extraer datos de todos los archivos en la lista
@main_bp.route("/extraer_de_lista", methods=["POST"])
def extraer_de_lista():
    archivos_subidos = datos_compartidos.get_archivos_subidos()

    # Verifica si hay archivos en la lista para procesar
    if not archivos_subidos:
        return jsonify({'error': 'No hay archivos en la lista para procesar'}), 400

    # Limpia los datos extraídos anteriormente
    datos_compartidos.clear_datos_extraidos()

    # Procesa cada archivo en la lista de subidos
    for info_archivo in archivos_subidos:
        try:
            # Extrae datos del PDF y los agrega a la lista de datos
            datos = extraer_datos_pdf(info_archivo['filepath'])
            if datos:
                datos_compartidos.add_datos_extraidos(datos)
        except Exception as e:
            print(f"Error procesando {info_archivo['filename']}: {str(e)}")
            continue

    # Devuelve una respuesta JSON indicando que el proceso fue exitoso y la URL para redirigir
    return jsonify({
        'success': True,
        'data_count': len(datos_compartidos.get_datos_extraidos()),
        'redirect_url': url_for('main.inicio')
    })

# Ruta para refrescar los datos de la aplicación (limpiar todo)
@main_bp.route("/refrescar", methods=["GET"])
def refrescar_datos():
    # Limpia tanto la lista de archivos subidos como la de datos extraídos
    datos_compartidos.clear_archivos_subidos()
    datos_compartidos.clear_datos_extraidos()

    # Redirige a la página de inicio, que ahora estará vacía
    return redirect(url_for("main.inicio"))
