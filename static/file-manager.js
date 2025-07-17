class FileManager {
  constructor() {
    console.log("Inicializando FileManager...");

    // Obtener elementos del DOM
    this.uploadBtn = document.getElementById("upload-btn");
    this.fileInput = document.getElementById("file-input");
    this.filesContainer = document.getElementById("files-container");
    this.extractForm = document.getElementById("extract-form");
    this.extractBtn = document.getElementById("extract-btn");
    this.uploadStatus = document.getElementById("upload-status");

    console.log("Elementos encontrados:", {
      uploadBtn: !!this.uploadBtn,
      fileInput: !!this.fileInput,
      filesContainer: !!this.filesContainer,
      extractForm: !!this.extractForm,
      extractBtn: !!this.extractBtn,
      uploadStatus: !!this.uploadStatus,
    });

    // Inicializar eventos y cargar archivos
    this.initEventListeners();
    this.loadFiles();
  }

  initEventListeners() {
    // Check if elements exist before adding event listeners
    if (this.uploadBtn) {
      this.uploadBtn.addEventListener("click", () => {
        if (this.fileInput) {
          this.fileInput.click();
        }
      });
    }

    if (this.fileInput) {
      this.fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
          this.uploadFile(e.target.files[0]);
        }
      });
    }

    // Event listener para el formulario de extracción
    if (this.extractForm) {
      console.log("Agregando event listener al formulario de extracción");
      this.extractForm.addEventListener("submit", (e) => {
        console.log("Evento submit del formulario capturado");
        e.preventDefault();
        this.extractData();
      });
    } else {
      console.error("No se encontró el formulario de extracción");
    }

    // Event listener adicional para el botón directamente (como respaldo)
    if (this.extractBtn) {
      console.log("Agregando event listener directo al botón de extracción");
      this.extractBtn.addEventListener("click", (e) => {
        console.log("Click directo en el botón de extracción");
        e.preventDefault();
        this.extractData();
      });
    }
  }

  async uploadFile(file) {
    const formData = new FormData();
    formData.append("pdf", file);

    try {
      this.showUploadStatus("Subiendo archivo...", "info");

      const response = await fetch("/upload_file", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        this.showUploadStatus("Archivo subido correctamente", "success");
        this.renderFiles(result.files);
        this.fileInput.value = ""; // Limpiar el input
      } else {
        this.showUploadStatus(
          result.error || "Error al subir el archivo",
          "error",
        );
      }
    } catch (error) {
      this.showUploadStatus("Error de conexión", "error");
      console.error("Error:", error);
    }
  }

  async deleteFile(filename) {
    try {
      const response = await fetch(
        `/delete_file/${encodeURIComponent(filename)}`,
        {
          method: "DELETE",
        },
      );

      const result = await response.json();

      if (response.ok) {
        this.showUploadStatus("Archivo eliminado correctamente", "success");
        this.renderFiles(result.files);
      } else {
        this.showUploadStatus(
          result.error || "Error al eliminar el archivo",
          "error",
        );
      }
    } catch (error) {
      this.showUploadStatus("Error de conexión", "error");
      console.error("Error:", error);
    }
  }

  async loadFiles() {
    try {
      const response = await fetch("/get_files");
      const result = await response.json();

      if (response.ok) {
        this.renderFiles(result.files);
      }
    } catch (error) {
      console.error("Error cargando archivos:", error);
    }
  }

  renderFiles(files) {
    if (!this.filesContainer) {
      console.error("Files container not found");
      return;
    }

    if (!files || files.length === 0) {
      this.filesContainer.innerHTML =
        '<li class="no-files">No hay archivos subidos</li>';
      if (this.extractBtn) {
        this.extractBtn.disabled = true;
      }
      return;
    }

    if (this.extractBtn) {
      this.extractBtn.disabled = false;
    }

    const filesHTML = files
      .map(
        (file) => `
            <li class="file-item">
                <div class="file-info">
                    <span class="file-icon">📄</span>
                    <span class="file-name">${file.filename}</span>
                </div>
                <button
                    class="delete-btn"
                    onclick="fileManager.deleteFile('${file.filename}')"
                    title="Eliminar archivo"
                >
                    🗑️
                </button>
            </li>
        `,
      )
      .join("");

    this.filesContainer.innerHTML = filesHTML;
  }

  async extractData() {
    console.log("Ejecutando extractData()...");
    try {
      this.showExtractStatus("Extrayendo datos...", "info");
      if (this.extractBtn) {
        this.extractBtn.disabled = true;
      }

      console.log("Enviando petición a /extract_from_list");
      const response = await fetch("/extract_from_list", {
        method: "POST",
      });

      const result = await response.json();
      console.log("Respuesta recibida:", result);

      if (response.ok) {
        this.showExtractStatus("Datos extraídos correctamente", "success");
        // Recargar la página para mostrar los resultados
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      } else {
        this.showExtractStatus(
          result.error || "Error al extraer datos",
          "error",
        );
        if (this.extractBtn) {
          this.extractBtn.disabled = false;
        }
      }
    } catch (error) {
      this.showExtractStatus("Error de conexión", "error");
      if (this.extractBtn) {
        this.extractBtn.disabled = false;
      }
      console.error("Error:", error);
    }
  }

  showUploadStatus(message, type) {
    if (this.uploadStatus) {
      this.uploadStatus.textContent = message;
      this.uploadStatus.className = `status-message ${type}`;

      // Limpiar el mensaje después de 3 segundos
      setTimeout(() => {
        if (this.uploadStatus) {
          this.uploadStatus.textContent = "";
          this.uploadStatus.className = "";
        }
      }, 3000);
    }
  }

  showExtractStatus(message, type) {
    if (this.uploadStatus) {
      this.uploadStatus.textContent = message;
      this.uploadStatus.className = `status-message ${type}`;

      // Limpiar el mensaje después de 3 segundos
      setTimeout(() => {
        if (this.uploadStatus) {
          this.uploadStatus.textContent = "";
          this.uploadStatus.className = "";
        }
      }, 3000);
    }
  }
}

// Función global simple para manejar la extracción
async function handleExtraction(event) {
  event.preventDefault();
  console.log("Función de extracción ejecutada");

  const extractBtn = document.getElementById("extract-btn");
  const uploadStatus = document.getElementById("upload-status");

  try {
    // Mostrar estado de extracción
    if (uploadStatus) {
      uploadStatus.textContent = "Extrayendo datos...";
      uploadStatus.className = "status-message info";
    }

    if (extractBtn) {
      extractBtn.disabled = true;
    }

    console.log("Enviando petición a /extract_from_list");
    const response = await fetch("/extract_from_list", {
      method: "POST",
    });

    const result = await response.json();
    console.log(result);
    console.log("Respuesta recibida:", result);

    if (response.ok && result.success) {
      // Mostrar mensaje de éxito
      if (uploadStatus) {
        uploadStatus.textContent = `Datos extraídos correctamente (${result.data_count} archivos procesados)`;
        uploadStatus.className = "status-message success";
      }

      // Redireccionar después de un breve delay
      setTimeout(() => {
        if (result.redirect_url) {
          window.location.href = "/";
        } else {
          window.location.reload();
        }
      }, 1500);
    } else {
      // Manejar errores del servidor
      if (uploadStatus) {
        uploadStatus.textContent = result.error || "Error al extraer datos";
        uploadStatus.className = "status-message error";
      }
      if (extractBtn) {
        extractBtn.disabled = false;
      }
    }
  } catch (error) {
    if (uploadStatus) {
      uploadStatus.textContent = "Error de conexión";
      uploadStatus.className = "status-message error";
    }
    if (extractBtn) {
      extractBtn.disabled = false;
    }
    console.error("Error:", error);
  }
}

// Inicializar el gestor de archivos cuando se carga la página
document.addEventListener("DOMContentLoaded", () => {
  try {
    window.fileManager = new FileManager();

    // Agregar event listener al formulario de extracción
    const extractForm = document.getElementById("extract-form");
    if (extractForm) {
      console.log("Agregando event listener al formulario");
      extractForm.addEventListener("submit", (e) => {
        console.log("Evento submit capturado");
        e.preventDefault();
        handleExtraction();
      });
    } else {
      console.error("No se encontró el formulario de extracción");
    }
  } catch (error) {
    console.error("Error initializing FileManager:", error);
  }
});
