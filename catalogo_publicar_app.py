
import streamlit as st
st.set_page_config(page_title="Catálogo", layout="wide")
import streamlit.components.v1 as components
import pandas as pd
import requests
from zipfile import ZipFile
from io import BytesIO








st.markdown("""
<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap' rel='stylesheet'>
<style>
html, body, [class*='css'] {
    font-family: 'Inter', sans-serif;
    background-color: #f9fafb;
    color: #1f2937;
    font-size: 16px;
}
.titulo {
    font-size: 2.3em;
    font-weight: 800;
    color: #2563eb;
    margin-bottom: 25px;
    text-align: center;
}
.producto-card {
    background: white;
    border-radius: 14px;
    padding: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    text-align: center;
    transition: all 0.2s ease;
    border: 1px solid #e5e7eb;
    margin-bottom: 18px;
}
.producto-card:hover {
    transform: scale(1.02);
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}
.producto-img {
    height: 180px;
    object-fit: contain;
    margin-bottom: 10px;
}
.producto-nombre {
    font-weight: 600;
    font-size: 15px;
    margin-bottom: 8px;
    color: #111827;
}
.boton-ver {
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)



# Estilos modernos



st.markdown('<div class="titulo">📦 Catálogo</div>', unsafe_allow_html=True)
@st.cache_data
def cargar_datos():
    df = pd.read_excel("productos_base.xlsx", sheet_name="Productos")
    df = df[df["Mostrar en catálogo"] == "Sí"]
    df = df.sort_values("ID", ascending=False)
    return df

df = cargar_datos()

# Buscador
busqueda = st.text_input("🔎 Buscar producto por nombre o ID").strip().lower()
if busqueda:
    df = df[df["Nombre del producto"].str.lower().str.contains(busqueda) | df["ID"].str.lower().str.contains(busqueda)]

# Mostrar productos como galería
cols = st.columns(4)
for idx, row in df.iterrows():
    with cols[idx % 4]:
        st.markdown('<div class="producto-card">', unsafe_allow_html=True)
        st.image(row["Imagen principal (URL)"], use_container_width=True, caption=None)
        st.markdown(f"<div class='producto-nombre'>{row['ID']} - {row['Nombre del producto']}</div>", unsafe_allow_html=True)
        if st.button("Ver detalles", key=row["ID"]):
            st.session_state["producto_seleccionado"] = row["ID"]
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
# Vista detallada al hacer clic en "Ver detalles"
producto_id = st.session_state.get("producto_seleccionado")
if producto_id:
    producto = df[df["ID"] == producto_id].iloc[0]

    st.markdown(f"## 🆔 {producto['ID']} - {producto['Nombre del producto']}")

    def render_selectable_text(label, text, key):
        html_code = f"""
        <div style="margin-bottom: 25px;">
            <p style="font-weight: 700; font-size: 1.1em;">{label}</p>
            <textarea id="text_{key}" readonly 
                      style="width:100%; font-size:15px; padding:12px;
                             border:none; border-radius:12px; background-color:#1f2937; 
                             color:#f9fafb; resize: vertical; box-sizing: border-box;
                             box-shadow: inset 0 0 0 1px #374151;">{text}</textarea>
            <div style="margin-top:10px;">
                <button onclick="document.getElementById('text_{key}').select();" 
                        style="background-color:#3b82f6; color:white; border:none; 
                               border-radius:10px; padding:10px 16px; font-weight:600;
                               font-size:14px; cursor:pointer; margin-right:10px;">
                    📋 Seleccionar Todo
                </button>
                <button id="copy-btn-{key}" 
                        style="background-color:#3b82f6; color:white; border:none; 
                               border-radius:10px; padding:10px 16px; font-weight:600;
                               font-size:14px; cursor:pointer;">
                    📎 Copiar
                </button>
            </div>
        </div>
        <script>
        function copyFunction_{key}() {{
            var text = document.getElementById('text_{key}').value;
            navigator.clipboard.writeText(text).then(function() {{
                document.getElementById("copy-btn-{key}").innerText = "✅ Copiado!";
                setTimeout(function() {{
                    document.getElementById("copy-btn-{key}").innerText = "📎 Copiar";
                }}, 1500);
            }});
        }}
        document.getElementById("copy-btn-{key}").onclick = copyFunction_{key};
        </script>
        """
        components.html(html_code, height=260)

    render_selectable_text("✏️ Título", producto["Nombre del producto"], "titulo")
    render_selectable_text("📝 Descripción", producto["Descripción"], "descripcion")
    render_selectable_text("🏷️ Etiquetas", producto["Etiquetas"], "etiquetas")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Facebook:** {producto['Precio Facebook']} CLP")
        st.markdown(f"**Comisión FB:** {producto['Comisión vendedor Facebook']} CLP")
        st.markdown(f"**Ganancia:** {producto['Ganancia Facebook']} CLP")
    with col2:
        st.markdown(f"**Mayor:** {producto['Precio al por mayor de 3 ']}")
        st.markdown(f"**Proveedor:** {producto['Proveedor']}")

    urls = [producto["Imagen principal (URL)"]] + [
        u.strip() for u in str(producto["Imágenes secundarias (URLs separadas por coma)"]).split(",") if u.strip()
    ]
    urls = [u for u in urls if u and not u == producto.get("Foto de proveedor", "")]

    st.markdown("### 🖼️ Imágenes del producto")
    img_cols = st.columns(3 if len(urls) >= 3 else len(urls))
    for idx, url in enumerate(urls):
        with img_cols[idx % len(img_cols)]:
            st.image(url, use_container_width=True)

    if st.button("⬇️ Generar ZIP con todas las imágenes"):
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, "w") as zip_file:
            for i, url in enumerate(urls):
                try:
                    img_data = requests.get(url).content
                    zip_file.writestr(f"imagen_{i+1}.jpg", img_data)
                except:
                    continue
        st.download_button("💾 Descargar ZIP", data=zip_buffer.getvalue(), file_name=f"{producto['ID']}_imagenes.zip", mime="application/zip")
