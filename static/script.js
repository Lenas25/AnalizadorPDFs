// Función para mostrar u ocultar una columna de la tabla de resultados.
function alternarColumna(casilla, nombreColumna) {
  // Selecciona todas las celdas (th y td) que pertenecen a una columna específica.
  const columnas = document.querySelectorAll(
    `[data-columna="${nombreColumna}"]`,
  );
  // Recorre cada celda y cambia su estilo 'display' según si la casilla está marcada o no.
  columnas.forEach((col) => {
    col.style.display = casilla.checked ? "table-cell" : "none";
  });
}

// Función para enviar los datos seleccionados al backend para generar un archivo Excel.
function enviarDatosExcel(evento) {
  evento.preventDefault(); // Evita que el enlace recargue la página.

  // Selecciona todas las casillas de verificación de las columnas.
  const casillas = document.querySelectorAll(
    '.options-container input[type="checkbox"]',
  );

  // Filtra solo las casillas que están marcadas y obtiene sus nombres (que corresponden a las columnas).
  const columnasSeleccionadas = Array.from(casillas)
    .filter((casilla) => casilla.checked)
    .map((casilla) => casilla.name);

  // La columna 'titulo' siempre se incluye, ya que es la principal.
  columnasSeleccionadas.push("titulo");

  // Valida que el usuario haya seleccionado al menos una columna adicional.
  if (columnasSeleccionadas.length === 1) {
    alert("Por favor, selecciona al menos una columna para exportar.");
    return;
  }

  // Crea un formulario oculto en la memoria para enviar los datos.
  const formulario = document.createElement("form");
  formulario.method = "POST";
  formulario.action = "/exportar_excel"; // Apunta al endpoint de exportación en Flask.

  // Agrega cada columna seleccionada como un campo oculto en el formulario.
  columnasSeleccionadas.forEach((columna) => {
    const entrada = document.createElement("input");
    entrada.type = "hidden";
    entrada.name = "columnas";
    entrada.value = columna;
    formulario.appendChild(entrada);
  });

  // Envía la petición fetch al servidor con los datos del formulario.
  fetch("/exportar_excel", {
    method: "POST",
    body: new FormData(formulario),
  })
    .then((respuesta) => respuesta.json())
    .then((datos) => {
      // Si el servidor devuelve un error, lo muestra en una alerta.
      if (datos.error) {
        alert(datos.error);
      } else if (datos.url) {
        // Si el servidor devuelve una URL de descarga, crea un enlace temporal para iniciarla.
        const enlace = document.createElement("a");
        enlace.href = datos.url;
        enlace.download = "datos.xlsx"; // Nombre del archivo que se descargará.
        document.body.appendChild(enlace);
        enlace.click(); // Simula un clic en el enlace para abrir el diálogo de descarga.
        document.body.removeChild(enlace); // Elimina el enlace temporal.
      }
    })
    .catch((error) => {
      console.error("Error al exportar:", error);
      alert("Ocurrió un error al intentar exportar los datos.");
    });
}

// Se ejecuta cuando el contenido del DOM se ha cargado completamente.
document.addEventListener("DOMContentLoaded", () => {
  // Selecciona todas las casillas de verificación.
  const casillas = document.querySelectorAll(
    '.options-container input[type="checkbox"]',
  );
  // Itera sobre ellas para asegurarse de que el estado inicial de visibilidad de las columnas coincida con el estado de las casillas.
  casillas.forEach((casilla) => {
    alternarColumna(casilla, casilla.name);
  });
});
