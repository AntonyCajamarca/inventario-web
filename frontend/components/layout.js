/* ============================================================
   components/layout.js — Sidebar + Header compartidos
   ============================================================ */

const MENU_ADMIN = [
  { key: "dashboard", label: "Panel de control", icon: "bi-house-door", href: "/pages/dashboard.html" },
  { key: "accesos", label: "Accesos", icon: "bi-people", href: "/pages/accesos.html" },
  { key: "categorias", label: "Categorías", icon: "bi-tags", href: "/pages/categorias.html" },
  { key: "productos", label: "Productos", icon: "bi-box-seam", href: "/pages/productos.html" },
  { key: "ventas", label: "Ventas", icon: "bi-cart3", href: "/pages/ventas.html" },
  { key: "reportes", label: "Reportes", icon: "bi-graph-up", href: "/pages/reportes.html" },
];

const MENU_VENDEDOR = MENU_ADMIN.filter((item) => item.key !== "accesos");

function _iniciales(nombre) {
  if (!nombre) return "?";
  const partes = nombre.trim().split(/\s+/);
  const letras = partes.slice(0, 2).map((p) => p[0].toUpperCase());
  return letras.join("");
}

function _avatarHtml(user) {
  if (user.foto) {
    return `<img src="${API_BASE_URL}${user.foto}" alt="${user.nombre}"
                 style="width:100%; height:100%; border-radius:50%; object-fit:cover;" />`;
  }
  return _iniciales(user.nombre);
}

/**
 * Renderiza el layout completo (sidebar + header) y protege la pagina.
 * @param {string} activeKey - clave del menu activo (ej: "dashboard")
 * @param {string} pageTitle - titulo mostrado en el header
 */
function renderLayout(activeKey, pageTitle) {
  Auth.requireLogin();
  const user = Auth.getUser();
  if (!user) return;

  const menu = user.nivel === "admin" ? MENU_ADMIN : MENU_VENDEDOR;

  const navHtml = menu
    .map(
      (item) => `
      <a class="nav-link ${item.key === activeKey ? "active" : ""}" href="${item.href}">
        <i class="bi ${item.icon}"></i>
        <span>${item.label}</span>
      </a>`
    )
    .join("");

  document.body.insertAdjacentHTML(
    "afterbegin",
    `
    <aside class="app-sidebar" id="appSidebar">
      <div class="brand" title="Bazar y Papelería Keylita">
        <i class="bi bi-shop"></i>
        Bazar <span>Keylita</span>
      </div>
      <nav class="nav flex-column">${navHtml}</nav>
    </aside>

    <header class="app-header">
      <div class="d-flex align-items-center gap-3">
        <button class="btn btn-sm btn-light d-md-none" id="sidebarToggle" type="button">
          <i class="bi bi-list"></i>
        </button>
        <h1 class="page-title">${pageTitle}</h1>
      </div>

      <div class="dropdown">
        <div class="user-menu" data-bs-toggle="dropdown" aria-expanded="false">
          <div class="user-avatar" id="userAvatar">${_avatarHtml(user)}</div>
          <div class="d-none d-sm-block">
            <div style="font-weight:600; font-size:0.9rem; line-height:1.1;">${user.nombre}</div>
            <div style="font-size:0.75rem; color:var(--text-muted); text-transform:capitalize;">${user.nivel}</div>
          </div>
          <i class="bi bi-caret-down-fill" style="font-size:0.7rem; color:var(--text-muted);"></i>
        </div>
        <ul class="dropdown-menu dropdown-menu-end">
          <li>
            <button class="dropdown-item" type="button" data-bs-toggle="modal" data-bs-target="#modalCambiarPassword">
              <i class="bi bi-key-fill me-2"></i>Cambiar contraseña
            </button>
          </li>
          <li>
            <button class="dropdown-item" type="button" data-bs-toggle="modal" data-bs-target="#modalFotoPerfil">
              <i class="bi bi-person-bounding-box me-2"></i>Foto de perfil
            </button>
          </li>
          <li>
            <a class="dropdown-item" href="${API_BASE_URL}/uploads/guides/guia_usuario.docx" download>
              <i class="bi bi-file-earmark-arrow-down-fill me-2"></i>Descargar guía
            </a>
          </li>
          <li><hr class="dropdown-divider" /></li>
          <li><button class="dropdown-item" id="logoutBtn" type="button"><i class="bi bi-box-arrow-right me-2"></i>Cerrar sesión</button></li>
        </ul>
      </div>
    </header>

    <!-- Modal: cambiar contraseña -->
    <div class="modal fade" id="modalCambiarPassword" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <form id="formCambiarPassword">
            <div class="modal-header">
              <h5 class="modal-title">Cambiar contraseña</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div id="passwordAlertBox"></div>
              <div class="mb-3">
                <label class="form-label">Contraseña actual</label>
                <input type="password" class="form-control" id="passwordActual" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Nueva contraseña</label>
                <input type="password" class="form-control" id="passwordNueva" required minlength="8" />
                <div class="form-text">Mínimo 8 caracteres.</div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancelar</button>
              <button type="submit" class="btn btn-primary" id="btnGuardarPassword">Guardar</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal: foto de perfil -->
    <div class="modal fade" id="modalFotoPerfil" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Foto de perfil</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body text-center">
            <div id="fotoAlertBox"></div>
            <img id="fotoPreview" src="" alt="Foto de perfil"
                 class="rounded-circle mb-3 d-none"
                 style="width:120px; height:120px; object-fit:cover;" />
            <div id="fotoPlaceholder" class="empty-state py-3">
              <i class="bi bi-person-circle fs-1 d-block mb-2"></i>
              No tienes una foto de perfil todavía.
            </div>
            <input type="file" class="form-control mb-3" id="inputFotoPerfil" accept=".jpg,.jpeg,.png,.gif" />
            <div class="d-flex gap-2 justify-content-center">
              <button type="button" class="btn btn-primary" id="btnSubirFoto">
                <i class="bi bi-upload me-1"></i>Subir
              </button>
              <button type="button" class="btn btn-outline-danger d-none" id="btnQuitarFoto">
                <i class="bi bi-trash me-1"></i>Quitar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    `
  );

  document.getElementById("logoutBtn").addEventListener("click", () => Auth.logout());

  const toggleBtn = document.getElementById("sidebarToggle");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      document.getElementById("appSidebar").classList.toggle("open");
    });
  }

  _configurarModalPassword();
  _configurarModalFoto();
}

/* ---------------------------------------------------------
   Modal: cambiar contraseña
   --------------------------------------------------------- */
function _configurarModalPassword() {
  const modalEl = document.getElementById("modalCambiarPassword");

  modalEl.addEventListener("show.bs.modal", () => {
    document.getElementById("formCambiarPassword").reset();
    clearAlert("passwordAlertBox");
  });

  document.getElementById("formCambiarPassword").addEventListener("submit", async (event) => {
    event.preventDefault();
    clearAlert("passwordAlertBox");

    const password_actual = document.getElementById("passwordActual").value;
    const password_nueva = document.getElementById("passwordNueva").value;

    const btn = document.getElementById("btnGuardarPassword");
    btn.disabled = true;

    try {
      await apiRequest("/api/auth/me/password", {
        method: "PUT",
        body: JSON.stringify({ password_actual, password_nueva }),
      });
      bootstrap.Modal.getInstance(modalEl).hide();
    } catch (error) {
      showAlert("passwordAlertBox", error.message);
    } finally {
      btn.disabled = false;
    }
  });
}

/* ---------------------------------------------------------
   Modal: foto de perfil
   --------------------------------------------------------- */
function _configurarModalFoto() {
  const modalEl = document.getElementById("modalFotoPerfil");

  modalEl.addEventListener("show.bs.modal", () => {
    clearAlert("fotoAlertBox");
    document.getElementById("inputFotoPerfil").value = "";

    const user = Auth.getUser();
    const img = document.getElementById("fotoPreview");
    const placeholder = document.getElementById("fotoPlaceholder");
    const btnQuitar = document.getElementById("btnQuitarFoto");

    if (user && user.foto) {
      img.src = `${API_BASE_URL}${user.foto}`;
      img.classList.remove("d-none");
      placeholder.classList.add("d-none");
      btnQuitar.classList.remove("d-none");
    } else {
      img.classList.add("d-none");
      placeholder.classList.remove("d-none");
      btnQuitar.classList.add("d-none");
    }
  });

  document.getElementById("btnSubirFoto").addEventListener("click", async () => {
    const input = document.getElementById("inputFotoPerfil");
    if (!input.files || input.files.length === 0) {
      showAlert("fotoAlertBox", "Selecciona una imagen primero.");
      return;
    }

    const formData = new FormData();
    formData.append("file", input.files[0]);

    const btn = document.getElementById("btnSubirFoto");
    btn.disabled = true;

    try {
      const usuarioActualizado = await apiRequest("/api/auth/me/photo", {
        method: "POST",
        body: formData,
      });
      Auth.setUser(usuarioActualizado);
      document.getElementById("userAvatar").innerHTML = _avatarHtml(usuarioActualizado);
      bootstrap.Modal.getInstance(modalEl).hide();
    } catch (error) {
      showAlert("fotoAlertBox", error.message);
    } finally {
      btn.disabled = false;
    }
  });

  document.getElementById("btnQuitarFoto").addEventListener("click", async () => {
    if (!confirm("¿Quitar tu foto de perfil?")) return;

    try {
      await apiRequest("/api/auth/me/photo", { method: "DELETE" });
      const user = Auth.getUser();
      user.foto = null;
      Auth.setUser(user);
      document.getElementById("userAvatar").innerHTML = _avatarHtml(user);
      bootstrap.Modal.getInstance(modalEl).hide();
    } catch (error) {
      showAlert("fotoAlertBox", error.message);
    }
  });
}
