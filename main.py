from flask import Flask, render_template, request, redirect, url_for, send_file
import fitz
import os
import re
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Border, Side, Font

app = Flask(__name__)

# Configuración de la carpeta de subida
app.config['UPLOAD_FOLDER'] = 'uploads'

# Variables temporales para mantener datos extraídos
extracted_data = {}

# Función para extraer título, autores y año con la librería fitz


def extract_data_pdf(filepath):

    # # Buscar el AÑO
    # year = "No detectado"
    # for line in lines:
    #     match = re.search(r"\b(20[0-3][0-9])\b", line)
    #     if match:
    #         year = match.group(1)
    #         break

    doc = fitz.open(filepath)
    metadata = doc.metadata
    title = metadata.get("title", "No detectado")
    authors = metadata.get("author", "No detectado")
    year = metadata.get("creationDate", "No detectado")

    extracted_data["title"] = title
    extracted_data["authors"] = authors
    extracted_data["year"] = year

    return extracted_data

# ruta para cargar el index.html, donde esta la información de la aplicacion y el formulario para subir el archivo PDF
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('index.html')

# ruta para poder extraer los datos del PDF que estan en una tabla, se usa la libreria openpyxl
@app.route("/export")
def exportar():
    if not extracted_data:
        return redirect(url_for("data", error="No hay datos para exportar"))

    wb = Workbook()
    ws = wb.active
    headers = ["Título", "Autores", "Año"]
    ws.append(headers)

    header_fill = PatternFill(start_color="002147",
                              end_color="002147", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    thin_border = Border(left=Side(style='thin'), right=Side(
        style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = header_fill
        cell.border = thin_border
        cell.font = header_font

    ws.append([extracted_data["title"],
              extracted_data["authors"], extracted_data["year"]])
    
    for row in ws.iter_rows(min_row=2, max_row=2, min_col=1, max_col=len(headers)):
        for cell in row:
            cell.border = thin_border

    filename = "datos.xlsx"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    wb.save(filepath)
    response = send_file(filepath, as_attachment=True)
    response.headers["Refresh"] = "0; url=/"
    return response

# ruta para extraer datos del PDF subido por el usuario, aqui se recibe el archivo y se guarda en una carpeta temporal y llama a la funcion extract_data_pdf para extraer los datos
@app.route("/extract", methods=["POST", "GET"])
def extract():

    if request.method == "POST":
        file = request.files.get("pdf")
        if not file or not file.filename.endswith('.pdf'):
            return render_template("index.html", error="Por favor, sube un archivo válido en formato PDF.")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        extracted_data = extract_data_pdf(filepath)
        return render_template("data.html", data=extracted_data)
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
