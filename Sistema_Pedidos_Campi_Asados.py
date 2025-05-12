import streamlit as st
import pandas as pd
from datetime import datetime
from collections import defaultdict
import io

st.set_page_config(page_title="Pedidos - Campi Asados", layout="wide")

# Encabezado con título centrado y estilo más grande
st.markdown("""
    <div style='display: flex; justify-content: center; align-items: center;'>
        <h1 style='font-size: 40px; margin-bottom: 0;'>🍽️ Sistema de Pedidos - Campi Asados</h1>
    </div>
""", unsafe_allow_html=True)

# Función para agrupar productos
def agrupar_productos(productos):
    agrupados = defaultdict(lambda: {"Cantidad": 0, "Subtotal": 0, "Obs": []})
    for item in productos:
        nombre = item["Nombre"]
        agrupados[nombre]["Cantidad"] += item["Cantidad"]
        agrupados[nombre]["Subtotal"] += item["Subtotal"]
        if item["Obs"]:
            agrupados[nombre]["Obs"].append(item["Obs"])
    return agrupados

# --- Inicializar variables ---
if "menu" not in st.session_state:
    st.session_state.menu = {
        "Carnes Especiales": {
            "Punta de Anca con Champiñones": 42000,
            "Cañon Especial": 42000,
            "Filete Especial": 42000,
            "Solomo Especial": 42000
        },
        "Carnes": {
            "Punta de Anca": 38000,
            "Churrasco": 38000,
            "Costilla BBQ": 38000,
            "Cañon": 30000,
            "Solomo": 33000,
            "Filete de Pollo": 30000
        },
        "Chuzos": {
            "Cerdo": 23000,
            "Pollo": 23000,
            "Res": 27000,
            "Combinado Cerdo - Res": 27000
        },
        "Hamburguesas": {
            "Filete de Pollo": 26000,
            "Cañon de Cerdo": 26000,
            "Solomo de Res": 26000,
            "Hamburguesa Carva": 23000,
            "Hamburguesa doble carne": 20000,
            "Hamburguesa Especial": 18000,
            "Hamburguesa Sencilla": 15000
        },
        "Perros": {
            "Super Especial": 17000,
            "Especial": 14000,
            "Sencillo": 12000,
            "Perra Pequeña": 16000,
            "Perra Grande": 20000,
            "Desmechado carne": 24000,
            "Desmechado Pollo": 24000,
            "Desmechado Mixto": 24000
        },
        "Arepas": {
            "Res": 20000,
            "Cerdo Pollo": 18000,
            "Combinada": 30000,
            "Mixta": 20000,
            "Carne": 18000
        },
        "Otros Platos": {
            "Alitas de Pollo": 27000,
            "Picada de Alitas Picantes": 60000,
            "Chicharron": 28000,
            "Picada para Dos": 50000,
            "Picada para Tres": 65000,
            "Picada para Cuatro": 85000
        },
        "Limonadas": {
            "Limonada de coco": 8000,
            "Limonada de cereza": 8000,
            "Limonada de coco con yerbabuena": 8000,
            "Limonada Natural": 7000
        },
        "Jugos Naturales": {
            "Fresa (agua)": 6000,
            "Mora (agua)": 6000,
            "Maracuya (agua)": 6000,
            "Frutos Rojos (agua)": 6000,
            "Mango (agua)": 6000,
            "Guanabano (agua)": 6000,
            "Mango Biche (agua)": 6000,
            "Lulo (agua)": 6000,
            "Fresa (leche)": 7000,
            "Mora (leche)": 7000,
            "Maracuya (leche)": 7000,
            "Frutos Rojos (leche)": 7000,
            "Mango (leche)": 7000,
            "Guanabano (leche)": 7000,
            "Mango Biche (leche)": 7000,
            "Lulo (leche)": 7000
        },
        "Otras Bebidas": {
            "Cervezas Michelada": 7000,
            "Cervezas": 4000,
            "Gaseosa": 4000,
            "Gaseosa 1.5": 8000,
            "Milo": 7000
        }
    }
if "pedidos" not in st.session_state:
    st.session_state.pedidos = []
if "propina_actual" not in st.session_state:
    st.session_state.propina_actual = 0

# Fecha actual y filtro de pedidos
hoy = datetime.now().strftime("%Y-%m-%d")
pedidos_del_dia = [p for p in st.session_state.pedidos if p["Fecha"].startswith(hoy)]
pedidos_visibles = [p for p in pedidos_del_dia if p["Estado"] != "Entregado"]

# Botón de nuevo pedido
if st.button("🆕 Nuevo pedido"):
    for key in list(st.session_state.keys()):
        if key.startswith("cant_") or key.startswith("obs_"):
            del st.session_state[key]
    st.session_state.propina_actual = 0
    st.rerun()

# Formulario de pedido
with st.form("formulario_pedido"):
    col1, col2 = st.columns(2)
    canal = col1.selectbox("Canal de venta", ["En sitio", "Domicilio", "Para llevar"])
    if canal == "En sitio":
        mesa = col2.number_input("Número de mesa (si aplica)", min_value=1, max_value=20, step=1)
    else:
        mesa = "-"
        col2.text_input("Número de mesa (no aplica)", value="No aplica", disabled=True)

    # Validación: advertir si la mesa ya tiene pedido en curso
    if canal == "En sitio":
        mesas_ocupadas = sorted(set(p['Mesa'] for p in pedidos_visibles if p['Mesa'] != '-' and p['Estado'] in ["Pendiente", "En preparación"]))
        mesa_ocupada = mesa in mesas_ocupadas
        mesa_ocupada = False
    if canal == "En sitio":
        mesas_ocupadas = sorted(set(p["Mesa"] for p in pedidos_visibles if p["Mesa"] != "-" and p["Estado"] in ["Pendiente", "En preparación"]))
        mesa_ocupada = mesa in mesas_ocupadas
            st.warning(f"⚠️ Mesas ocupadas: {' - '.join(map(str, mesas_ocupadas))}")

    selected_items = []
    cantidades = {}
    observaciones = {}

    st.markdown("<h3 style='color:#A52A2A;'>🧾 Selección de productos</h3>", unsafe_allow_html=True)
    for categoria, items in st.session_state.menu.items():
        with st.expander(f"🍽️ {categoria}", expanded=False):
            st.markdown(f"<h4 style='font-size:18px; color:#444;'>{categoria}</h4>", unsafe_allow_html=True)
            for item, precio in items.items():
                key_base = f"{categoria}_{item}".replace(" ", "_").lower()
                cols = st.columns([4, 1, 2])
                cantidades[item] = cols[0].number_input(f"{item}", min_value=0, value=0, key=f"cant_{key_base}")
                cols[1].markdown(f"**$ {precio:,.0f}**")
                observaciones[item] = cols[2].text_input("Observaciones", max_chars=100, key=f"obs_{key_base}")
                if cantidades[item] > 0:
                    selected_items.append((item, precio))

    editing_index = st.session_state.get("editing_index", None)
    submit_label = "Guardar pedido" if editing_index is not None else "Agregar pedido"
    submitted = st.form_submit_button(submit_label)

    if submitted and selected_items and (editing_index is not None or not mesa_ocupada):
        total = sum(cantidades[p] * precio for p, precio in selected_items)
        pedido = {
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Canal": canal,
            "Mesa": mesa if canal == "En sitio" else "-",
            "Productos": [
                {"Nombre": p, "Cantidad": cantidades[p], "Obs": observaciones[p], "Precio": precio, "Subtotal": cantidades[p] * precio}
                for p, precio in selected_items
            ],
            "Estado": "Pendiente",
            "Total": total,
            "Propina": st.session_state.propina_actual
        }
        if editing_index is not None:
            st.session_state.pedidos[editing_index] = pedido
            del st.session_state["editing_index"]
        else:
            st.session_state.pedidos.append(pedido)
        for key in list(st.session_state.keys()):
            if key.startswith("cant_") or key.startswith("obs_"):
                del st.session_state[key]
        st.session_state.propina_actual = 0
        st.success("Pedido agregado correctamente ✅")
        st.rerun()

st.divider()

st.subheader("📋 Pedidos del día")

for i, pedido in enumerate(pedidos_visibles):
    mesa_info = f"Mesa {pedido['Mesa']}" if pedido['Mesa'] != "-" else "Sin mesa"
    with st.expander(f"Pedido #{i+1} - {pedido['Canal']} - {mesa_info} - {pedido['Estado']}"):
        st.write(f"🕐 Fecha: {pedido['Fecha']}")
        agrupados = agrupar_productos(pedido['Productos'])
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Productos:**")
            for nombre, datos in agrupados.items():
                st.write(f"- {datos['Cantidad']} x {nombre} ($ {datos['Subtotal']:,.0f})")
                for obs in datos['Obs']:
                    st.caption(f"   Observaciones: {obs}")
        with col2:
            st.session_state.propina_actual = st.number_input("Propina (opcional)", min_value=0, value=pedido["Propina"], step=1000, key=f"propina_{i}")
            pedido['Propina'] = st.session_state.propina_actual
            st.write(f"**Subtotal: $ {pedido['Total']:,.0f}**")
            st.write(f"**Propina: $ {pedido['Propina']:,.0f}**")
            st.write(f"**Total: $ {pedido['Total'] + pedido['Propina']:,.0f}**")
            if pedido['Estado'] in ["Pendiente", "En preparación"]:
                if st.button("✏️ Editar pedido", key=f"editar_{i}"):
                    for item in pedido['Productos']:
                        key_base = f"{item['Nombre']}".replace(" ", "_").lower()
                        st.session_state[f"cant_{key_base}"] = item['Cantidad']
                        st.session_state[f"obs_{key_base}"] = item['Obs']
                    st.session_state.propina_actual = pedido['Propina']
                    st.session_state["editing_index"] = i
                    st.info(f"Editando pedido #{i+1}. Puedes modificar los productos desde el formulario de arriba.")

            nuevo_estado = st.selectbox("Cambiar estado", ["Pendiente", "En preparación", "Entregado"],
                                        index=["Pendiente", "En preparación", "Entregado"].index(pedido['Estado']),
                                        key=f"estado_{i}")
            pedido['Estado'] = nuevo_estado
