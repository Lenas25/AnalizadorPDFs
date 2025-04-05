from flask import Flask, render_template

app = Flask(__name__)

# Para el avance 1 identificar el titulo, autor y año de la publicacion, fuente
# Exportar la tabla a un excel

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)