_uploaded_files = []
_data_extraida = []

def get_uploaded_files():
    return _uploaded_files

def add_uploaded_file(file_info):
    _uploaded_files.append(file_info)

def remove_uploaded_file(filename):
    global _uploaded_files
    _uploaded_files = [f for f in _uploaded_files if f['filename'] != filename]

def clear_uploaded_files():
    _uploaded_files.clear()

def get_data_extraida():
    return _data_extraida

def add_data_extraida(data):
    _data_extraida.append(data)

def clear_data_extraida():
    _data_extraida.clear()