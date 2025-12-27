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

# --- ESTILOS PERSONALIZADOS (CSS MEJORADO PARA VISIBILIDAD) ---
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.2em;
        background-color: #2563eb;
        color: white;
        font-weight: bold;
        border: none;
    }

    /* Credencial Principal */
    .credential-card {
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
        color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        position: relative;
        overflow: hidden;
        user-select: none;
    }

    .watermark {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-15deg);
        width: 180px;
        opacity: 0.12;
        z-index: 0;
    }

    /* TARJETAS DE FAMILIARES (MÁS VISIBLES) */
    .family-container {
        margin-top: 20px;
    }

    .family-card {
        background-color: #ffffff; /* Fondo blanco para máximo contraste */
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        border-left: 8px solid #3b82f6; /* Borde lateral grueso azul */
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
    }

    .family-name {
        color: #1e293b; /* Azul muy oscuro casi negro */
        font-size: 1.1em;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    .family-info {
        color: #475569; /* Gris oscuro para legibilidad */
        font-size: 0.9em;
        font-weight: 600;
    }

    .family-tag {
        display: inline-block;
        background-color: #dbeafe;
        color: #1e40af;
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 0.75em;
        font-weight: bold;
        margin-top: 8px;
        width: fit-content;
    }

    .logout-btn > div > button {
        background-color: #ef4444 !important;
        margin-top: 20px;
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

# --- CARGA DE DATOS ---
URL_SOCIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=0&single=true&output=csv"
URL_FAMILIA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=1889067091&single=true&output=csv"

@st.cache_data(ttl=600)
def cargar_datos():
    try:
        res_s = requests.get(URL_SOCIOS)
        res_f = requests.get(URL_FAMILIA)
        df_s = pd.read_csv(StringIO(res_s.text))
        df_f = pd.read_csv(StringIO(res_f.text))
        df_s.columns = df_s.columns.str.strip().str.lower()
        df_f.columns = df_f.columns.str.strip().str.lower()
        
        # Mejora 1: Normalización de DNIs
        for df in [df_s, df_f]:
            col = 'dni' if 'dni' in df.columns else 'dni_titular'
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return df_s, df_f
    except:
        return pd.DataFrame(), pd.DataFrame()

db_socios, db_familia = cargar_datos()

if "dni_activo" not in st.session_state:
    st.session_state["dni_activo"] = None
if "seccion" not in st.session_state:
    st.session_state["seccion"] = "credencial"

# UI Cabecera
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mostrar_logo_cabecera()

if st.session_state["dni_activo"] is None:
    st.markdown("<h1 style='text-align: center; color: white;'>STVP Digital</h1>", unsafe_allow_html=True)
    dni_input = st.text_input("Ingrese su DNI:")
    if st.button("Ingresar"):
        dni_clean = str(dni_input).replace(".", "").strip()
        if not db_socios.empty and dni_clean in db_socios['dni'].values:
            st.session_state["dni_activo"] = dni_clean
            st.rerun()
        else:
            st.error("DNI no registrado.")
else:
    socio = db_socios[db_socios['dni'] == st.session_state["dni_activo"]].iloc[0]
    
    # Navegación
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        if st.button("🪪"): st.session_state["seccion"] = "credencial"; st.rerun()
    with m2:
        if st.button("📣"): st.session_state["seccion"] = "gremial"; st.rerun()
    with m3:
        if st.button("⚖️"): st.session_state["seccion"] = "legal"; st.rerun()
    with m4:
        if st.button("🎁"): st.session_state["seccion"] = "beneficios"; st.rerun()

    st.markdown("---")

    if st.session_state["seccion"] == "credencial":
        # Lógica de Colores de Credencial
        cargo = str(socio.get('cargo', 'AFILIADO')).upper()
        if any(x in cargo for x in ["COMISIÓN", "DIRECTIVA", "SECRETARIO"]):
            bg, border, label = "linear-gradient(135deg, #854d0e 0%, #422006 100%)", "#fbbf24", "COMISIÓN DIRECTIVA"
        elif "DELEGADO" in cargo:
            bg, border, label = "linear-gradient(135deg, #064e3b 0%, #022c22 100%)", "#4ade80", "DELEGADO"
        else:
            bg, border, label = "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)", "#3b82f6", "AFILIADO"

        logo_b64 = get_image_base64("logo_stvp")
        watermark = f'<img src="{logo_b64}" class="watermark">' if logo_b64 else ''

        # Render Credencial
        st.markdown(f"""
            <div class="credential-card" style="background: {bg}; border: 2px solid {border};">
                {watermark}
                <div style="position: relative; z-index: 10; text-align: center;">
                    <p style="text-align: left; font-size: 0.7em; letter-spacing: 2px; opacity: 0.8; margin: 0;">SINDICATO STVP</p>
                    <div style="height: 25px;"></div>
                    <h2 style="margin: 0; font-size: 1.7em;">{socio['nombre']}</h2>
                    <div style="background: rgba(0,0,0,0.4); padding: 4px 12px; border-radius: 50px; display: inline-block; margin-top: 10px; color: {border}; font-weight: bold; border: 1px solid {border};">
                        {label}
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 35px; font-size: 0.9em;">
                        <div style="text-align: left;">DNI<br><b>{socio['dni']}</b></div>
                        <div style="text-align: right;">ESTADO<br><b style="color: #4ade80;">ACTIVO</b></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # SECCIÓN FAMILIARES MEJORADA (Mejora solicitada)
        fams = db_familia[db_familia['dni_titular'] == st.session_state["dni_activo"]]
        if not fams.empty:
            st.markdown("<h3 style='color: white; margin-bottom: 15px;'>👨‍👩‍👧‍👦 Grupo Familiar</h3>", unsafe_allow_html=True)
            for _, f in fams.iterrows():
                parentesco = f.get('parentesco', 'Familiar').upper()
                st.markdown(f"""
                    <div class="family-card">
                        <div class="family-name">{f['nombre']}</div>
                        <div class="family-info">DNI: {f.get('dni_familiar', 'N/A')}</div>
                        <div class="family-tag">{parentesco}</div>
                    </div>
                """, unsafe_allow_html=True)

    # Botón Salir visible al final
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("❌ Salir de la Cuenta"):
        st.session_state["dni_activo"] = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
