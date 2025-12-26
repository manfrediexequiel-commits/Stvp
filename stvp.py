import streamlit as st
import pandas as pd
import requests
from io import StringIO
import os
import base64
import urllib.parse
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="SINDICATO STVP - Credencial Digital", 
    page_icon="🛡️", 
    layout="centered"
)

# --- ESTILOS PERSONALIZADOS (CSS MEJORADO) ---
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
    }
    
    /* Botones de menú */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.2em;
        background-color: #2563eb;
        color: white;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    /* Credencial con Efectos (Mejora 2) */
    .credential-card {
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 20px;
        color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
        user-select: none;
        transition: all 0.4s ease;
    }
    .credential-card:hover {
        box-shadow: 0 15px 35px rgba(59, 130, 246, 0.3);
        transform: scale(1.01);
    }

    .watermark {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-15deg);
        width: 180px;
        opacity: 0.12;
        pointer-events: none;
        z-index: 0;
    }

    /* Botón Cerrar Sesión Rojo (Mejora 4) */
    .logout-btn > div > button {
        background-color: #ef4444 !important;
        margin-top: 20px;
    }
    .logout-btn > div > button:hover {
        background-color: #dc2626 !important;
    }

    .family-card {
        background-color: #1e293b;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #3b82f6;
    }

    .benefit-item {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid rgba(59, 130, 246, 0.2);
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

def mostrar_logo_cabecera():
    b64 = get_image_base64("logo_stvp")
    if b64:
        st.image(b64, width=120)
    else:
        st.markdown('<div style="text-align:center"><h2 style="color:#2563eb">STVP</h2></div>', unsafe_allow_html=True)

# --- CARGA DE DATOS NORMALIZADA (Mejora 1) ---
URL_SOCIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=0&single=true&output=csv"
URL_FAMILIA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=1889067091&single=true&output=csv"

@st.cache_data(ttl=600)
def cargar_datos():
    try:
        res_s = requests.get(URL_SOCIOS)
        res_f = requests.get(URL_FAMILIA)
        df_s = pd.read_csv(StringIO(res_s.text))
        df_f = pd.read_csv(StringIO(res_f.text))
        
        # Limpieza de columnas
        df_s.columns = df_s.columns.str.strip().str.lower()
        df_f.columns = df_f.columns.str.strip().str.lower()
        
        # Normalización de DNIs: Eliminar .0 y espacios
        for df in [df_s, df_f]:
            col_dni = 'dni' if 'dni' in df.columns else 'dni_titular'
            if col_dni in df.columns:
                df[col_dni] = df[col_dni].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        return df_s, df_f
    except:
        return pd.DataFrame(), pd.DataFrame()

# --- LÓGICA DE LA APP ---
db_socios, db_familia = cargar_datos()

if "dni_activo" not in st.session_state:
    st.session_state["dni_activo"] = None
if "seccion" not in st.session_state:
    st.session_state["seccion"] = "credencial"

# Cabecera
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mostrar_logo_cabecera()

if st.session_state["dni_activo"] is None:
    st.markdown("<h1 style='text-align: center; color: white;'>STVP Digital</h1>", unsafe_allow_html=True)
    st.markdown("### Acceso Afiliados")
    dni_input = st.text_input("Ingrese su DNI (sin puntos):")
    
    if st.button("Validar"):
        # Normalizar la entrada del usuario para comparar
        dni_clean = str(dni_input).replace(".", "").replace(" ", "").strip()
        if not db_socios.empty and dni_clean in db_socios['dni'].values:
            st.session_state["dni_activo"] = dni_clean
            st.rerun()
        else:
            st.error("DNI no encontrado o error de conexión.")
else:
    # Datos del socio
    socio = db_socios[db_socios['dni'] == st.session_state["dni_activo"]].iloc[0]
    
    # Menú de Navegación
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        if st.button("🪪 Inicio"): st.session_state["seccion"] = "credencial"; st.rerun()
    with m2:
        if st.button("📣 Gremial"): st.session_state["seccion"] = "gremial"; st.rerun()
    with m3:
        if st.button("⚖️ Legal"): st.session_state["seccion"] = "legal"; st.rerun()
    with m4:
        if st.button("🎁 Benef."): st.session_state["seccion"] = "beneficios"; st.rerun()

    st.markdown("---")

    # SECCIONES
    if st.session_state["seccion"] == "credencial":
        cargo_raw = str(socio.get('cargo', 'AFILIADO')).upper()
        
        # Lógica de colores (Mejora 2)
        if any(x in cargo_raw for x in ["COMISIÓN", "DIRECTIVA", "SECRETARIO"]):
            bg_color = "linear-gradient(135deg, #854d0e 0%, #422006 100%)"
            border_color = "#fbbf24"
            label_text = "COMISIÓN DIRECTIVA"
        elif "DELEGADO" in cargo_raw:
            bg_color = "linear-gradient(135deg, #064e3b 0%, #022c22 100%)"
            border_color = "#4ade80"
            label_text = "DELEGADO"
        else:
            bg_color = "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)"
            border_color = "#3b82f6"
            label_text = "AFILIADO"

        logo_b64 = get_image_base64("logo_stvp")
        watermark_html = f'<img src="{logo_b64}" class="watermark">' if logo_b64 else ''

        st.markdown(f"""
            <div class="credential-card" style="background: {bg_color}; border: 2px solid {border_color};">
                {watermark_html}
                <div class="card-content">
                    <p style="text-align: left; font-size: 0.7em; letter-spacing: 2px; opacity: 0.7; margin: 0;">SINDICATO STVP</p>
                    <div style="height: 30px;"></div>
                    <h2 style="margin: 0; font-size: 1.8em; text-transform: uppercase;">{socio['nombre']}</h2>
                    <div style="background: rgba(0,0,0,0.4); padding: 5px 15px; border-radius: 50px; display: inline-block; margin-top: 15px; color: {border_color}; font-weight: bold; border: 1px solid {border_color};">
                        {label_text}
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 40px; font-size: 0.9em;">
                        <div style="text-align: left;">DNI<br><b>{socio['dni']}</b></div>
                        <div style="text-align: right;">ESTADO<br><b style="color: #4ade80;">ACTIVO</b></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Familiares
        fams = db_familia[db_familia['dni_titular'] == st.session_state["dni_activo"]]
        if not fams.empty:
            st.subheader("👨‍👩‍👧‍👦 Grupo Familiar")
            for _, f in fams.iterrows():
                st.markdown(f"""
                    <div class="family-card">
                        <div style="font-weight: bold; color: white;">{f['nombre']}</div>
                        <div style="font-size: 0.8em; color: #94a3b8;">{f.get('parentesco', 'Familiar')} • DNI: {f.get('dni_familiar', 'N/A')}</div>
                    </div>
                """, unsafe_allow_html=True)

    elif st.session_state["seccion"] in ["gremial", "legal"]:
        st.subheader("Consultas")
        st.info("Su mensaje será enviado a un secretario.")
        detalle = st.text_area("Escriba su consulta:")
        if st.button("Enviar WhatsApp"):
            mensaje = f"Hola, soy {socio['nombre']} (DNI {socio['dni']}). Consulta: {detalle}"
            url_wa = f"https://wa.me/5491156424903?text={urllib.parse.quote(mensaje)}"
            st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; padding:15px; border-radius:12px; text-align:center; font-weight:bold;">📲 Abrir WhatsApp</div></a>', unsafe_allow_html=True)

    # Mejora 4: Botón de cierre de sesión visible al final
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("❌ Cerrar Sesión"):
        st.session_state["dni_activo"] = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar Admin
with st.sidebar:
    st.title("Administración")
    if st.checkbox("Acceso Admin"):
        if st.text_input("Clave", type="password") == "stvp2025":
            if st.button("Forzar Sincronización"):
                st.cache_data.clear()
                st.success("Datos actualizados.")
