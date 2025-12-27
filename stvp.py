import streamlit as st
import pandas as pd
import requests
from io import StringIO
import os
import base64
import urllib.parse
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="SINDICATO STVP - Credencial Digital", 
    page_icon="🛡️", 
    layout="centered"
)

# --- ESTILOS PERSONALIZADOS (CSS CONSOLIDADO) ---
st.markdown("""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
    .main { background-color: #0f172a; }
    
    /* Botones de menú */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.2em;
        background-color: #2563eb; color: white; font-weight: bold; border: none;
    }

    /* Foto Circular */
    .photo-container {
        width: 90px; height: 90px; border-radius: 50%;
        border: 3px solid rgba(255,255,255,0.8); overflow: hidden;
        margin-right: 15px; background-color: #334155; flex-shrink: 0;
    }
    .photo-container img { width: 100%; height: 100%; object-fit: cover; }

    /* Credencial */
    .credential-card {
        border-radius: 20px; padding: 25px; margin-bottom: 20px;
        color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        position: relative; overflow: hidden; display: flex; flex-direction: column;
        user-select: none;
    }
    .card-header { display: flex; align-items: center; text-align: left; margin-top: 10px; position: relative; z-index: 10; }

    /* Botón Descarga */
    .download-btn {
        background: #059669; color: white; padding: 12px; border-radius: 12px;
        text-align: center; font-weight: bold; cursor: pointer; margin-bottom: 20px;
        border: none; width: 100%; display: block;
    }

    /* Familiares Mejorados */
    .family-card {
        background-color: #ffffff; border-radius: 12px; padding: 15px;
        margin-bottom: 12px; border-left: 8px solid #3b82f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .family-name { color: #1e293b; font-weight: 800; text-transform: uppercase; }
    .family-tag {
        display: inline-block; background-color: #dbeafe; color: #1e40af;
        padding: 2px 8px; border-radius: 6px; font-size: 0.75em; font-weight: bold; margin-top: 5px;
    }

    /* Beneficios */
    .benefit-item {
        background-color: #1e293b; border-radius: 12px; padding: 15px;
        margin-bottom: 10px; border: 1px solid rgba(59, 130, 246, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- UTILIDADES ---
def get_image_base64(path_no_ext):
    posibles_ext = ['png', 'jpg', 'jpeg', 'webp']
    for ext in posibles_ext:
        full_path = f"{path_no_ext}.{ext}"
        if os.path.exists(full_path):
            with open(full_path, "rb") as img_file:
                return f"data:image/{ext};base64," + base64.b64encode(img_file.read()).decode()
    return None

# --- CARGA DE DATOS NORMALIZADA ---
@st.cache_data(ttl=300)
def cargar_datos():
    URL_SOCIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=0&single=true&output=csv"
    URL_FAMILIA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=1889067091&single=true&output=csv"
    try:
        df_s = pd.read_csv(StringIO(requests.get(URL_SOCIOS).text))
        df_f = pd.read_csv(StringIO(requests.get(URL_FAMILIA).text))
        df_s.columns = df_s.columns.str.strip().str.lower()
        df_f.columns = df_f.columns.str.strip().str.lower()
        # Normalizar DNI
        for df in [df_s, df_f]:
            col = 'dni' if 'dni' in df.columns else 'dni_titular'
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return df_s, df_f
    except: return pd.DataFrame(), pd.DataFrame()

db_socios, db_familia = cargar_datos()

# --- ESTADO DE SESIÓN ---
if "dni_activo" not in st.session_state: st.session_state["dni_activo"] = None
if "seccion" not in st.session_state: st.session_state["seccion"] = "credencial"

# --- LOGIN ---
if st.session_state["dni_activo"] is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_b64 = get_image_base64("logo_stvp")
        if logo_b64: st.image(logo_b64, width=120)
    st.markdown("<h1 style='text-align: center; color: white;'>STVP Digital</h1>", unsafe_allow_html=True)
    dni_input = st.text_input("Ingrese su DNI:")
    if st.button("Ingresar"):
        dni_clean = str(dni_input).replace(".", "").replace(" ", "").strip()
        if not db_socios.empty and dni_clean in db_socios['dni'].values:
            st.session_state["dni_activo"] = dni_clean
            st.rerun()
        else: st.error("DNI no encontrado.")

# --- APP PRINCIPAL ---
else:
    socio = db_socios[db_socios['dni'] == st.session_state["dni_activo"]].iloc[0]
    cargo_str = str(socio.get('cargo', 'AFILIADO')).upper()
    
    # Menú Navegación
    m1, m2, m3, m4 = st.columns(4)
    with m1: 
        if st.button("🪪"): st.session_state["seccion"] = "credencial"
    with m2: 
        if st.button("📣"): st.session_state["seccion"] = "gremial"
    with m3: 
        if st.button("⚖️"): st.session_state["seccion"] = "legal"
    with m4: 
        if st.button("🎁"): st.session_state["seccion"] = "beneficios"

    st.markdown("---")

    # SECCIÓN 1: CREDENCIAL
    if st.session_state["seccion"] == "credencial":
        # Colores por jerarquía
        if any(x in cargo_str for x in ["COMISIÓN", "DIRECTIVA"]):
            bg, border, label = "linear-gradient(135deg, #854d0e 0%, #422006 100%)", "#fbbf24", "COMISIÓN DIRECTIVA"
        elif "DELEGADO" in cargo_str:
            bg, border, label = "linear-gradient(135deg, #064e3b 0%, #022c22 100%)", "#4ade80", "DELEGADO"
        else:
            bg, border, label = "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)", "#3b82f6", "AFILIADO"

        url_foto = socio.get('foto', 'https://www.w3schools.com/howto/img_avatar.png')
        if pd.isna(url_foto) or str(url_foto).strip() == "": url_foto = "https://www.w3schools.com/howto/img_avatar.png"

        st.markdown(f"""
            <div id="digital-credential" class="credential-card" style="background: {bg}; border: 2px solid {border};">
                <p style="font-size: 0.6em; letter-spacing: 2px; opacity: 0.7; margin: 0;">SINDICATO STVP</p>
                <div class="card-header">
                    <div class="photo-container"><img src="{url_foto}"></div>
                    <div>
                        <h2 style="margin: 0; font-size: 1.4em; line-height: 1.1;">{socio['nombre']}</h2>
                        <div style="background: rgba(0,0,0,0.4); padding: 2px 10px; border-radius: 50px; color: {border}; font-weight: bold; font-size: 0.7em; border: 1px solid {border}; margin-top: 5px;">{label}</div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 25px; font-size: 0.85em;">
                    <div>DNI<br><b>{socio['dni']}</b></div>
                    <div style="text-align: right;">ESTADO<br><b style="color: #4ade80;">ACTIVO</b></div>
                </div>
            </div>
            <button class="download-btn" onclick="downloadCredential()">⬇️ GUARDAR CREDENCIAL EN CELULAR</button>
            <script>
            function downloadCredential() {{
                const element = document.getElementById('digital-credential');
                html2canvas(element, {{ scale: 3, backgroundColor: null }}).then(canvas => {{
                    const link = document.createElement('a');
                    link.download = 'Credencial_STVP_{socio['dni']}.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                }});
            }}
            </script>
        """, unsafe_allow_html=True)

        # Familiares
        fams = db_familia[db_familia['dni_titular'] == st.session_state["dni_activo"]]
        if not fams.empty:
            st.markdown("<h3 style='color: white;'>👨‍👩‍👧‍👦 Grupo Familiar</h3>", unsafe_allow_html=True)
            for _, f in fams.iterrows():
                st.markdown(f"""
                    <div class="family-card">
                        <div class="family-name">{f['nombre']}</div>
                        <div style="color: #475569; font-size: 0.9em;">DNI: {f.get('dni_familiar', 'N/A')}</div>
                        <div class="family-tag">{str(f.get('parentesco', 'Familiar')).upper()}</div>
                    </div>
                """, unsafe_allow_html=True)

    # SECCIÓN 2 Y 3: CONSULTAS
    elif st.session_state["seccion"] in ["gremial", "legal"]:
        titulo = "Gremial" if st.session_state["seccion"] == "gremial" else "Legal"
        st.subheader(f"Consulta {titulo}")
        detalle = st.text_area("Describa su inquietud:")
        if st.button("Enviar por WhatsApp"):
            mensaje = f"Hola STVP, soy {socio['nombre']} (DNI {socio['dni']}). Consulta {titulo}: {detalle}"
            url_wa = f"https://wa.me/5491156424903?text={urllib.parse.quote(mensaje)}"
            st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; padding:15px; border-radius:12px; text-align:center; font-weight:bold;">📲 Abrir WhatsApp</div></a>', unsafe_allow_html=True)

    # SECCIÓN 4: BENEFICIOS
    elif st.session_state["seccion"] == "beneficios":
        st.subheader("Beneficios")
        items = [
            ("🏨 Turismo", "Hotelería y convenios.", "https://whatsapp.com/channel/0029VbAua9BJENy8oScpAH2B"),
            ("📚 Útiles Escolares", "Kits anuales.", None),
            ("👶 Nacimiento", "Ajuar para el bebé.", None)
        ]
        for t, d, link in items:
            with st.container():
                st.markdown(f"""<div class="benefit-item"><b style="color:#3b82f6;">{t}</b><br><small style="color:#94a3b8;">{d}</small></div>""", unsafe_allow_html=True)
                if link: st.link_button("Ver más", link)

    # PANEL DE DELEGADOS (GESTIÓN DE FOTOS)
    if any(x in cargo_str for x in ["DELEGADO", "COMISIÓN", "DIRECTIVA"]):
        st.markdown("---")
        with st.expander("📸 Gestión de Fotos (Solo Delegados)"):
            archivo = st.file_uploader("Subir nueva foto de afiliado", type=['jpg', 'png'])
            if archivo:
                st.image(archivo, width=100)
                if st.button("Enviar para actualización"):
                    msg = f"Delegado {socio['nombre']} solicita actualizar foto de DNI {socio['dni']}"
                    st.markdown(f'<a href="https://wa.me/5491156424903?text={urllib.parse.quote(msg)}" target="_blank">📲 Notificar por WhatsApp</a>', unsafe_allow_html=True)

    # CERRAR SESIÓN
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("❌ Cerrar Sesión"):
        st.session_state["dni_activo"] = None
        st.rerun()

    # SIDEBAR ADMIN
    with st.sidebar:
        if st.checkbox("Modo Admin") and st.text_input("Clave", type="password") == "stvp2025":
            if st.button("Actualizar Base de Datos"):
                st.cache_data.clear()
                st.success("Sincronizado!")
