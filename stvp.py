import streamlit as st
import pandas as pd
import requests
from io import StringIO
import base64
import urllib.parse
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Credencial Digital STVP", page_icon="🛡️", layout="centered")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.2em;
        background-color: #2563eb; color: white; font-weight: bold; border: none;
    }
    .nav-button>button { background-color: #1e293b; border: 1px solid #3b82f6; }
    .credential-card {
        border-radius: 20px; padding: 25px; margin-bottom: 20px; color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1);
        position: relative; overflow: hidden; min-height: 250px;
    }
    .profile-img {
        width: 110px; height: 110px; border-radius: 50%; object-fit: cover;
        border: 3px solid white; margin-bottom: 10px; background-color: #334155;
    }
    .benefit-card {
        background-color: #1e293b; border-radius: 15px; padding: 20px;
        margin-bottom: 15px; border: 1px solid rgba(59, 130, 246, 0.3); text-align: center;
    }
    .family-card {
        background-color: #1e293b; border-radius: 15px; padding: 15px;
        margin-bottom: 10px; border-left: 5px solid #3b82f6; display: flex; align-items: center; gap: 15px;
    }
    .family-img {
        width: 45px; height: 45px; border-radius: 50%; object-fit: cover;
    }
    </style>
""", unsafe_allow_html=True)

# --- UTILIDADES PARA DATOS Y GOOGLE DRIVE ---

def fix_drive_url(url):
    """Convierte enlaces de Google Drive en enlaces directos de imagen."""
    if not isinstance(url, str) or "drive.google.com" not in url:
        return url
    file_id = ""
    if "/d/" in url:
        file_id = url.split("/d/")[1].split("/")[0]
    elif "id=" in url:
        file_id = url.split("id=")[1].split("&")[0]
    return f"https://lh3.googleusercontent.com/u/0/d/{file_id}" if file_id else url

# --- CARGA DE DATOS DESDE HOJAS DE CÁLCULO ---
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

# --- LÓGICA DE NAVEGACIÓN ---
if "dni_activo" not in st.session_state: st.session_state["dni_activo"] = None
if "pantalla" not in st.session_state: st.session_state["pantalla"] = "inicio"

db_socios, db_familia = cargar_datos_reales()

def get_style(cargo):
    c = str(cargo).upper()
    if "COMISIÓN" in c or "DIRECTIVA" in c: 
        return "linear-gradient(135deg, #854d0e 0%, #422006 100%)", "#fbbf24"
    if "DELEGADO" in c:
        return "linear-gradient(135deg, #065f46 0%, #064e3b 100%)", "#6ee7b7"
    return "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)", "#3b82f6"

# --- RENDERIZADO ---
st.markdown("<h1 style='text-align:center; color:#2563eb;'>STVP DIGITAL</h1>", unsafe_allow_html=True)

if st.session_state["dni_activo"] is None:
    st.markdown("### Acceso al Padrón")
    dni_in = st.text_input("Ingrese su DNI (sin puntos):", placeholder="Ej: 12345678")
    if st.button("Ingresar"):
        if dni_in:
            # Buscar en el DataFrame cargado de Google Sheets
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
        foto_url = fix_drive_url(socio.get('foto', ''))
        foto_html = f'<img src="{foto_url}" class="profile-img">' if foto_url else '<div style="height:20px"></div>'
        
        st.markdown(f"""
            <div class="credential-card" style="background: {bg}; border: 2px solid {brd};">
                <div style="text-align: center;">
                    {foto_html}
                    <h2 style="margin:0; text-transform: uppercase;">{socio['nombre']}</h2>
                    <div style="background: rgba(0,0,0,0.3); display: inline-block; padding: 2px 10px; border-radius: 10px; border: 1px solid {brd}; color: {brd}; font-size: 0.8em; font-weight: bold; margin-top: 5px;">
                        {socio.get('cargo', socio.get('miembro', 'AFILIADO'))}
                    </div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:20px; font-size:0.8em;">
                    <div>DNI<br><b>{socio['dni']}</b></div>
                    <div style="text-align:right;">ESTADO<br><b style="color:#4ade80;">ACTIVO</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Cargar Familiares relacionados
        fams = db_familia[db_familia['dni_titular'].astype(str) == str(st.session_state["dni_activo"])]
        if not fams.empty:
            st.subheader("👨‍👩‍👧‍👦 Grupo Familiar")
            for _, f in fams.iterrows():
                f_img = fix_drive_url(f.get('foto', ''))
                f_tag = f'<img src="{f_img}" class="family-img">' if f_img else '<div style="font-size:1.5em;">👤</div>'
                st.markdown(f"""
                    <div class="family-card">
                        {f_tag}
                        <div>
                            <b>{f["nombre"]}</b><br>
                            <small>{f.get('parentesco', 'Familiar')} • DNI: {f.get('dni_familiar', 'N/A')}</small>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    elif st.session_state["pantalla"] in ["gremial", "legal"]:
        tipo = "GREMIAL" if st.session_state["pantalla"] == "gremial" else "LEGAL"
        st.subheader(f"Consulta {tipo}")
        msg = st.text_area("Describa su consulta:")
        if st.button("Preparar WhatsApp"):
            t_url = urllib.parse.quote(f"*{tipo} STVP*\nSocio: {socio['nombre']}\nDNI: {socio['dni']}\n\nConsulta: {msg}")
            # Números configurados anteriormente
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
    if st.button("Cerrar Sesión"):
        st.session_state["dni_activo"] = None
        st.rerun()
