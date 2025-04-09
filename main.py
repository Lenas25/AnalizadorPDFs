from flask import Flask, render_template, request, redirect, url_for, send_file
import fitz
import os
import re
from openpyxl import Workbook

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Para el avance 1 identificar el titulo, autor y año de la publicacion, fuente
# Exportar la tabla a un excel

# Variables temporales para mantener datos extraídos
extracted_data = {}

# Función para extraer título, autores y año
def extract_data_pdf(filepath):
    doc = fitz.open(filepath)
    first_page_text = doc[0].get_text()  # Solo primera página

    # Dividir por líneas, conservar estructura
    lines = [line.strip() for line in first_page_text.split('\n') if line.strip()]

    # Buscar el AÑO
    year = "No detectado"
    for line in lines:
        match = re.search(r"\b(20[0-3][0-9])\b", line)
        if match:
            year = match.group(1)
            break

    # Buscar TÍTULO
    # Se busca líneas largas con estilo título
    possible_titles = [line for line in lines if 30 < len(line) < 150 and line.isupper() == False]
    title = possible_titles[0] if possible_titles else "No detectado"

    # Buscar AUTORES
    author_pattern = re.compile(r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+ [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?: [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?")
    authors = []
    for line in lines[:10]:
        authors += author_pattern.findall(line)

    unique_authors = list(dict.fromkeys(authors))
    authors_text = ', '.join(unique_authors[:3]) if unique_authors else "No detectado"

    return {
        "Título": title,
        "Autores": authors_text,
        "Año": year
    }

@app.route("/", methods=["GET", "POST"])
def index():
    global extracted_data

    if request.method == "POST":
        if "pdf" not in request.files:
            return "No se envió ningún archivo PDF"
        file = request.files["pdf"]
        if file.filename == "":
            return "Nombre de archivo vacío"
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            extracted_data = extract_data_pdf(filepath)
            return render_template("index.html", data=extracted_data)
        
    return render_template('index.html')

@app.route("/exportar")
def exportar():
    if not extracted_data:
        return "No hay datos para exportar"

    wb = Workbook()
    ws = wb.active
    ws.append(["Título", "Autores", "Año"])
    ws.append([extracted_data["Título"], extracted_data["Autores"], extracted_data["Año"]])

    filename = "articulo_extraido.xlsx"
    wb.save(filename)

    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)