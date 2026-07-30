/* ============================================================
   ventas.js — Registrar venta (carrito) + Historial
   ============================================================ */

const modalDetalleVenta = new bootstrap.Modal(document.getElementById("modalDetalleVenta"));

let productosDisponibles = [];
let carrito = []; // [{producto_id, nombre, precio, cantidad, stockDisponible}]

function formatoMoneda(valor) {
  return `$${Number(valor).toFixed(2)}`;
}

function formatoFechaHora(isoString) {
  return new Date(isoString).toLocaleString("es-EC", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/* ---------- Cargar productos para el selector ---------- */
async function cargarProductosSelector() {
  try {
    productosDisponibles = await apiRequest("/api/products");
    const select = document.getElementById("selectProducto");
    select.innerHTML = productosDisponibles
      .map(
        (p) =>
          `<option value="${p.id}" ${p.stock <= 0 ? "disabled" : ""}>
            ${p.nombre} (${p.codigo})${p.stock <= 0 ? " — agotado" : ""}
          </option>`
      )
      .join("");
    mostrarStockDisponible();
  } catch (error) {
    showAlert("alertBox", "No se pudieron cargar los productos: " + error.message);
  }
}

function mostrarStockDisponible() {
  const id = parseInt(document.getElementById("selectProducto").value);
  const producto = productosDisponibles.find((p) => p.id === id);
  const info = document.getElementById("stockDisponibleInfo");
  if (producto) {
    info.textContent = `Stock disponible: ${producto.stock} — Precio: ${formatoMoneda(producto.precio)}`;
  } else {
    info.textContent = "";
  }
}

document.getElementById("selectProducto").addEventListener("change", mostrarStockDisponible);

/* ---------- Carrito ---------- */
function renderCarrito() {
  const tabla = document.getElementById("tablaCarrito");
  const vacio = document.getElementById("carritoVacio");
  const btnRegistrar = document.getElementById("btnRegistrarVenta");

  if (carrito.length === 0) {
    tabla.innerHTML = "";
    vacio.classList.remove("d-none");
    btnRegistrar.disabled = true;
  } else {
    vacio.classList.add("d-none");
    btnRegistrar.disabled = false;
    tabla.innerHTML = carrito
      .map(
        (item, index) => `
        <tr>
          <td>${item.nombre}</td>
          <td class="text-end">${formatoMoneda(item.precio)}</td>
          <td class="text-center">
            <input type="number" min="1" step="1" value="${item.cantidad}"
                   class="form-control form-control-sm text-center"
                   style="width:80px; display:inline-block;"
                   onchange="actualizarCantidad(${index}, this.value)" />
          </td>
          <td class="text-end">${formatoMoneda(item.precio * item.cantidad)}</td>
          <td class="text-end">
            <button class="btn btn-sm btn-light text-danger" onclick="quitarDelCarrito(${index})" title="Quitar">
              <i class="bi bi-x-lg"></i>
            </button>
          </td>
        </tr>`
      )
      .join("");
  }

  const total = carrito.reduce((acc, item) => acc + item.precio * item.cantidad, 0);
  document.getElementById("carritoTotal").textContent = formatoMoneda(total);
}

function actualizarCantidad(index, valor) {
  const cantidad = parseInt(valor);
  if (!cantidad || cantidad < 1) {
    renderCarrito();
    return;
  }
  carrito[index].cantidad = cantidad;
  renderCarrito();
}

function quitarDelCarrito(index) {
  carrito.splice(index, 1);
  renderCarrito();
}

document.getElementById("btnAgregarCarrito").addEventListener("click", () => {
  const id = parseInt(document.getElementById("selectProducto").value);
  const cantidad = parseInt(document.getElementById("inputCantidad").value) || 1;
  const producto = productosDisponibles.find((p) => p.id === id);

  if (!producto) return;
  if (cantidad < 1) return;

  const existente = carrito.find((item) => item.producto_id === id);
  if (existente) {
    existente.cantidad += cantidad;
  } else {
    carrito.push({
      producto_id: id,
      nombre: producto.nombre,
      precio: parseFloat(producto.precio),
      cantidad,
    });
  }

  document.getElementById("inputCantidad").value = 1;
  renderCarrito();
});

document.getElementById("btnRegistrarVenta").addEventListener("click", async () => {
  clearAlert("alertBox");
  const btn = document.getElementById("btnRegistrarVenta");
  btn.disabled = true;

  try {
    const payload = {
      items: carrito.map((item) => ({ producto_id: item.producto_id, cantidad: item.cantidad })),
    };
    const venta = await apiRequest("/api/sales", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    showAlert(
      "alertBox",
      `<i class="bi bi-check-circle-fill me-1"></i>Venta #${venta.id} registrada por ${formatoMoneda(venta.total)}.`,
      "success"
    );

    carrito = [];
    renderCarrito();
    await cargarProductosSelector(); // refresca stock disponible
    cargarHistorial();
  } catch (error) {
    showAlert("alertBox", error.message);
    btn.disabled = false;
  }
});

/* ---------- Historial ---------- */
async function cargarHistorial() {
  try {
    const params = new URLSearchParams();
    const fecha = document.getElementById("filtroFecha").value;
    const producto = document.getElementById("filtroProducto").value.trim();
    const numero = document.getElementById("filtroNumero").value;

    if (fecha) params.append("fecha", fecha);
    if (producto) params.append("producto", producto);
    if (numero) params.append("numero_venta", numero);

    const query = params.toString() ? `?${params.toString()}` : "";
    const ventas = await apiRequest(`/api/sales${query}`);
    if (!ventas) return;

    const tabla = document.getElementById("tablaHistorial");
    const vacio = document.getElementById("historialVacio");

    if (ventas.length === 0) {
      tabla.innerHTML = "";
      vacio.classList.remove("d-none");
      return;
    }
    vacio.classList.add("d-none");

    tabla.innerHTML = ventas
      .map(
        (v) => `
        <tr onclick="verDetalleVenta(${v.id})">
          <td>#${v.id}</td>
          <td>${formatoFechaHora(v.fecha)}</td>
          <td>${v.vendedor}</td>
          <td class="text-muted">${v.productos}</td>
          <td class="text-end">${formatoMoneda(v.total)}</td>
          <td class="text-end"><i class="bi bi-eye"></i></td>
        </tr>`
      )
      .join("");
  } catch (error) {
    showAlert("alertBox", error.message);
  }
}

async function verDetalleVenta(id) {
  try {
    const venta = await apiRequest(`/api/sales/${id}`);
    if (!venta) return;

    document.getElementById("detalleVentaTitulo").textContent = `Venta #${venta.id}`;
    document.getElementById("detalleVentaMeta").textContent =
      `${formatoFechaHora(venta.fecha)} — Vendedor: ${venta.vendedor}`;
    document.getElementById("detalleVentaTotal").textContent = formatoMoneda(venta.total);

    document.getElementById("tablaDetalleVenta").innerHTML = venta.detalles
      .map(
        (d) => `
        <tr>
          <td>${d.producto}</td>
          <td class="text-center">${d.cantidad}</td>
          <td class="text-end">${formatoMoneda(d.precio_unitario)}</td>
          <td class="text-end">${formatoMoneda(d.subtotal)}</td>
        </tr>`
      )
      .join("");

    modalDetalleVenta.show();
  } catch (error) {
    showAlert("alertBox", error.message);
  }
}

document.getElementById("btnFiltrar").addEventListener("click", cargarHistorial);
document.getElementById("btnLimpiarFiltros").addEventListener("click", () => {
  document.getElementById("filtroFecha").value = "";
  document.getElementById("filtroProducto").value = "";
  document.getElementById("filtroNumero").value = "";
  cargarHistorial();
});

/* ---------- Inicio ---------- */
cargarProductosSelector();
cargarHistorial();
