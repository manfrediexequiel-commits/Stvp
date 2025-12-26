import streamlit as st
import pandas as pd
import requests
from io import StringIO
import os
import base64
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="SINDICATO STVP - Credencial Digital", 
    page_icon="🛡️", 
    layout="centered"
)

# --- ESTILOS Y LIBRERÍA DE CAPTURA ---
st.markdown("""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script>
    function downloadCredential() {
        const element = document.getElementById('digital-credential');
        html2canvas(element, {
            scale: 2,
            backgroundColor: null,
            logging: false
        }).then(canvas => {
            const link = document.createElement('a');
            link.download = 'Credencial_STVP.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        });
    }
    </script>
    
    <style>
    .main { background-color: #0f172a; }
    
    /* Estilo del Botón de Descarga */
    .download-btn {
        background: #059669;
        color: white;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        cursor: pointer;
        margin-bottom: 20px;
        border: none;
        width: 100%;
        display: block;
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

    /* Familiares */
    .family-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        border-left: 8px solid #3b82f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .family-name { color: #1e293b; font-weight: 800; text-transform: uppercase; }
    .family-tag {
        display: inline-block;
        background-color: #dbeafe;
        color: #1e40af;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75em;
        font-weight: bold;
        margin-top: 5px;
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

@st.cache_data(ttl=600)
def cargar_datos():
    URL_SOCIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=0&single=true&output=csv"
    URL_FAMILIA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=1889067091&single=true&output=csv"
    try:
        df_s = pd.read_csv(StringIO(requests.get(URL_SOCIOS).text))
        df_f = pd.read_csv(StringIO(requests.get(URL_FAMILIA).text))
        df_s.columns = df_s.columns.str.strip().str.lower()
        df_f.columns = df_f.columns.str.strip().str.lower()
        for df in [df_s, df_f]:
            col = 'dni' if 'dni' in df.columns else 'dni_titular'
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return df_s, df_f
    except: return pd.DataFrame(), pd.DataFrame()

db_socios, db_familia = cargar_datos()

if "dni_activo" not in st.session_state: st.session_state["dni_activo"] = None

if st.session_state["dni_activo"] is None:
    st.markdown("<h1 style='text-align: center; color: white;'>STVP Digital</h1>", unsafe_allow_html=True)
    dni_input = st.text_input("Ingrese su DNI:")
    if st.button("Ingresar"):
        dni_clean = str(dni_input).replace(".", "").strip()
        if dni_clean in db_socios['dni'].values:
            st.session_state["dni_activo"] = dni_clean
            st.rerun()
else:
    socio = db_socios[db_socios['dni'] == st.session_state["dni_activo"]].iloc[0]
    
    # Render Credencial con ID para captura
    cargo = str(socio.get('cargo', 'AFILIADO')).upper()
    if any(x in cargo for x in ["COMISIÓN", "DIRECTIVA"]):
        bg, border, label = "linear-gradient(135deg, #854d0e 0%, #422006 100%)", "#fbbf24", "COMISIÓN DIRECTIVA"
    elif "DELEGADO" in cargo:
        bg, border, label = "linear-gradient(135deg, #064e3b 0%, #022c22 100%)", "#4ade80", "DELEGADO"
    else:
        bg, border, label = "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)", "#3b82f6", "AFILIADO"

    logo_b64 = get_image_base64("logo_stvp")
    watermark = f'<img src="{logo_b64}" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%) rotate(-15deg); width:180px; opacity:0.12;">' if logo_b64 else ''

    # Bloque de la credencial
    st.markdown(f"""
        <div id="digital-credential" class="credential-card" style="background: {bg}; border: 2px solid {border};">
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
        <button class="download-btn" onclick="downloadCredential()">⬇️ DESCARGAR CREDENCIAL (IMAGEN)</button>
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
                    <div class="family-tag">{str(f.get('parentesco', 'FAMILIAR')).upper()}</div>
                </div>
            """, unsafe_allow_html=True)

    if st.button("❌ Salir"):
        st.session_state["dni_activo"] = None
        st.rerun()
