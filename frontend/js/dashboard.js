/* ============================================================
   dashboard.js — Panel de control
   ============================================================ */

function formatoMoneda(valor) {
  return `$${Number(valor).toFixed(2)}`;
}

function formatoFechaHora(isoString) {
  const fecha = new Date(isoString);
  return fecha.toLocaleString("es-EC", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function cargarDashboard() {
  try {
    const data = await apiRequest("/api/dashboard");
    if (!data) return;

    // Tarjetas
    document.getElementById("statUsuarios").textContent = data.counts.usuarios;
    document.getElementById("statCategorias").textContent = data.counts.categorias;
    document.getElementById("statProductos").textContent = data.counts.productos;
    document.getElementById("statVentas").textContent = data.counts.ventas;

    // Productos mas vendidos
    const tablaMasVendidos = document.getElementById("tablaMasVendidos");
    if (data.productos_mas_vendidos.length === 0) {
      document.getElementById("masVendidosVacio").classList.remove("d-none");
    } else {
      tablaMasVendidos.innerHTML = data.productos_mas_vendidos
        .map(
          (p) => `
          <tr>
            <td>${p.nombre}</td>
            <td class="text-end">${p.total_vendido}</td>
            <td class="text-end">${p.cantidad_total}</td>
          </tr>`
        )
        .join("");
    }

    // Ultimas ventas
    const tablaVentas = document.getElementById("tablaUltimasVentas");
    if (data.ultimas_ventas.length === 0) {
      document.getElementById("ventasVacio").classList.remove("d-none");
    } else {
      tablaVentas.innerHTML = data.ultimas_ventas
        .map(
          (v) => `
          <tr>
            <td>${v.id}</td>
            <td>${v.vendedor}</td>
            <td>${formatoFechaHora(v.fecha)}</td>
            <td class="text-end">${formatoMoneda(v.total)}</td>
          </tr>`
        )
        .join("");
    }

    // Productos recientes
    const listaRecientes = document.getElementById("listaRecientes");
    if (data.productos_recientes.length === 0) {
      document.getElementById("recientesVacio").classList.remove("d-none");
    } else {
      listaRecientes.innerHTML = data.productos_recientes
        .map(
          (p) => `
          <div class="d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-2">
              <div class="rounded-circle d-flex align-items-center justify-content-center"
                   style="width:42px; height:42px; background:var(--page-bg); color:var(--accent);">
                <i class="bi bi-box-seam"></i>
              </div>
              <div>
                <div style="font-weight:600; font-size:0.9rem;">${p.nombre}</div>
                <div style="font-size:0.78rem; color:var(--text-muted);">${p.categoria}</div>
              </div>
            </div>
            <span class="badge rounded-pill" style="background:var(--card-yellow); color:#3a2c05;">
              ${formatoMoneda(p.precio)}
            </span>
          </div>`
        )
        .join("");
    }
  } catch (error) {
    showAlert("alertBox", error.message);
  }
}

cargarDashboard();
