const resources = {
    clientes: { label: "Clientes", icon: "♙", endpoint: "/clientes", description: "Personas que compran en tu tienda.", columns: ["id", "nombre", "email", "telefono", "direccion"], fields: [{ name: "nombre", label: "Nombre", required: true }, { name: "email", label: "Correo", type: "email", required: true }, { name: "telefono", label: "Teléfono", required: true }, { name: "direccion", label: "Dirección", required: true }] },
    proveedores: { label: "Proveedores", icon: "⌂", endpoint: "/proveedores", description: "Empresas que abastecen tu inventario.", columns: ["id", "nombre_empresa", "contactos", "email", "telefono"], fields: [{ name: "nombre_empresa", label: "Empresa", required: true }, { name: "contactos", label: "Persona de contacto", required: true }, { name: "email", label: "Correo", type: "email", required: true }, { name: "telefono", label: "Teléfono", required: true }] },
    productos: { label: "Productos", icon: "▦", endpoint: "/productos", description: "Catálogo y precios de venta.", columns: ["id", "nombre", "marca", "precio_venta", "id_proveedores"], fields: [{ name: "nombre", label: "Nombre", required: true }, { name: "marca", label: "Marca", required: true }, { name: "precio_venta", label: "Precio de venta", type: "number", step: "0.01", required: true }, { name: "id_proveedor", label: "Proveedor", type: "select", source: "proveedores" }] },
    compras: { label: "Compras", icon: "↓", endpoint: "/compras", description: "Entradas de mercancía y abastecimiento.", columns: ["id", "id_proveedores", "fecha", "total", "estado"], fields: [{ name: "id_proveedores", label: "Proveedor", type: "select", source: "proveedores", required: true }, { name: "fecha", label: "Fecha", type: "datetime-local", required: true }, { name: "total", label: "Total", type: "number", step: "0.01", required: true }, { name: "estado", label: "Estado", required: true }] },
    ventas: { label: "Ventas", icon: "↑", endpoint: "/ventas", description: "Operaciones realizadas a clientes.", columns: ["id", "id_clientes", "fecha", "metodo_pago", "estado", "total"], fields: [{ name: "id_clientes", label: "Cliente", type: "select", source: "clientes", required: true }, { name: "fecha", label: "Fecha", type: "datetime-local", required: true }, { name: "metodo_pago", label: "Método de pago", required: true }, { name: "estado", label: "Estado", required: true }] },
    "detalles-compras": { label: "Detalle de compras", icon: "≡", endpoint: "/detalles-compras", description: "Productos incluidos en cada compra.", columns: ["id", "id_compras", "id_productos", "cantidad", "precio_unitario", "subtotal"], fields: [{ name: "id_compras", label: "Compra", type: "select", source: "compras" }, { name: "id_productos", label: "Producto", type: "select", source: "productos", required: true }, { name: "cantidad", label: "Cantidad", type: "number", required: true }] },
    "detalles-ventas": { label: "Detalle de ventas", icon: "≣", endpoint: "/detalles-ventas", description: "Productos incluidos en cada venta.", columns: ["id", "id_ventas", "id_productos", "cantidad", "precio_unitario", "subtotal"], fields: [{ name: "id_ventas", label: "Venta", type: "select", source: "ventas" }, { name: "id_productos", label: "Producto", type: "select", source: "productos", required: true }, { name: "cantidad", label: "Cantidad", type: "number", required: true }] }
};

const state = { current: null, records: [], editingId: null, cache: {} };
const $ = (selector) => document.querySelector(selector);
const nav = $("#resource-nav");

function displayValue(record, column) {
    const value = record[column];
    if (value === null || value === undefined || value === "") return "—";
    if (column === "fecha") return new Date(value).toLocaleString("es-ES", { dateStyle: "short", timeStyle: "short" });
    if (["precio_venta", "total", "precio_unitario", "subtotal"].includes(column)) return Number(value).toLocaleString("es-ES", { style: "currency", currency: "EUR" });
    return String(value);
}

function buildNavigation() {
    nav.innerHTML = `<button class="nav-button active" data-view="overview"><span class="nav-icon">⌂</span> Resumen</button>`;
    Object.entries(resources).forEach(([key, resource]) => {
        const button = document.createElement("button");
        button.className = "nav-button";
        button.dataset.resource = key;
        button.innerHTML = `<span class="nav-icon">${resource.icon}</span> ${resource.label}`;
        nav.appendChild(button);
    });
    nav.addEventListener("click", (event) => {
        const button = event.target.closest("button");
        if (!button) return;
        document.body.classList.remove("menu-open");
        if (button.dataset.view === "overview") showOverview();
        else showResource(button.dataset.resource);
    });
}

async function fetchRecords(key) {
    if (state.cache[key]) return state.cache[key];
    const response = await fetch(resources[key].endpoint);
    if (!response.ok) throw new Error(`No se pudo cargar ${resources[key].label}`);
    state.cache[key] = await response.json();
    return state.cache[key];
}

async function showOverview() {
    state.current = null;
    $("#page-title").textContent = "Resumen";
    $("#overview").classList.remove("hidden");
    $("#table-view").classList.add("hidden");
    document.querySelectorAll(".nav-button").forEach((button) => button.classList.toggle("active", button.dataset.view === "overview"));
    const counts = await Promise.all(Object.keys(resources).map(async (key) => [key, (await fetchRecords(key)).length]));
    $("#stats-grid").innerHTML = counts.slice(0, 4).map(([key, count]) => `<article class="stat-card"><span class="stat-label">${resources[key].label}</span><div class="stat-value">${count}</div></article>`).join("");
    $("#quick-links").innerHTML = counts.map(([key, count]) => `<button class="quick-link" data-resource="${key}"><span class="quick-icon">${resources[key].icon}</span><span>${resources[key].label}</span></button>`).join("");
    $("#quick-links").querySelectorAll("button").forEach((button) => button.addEventListener("click", () => showResource(button.dataset.resource)));
}

async function showResource(key) {
    state.current = key;
    const resource = resources[key];
    $("#page-title").textContent = resource.label;
    $("#table-description").textContent = resource.description;
    $("#overview").classList.add("hidden");
    $("#table-view").classList.remove("hidden");
    document.querySelectorAll(".nav-button").forEach((button) => button.classList.toggle("active", button.dataset.resource === key));
    await renderTable();
}

async function renderTable() {
    try {
        state.records = await fetchRecords(state.current);
        const resource = resources[state.current];
        $("#record-count").textContent = `${state.records.length} registro${state.records.length === 1 ? "" : "s"}`;
        $("#table-head").innerHTML = `<tr>${resource.columns.map((column) => `<th>${column.replaceAll("_", " ")}</th>`).join("")}<th>Acciones</th></tr>`;
        $("#table-body").innerHTML = state.records.map((record) => `<tr>${resource.columns.map((column) => `<td>${displayValue(record, column)}</td>`).join("")}<td><div class="actions"><button class="action-button" data-edit="${record.id}">Editar</button><button class="action-button delete" data-delete="${record.id}">Eliminar</button></div></td></tr>`).join("");
        $("#empty-state").classList.toggle("hidden", state.records.length > 0);
        $("#table-body").querySelectorAll("[data-edit]").forEach((button) => button.addEventListener("click", () => openDialog(Number(button.dataset.edit))));
        $("#table-body").querySelectorAll("[data-delete]").forEach((button) => button.addEventListener("click", () => deleteRecord(Number(button.dataset.delete))));
        hideAlert();
    } catch (error) { showAlert(error.message); }
}

async function buildForm(record = {}) {
    const resource = resources[state.current];
    const fields = await Promise.all(resource.fields.map(async (field) => {
        const value = record[field.name] ?? (field.name === "fecha" ? new Date().toISOString().slice(0, 16) : "");
        let control;
        if (field.type === "select") {
            const options = await fetchRecords(field.source);
            control = `<select id="field-${field.name}" name="${field.name}" ${field.required ? "required" : ""}><option value="">Selecciona una opción</option>${options.map((option) => `<option value="${option.id}" ${String(option.id) === String(value) ? "selected" : ""}>#${option.id} · ${option.nombre || option.nombre_empresa || option.fecha || "Registro"}</option>`).join("")}</select>`;
        } else {
            control = `<input id="field-${field.name}" name="${field.name}" type="${field.type || "text"}" value="${String(value).replaceAll('"', "&quot;")}" ${field.step ? `step="${field.step}"` : ""} ${field.required ? "required" : ""}>`;
        }
        return `<div class="field"><label for="field-${field.name}">${field.label}</label>${control}</div>`;
    }));
    $("#form-fields").innerHTML = fields.join("");
}

async function openDialog(id = null) {
    state.editingId = id;
    const record = id ? state.records.find((item) => item.id === id) : {};
    $("#dialog-title").textContent = id ? "Editar registro" : "Nuevo registro";
    await buildForm(record);
    $("#record-dialog").showModal();
}

async function saveRecord(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const payload = Object.fromEntries(formData.entries());
    Object.keys(payload).forEach((key) => { if (payload[key] === "") delete payload[key]; });
    if (payload.fecha) payload.fecha = new Date(payload.fecha).toISOString().slice(0, 19);
    ["id_proveedores", "id_proveedor", "id_clientes", "id_compras", "id_ventas", "id_productos", "cantidad"].forEach((key) => { if (payload[key]) payload[key] = Number(payload[key]); });
    ["precio_venta", "total"].forEach((key) => { if (payload[key]) payload[key] = Number(payload[key]); });
    const resource = resources[state.current];
    const url = state.editingId ? `${resource.endpoint}/${state.editingId}` : resource.endpoint;
    const response = await fetch(url, { method: state.editingId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detalle || result.mensaje || "No se pudo guardar el registro");
    state.cache = {};
    $("#record-dialog").close();
    await renderTable();
}

async function deleteRecord(id) {
    if (!window.confirm("¿Eliminar este registro? Esta acción no se puede deshacer.")) return;
    const resource = resources[state.current];
    const response = await fetch(`${resource.endpoint}/${id}`, { method: "DELETE" });
    const result = await response.json();
    if (!response.ok) { showAlert(result.detalle || result.mensaje || "No se pudo eliminar"); return; }
    state.cache = {};
    await renderTable();
}

function showAlert(message) { $("#alert").textContent = message; $("#alert").classList.remove("hidden"); }
function hideAlert() { $("#alert").classList.add("hidden"); }

$("#new-record").addEventListener("click", () => { if (state.current) openDialog(); });
$("#refresh-table").addEventListener("click", () => { state.cache = {}; renderTable(); });
$("#record-form").addEventListener("submit", async (event) => { try { await saveRecord(event); } catch (error) { showAlert(error.message); } });
$("#close-dialog").addEventListener("click", () => $("#record-dialog").close());
$("#cancel-dialog").addEventListener("click", () => $("#record-dialog").close());
$("#menu-toggle").addEventListener("click", () => document.body.classList.toggle("menu-open"));

buildNavigation();
showOverview().catch((error) => showAlert(error.message));
