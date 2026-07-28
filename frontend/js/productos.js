/* ============================================================
   productos.js — Modulo de Productos (incluye imagen / Media)
   ============================================================ */

const modalProducto = new bootstrap.Modal(document.getElementById("modalProducto"));
const modalImagen = new bootstrap.Modal(document.getElementById("modalImagen"));

let productoEditandoId = null;
let productoImagenActualId = null;
let categoriasDisponibles = [];

function formatoMoneda(valor) {
  return `$${Number(valor).toFixed(2)}`;
}

function badgeStock(producto) {
  const etiquetas = {
    agotado: { texto: "❌ Agotado", clase: "badge-stock-agotado" },
    bajo: { texto: "⚠ Bajo", clase: "badge-stock-bajo" },
    disponible: { texto: "Disponible", clase: "badge-stock-disponible" },
  };
  const info = etiquetas[producto.estado_stock] || etiquetas.disponible;
  return `<span class="badge ${info.clase}">${producto.stock} · ${info.texto}</span>`;
}

function miniaturaProducto(producto) {
  if (producto.imagen) {
    return `<img src="${API_BASE_URL}${producto.imagen}" alt="${producto.nombre}"
                 style="width:42px;height:42px;object-fit:cover;border-radius:6px;" />`;
  }
  return `<div style="width:42px;height:42px;border-radius:6px;background:var(--page-bg);
               display:flex;align-items:center;justify-content:center;color:var(--text-muted);">
            <i class="bi bi-image"></i>
          </div>`;
}

async function cargarCategoriasSelect() {
  try {
    categoriasDisponibles = await apiRequest("/api/categories");
    const select = document.getElementById("productoCategoria");
    select.innerHTML = categoriasDisponibles
      .map((c) => `<option value="${c.id}">${c.nombre}</option>`)
      .join("");
  } catch (error) {
    showAlert("alertBox", "No se pudieron cargar las categorías: " + error.message);
  }
}

async function cargarProductos(buscar = "") {
  try {
    const query = buscar ? `?buscar=${encodeURIComponent(buscar)}` : "";
    const productos = await apiRequest(`/api/products${query}`);
    if (!productos) return;

    const tabla = document.getElementById("tablaProductos");
    const vacio = document.getElementById("productosVacio");

    if (productos.length === 0) {
      tabla.innerHTML = "";
      vacio.classList.remove("d-none");
      return;
    }
    vacio.classList.add("d-none");

    tabla.innerHTML = productos
      .map(
        (p) => `
        <tr>
          <td>${miniaturaProducto(p)}</td>
          <td>${p.codigo}</td>
          <td style="font-weight:600;">${p.nombre}</td>
          <td class="text-muted">${p.categoria}</td>
          <td class="text-end">${formatoMoneda(p.precio)}</td>
          <td class="text-center">${badgeStock(p)}</td>
          <td class="text-end">
            <button class="btn btn-sm btn-light me-1" onclick='abrirImagen(${JSON.stringify({ id: p.id, nombre: p.nombre, imagen: p.imagen })})' title="Imagen">
              <i class="bi bi-image"></i>
            </button>
            <button class="btn btn-sm btn-light me-1" onclick='abrirEditarProducto(${JSON.stringify(p)})' title="Editar">
              <i class="bi bi-pencil-square"></i>
            </button>
            <button class="btn btn-sm btn-light text-danger" onclick="eliminarProducto(${p.id}, '${p.nombre.replace(/'/g, "")}')" title="Eliminar">
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

function abrirNuevoProducto() {
  productoEditandoId = null;
  document.getElementById("formProducto").reset();
  document.getElementById("productoId").value = "";
  document.getElementById("modalProductoTitulo").textContent = "Nuevo producto";
  document.getElementById("productoCodigo").disabled = false;
  clearAlert("modalProductoAlertBox");
  modalProducto.show();
}

function abrirEditarProducto(producto) {
  productoEditandoId = producto.id;
  document.getElementById("productoId").value = producto.id;
  document.getElementById("productoCodigo").value = producto.codigo;
  document.getElementById("productoNombre").value = producto.nombre;
  document.getElementById("productoDescripcion").value = producto.descripcion || "";
  document.getElementById("productoCategoria").value = producto.categoria_id;
  document.getElementById("productoPrecio").value = producto.precio;
  document.getElementById("productoStock").value = producto.stock;
  document.getElementById("modalProductoTitulo").textContent = "Editar producto";
  clearAlert("modalProductoAlertBox");
  modalProducto.show();
}

async function eliminarProducto(id, nombre) {
  if (!confirm(`¿Eliminar el producto "${nombre}"?`)) return;
  try {
    await apiRequest(`/api/products/${id}`, { method: "DELETE" });
    cargarProductos(document.getElementById("inputBuscar").value.trim());
  } catch (error) {
    showAlert("alertBox", error.message);
  }
}

document.getElementById("btnNuevoProducto").addEventListener("click", abrirNuevoProducto);

document.getElementById("formProducto").addEventListener("submit", async (event) => {
  event.preventDefault();
  clearAlert("modalProductoAlertBox");

  const payload = {
    codigo: document.getElementById("productoCodigo").value.trim(),
    nombre: document.getElementById("productoNombre").value.trim(),
    descripcion: document.getElementById("productoDescripcion").value.trim() || null,
    categoria_id: parseInt(document.getElementById("productoCategoria").value),
    precio: parseFloat(document.getElementById("productoPrecio").value),
    stock: parseInt(document.getElementById("productoStock").value),
  };

  const btn = document.getElementById("btnGuardarProducto");
  btn.disabled = true;

  try {
    if (productoEditandoId) {
      await apiRequest(`/api/products/${productoEditandoId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
    } else {
      await apiRequest("/api/products", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    }

    modalProducto.hide();
    cargarProductos(document.getElementById("inputBuscar").value.trim());
  } catch (error) {
    showAlert("modalProductoAlertBox", error.message);
  } finally {
    btn.disabled = false;
  }
});

/* ---------- Busqueda ---------- */
let temporizadorBusqueda = null;
document.getElementById("inputBuscar").addEventListener("input", (event) => {
  clearTimeout(temporizadorBusqueda);
  const texto = event.target.value.trim();
  temporizadorBusqueda = setTimeout(() => cargarProductos(texto), 350);
});

/* ---------- Imagen del producto (Media) ---------- */
function abrirImagen(producto) {
  productoImagenActualId = producto.id;
  document.getElementById("inputImagen").value = "";
  clearAlert("modalImagenAlertBox");

  const img = document.getElementById("imagenPreview");
  const placeholder = document.getElementById("imagenPlaceholder");
  const btnEliminar = document.getElementById("btnEliminarImagen");

  if (producto.imagen) {
    img.src = `${API_BASE_URL}${producto.imagen}`;
    img.classList.remove("d-none");
    placeholder.classList.add("d-none");
    btnEliminar.classList.remove("d-none");
  } else {
    img.classList.add("d-none");
    placeholder.classList.remove("d-none");
    btnEliminar.classList.add("d-none");
  }

  modalImagen.show();
}

document.getElementById("btnSubirImagen").addEventListener("click", async () => {
  const input = document.getElementById("inputImagen");
  if (!input.files || input.files.length === 0) {
    showAlert("modalImagenAlertBox", "Selecciona un archivo de imagen primero.");
    return;
  }

  const formData = new FormData();
  formData.append("file", input.files[0]);

  const btn = document.getElementById("btnSubirImagen");
  btn.disabled = true;

  try {
    await apiRequest(`/api/products/${productoImagenActualId}/media`, {
      method: "POST",
      body: formData,
    });
    modalImagen.hide();
    cargarProductos(document.getElementById("inputBuscar").value.trim());
  } catch (error) {
    showAlert("modalImagenAlertBox", error.message);
  } finally {
    btn.disabled = false;
  }
});

document.getElementById("btnEliminarImagen").addEventListener("click", async () => {
  if (!confirm("¿Quitar la imagen de este producto?")) return;
  try {
    await apiRequest(`/api/products/${productoImagenActualId}/media`, { method: "DELETE" });
    modalImagen.hide();
    cargarProductos(document.getElementById("inputBuscar").value.trim());
  } catch (error) {
    showAlert("modalImagenAlertBox", error.message);
  }
});

/* ---------- Inicio ---------- */
cargarCategoriasSelect().then(() => cargarProductos());
