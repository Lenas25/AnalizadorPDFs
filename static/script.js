function toggleColumna(checkbox, columna) {
  const columnas = document.querySelectorAll(`[data-columna="${columna}"]`);
  columnas.forEach((col) => {
    col.style.display = checkbox.checked ? "table-cell" : "none";
  });
}

function enviarDatosExcel(event) {
  event.preventDefault();
  const checkboxes = document.querySelectorAll(
    '.options-container input[type="checkbox"]',
  );
  const columnasSeleccionadas = Array.from(checkboxes)
    .filter((checkbox) => checkbox.checked)
    .map((checkbox) => checkbox.name);

  columnasSeleccionadas.push("titulo");

  if (columnasSeleccionadas.length === 1) {
    alert("Por favor, selecciona al menos una columna para exportar.");
    return;
  }

  const form = document.createElement("form");
  form.method = "POST";
  form.action = "/exportar_excel";

  columnasSeleccionadas.forEach((columna) => {
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = "columnas";
    input.value = columna;
    form.appendChild(input);
  });

  document.body.appendChild(form);

  fetch("/exportar_excel", {
    method: "POST",
    body: new FormData(form),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        alert(data.error);
      } else if (data.url) {
        const a = document.createElement("a");
        a.href = data.url;
        a.download = "datos.xlsx";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        setTimeout(() => {
          window.location.href = "/";
        }, 500);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Ocurrió un error al intentar exportar los datos.");
    });
}

document.addEventListener("DOMContentLoaded", () => {
  const checkboxes = document.querySelectorAll(
    '.options-container input[type="checkbox"]',
  );
  checkboxes.forEach((checkbox) => {
    toggleColumna(checkbox, checkbox.name);
  });
});
