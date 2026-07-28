/* ============================================================
   accesos.js — Administrar usuarios (solo admin)
   ============================================================ */

const modalUsuario = new bootstrap.Modal(document.getElementById("modalUsuario"));
let modoEdicion = false;

function formatoFecha(isoString) {
  if (!isoString) return "Nunca";
  return new Date(isoString).toLocaleString("es-EC", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function badgeNivel(nivel) {
  const color = nivel === "admin" ? "var(--accent)" : "var(--card-blue)";
  return `<span class="badge rounded-pill" style="background:${color};">${nivel}</span>`;
}

function badgeEstado(estado) {
  const color = estado === "activo" ? "var(--success)" : "var(--danger)";
  return `<span class="badge rounded-pill" style="background:${color};">${estado}</span>`;
}

async function cargarUsuarios() {
  try {
    const usuarios = await apiRequest("/api/users");
    if (!usuarios) return;

    const tabla = document.getElementById("tablaUsuarios");
    const vacio = document.getElementById("usuariosVacio");

    if (usuarios.length === 0) {
      tabla.innerHTML = "";
      vacio.classList.remove("d-none");
      return;
    }
    vacio.classList.add("d-none");

    tabla.innerHTML = usuarios
      .map(
        (u) => `
        <tr>
          <td>${u.nombre}</td>
          <td>${u.email}</td>
          <td>${badgeNivel(u.nivel)}</td>
          <td>${badgeEstado(u.estado)}</td>
          <td>${formatoFecha(u.ultimo_login)}</td>
          <td class="text-end">
            <button class="btn btn-sm btn-light me-1" onclick='abrirEditar(${JSON.stringify(u)})' title="Editar">
              <i class="bi bi-pencil-square"></i>
            </button>
            <button class="btn btn-sm btn-light text-danger" onclick="eliminarUsuario(${u.id}, '${u.nombre.replace(/'/g, "")}')" title="Eliminar">
              <i class="bi bi-trash"></i>
            </button>
          </td>
        </tr>`
      )
      .join("");
  } catch (error) {
    showAlert("alertBox", error.message);
  }
}

function abrirNuevo() {
  modoEdicion = false;
  document.getElementById("formUsuario").reset();
  document.getElementById("usuarioId").value = "";
  document.getElementById("modalUsuarioTitulo").textContent = "Nuevo usuario";
  document.getElementById("usuarioEmail").disabled = false;
  document.getElementById("usuarioPassword").required = true;
  document.getElementById("passwordHint").textContent = "Mínimo 8 caracteres.";
  document.getElementById("campoEstado").classList.add("d-none");
  clearAlert("modalAlertBox");
  modalUsuario.show();
}

function abrirEditar(usuario) {
  modoEdicion = true;
  document.getElementById("formUsuario").reset();
  document.getElementById("modalUsuarioTitulo").textContent = "Editar usuario";
  document.getElementById("usuarioId").value = usuario.id;
  document.getElementById("usuarioNombre").value = usuario.nombre;
  document.getElementById("usuarioEmail").value = usuario.email;
  document.getElementById("usuarioEmail").disabled = true;
  document.getElementById("usuarioNivel").value = usuario.nivel;
  document.getElementById("usuarioEstado").value = usuario.estado;
  document.getElementById("usuarioPassword").required = false;
  document.getElementById("passwordHint").textContent = "Deja este campo en blanco para no cambiar la contraseña.";
  document.getElementById("campoEstado").classList.remove("d-none");
  clearAlert("modalAlertBox");
  modalUsuario.show();
}

async function eliminarUsuario(id, nombre) {
  if (!confirm(`¿Eliminar al usuario "${nombre}"? Esta acción no se puede deshacer.`)) {
    return;
  }
  try {
    await apiRequest(`/api/users/${id}`, { method: "DELETE" });
    cargarUsuarios();
  } catch (error) {
    showAlert("alertBox", error.message);
  }
}

document.getElementById("btnNuevoUsuario").addEventListener("click", abrirNuevo);

document.getElementById("formUsuario").addEventListener("submit", async (event) => {
  event.preventDefault();
  clearAlert("modalAlertBox");

  const id = document.getElementById("usuarioId").value;
  const nombre = document.getElementById("usuarioNombre").value.trim();
  const email = document.getElementById("usuarioEmail").value.trim();
  const password = document.getElementById("usuarioPassword").value;
  const nivel = document.getElementById("usuarioNivel").value;
  const estado = document.getElementById("usuarioEstado").value;

  const btn = document.getElementById("btnGuardarUsuario");
  btn.disabled = true;

  try {
    if (modoEdicion) {
      const payload = { nombre, nivel, estado };
      if (password) payload.password = password;
      await apiRequest(`/api/users/${id}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
    } else {
      await apiRequest("/api/users", {
        method: "POST",
        body: JSON.stringify({ nombre, email, password, nivel }),
      });
    }

    modalUsuario.hide();
    cargarUsuarios();
  } catch (error) {
    showAlert("modalAlertBox", error.message);
  } finally {
    btn.disabled = false;
  }
});

cargarUsuarios();
