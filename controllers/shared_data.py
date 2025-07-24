# Define una lista para almacenar la información de los archivos que se han subido
_archivos_subidos = []
# Define una lista para almacenar los datos que se extraen de los archivos
_datos_extraidos = []

# Función para obtener la lista de todos los archivos subidos
def get_archivos_subidos():
    return _archivos_subidos

# Función para agregar la información de un nuevo archivo a la lista
def add_archivo_subido(info_archivo):
    _archivos_subidos.append(info_archivo)

# Función para eliminar un archivo de la lista de archivos subidos por su nombre
def remove_archivo_subido(nombre_archivo):
    global _archivos_subidos
    # Filtra la lista para mantener solo los archivos cuyo nombre no coincida
    _archivos_subidos = [f for f in _archivos_subidos if f['filename'] != nombre_archivo]

# Función para limpiar completamente la lista de archivos subidos
def clear_archivos_subidos():
    _archivos_subidos.clear()

# Función para obtener la lista de todos los datos extraídos
def get_datos_extraidos():
    return _datos_extraidos

# Función para agregar un nuevo conjunto de datos a la lista de datos extraídos
def add_datos_extraidos(datos):
    _datos_extraidos.append(datos)

# Función para limpiar completamente la lista de datos extraídos
def clear_datos_extraidos():
    _datos_extraidos.clear()
