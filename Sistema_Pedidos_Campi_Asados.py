# Sistema de Pedidos para Restaurante - Completo y funcional

import streamlit as st
from datetime import datetime
import pandas as pd
import io

st.set_page_config(page_title="🍽️ Sistema Restaurante", layout="wide")

# --- Encabezado ---
st.markdown("""
    <div style='text-align: center;'>
        <h1>🍽️ Sistema de Pedidos - Restaurante</h1>
        <p>Compatible con celular, tablet y PC</p>
    </div>
""", unsafe_allow_html=True)

# --- Inicializar sesión ---
if "pedidos" not in st.session_state:
    st.session_state.pedidos = []
if "productos" not in st.session_state:
    st.session_state.productos = {
        "Carne Asada": {
            "precio": 20000,
            "descripcion": "Carne Asada, Papitas, arepa con lonchita, Ensalada",
            "categoria": "Carnes Especiales",
            "imagen": "https://tinyurl.com/yr2e7jfy"
        },
        "Hamburguesa": {
            "precio": 15000,
            "descripcion": "Carne, Ripio, Tomate, Queso, Ensalada",
            "categoria": "Comidas Rápidas",
            "imagen": "https://tinyurl.com/yr2e7jfy"
        },
        "Limonadas": {
            "precio": 7000,
            "descripcion": "Limonadas de diferentes sabores",
            "categoria": "Bebidas",
            "imagen": ""
        }
    }
if "editar_id" not in st.session_state:
    st.session_state.editar_id = None
if "form_reset" not in st.session_state:
    st.session_state.form_reset = False
if "inputs_reset" not in st.session_state:
    st.session_state.inputs_reset = False

# --- Menú principal ---
opciones_menu = ["📋 Tomar Pedido", "🛠️ Gestionar Productos", "📊 Reportes", "📂 Historial", "👨‍🍳 Pantalla Cocina"]
menu = st.sidebar.radio("Menú", opciones_menu)

# --- Función para avanzar de estado ---
def avanzar_estado(pedido):
    estados = ["Registrado", "En preparación", "Entregado", "Pagado"]
    if pedido['estado'] in estados:
        i = estados.index(pedido['estado'])
        if i < len(estados) - 1:
            pedido['estado'] = estados[i + 1]

# --- Función para agregar pedido ---
def agregar_pedido(tipo, mesa, productos, propina):
    total = sum(item['subtotal'] for item in productos)
    propina_valor = round(total * propina, 2)
    pedido = {
        "id": len(st.session_state.pedidos) + 1,
        "tipo": tipo,
        "mesa": mesa if tipo == "Mesa" else "-",
        "productos": productos,
        "estado": "Registrado",
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "subtotal": total,
        "propina": propina_valor,
        "total": total + propina_valor
    }
    st.session_state.pedidos.append(pedido)

# --- Función para verificar si mesa está ocupada ---
def mesa_ocupada(mesa):
    for p in st.session_state.pedidos:
        if p['mesa'] == mesa and p['estado'] in ["Registrado", "En preparación", "Entregado"]:
            return True
    return False

# --- Página: Tomar Pedido ---
if menu == "📋 Tomar Pedido":
    st.subheader("📝 Nuevo Pedido")
    tipo_pedido = st.selectbox("Tipo de pedido", ["Mesa", "Para llevar", "Domicilio"])
    mesa = st.selectbox("Número de mesa", [str(i) for i in range(1, 21)]) if tipo_pedido == "Mesa" else "-"
    propina_opcional = st.checkbox("Incluir propina (10%)")
    propina = 0.1 if propina_opcional else 0.0

    st.markdown("---")
    st.write("### Selección de productos")

    productos_seleccionados = []
    for nombre, info in st.session_state.productos.items():
        cantidad_key = f"cantidad_{nombre}"
        obs_key = f"obs_{nombre}"
        if st.session_state.inputs_reset:
            st.session_state[cantidad_key] = 0
            st.session_state[obs_key] = ""

        col1, col2 = st.columns([6, 4])
        with col1:
            st.markdown(f"**{nombre}** - ${info['precio']:,.0f}")
            if 'descripcion' in info:
                st.markdown(f"_Descripción:_ {info['descripcion']}")
            if 'categoria' in info:
                st.markdown(f"_Categoría:_ {info['categoria']}")
        with col2:
            if 'imagen' in info and info['imagen']:
                st.image(info['imagen'], width=100)

        cantidad = st.number_input(f"Cantidad - {nombre}", min_value=0, max_value=20, step=1, key=cantidad_key)
        obs = st.text_input(f"Observación - {nombre}", key=obs_key)
        if cantidad > 0:
            productos_seleccionados.append({"nombre": nombre, "cantidad": cantidad, "obs": obs, "subtotal": cantidad * info['precio']})

    if st.button("Guardar pedido"):
        if tipo_pedido == "Mesa" and mesa_ocupada(mesa):
            st.error("⚠️ Mesa ocupada. Debe seleccionar otra mesa.")
        elif tipo_pedido and productos_seleccionados:
            agregar_pedido(tipo_pedido, mesa, productos_seleccionados, propina)
            st.success("✅ Pedido guardado exitosamente")
            st.session_state.inputs_reset = True
            st.rerun()
        else:
            st.error("⚠️ Debe seleccionar al menos un producto")

    st.session_state.inputs_reset = False

    st.markdown("---")
    st.subheader("📋 Pedidos Activos")
    for pedido in st.session_state.pedidos:
        if pedido['estado'] != "Pagado":
            st.markdown(f"**#{pedido['id']}** - {pedido['tipo']} - Mesa {pedido['mesa']} - Total: ${pedido['total']:,.0f} - Estado: {pedido['estado']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Avanzar estado #{pedido['id']}"):
                    avanzar_estado(pedido)
                    st.success(f"🔄 Pedido #{pedido['id']} ahora está en estado: {pedido['estado']}")
                    st.rerun()
            with col2:
                st.markdown(f"🕒 {pedido['hora']}")

# --- Página: Gestionar Productos ---
elif menu == "🛠️ Gestionar Productos":
    st.subheader("🛒 Administración de productos")

    with st.form("nuevo_producto"):
        nombre = st.text_input("Nombre del producto", value="" if st.session_state.form_reset else None)
        precio = st.number_input("Precio ($)", min_value=0, step=500, value=0 if st.session_state.form_reset else 0, format="%d")
        descripcion = st.text_input("Descripción", value="" if st.session_state.form_reset else None)
        categoria = st.text_input("Categoría", value="" if st.session_state.form_reset else None)
        imagen = st.text_input("URL de imagen (opcional)", value="" if st.session_state.form_reset else None)
        submitted = st.form_submit_button("Agregar producto")
        if submitted and nombre:
            st.session_state.productos[nombre] = {
                "precio": precio,
                "descripcion": descripcion,
                "categoria": categoria,
                "imagen": imagen
            }
            st.success(f"✅ Producto '{nombre}' agregado")
            st.session_state.form_reset = True
            st.rerun()
        else:
            st.session_state.form_reset = False

    st.markdown("---")
    st.write("### Productos actuales")
    for nombre, info in st.session_state.productos.items():
        st.markdown(f"- **{nombre}** ($ {info['precio']:,.0f}) - {info.get('categoria', '')} - {info.get('descripcion', '')}")
        if info.get("imagen"):
            st.image(info["imagen"], width=100)

# --- Página: Reportes ---
elif menu == "📊 Reportes":
    st.subheader("📈 Reportes de ventas")
    pedidos_df = pd.DataFrame(st.session_state.pedidos)

    if not pedidos_df.empty:
        st.write("### Ventas por tipo de pedido")
        st.bar_chart(pedidos_df.groupby("tipo")["total"].sum())

        st.write("### Ventas por estado")
        st.bar_chart(pedidos_df.groupby("estado")["total"].sum())

        st.write("### Tabla completa")
        st.dataframe(pedidos_df)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            pedidos_df.to_excel(writer, index=False, sheet_name='Pedidos')
            writer.save()
            st.download_button(
                label="📥 Descargar reporte en Excel",
                data=buffer.getvalue(),
                file_name="reporte_pedidos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("No hay pedidos aún para mostrar reportes")

# --- Página: Historial ---
elif menu == "📂 Historial":
    st.subheader("📁 Historial de Pedidos Pagados")
    pagados = [p for p in st.session_state.pedidos if p['estado'] == "Pagado"]
    if pagados:
        for pedido in pagados:
            st.markdown(f"**#{pedido['id']}** - {pedido['tipo']} - Mesa {pedido['mesa']} - Total: ${pedido['total']:,.0f} - Hora: {pedido['hora']}")
            for prod in pedido['productos']:
                st.markdown(f"- {prod['cantidad']}x {prod['nombre']} ({prod['obs']}) - ${prod['subtotal']:,.0f}")
            st.markdown("---")
    else:
        st.info("No hay pedidos pagados aún.")

# --- Página: Pantalla Cocina ---
elif menu == "👨‍🍳 Pantalla Cocina":
    st.subheader("👨‍🍳 Pedidos en Cocina")
    en_preparacion = [p for p in st.session_state.pedidos if p['estado'] == "En preparación"]

    if en_preparacion:
        for pedido in en_preparacion:
            st.markdown(f"### Pedido #{pedido['id']} - {pedido['tipo']} - Mesa {pedido['mesa']}")
            st.markdown(f"🕒 Hora: {pedido['hora']}")
            for prod in pedido['productos']:
                st.markdown(f"- {prod['cantidad']}x **{prod['nombre']}** ({prod['obs']})")
            st.markdown(f"**Total:** ${pedido['total']:,.0f}")
            st.markdown("---")
        if st.button("🖨️ Imprimir pantalla de cocina"):
            st.markdown("Descarga o imprime esta vista desde el navegador (Ctrl + P)")
            st.info("Puedes usar la opción de impresión del navegador para imprimir esta pantalla si cuentas con una impresora conectada.")
    else:
        st.info("No hay pedidos en preparación.")
