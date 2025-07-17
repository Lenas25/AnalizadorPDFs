# Importación de librerías necesarias para la exportación y descarga de archivos
from flask import Blueprint, request, jsonify, url_for, send_from_directory, current_app
from openpyxl import Workbook                      # Para crear archivos Excel
from openpyxl.styles import PatternFill, Border, Side, Font, Alignment  # Estilos para Excel
import os
from controllers import shared_data

# Crear un blueprint específico para funcionalidades de exportación
export_bp = Blueprint('export', __name__)

# Ruta que genera un archivo Excel con los datos seleccionados por el usuario
@export_bp.route("/exportar_excel", methods=["POST"])
def exportar():
    data_extraida = shared_data.get_data_extraida()
    print(data_extraida)
    # Validar que haya datos disponibles para exportar
    if not data_extraida:
        return jsonify(error="No hay datos para exportar.")

    # Obtener la lista de columnas seleccionadas por el usuario en el formulario
    columnas_seleccionadas = request.form.getlist('columnas')

    # Crear un nuevo archivo de Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Datos extraídos"

    # Mapeo de nombres visibles a claves internas del diccionario
    mapeo_columnas = {
        "titulo": "titulo",
        "autores": "autores",
        "anio": "anio",
        "tema": "tema",
        "pais": "pais",
        "palabras": "palabras",
        "resumen": "resumen",
    }

    # Construir el encabezado del Excel con los campos seleccionados
    encabezado = [col.capitalize() for col in mapeo_columnas if col in columnas_seleccionadas]
    ws.append(encabezado)

    # Estilos para el encabezado del Excel
    estilo = {
        "relleno": PatternFill(start_color="002147", end_color="002147", fill_type="solid"),
        "fuente": Font(color="FFFFFF", bold=True),
        "borde": Border(left=Side(style='thin'), right=Side(style='thin'),
                        top=Side(style='thin'), bottom=Side(style='thin')),
        "alineacion": Alignment(horizontal="center", vertical="center")
    }

    # Aplicar los estilos al encabezado
    for col in range(1, len(encabezado) + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = estilo["relleno"]
        cell.border = estilo["borde"]
        cell.font = estilo["fuente"]
        cell.alignment = estilo["alineacion"]

    # Llenar las filas con los datos seleccionados
    for data in data_extraida:
        fila = [data.get(mapeo_columnas[col.lower()], "") for col in encabezado]
        ws.append(fila)

    # Aplicar estilos a las celdas de datos
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.border = estilo["borde"]
            cell.alignment = Alignment(horizontal="left", vertical="top")

    # Guardar el archivo Excel generado en la carpeta de subidas
    nombrearchivo = "datos.xlsx"
    ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], nombrearchivo)
    wb.save(ruta)

    # Devolver la URL para que el frontend pueda descargar el archivo
    return jsonify(url=url_for("export.descargar_excel"))

# Ruta que permite descargar el archivo Excel generado
@export_bp.route("/descargar_excel")
def descargar_excel():
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        "datos.xlsx",
        as_attachment=True  # Indica que debe descargarse, no abrirse en navegador
    )
