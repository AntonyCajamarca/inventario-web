/* ============================================================
   categorias.js — Modulo de Categorias
   ============================================================ */

let categoriaEditandoId = null;

async function cargarCategorias() {
  try {
    const categorias = await apiRequest("/api/categories");
    if (!categorias) return;

    const tabla = document.getElementById("tablaCategorias");
    const vacio = document.getElementById("categoriasVacio");

    if (categorias.length === 0) {
      tabla.innerHTML = "";
      vacio.classList.remove("d-none");
      return;
    }
    vacio.classList.add("d-none");

    tabla.innerHTML = categorias
      .map(
        (c) => `
        <tr>
          <td style="font-weight:600;">${c.nombre}</td>
          <td class="text-muted">${c.descripcion ? c.descripcion : "—"}</td>
          <td class="text-center">
            <span class="badge rounded-pill" style="background:var(--accent);">${c.total_productos}</span>
          </td>
          <td class="text-end">
            <button class="btn btn-sm btn-light me-1" onclick='editarCategoria(${JSON.stringify(c)})' title="Editar">
              <i class="bi bi-pencil-square"></i>
            </button>
            <button class="btn btn-sm btn-light text-danger" onclick="eliminarCategoria(${c.id}, '${c.nombre.replace(/'/g, "")}')" title="Eliminar">
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

function editarCategoria(categoria) {
  categoriaEditandoId = categoria.id;
  document.getElementById("categoriaId").value = categoria.id;
  document.getElementById("categoriaNombre").value = categoria.nombre;
  document.getElementById("categoriaDescripcion").value = categoria.descripcion || "";
  document.getElementById("formTitulo").innerHTML = '<i class="bi bi-pencil-fill me-1"></i>Editar categoría';
  document.getElementById("btnGuardarCategoria").innerHTML = '<i class="bi bi-check-lg me-1"></i>Actualizar';
  document.getElementById("btnCancelarEdicion").classList.remove("d-none");
  clearAlert("formAlertBox");
  document.getElementById("categoriaNombre").focus();
}

function cancelarEdicion() {
  categoriaEditandoId = null;
  document.getElementById("formCategoria").reset();
  document.getElementById("categoriaId").value = "";
  document.getElementById("formTitulo").innerHTML = '<i class="bi bi-tag-fill me-1"></i>Nueva categoría';
  document.getElementById("btnGuardarCategoria").innerHTML = '<i class="bi bi-check-lg me-1"></i>Guardar';
  document.getElementById("btnCancelarEdicion").classList.add("d-none");
  clearAlert("formAlertBox");
}

async function eliminarCategoria(id, nombre) {
  if (!confirm(`¿Eliminar la categoría "${nombre}"?`)) return;
  try {
    await apiRequest(`/api/categories/${id}`, { method: "DELETE" });
    cargarCategorias();
  } catch (error) {
    showAlert("alertBox", error.message);
  }
}

document.getElementById("btnCancelarEdicion").addEventListener("click", cancelarEdicion);

document.getElementById("formCategoria").addEventListener("submit", async (event) => {
  event.preventDefault();
  clearAlert("formAlertBox");

  const nombre = document.getElementById("categoriaNombre").value.trim();
  const descripcion = document.getElementById("categoriaDescripcion").value.trim() || null;

  const btn = document.getElementById("btnGuardarCategoria");
  btn.disabled = true;

  try {
    if (categoriaEditandoId) {
      await apiRequest(`/api/categories/${categoriaEditandoId}`, {
        method: "PUT",
        body: JSON.stringify({ nombre, descripcion }),
      });
    } else {
      await apiRequest("/api/categories", {
        method: "POST",
        body: JSON.stringify({ nombre, descripcion }),
      });
    }

    cancelarEdicion();
    cargarCategorias();
  } catch (error) {
    showAlert("formAlertBox", error.message);
  } finally {
    btn.disabled = false;
  }
});

cargarCategorias();
