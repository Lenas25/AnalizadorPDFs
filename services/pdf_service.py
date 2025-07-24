# Importar librerías necesarias
import fitz as pymupdf     # PyMuPDF para leer y extraer contenido de archivos PDF
import os                   # Para manipulación de rutas y nombres de archivos
import re                   # Para usar expresiones regulares en la búsqueda de patrones (como el año)
from google import genai    # Cliente oficial de Google para la API de Gemini
from config import Config   # Archivo de configuración que contiene la clave de la API

# Crear una instancia del cliente de Gemini AI, usando la clave de API desde la configuración
cliente = genai.Client(api_key=Config.GEMINI_API_KEY)

# Función principal que se encarga de extraer toda la información de un archivo PDF
def extraer_datos_pdf(ruta_archivo):
    # Obtener la ruta absoluta del archivo para evitar problemas de rutas relativas
    ruta_absoluta = os.path.abspath(ruta_archivo)

    # Abrir el documento PDF utilizando PyMuPDF
    documento = pymupdf.open(ruta_absoluta)
    # Contar el número total de páginas en el documento
    contador_paginas = documento.page_count

    # Diccionario para almacenar toda la información que se extraiga del PDF
    datos = {}

    # Contar el número total de imágenes en todas las páginas del documento
    contador_imagenes = sum(len(pagina.get_images()) for pagina in documento)

    # Extraer los metadatos básicos del PDF (título, autor, etc.)
    metadatos = documento.metadata
    datos["nombre_archivo"] = os.path.basename(ruta_absoluta)
    datos["titulo"] = metadatos.get("title", "N/A")  # Obtiene el título o "N/A" si no existe
    datos["autores"] = metadatos.get("author", "N/A") # Obtiene el autor o "N/A"
    datos["palabras"] = metadatos.get("keywords", "N/A") # Obtiene las palabras clave o "N/A"
    datos["tema"] = metadatos.get("subject", "N/A") # Obtiene el tema o "N/A"
    datos["paginas_imagenes"]  = f"{contador_paginas} / {contador_imagenes}"

    # Extraer el texto completo de todas las páginas del PDF
    texto_completo = "".join([pagina.get_text() for pagina in documento])

    # Cerrar el documento para liberar los recursos y la memoria
    documento.close()

    # Limitar la longitud del texto a 10,000 caracteres para no exceder los límites de la API de Gemini
    longitud_maxima = 10000
    texto_corto = texto_completo[:longitud_maxima]

    # Intentar generar el resumen y detectar el país usando la API de Gemini
    try:
        # Petición a Gemini para generar un resumen del texto en un solo párrafo
        respuesta_resumen = cliente.models.generate_content(
            model="gemini-2.0-flash", # Modelo de IA a utilizar
            contents=f"Resume este texto en un solo párrafo en español: {texto_corto}"
        )
        datos["resumen"] = respuesta_resumen.text

        # Petición a Gemini para que determine el país de origen del texto
        respuesta_pais = cliente.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Según tu análisis, ¿de qué país es este texto? Responde solo con el nombre del país en inglés: {texto_corto}"
        )
        # Limpia espacios en blanco y asigna el país, o "N/A" si no hay respuesta
        datos["pais"] = respuesta_pais.text.strip() if respuesta_pais.text else "N/A"

    except Exception as e:
        # Si falla la comunicación con la API, se asignan valores por defecto
        datos["resumen"] = "N/A"
        datos["pais"] = "N/A"
        print(f"Error con la API de Gemini: {e}")

    # Buscar un año en formato de 4 dígitos (20xx) en el texto completo usando una expresión regular
    coincidencia_anio = re.search(r'\b(20[0-3][0-9])\b', texto_completo)
    # Si se encuentra una coincidencia, se asigna el año; de lo contrario, "N/A"
    datos["anio"] = coincidencia_anio.group(1) if coincidencia_anio else "N/A"

    # Devolver el diccionario con todos los datos extraídos del PDF
    return datos
