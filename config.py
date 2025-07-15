# Importar módulo OS para trabajar con rutas y variables de entorno
import os

# Cargar las variables de entorno desde el archivo .env
from dotenv import load_dotenv
load_dotenv()

# Clase de configuración para la aplicación Flask
class Config:
    # Carpeta donde se almacenarán los archivos subidos (PDFs y Excel)
    UPLOAD_FOLDER = 'uploads'


    # Clave API para el uso del modelo Gemini AI, obtenida desde el archivo .env
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Crear la carpeta de subida si no existe, para evitar errores al guardar archivos
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
