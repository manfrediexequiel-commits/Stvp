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

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #2563eb;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        border: none;
        color: white;
    }
    .nav-button>button { 
        background-color: #1e293b; 
        border: 1px solid #3b82f6; 
    }
    .credential-card {
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
        min-height: 250px;
    }
    /* Estilo para el logo de fondo (Marca de agua) */
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
    .card-content {
        position: relative;
        z-index: 10;
    }
    .profile-img {
        width: 110px;
        height: 110px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        margin-bottom: 10px;
        background-color: #1e293b;
    }
    .benefit-card {
        background-color: #1e293b; 
        border-radius: 15px; 
        padding: 20px;
        margin-bottom: 15px; 
        border: 1px solid rgba(59, 130, 246, 0.3); 
        text-align: center;
    }
    .family-card {
        background-color: #1e293b;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #3b82f6;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .family-img {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid rgba(255,255,255,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- UTILIDADES PARA IMÁGENES Y DATOS ---

def format_drive_url(url):
    """Convierte enlaces de Google Drive en enlaces directos de imagen."""
    if not isinstance(url, str):
        return url
    drive_match = re.search(r"(?:https?://)?(?:drive\.google\.com/(?:file/d/|open\?id=)|googledrive\.com/host/)([\w-]+)", url)
    if drive_match:
        file_id = drive_match.group(1)
        return f"https://lh3.googleusercontent.com/u/0/d/{file_id}"
    return url

def get_image_base64(path_no_ext):
    """Convierte una imagen local a Base64 para usar en HTML/CSS."""
    posibles_ext = ['png', 'jpg', 'jpeg', 'webp']
    for ext in posibles_ext:
        full_path = f"{path_no_ext}.{ext}"
        if os.path.exists(full_path):
            with open(full_path, "rb") as img_file:
                return f"data:image/{ext};base64," + base64.b64encode(img_file.read()).decode()
    return None

def mostrar_logo_cabecera():
    """Muestra el logo del sindicato arriba del login."""
    b64 = get_image_base64("logo_stvp")
    if b64:
        st.image(b64, width=120)
    else:
        st.markdown('<div style="text-align:center"><h2 style="color:#2563eb">STVP</h2></div>', unsafe_allow_html=True)

# --- CONFIGURACIÓN DE DATOS (Google Sheets) ---
URL_SOCIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=0&single=true&output=csv"
URL_FAMILIA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=1889067091&single=true&output=csv"

@st.cache_data(ttl=600)
def cargar_datos_reales():
    try:
        res_s = requests.get(URL_SOCIOS)
        res_f = requests.get(URL_FAMILIA)
        df_s = pd.read_csv(StringIO(res_s.text))
        df_f = pd.read_csv(StringIO(res_f.text))
        # Normalizar nombres de columnas a minúsculas
        df_s.columns = df_s.columns.str.strip().str.lower()
        df_f.columns = df_f.columns.str.strip().str.lower()
        return df_s, df_f
    except Exception as e:
        st.error(f"Error conectando con la base de datos: {e}")
        return pd.DataFrame(), pd.DataFrame()

def get_style(cargo):
    c = str(cargo).upper()
    if "COMISIÓN" in c or "DIRECTIVA" in c: 
        return "linear-gradient(135deg, #854d0e 0%, #422006 100%)", "#fbbf24"
    if "DELEGADO" in c:
        return "linear-gradient(135deg, #065f46 0%, #064e3b 100%)", "#6ee7b7"
    return "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)", "#3b82f6"

# --- LÓGICA DE NAVEGACIÓN Y ESTADO ---
if "dni_activo" not in st.session_state: st.session_state["dni_activo"] = None
if "pantalla" not in st.session_state: st.session_state["pantalla"] = "inicio"

db_socios, db_familia = cargar_datos_reales()

# --- RENDERIZADO ---

# Encabezado Principal
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mostrar_logo_cabecera()

st.markdown("<h1 style='text-align: center; color: white; margin-top: -10px;'>STVP Digital</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Sindicato de Trabajadores de Vigilancia Privada</p>", unsafe_allow_html=True)

if st.session_state["dni_activo"] is None:
    # --- VISTA DE LOGIN ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Acceso al Portal")
    dni_in = st.text_input("Ingrese su DNI (sin puntos):", placeholder="Ej: 12345678")
    if st.button("Consultar Padrón"):
        if dni_in:
            socio_encontrado = db_socios[db_socios['dni'].astype(str) == str(dni_in)]
            if not socio_encontrado.empty:
                st.session_state["dni_activo"] = str(dni_in)
                st.rerun()
            else:
                st.error("DNI no encontrado en el padrón actual.")
        else:
            st.warning("Por favor ingrese su documento.")

else:
    # Menú Superior
    st.markdown('<div class="nav-button">', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1: 
        if st.button("🪪 Credencial"): st.session_state["pantalla"] = "inicio"; st.rerun()
    with m2: 
        if st.button("📣 Gremial"): st.session_state["pantalla"] = "gremial"; st.rerun()
    with m3: 
        if st.button("⚖️ Legal"): st.session_state["pantalla"] = "legal"; st.rerun()
    with m4: 
        if st.button("🎁 Beneficios"): st.session_state["pantalla"] = "bonos"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    socio = db_socios[db_socios['dni'].astype(str) == st.session_state["dni_activo"]].iloc[0]

    if st.session_state["pantalla"] == "inicio":
        bg, brd = get_style(socio.get('cargo', socio.get('miembro', 'Afiliado')))
        logo_b64 = get_image_base64("logo_stvp")
        watermark_html = f'<img src="{logo_b64}" class="watermark">' if logo_b64 else ''
        
        foto_url = format_drive_url(socio.get('foto', ''))
        foto_html = f'<img src="{foto_url}" class="profile-img">' if foto_url else '<div style="height:20px"></div>'
        
        st.markdown(f"""
            <div class="credential-card" style="background: {bg}; border: 2px solid {brd};">
                {watermark_html}
                <div class="card-content">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div style="font-size: 0.7em; font-weight: bold; letter-spacing: 2px; opacity: 0.8;">SINDICATO STVP</div>
                        <div style="font-size: 0.6em; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 5px;">VIGENTE 2025</div>
                    </div>
                    
                    <div style="text-align: center; margin: 15px 0;">
                        {foto_html}
                        <h2 style="margin: 5px 0 0 0; font-size: 1.6em; text-transform: uppercase; color: white; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);">{socio['nombre']}</h2>
                        <div style="margin-top: 5px; display: inline-block; background: rgba(0,0,0,0.5); padding: 4px 12px; border-radius: 50px; font-size: 0.75em; font-weight: bold; color: {brd}; border: 1px solid {brd};">
                            {socio.get('cargo', socio.get('miembro', 'AFILIADO'))}
                        </div>
                    </div>

                    <div style="display: flex; justify-content: space-between; font-size: 0.8em; opacity: 0.9; margin-top: 10px;">
                        <div>
                            <div style="font-size: 0.7em; opacity: 0.6;">DOCUMENTO</div>
                            <div style="font-weight: bold;">{socio['dni']}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 0.7em; opacity: 0.6;">ESTADO</div>
                            <div style="font-weight: bold; color: #4ade80;">ACTIVO</div>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Cargar Familiares relacionados
        fams = db_familia[db_familia['dni_titular'].astype(str) == str(st.session_state["dni_activo"])]
        if not fams.empty:
            st.subheader("👨‍👩‍👧‍👦 Grupo Familiar")
            for _, f in fams.iterrows():
                f_img = format_drive_url(f.get('foto', ''))
                f_tag = f'<img src="{f_img}" class="family-img">' if pd.notna(f_img) else '<div class="family-img" style="background:#475569; display:flex; align-items:center; justify-content:center;">👤</div>'
                st.markdown(f"""
                    <div class="family-card">
                        {f_tag}
                        <div>
                            <div style="font-weight: bold; font-size: 0.9em; color: white;">{f["nombre"]}</div>
                            <div style="font-size: 0.8em; color: #94a3b8;">{f.get('parentesco', 'Familiar')} • DNI: {f.get('dni_familiar', 'N/A')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No se encuentran familiares vinculados en el padrón actual.")

    elif st.session_state["pantalla"] in ["gremial", "legal"]:
        tipo = "GREMIAL" if st.session_state["pantalla"] == "gremial" else "LEGAL"
        st.subheader(f"Consulta {tipo}")
        msg = st.text_area("Describa su consulta:")
        if st.button("Preparar WhatsApp"):
            t_url = urllib.parse.quote(f"*{tipo} STVP*\nSocio: {socio['nombre']}\nDNI: {socio['dni']}\n\nConsulta: {msg}")
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <a href="https://wa.me/5491156424903?text={t_url}" target="_blank" style="text-decoration:none; background:#25D366; color:white; padding:12px; border-radius:10px; text-align:center; font-weight:bold;">📲 Enviar a Representante 1</a>
                    <a href="https://wa.me/5491161080024?text={t_url}" target="_blank" style="text-decoration:none; background:#25D366; color:white; padding:12px; border-radius:10px; text-align:center; font-weight:bold;">📲 Enviar a Representante 2</a>
                </div>
            """, unsafe_allow_html=True)

    elif st.session_state["pantalla"] == "bonos":
        st.subheader("🎁 Beneficios")
        beneficios = [
            ("🏨", "Turismo", "Convenios en Hoteles de todo el país."),
            ("💊", "Salud", "Descuentos en farmacias adheridas."),
            ("📚", "Educación", "Kits de útiles escolares anuales."),
            ("🏊", "Recreación", "Acceso a predios y campings.")
        ]
        for icon, title, desc in beneficios:
            st.markdown(f'<div class="benefit-card"><div style="font-size:2em;">{icon}</div><b>{title}</b><br><small>{desc}</small></div>', unsafe_allow_html=True)

    st.write("---")
    if st.button("❌ Cerrar Sesión"):
        st.session_state["dni_activo"] = None
        st.rerun()

# --- BARRA LATERAL (ADMIN) ---
with st.sidebar:
    st.markdown("### ⚙️ Panel de Control")
    if st.checkbox("Acceso Administrador"):
        pwd = st.text_input("Contraseña:", type="password")
        if pwd == "stvp2025":
            st.success("Acceso Concedido")
            if st.button("🔄 Sincronizar con Google Sheets"):
                st.cache_data.clear()
                st.success("Padrón actualizado correctamente")
                st.rerun()
            
            st.metric("Total Afiliados", len(db_socios))
            st.metric("Total Familiares", len(db_familia))
