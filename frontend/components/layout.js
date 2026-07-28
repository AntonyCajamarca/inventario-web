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
          <div class="user-avatar">${_iniciales(user.nombre)}</div>
          <div class="d-none d-sm-block">
            <div style="font-weight:600; font-size:0.9rem; line-height:1.1;">${user.nombre}</div>
            <div style="font-size:0.75rem; color:var(--text-muted); text-transform:capitalize;">${user.nivel}</div>
          </div>
          <i class="bi bi-caret-down-fill" style="font-size:0.7rem; color:var(--text-muted);"></i>
        </div>
        <ul class="dropdown-menu dropdown-menu-end">
          <li><button class="dropdown-item" id="logoutBtn" type="button"><i class="bi bi-box-arrow-right me-2"></i>Cerrar sesión</button></li>
        </ul>
      </div>
    </header>
    `
  );

  document.getElementById("logoutBtn").addEventListener("click", () => Auth.logout());

  const toggleBtn = document.getElementById("sidebarToggle");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      document.getElementById("appSidebar").classList.toggle("open");
    });
  }
}
