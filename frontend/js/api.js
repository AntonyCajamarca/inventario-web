/* ============================================================
   api.js — Cliente HTTP compartido para hablar con el backend
   ============================================================ */

/*const API_BASE_URL = "http://127.0.0.1:8000";*/
const API_BASE_URL = "https://frontend-nine-kappa-32.vercel.app/";

const Auth = {
  getToken() {
    return localStorage.getItem("token");
  },
  setToken(token) {
    localStorage.setItem("token", token);
  },
  getUser() {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  },
  setUser(user) {
    localStorage.setItem("user", JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  },
  isLoggedIn() {
    return Boolean(this.getToken());
  },
  isAdmin() {
    const user = this.getUser();
    return Boolean(user && user.nivel === "admin");
  },
  /**
   * Protege una pagina interna: si no hay sesion, redirige al login.
   * Se debe llamar al inicio de cada pagina dentro de /pages.
   */
  requireLogin() {
    if (!this.isLoggedIn()) {
      window.location.href = "/index.html";
    }
  },
  logout() {
    this.clear();
    window.location.href = "/index.html";
  },
};

/**
 * Llama a la API del backend.
 * @param {string} path - ej: "/api/products"
 * @param {object} options - fetch options (method, body, etc.)
 * @returns {Promise<any>} el cuerpo de la respuesta ya parseado (JSON o Blob)
 */
async function apiRequest(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const isFormData = options.body instanceof FormData;
  const redirectOn401 = options.redirectOn401 !== false; // por defecto true

  if (!isFormData && options.body) {
    headers["Content-Type"] = "application/json";
  }

  const token = Auth.getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  } catch (networkError) {
    throw new Error(
      "No se pudo conectar con el servidor. Verifica que el backend esté corriendo."
    );
  }

  if (response.status === 401 && redirectOn401) {
    Auth.clear();
    window.location.href = "/index.html";
    return null;
  }

  const contentType = response.headers.get("content-type") || "";

  // Reportes en PDF/imagen: devolvemos el blob y dejamos que el llamador lo descargue
  if (!contentType.includes("application/json")) {
    if (!response.ok) {
      throw new Error("Ocurrió un error inesperado al generar el archivo.");
    }
    return response.blob();
  }

  const data = await response.json();

  if (!response.ok) {
    const detail = data && data.detail ? data.detail : "Ocurrió un error inesperado.";
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  return data;
}

/**
 * Descarga un blob como archivo, disparando el dialogo de "guardar como" del navegador.
 */
function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

/**
 * Muestra una alerta Bootstrap dentro de un contenedor (ej: <div id="alertBox"></div>).
 */
function showAlert(containerId, message, type = "danger") {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
    </div>
  `;
}

function clearAlert(containerId) {
  const container = document.getElementById(containerId);
  if (container) container.innerHTML = "";
}
