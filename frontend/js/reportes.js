/* ============================================================
   reportes.js — Generación y descarga de reportes
   ============================================================ */

let tipoActual = "ventas-dia";

function formatoMoneda(valor) {
  return `$${Number(valor).toFixed(2)}`;
}

function formatoHora(iso) {
  const fecha = new Date(iso);
  return fecha.toLocaleTimeString("es-EC", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function formatoFechaHora(iso) {
  const fecha = new Date(iso);
  return fecha.toLocaleString("es-EC", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const REPORTES = {
  "ventas-dia": {
    endpoint: "/api/reports/ventas-dia",
    params() {
      const fecha = document.getElementById("rvFecha").value;
      if (!fecha) {
        showAlert("reporteAlertBox", "Selecciona una fecha.");
        return null;
      }
      return { query: { fecha }, filenameBase: `ventas_dia_${fecha}` };
    },
    headers: ["N° venta", "Hora", "Vendedor", "Productos", "Total"],
    titulo: (d) => `Reporte de ventas del día ${d.fecha}`,
    meta: (d) => `Total de ventas: ${d.total_ventas}`,
    filas: (d) =>
      d.ventas.map((v) => [v.numero_venta, formatoHora(v.hora), v.vendedor, v.productos, formatoMoneda(v.total)]),
    totalLine: (d) => `Total ingresos: ${formatoMoneda(d.total_ingresos)}`,
  },

  "ventas-rango": {
    endpoint: "/api/reports/ventas-por-fecha",
    params() {
      const inicio = document.getElementById("rvFechaInicio").value;
      const fin = document.getElementById("rvFechaFin").value;
      if (!inicio || !fin) {
        showAlert("reporteAlertBox", "Selecciona la fecha de inicio y de fin.");
        return null;
      }
      if (inicio > fin) {
        showAlert("reporteAlertBox", "La fecha 'Desde' no puede ser posterior a la fecha 'Hasta'.");
        return null;
      }
      return {
        query: { fecha_inicio: inicio, fecha_fin: fin },
        filenameBase: `ventas_${inicio}_a_${fin}`,
      };
    },
    headers: ["N° venta", "Fecha", "Vendedor", "Productos", "Total"],
    titulo: (d) => `Reporte de ventas del ${d.fecha_inicio} al ${d.fecha_fin}`,
    meta: (d) => `Total de ventas: ${d.total_ventas}`,
    filas: (d) =>
      d.ventas.map((v) => [v.numero_venta, formatoFechaHora(v.hora), v.vendedor, v.productos, formatoMoneda(v.total)]),
    totalLine: (d) => `Total ingresos: ${formatoMoneda(d.total_ingresos)}`,
  },

  "ventas-mensuales": {
    endpoint: "/api/reports/ventas-mensuales",
    params() {
      const valor = document.getElementById("rvMes").value;
      if (!valor) {
        showAlert("reporteAlertBox", "Selecciona un mes.");
        return null;
      }
      const [anio, mes] = valor.split("-").map(Number);
      return { query: { anio, mes }, filenameBase: `ventas_mensuales_${anio}_${String(mes).padStart(2, "0")}` };
    },
    headers: ["Fecha", "N° de ventas", "Ingresos"],
    titulo: (d) => `Reporte de ventas mensuales ${String(d.mes).padStart(2, "0")}/${d.anio}`,
    meta: (d) => `Total de ventas del mes: ${d.total_ventas}`,
    filas: (d) => d.dias.map((dia) => [dia.fecha, dia.total_ventas, formatoMoneda(dia.total_ingresos)]),
    totalLine: (d) => `Total ingresos del mes: ${formatoMoneda(d.total_ingresos)}`,
  },

  "stock-bajo": {
    endpoint: "/api/reports/stock-bajo",
    params() {
      return { query: {}, filenameBase: "productos_stock_bajo" };
    },
    headers: ["Código", "Producto", "Categoría", "Stock", "Estado"],
    titulo: () => "Reporte de productos con poco stock",
    meta: (d) => `Total de productos con stock bajo o agotado: ${d.total_productos}`,
    filas: (d) =>
      d.productos.map((p) => [
        p.codigo,
        p.nombre,
        p.categoria,
        p.stock,
        p.estado_stock === "agotado" ? "❌ Agotado" : "⚠ Bajo",
      ]),
    totalLine: null,
  },

  "mas-vendidos": {
    endpoint: "/api/reports/mas-vendidos",
    params() {
      const limite = parseInt(document.getElementById("rvLimite").value) || 10;
      return { query: { limite }, filenameBase: "productos_mas_vendidos" };
    },
    headers: ["Producto", "N° de ventas", "Cantidad total vendida"],
    titulo() {
      const limite = parseInt(document.getElementById("rvLimite").value) || 10;
      return `Reporte de los ${limite} productos más vendidos`;
    },
    meta: () => "",
    filas: (d) => d.productos.map((p) => [p.nombre, p.total_vendido, p.cantidad_total]),
    totalLine: null,
  },
};

document.querySelectorAll("#tabsReportes .nav-link").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#tabsReportes .nav-link").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");

    tipoActual = btn.dataset.tipo;

    document.querySelectorAll(".filtro-grupo").forEach((grupo) => {
      grupo.classList.toggle("d-none", grupo.dataset.filtro !== tipoActual);
    });

    clearAlert("reporteAlertBox");
    document.getElementById("reporteContenido").classList.add("d-none");
    document.getElementById("reporteVacio").classList.remove("d-none");
  });
});

function construirQuery(query, formato) {
  const params = new URLSearchParams();
  Object.entries(query).forEach(([clave, valor]) => {
    if (valor !== undefined && valor !== null && valor !== "") params.set(clave, valor);
  });
  if (formato) params.set("formato", formato);
  const texto = params.toString();
  return texto ? `?${texto}` : "";
}

async function generarReporte() {
  clearAlert("reporteAlertBox");
  const config = REPORTES[tipoActual];
  const info = config.params();
  if (!info) return;

  const btn = document.getElementById("btnGenerarReporte");
  btn.disabled = true;

  try {
    const datos = await apiRequest(`${config.endpoint}${construirQuery(info.query)}`);
    if (!datos) return;

    const filas = config.filas(datos);

    document.getElementById("reporteVacio").classList.toggle("d-none", filas.length > 0);
    document.getElementById("reporteContenido").classList.toggle("d-none", filas.length === 0);

    if (filas.length === 0) return;

    document.getElementById("reporteTitulo").textContent = config.titulo(datos);
    document.getElementById("reporteMeta").textContent = config.meta(datos);

    document.getElementById("reporteHeaders").innerHTML = config.headers
      .map((h, i) => `<th class="${i === config.headers.length - 1 ? "text-end" : ""}">${h}</th>`)
      .join("");

    document.getElementById("reporteFilas").innerHTML = filas
      .map(
        (fila) =>
          `<tr>${fila
            .map((celda, i) => `<td class="${i === fila.length - 1 ? "text-end" : ""}">${celda}</td>`)
            .join("")}</tr>`
      )
      .join("");

    const totalWrap = document.getElementById("reporteTotalWrap");
    if (config.totalLine) {
      document.getElementById("reporteTotalLine").textContent = config.totalLine(datos);
      totalWrap.classList.remove("d-none");
    } else {
      totalWrap.classList.add("d-none");
    }
  } catch (error) {
    showAlert("reporteAlertBox", error.message);
  } finally {
    btn.disabled = false;
  }
}

async function descargarReporte(formato) {
  clearAlert("reporteAlertBox");
  const config = REPORTES[tipoActual];
  const info = config.params();
  if (!info) return;

  const extension = formato === "pdf" ? "pdf" : "png";
  const btn = formato === "pdf" ? document.getElementById("btnDescargarPdf") : document.getElementById("btnDescargarImagen");
  btn.disabled = true;

  try {
    const blob = await apiRequest(`${config.endpoint}${construirQuery(info.query, formato === "pdf" ? "pdf" : "imagen")}`);
    if (!blob) return;
    downloadBlob(blob, `${info.filenameBase}.${extension}`);
  } catch (error) {
    showAlert("reporteAlertBox", error.message);
  } finally {
    btn.disabled = false;
  }
}

document.getElementById("btnGenerarReporte").addEventListener("click", generarReporte);
document.getElementById("btnDescargarPdf").addEventListener("click", () => descargarReporte("pdf"));
document.getElementById("btnDescargarImagen").addEventListener("click", () => descargarReporte("imagen"));

(function inicializarFiltros() {
  const hoy = new Date();
  const iso = hoy.toISOString().slice(0, 10);
  const mesActual = iso.slice(0, 7);

  document.getElementById("rvFecha").value = iso;
  document.getElementById("rvFechaInicio").value = iso;
  document.getElementById("rvFechaFin").value = iso;
  document.getElementById("rvMes").value = mesActual;
})();
