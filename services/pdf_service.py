# Importar librerías necesarias
import fitz as pymupdf     # PyMuPDF para leer PDFs
import os                       # Para manipulación de archivos y rutas
import re                       # Para expresiones regulares (detección de año)
from google import genai        # Cliente de Gemini AI
from config import Config       # Configuración de la app (clave API y carpeta)

# Crear instancia del cliente de Gemini AI con la clave cargada desde el archivo .env
cliente = genai.Client(api_key=Config.GEMINI_API_KEY)

# Función principal para extraer datos de un archivo PDF
def extraer_data_pdf(urlarchivo):
    # Obtener la ruta absoluta del archivo
    urlarchivo = os.path.abspath(urlarchivo)

    # Abrir el PDF usando PyMuPDF
    doc = pymupdf.open(urlarchivo)
    paginas_count  = doc.page_count

    # Diccionario donde se almacenará la información extraída
    data = {}

    imagenes_count = sum(len(page.get_images()) for page in doc)
    # Extraer metadatos del documento
    metadata = doc.metadata
    data["nombre_archivo"] = os.path.basename(urlarchivo)
    data["titulo"] = metadata.get("title", "N/A")
    data["autores"] = metadata.get("author", "N/A")
    data["palabras"] = metadata.get("keywords", "N/A")
    data["tema"] = metadata.get("subject", "N/A")
    data["paginas_imagenes"]  = f"{paginas_count} / {imagenes_count}"

    # Obtener el texto completo de todas las páginas del PDF
    texto = "".join([page.get_text() for page in doc])

    # Cerrar el documento para liberar memoria
    doc.close()

    # Limitar el texto a 10,000 caracteres para evitar errores con la API
    max_len = 10000
    texto_corto = texto[:max_len]

    # Intentar generar resumen y país utilizando la API de Gemini
    try:
        # Generar resumen del contenido en un solo párrafo
        resumen = cliente.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Resumen este texto en un solo párrafo en español: {texto_corto}"
        )
        data["resumen"] = resumen.text

        # Detectar el país del contenido del texto
        pais = cliente.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"¿De qué país es este texto? Solo dime el país en inglés: {texto}"
        )
        data["pais"] = pais.text.strip() if pais.text == "" else "N/A"

    except Exception as e:
        # Si ocurre un error con la API, registrar el mensaje de error en el campo resumen
        data["resumen"] = "N/A"
        data["pais"] = "N/A"

    # Buscar un año en formato 20XX en el texto completo (usando regex)
    anio = re.search(r'\b(20[0-3][0-9])\b', texto)
    data["anio"] = anio.group(1) if anio else "N/A"

    # Retornar el diccionario con todos los datos extraídos
    return data
