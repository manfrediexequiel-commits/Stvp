import streamlit as st
import pandas as pd
import requests
from io import StringIO
import os
import base64
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="STVP - Credencial Digital", page_icon="🛡️", layout="centered")

# --- ESTILOS CSS ---
st.markdown("""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
    .main { background-color: #0f172a; }
    
    /* Estilo de la Foto en la Credencial */
    .photo-container {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 3px solid rgba(255,255,255,0.8);
        overflow: hidden;
        margin-right: 20px;
        background-color: #334155;
        flex-shrink: 0;
    }
    .photo-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .credential-card {
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }

    .card-header {
        display: flex;
        align-items: center;
        text-align: left;
        margin-top: 15px;
        position: relative;
        z-index: 10;
    }

    .download-btn {
        background: #059669; color: white; padding: 12px; border-radius: 12px;
        text-align: center; font-weight: bold; cursor: pointer; margin-bottom: 20px;
        border: none; width: 100%;
    }

    .family-card {
        background-color: #ffffff; border-radius: 12px; padding: 15px;
        margin-bottom: 12px; border-left: 8px solid #3b82f6;
    }
    </style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data(ttl=300)
def cargar_datos():
    URL_SOCIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=0&single=true&output=csv"
    URL_FAMILIA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=1889067091&single=true&output=csv"
    try:
        df_s = pd.read_csv(StringIO(requests.get(URL_SOCIOS).text))
        df_f = pd.read_csv(StringIO(requests.get(URL_FAMILIA).text))
        df_s.columns = df_s.columns.str.strip().str.lower()
        df_f.columns = df_f.columns.str.strip().str.lower()
        df_s['dni'] = df_s['dni'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return df_s, df_f
    except: return pd.DataFrame(), pd.DataFrame()

db_socios, db_familia = cargar_datos()

if "dni_activo" not in st.session_state: st.session_state["dni_activo"] = None

if st.session_state["dni_activo"] is None:
    st.markdown("<h1 style='text-align: center; color: white;'>STVP Digital</h1>", unsafe_allow_html=True)
    dni_input = st.text_input("DNI:")
    if st.button("Ingresar"):
        dni_clean = str(dni_input).replace(".", "").strip()
        if dni_clean in db_socios['dni'].values:
            st.session_state["dni_activo"] = dni_clean
            st.rerun()
else:
    socio = db_socios[db_socios['dni'] == st.session_state["dni_activo"]].iloc[0]
    
    # Manejo de la URL de la foto
    # Si no hay columna 'foto' o está vacía, usamos un placeholder
    url_foto = socio.get('foto', 'https://www.w3schools.com/howto/img_avatar.png')
    if pd.isna(url_foto) or str(url_foto).strip() == "":
        url_foto = "https://www.w3schools.com/howto/img_avatar.png"

    # Lógica de colores según cargo
    cargo = str(socio.get('cargo', 'AFILIADO')).upper()
    if any(x in cargo for x in ["COMISIÓN", "DIRECTIVA"]):
        bg, border, label = "linear-gradient(135deg, #854d0e 0%, #422006 100%)", "#fbbf24", "COMISIÓN DIRECTIVA"
    elif "DELEGADO" in cargo:
        bg, border, label = "linear-gradient(135deg, #064e3b 0%, #022c22 100%)", "#4ade80", "DELEGADO"
    else:
        bg, border, label = "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)", "#3b82f6", "AFILIADO"

    # HTML de la Credencial con Foto
    st.markdown(f"""
        <div id="digital-credential" class="credential-card" style="background: {bg}; border: 2px solid {border};">
            <p style="font-size: 0.7em; letter-spacing: 2px; opacity: 0.8; margin: 0;">SINDICATO STVP</p>
            
            <div class="card-header">
                <div class="photo-container">
                    <img src="{url_foto}" alt="Foto Afiliado">
                </div>
                <div>
                    <h2 style="margin: 0; font-size: 1.5em; line-height: 1.1;">{socio['nombre']}</h2>
                    <div style="background: rgba(0,0,0,0.4); padding: 3px 10px; border-radius: 50px; display: inline-block; margin-top: 8px; color: {border}; font-weight: bold; font-size: 0.75em; border: 1px solid {border};">
                        {label}
                    </div>
                </div>
            </div>

            <div style="display: flex; justify-content: space-between; margin-top: 30px; font-size: 0.9em; position: relative; z-index: 10;">
                <div style="text-align: left;">DNI<br><b>{socio['dni']}</b></div>
                <div style="text-align: right;">ESTADO<br><b style="color: #4ade80;">ACTIVO</b></div>
            </div>
        </div>
        
        <script>
        function downloadCredential() {{
            const element = document.getElementById('digital-credential');
            html2canvas(element, {{ scale: 2, backgroundColor: null }}).then(canvas => {{
                const link = document.createElement('a');
                link.download = 'Credencial_{socio['dni']}.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
            }});
        }}
        </script>
        <button class="download-btn" onclick="downloadCredential()">⬇️ GUARDAR COMO IMAGEN</button>
    """, unsafe_allow_html=True)

    # Mostrar Familiares (mismo código anterior)
    fams = db_familia[db_familia['dni_titular'] == st.session_state["dni_activo"]]
    if not fams.empty:
        st.markdown("<h3 style='color: white;'>👨‍👩‍👧‍👦 Grupo Familiar</h3>", unsafe_allow_html=True)
        for _, f in fams.iterrows():
            st.markdown(f"""
                <div class="family-card">
                    <div style="color: #1e293b; font-weight: 800; text-transform: uppercase;">{f['nombre']}</div>
                    <div style="color: #475569; font-size: 0.9em;">DNI: {f.get('dni_familiar', 'N/A')}</div>
                </div>
            """, unsafe_allow_html=True)

    if st.button("❌ Salir"):
        st.session_state["dni_activo"] = None
        st.rerun()
