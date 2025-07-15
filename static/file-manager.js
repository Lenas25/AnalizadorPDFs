class FileManager {
  constructor() {
    this.uploadBtn = document.getElementById("upload-btn");
    this.fileInput = document.getElementById("file-input");
    this.filesContainer = document.getElementById("files-container");
    this.extractForm = document.getElementById("extract-form");
    this.extractBtn = document.getElementById("extract-btn");
    this.uploadStatus = document.getElementById("upload-status");
    // Check if all required elements exist
    if (
      !this.uploadBtn ||
      !this.fileInput ||
      !this.filesContainer ||
      !this.extractForm ||
      !this.extractBtn ||
      !this.uploadStatus
    ) {
      console.error("One or more required DOM elements not found");
      return;
    }

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

    if (this.extractForm) {
      this.extractForm.addEventListener("submit", (e) => {
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
    try {
      this.showExtractStatus("Extrayendo datos...", "info");
      if (this.extractBtn) {
        this.extractBtn.disabled = true;
      }

      const response = await fetch("/extract_from_list", {
        method: "POST",
      });

      const result = await response.json();

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
}

// Inicializar el gestor de archivos cuando se carga la página
document.addEventListener("DOMContentLoaded", () => {
  try {
    window.fileManager = new FileManager();
  } catch (error) {
    console.error("Error initializing FileManager:", error);
  }
});
