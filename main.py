# Importar Flask para crear la aplicación web
from flask import Flask

# Importar configuración personalizada desde config.py
from config import Config

# Importar los blueprints que contienen las rutas (controladores) de la app
from controllers.main_controller import main_bp
from controllers.export_controller import export_bp

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Cargar la configuración desde el archivo Config
app.config.from_object(Config)

# Registrar el blueprint principal (página de inicio, búsqueda, estadísticas, etc.)
app.register_blueprint(main_bp)

# Registrar el blueprint para exportación a Excel y descarga
app.register_blueprint(export_bp)

# Punto de entrada principal de la aplicación
# Ejecuta el servidor Flask en modo de depuración (debug=True)
if __name__ == "__main__":
    app.run(debug=True)
