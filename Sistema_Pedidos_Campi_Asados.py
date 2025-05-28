import streamlit as st
from datetime import datetime
import pandas as pd
import io

# Configuración de página
st.set_page_config(page_title="🍽️ Sistema Restaurante", layout="wide")

# --- Categorías definidas ---
categories_list = [
    "Carnes Especiales", "Carnes", "Chuzos", "Arepas", "Hamburguesas",
    "Perros", "Otros Platos", "Bebidas", "Jugos", "Limonadas"
]

# --- Encabezado ---
st.markdown(
    """
    <div style='text-align: center;'>
        <h1>🍽️ Sistema de Pedidos - Restaurante</h1>
        <p>Compatible con celular, tablet y PC</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Inicializar estado ---
if "pedidos" not in st.session_state:
    st.session_state.pedidos = []
if "productos" not in st.session_state:
    st.session_state.productos = {
        "punta de Anca con Champiñones": {"precio":20000, "descripcion":"Carne Asada, Papitas, arepa con lonchita, Ensalada", "categoria":"Carnes Especiales"},
        "Solomito Especial": {"precio":50000, "descripcion":"Carne Asada, Papitas, arepa con lonchita, Ensalada", "categoria":"Carnes Especiales"},
        "Punta de Anca": {"precio":15000, "descripcion":"Carne, papas, arepa", "categoria":"Carnes"},
        "Chuzo de Pollo": {"precio":10000, "descripcion":"Chuzo, papas, arepa, Ensalada", "categoria":"Chuzos"},
        "Arepa con Carne": {"precio":10000, "descripcion":"Carne desmechada y queso", "categoria":"Arepas"},
        "Hamburguesa Especial": {"precio":10000, "descripcion":"Con todos los Juguetes", "categoria":"Hamburguesas"},
        "Perro Grande Especial": {"precio":10000, "descripcion":"Ripio, Queso, Ensalada", "categoria":"Perros"},
        "Picada para dos": {"precio":10000, "descripcion":"Picada de Chicharron, Papas, Morcilla, Carne, Maduritos", "categoria":"Otros Platos"},
        "Cerveza": {"precio":5000, "descripcion":"Cerveza Fria", "categoria":"Bebidas"},
        "Jugo de Mora": {"precio":10000, "descripcion":"Jugo Natural de Mora", "categoria":"Jugos"},
        "Limonada de Mango": {"precio":5000, "descripcion":"Limonada de Mango", "categoria":"Limonadas"},
        "Limonada de Coco": {"precio":5000, "descripcion":"Limonada de Coco", "categoria":"Limonadas"}
    }
if "inputs_reset" not in st.session_state:
    st.session_state.inputs_reset = False

# --- Menú principal ---
opciones_menu = ["📋 Tomar Pedido", "🛠️ Gestionar Productos", "📊 Reportes", "📂 Historial", "👨‍🍳 Pantalla Cocina"]
menu = st.sidebar.radio("Menú", opciones_menu)

# --- Funciones auxiliares ---
def avanzar_estado(pedido):
    estados = ["Registrado", "En preparación", "Entregado", "Pagado"]
    idx = estados.index(pedido['estado'])
    if idx < len(estados) - 1:
        pedido['estado'] = estados[idx + 1]

def mesa_ocupada(mesa):
    return any(p['mesa'] == mesa and p['estado'] in ["Registrado", "En preparación", "Entregado"]
               for p in st.session_state.pedidos)

def agregar_pedido(tipo, mesa, productos):
    subtotal = sum(item['subtotal'] for item in productos)
    pedido = {
        "id": len(st.session_state.pedidos) + 1,
        "tipo": tipo,
        "mesa": mesa if tipo == "Mesa" else None,
        "productos": productos,
        "estado": "Registrado",
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "subtotal": subtotal,
        "propina": 0.0,
        "total": subtotal
    }
    st.session_state.pedidos.append(pedido)

# --- Página: Tomar Pedido y Pedidos Activos ---
if menu == "📋 Tomar Pedido":
    st.subheader("📝 Nuevo Pedido")
    tipo = st.selectbox("Tipo de pedido", ["Mesa", "Para llevar", "Domicilio"])
    mesa = st.selectbox("Número de mesa", [str(i) for i in range(1, 21)]) if tipo == "Mesa" else None
    st.markdown("---")
    st.write("### Selección de productos por categoría")
    seleccion = []
    for cat in categories_list:
        with st.expander(cat, expanded=False):
            for nombre, info in st.session_state.productos.items():
                if info['categoria'] == cat:
                    c1, c2 = st.columns([6, 4])
                    c1.markdown(f"**{nombre}** — ${info['precio']:,.0f}")
                    c1.markdown(f"_Desc:_ {info['descripcion']}")
                    key_c, key_o = f"cant_{nombre}", f"obs_{nombre}"
                    if st.session_state.inputs_reset:
                        st.session_state[key_c], st.session_state[key_o] = 0, ''
                    cantidad = c2.number_input(f"Cantidad - {nombre}", 0, 20, key=key_c)
                    obs = c2.text_input(f"Observación - {nombre}", key=key_o)
                    if cantidad > 0:
                        seleccion.append({
                            "nombre": nombre,
                            "cantidad": cantidad,
                            "obs": obs,
                            "subtotal": cantidad * info['precio']
                        })
    if st.button("Guardar pedido"):
        if tipo == "Mesa" and mesa and mesa_ocupada(mesa):
            st.error("⚠️ Mesa ocupada; elige otra.")
        elif seleccion:
            agregar_pedido(tipo, mesa, seleccion)
            st.success("✅ Pedido registrado exitosamente.")
            st.session_state.inputs_reset = True
            st.rerun()
        else:
            st.error("⚠️ Selecciona al menos un producto.")
    st.session_state.inputs_reset = False

    # -- Pedidos Activos --
    st.markdown("---")
    # Registrados
    with st.expander("📋 Pedidos Registrados", expanded=True):
        regs = [p for p in st.session_state.pedidos if p['estado'] == "Registrado"]
        if regs:
            for p in regs:
                cols = st.columns([2, 1, 1])
                cols[0].markdown(f"**#{p['id']}** - {p['tipo']}" + (f" - Mesa {p['mesa']}" if p['tipo']=='Mesa' and p['mesa'] else ''))
                cols[1].markdown(f"_Subtotal:_ ${p['subtotal']:,.2f}")
                default_tip = round(p['subtotal'] * 0.1, 2)
                use_def = cols[2].checkbox(f"Propina 10% (${default_tip:,.2f})", key=f"tipdef_{p['id']}")
                tip_val = default_tip if use_def else 0.0
                tip_val = cols[2].number_input("Otro valor", 0.0, value=tip_val, format="%.2f", key=f"tipcus_{p['id']}")
                if cols[2].button("Aplicar", key=f"apply_{p['id']}"):
                    p['propina'] = round(tip_val, 2)
                    p['total'] = round(p['subtotal'] + p['propina'], 2)
                    st.rerun()
                st.markdown(f"**Total:** ${p['total']:,.2f}")
                for pr in p['productos']:
                    st.markdown(f"- {pr['cantidad']}× {pr['nombre']} ({pr['obs']}) — ${pr['subtotal']:,.2f}")
                c1, c2 = st.columns([1, 4])
                with c1:
                    if st.button(f"▶️ Avanzar #{p['id']}", key=f"adv1_{p['id']}"):
                        avanzar_estado(p)
                        st.success(f"Pedido #{p['id']} ahora {p['estado']}")
                        st.rerun()
                with c2:
                    st.markdown(f"🕒 {p['hora']}")
        else:
            st.write("No hay pedidos en estado Registrado.")
    # En preparación
    with st.expander("🍳 Pedidos En preparación", expanded=True):
        prep = [p for p in st.session_state.pedidos if p['estado'] == "En preparación"]
        if prep:
            for p in prep:
                cols = st.columns([2, 1])
                cols[0].markdown(f"**#{p['id']}** - {p['tipo']}" + (f" - Mesa {p['mesa']}" if p['tipo']=='Mesa' and p['mesa'] else ''))
                cols[1].markdown(f"_Estado:_ {p['estado']}")
                for pr in p['productos']:
                    st.markdown(f"- {pr['cantidad']}× {pr['nombre']} ({pr['obs']})")
                c1, c2 = st.columns([1, 4])
                with c1:
                    if st.button(f"✔️ Marcar preparado #{p['id']}", key=f"adv2_{p['id']}"):
                        avanzar_estado(p)
                        st.success(f"Pedido #{p['id']} ahora {p['estado']}")
                        st.rerun()
                with c2:
                    st.markdown(f"🕒 {p['hora']}")
        else:
            st.write("No hay pedidos en preparación.")
    # Entregados
    with st.expander("📦 Pedidos Entregados", expanded=True):
        ent = [p for p in st.session_state.pedidos if p['estado'] == "Entregado"]
        if ent:
            for p in ent:
                cols = st.columns([2, 1, 1])
                cols[0].markdown(f"**#{p['id']}** - {p['tipo']}" + (f" - Mesa {p['mesa']}" if p['tipo']=='Mesa' and p['mesa'] else ''))
                cols[1].markdown(f"_Subtotal:_ ${p['subtotal']:,.2f}")
                if p['propina'] == 0.0:
                    default_tip = round(p['subtotal'] * 0.1, 2)
                    use_def = cols[2].checkbox(f"Propina 10% (${default_tip:,.2f})", key=f"tipdef_ent_{p['id']}")
                    tip_val = default_tip if use_def else 0.0
                    tip_val = cols[2].number_input("Otro valor", 0.0, value=tip_val, format="%.2f", key=f"tipcus_ent_{p['id']}")
                    if cols[2].button("Aplicar propina", key=f"apply_ent_{p['id']}"):
                        p['propina'] = round(tip_val, 2)
                        p['total'] = round(p['subtotal'] + p['propina'], 2)
                        st.rerun()
                else:
                    cols[2].markdown(f"_Propina:_ ${p['propina']:,.2f}")
                st.markdown(f"**Total:** ${p['total']:,.2f}")
                for pr in p['productos']:
                    st.markdown(f"- {pr['cantidad']}× {pr['nombre']} ({pr['obs']})")
                if st.button(f"💰 Marcar pagado #{p['id']}", key=f"adv3_{p['id']}"):
                    avanzar_estado(p)
                    st.success(f"Pedido #{p['id']} ahora {p['estado']}")
                    st.rerun()
        else:
            st.write("No hay pedidos entregados.")

# --- Página: Gestionar Productos ---
elif menu == "🛠️ Gestionar Productos":
    st.subheader("🛒 Gestionar Productos y Categorías")
    # Crear producto
    with st.form("form_producto"):
        n = st.text_input("Nombre")
        p_val = st.number_input("Precio", 0, step=500)
        d = st.text_input("Descripción")
        c = st.selectbox("Categoría", categories_list)
        if st.form_submit_button("Agregar Producto") and n:
            st.session_state.productos[n] = {"precio": p_val, "descripcion": d, "categoria": c}
            st.success(f"Producto '{n}' agregado.")
            st.rerun()
    st.markdown("---")
    # Editar o eliminar producto
    st.write("**Editar o Eliminar Producto**")
    prod_sel = st.selectbox("Seleccionar producto", list(st.session_state.productos.keys()))
    if prod_sel:
        info = st.session_state.productos[prod_sel]
        new_name = st.text_input("Nombre", value=prod_sel)
        new_price = st.number_input("Precio", value=info["precio"], step=500)
        new_desc = st.text_input("Descripción", value=info["descripcion"])
        new_cat = st.selectbox("Categoría", categories_list, index=categories_list.index(info["categoria"]))
        if st.button("Actualizar Producto"):
            if new_name != prod_sel:
                st.session_state.productos.pop(prod_sel)
            st.session_state.productos[new_name] = {"precio": new_price, "descripcion": new_desc, "categoria": new_cat}
            st.success("Producto actualizado.")
            st.rerun()
        if st.button("Eliminar Producto"):
            st.session_state.productos.pop(prod_sel)
            st.success("Producto eliminado.")
            st.rerun()
    st.markdown("---")
    # Gestionar categorías
    st.subheader("🏷️ Gestionar Categorías")
    with st.form("form_categoria"):
        new_cat = st.text_input("Nueva categoría")
        if st.form_submit_button("Agregar Categoría") and new_cat:
            categories_list.append(new_cat)
            st.success(f"Categoría '{new_cat}' agregada.")
            st.rerun()
    cat_sel = st.selectbox("Seleccionar categoría", categories_list)
    if cat_sel:
        rename_cat = st.text_input("Renombrar categoría", value=cat_sel)
        if st.button("Actualizar Categoría"):
            idx = categories_list.index(cat_sel)
            categories_list[idx] = rename_cat
            for prod in st.session_state.productos.values():
                if prod["categoria"] == cat_sel:
                    prod["categoria"] = rename_cat
            st.success("Categoría actualizada.")
            st.rerun()
        if st.button("Eliminar Categoría"):
            categories_list.remove(cat_sel)
            for prod in st.session_state.productos.values():
                if prod["categoria"] == cat_sel:
                    prod["categoria"] = None
            st.success("Categoría eliminada.")
            st.rerun()
    st.markdown("---")
    st.write("### Productos actuales")
    for nombre, info in st.session_state.productos.items():
        st.markdown(f"- **{nombre}** — ${info['precio']:,.2f} ({info['categoria']})")

# --- Página: Reportes ---
elif menu == "📊 Reportes":
    st.subheader("📈 Reportes de ventas")
    pedidos = st.session_state.pedidos
    if pedidos:
        detalle = []
        for pdx in pedidos:
            for pr in pdx['productos']:
                detalle.append({
                    'Fecha_Venta': pdx['hora'], 'Tipo': pdx['tipo'], 'Estado': pdx['estado'], 'Id_pedido': pdx['id'],
                    'Producto': pr['nombre'], 'Valor': pr['subtotal']
                })
        df_detalle = pd.DataFrame(detalle)
        st.write("### Ventas detalladas por producto")
        st.dataframe(df_detalle)

        resumen = []
        for pdx in pedidos:
            resumen.append({
                'Fecha_Venta': pdx['hora'], 'Tipo': pdx['tipo'], 'Estado': pdx['estado'], 'Id_pedido': pdx['id'],
                'Subtotal': pdx['subtotal'], 'Propina': pdx['propina'], 'Total': pdx['total']
            })
        df_resumen = pd.DataFrame(resumen)
        st.write("### Resumen de ventas por pedido")
        st.dataframe(df_resumen)

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            df_detalle.to_excel(writer, index=False, sheet_name='Detalle')
            df_resumen.to_excel(writer, index=False, sheet_name='Resumen')
        st.download_button("📥 Descargar reportes en Excel", data=buf.getvalue(), file_name="reportes_pedidos.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("No hay pedidos para mostrar.")

# --- Página: Historial ---
elif menu == "📂 Historial":
    st.subheader("📁 Historial de Pedidos Pagados")
    pagados = [p for p in st.session_state.pedidos if p['estado'] == "Pagado"]
    if pagados:
        for p in pagados:
            st.markdown(f"**#{p['id']}** - {p['tipo']}" + (f" - Mesa {p['mesa']}" if p['tipo']=='Mesa' and p['mesa'] else '') + f" - Total: ${p['total']:,.2f}")
            for pr in p['productos']:
                st.markdown(f"- {pr['cantidad']}× {pr['nombre']} ({pr['obs']}) — ${pr['subtotal']:,.2f}")
            st.markdown("---")
    else:
        st.info("No hay pedidos pagados.")

# --- Página: Pantalla Cocina ---
elif menu == "👨‍🍳 Pantalla Cocina":
    st.subheader("👨‍🍳 Pedidos en Cocina")
    en_preparacion = [p for p in st.session_state.pedidos if p['estado'] == "En preparación"]
    if en_preparacion:
        for p in en_preparacion:
            st.markdown(f"### Pedido #{p['id']} - {p['tipo']}" + (f" - Mesa {p['mesa']}" if p['tipo']=='Mesa' and p['mesa'] else ''))
            st.markdown(f"🕒 {p['hora']}")
            for pr in p['productos']:
                st.markdown(f"- {pr['cantidad']}× **{pr['nombre']}** ({pr['obs']})")
            st.markdown(f"**Total:** ${p['total']:,.2f}")
            st.markdown("---")
        if st.button("🖨️ Imprimir Cocina"):
            st.info("Usa Ctrl+P para imprimir esta vista.")
    else:
        st.info("No hay pedidos en preparación.")
