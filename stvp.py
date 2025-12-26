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
    .credential-card {
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
    }
    .profile-img {
        width: 110px;
        height: 110px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid white;
        margin-bottom: 10px;
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
    </style>
""", unsafe_allow_html=True)

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
        return df_s, df_f
    except:
        return pd.DataFrame(), pd.DataFrame()

# --- LÓGICA PRINCIPAL ---
db_socios, db_familia = cargar_datos()

if "dni_activo" not in st.session_state:
    st.session_state["dni_activo"] = None

if st.session_state["dni_activo"] is None:
    st.title("🛡️ Credencial STVP")
    dni_in = st.text_input("Ingrese su DNI para acceder:")
    if st.button("Validar Afiliado"):
        dni_str = str(dni_in).strip()
        if not db_socios.empty and dni_str in db_socios['dni'].astype(str).values:
            st.session_state["dni_activo"] = dni_str
            st.rerun()
        else:
            st.error("DNI no encontrado.")
else:
    socio = db_socios[db_socios['dni'].astype(str) == st.session_state["dni_activo"]].iloc[0]
    
    # Renderizado de Credencial
    st.markdown(f"""
        <div class="credential-card" style="background: linear-gradient(135deg, #1e3a8a 0%, #172554 100%); border: 2px solid #3b82f6;">
            <div style="text-align: center;">
                <h2 style="margin: 0; color: white;">{socio['nombre']}</h2>
                <div style="color: #3b82f6; font-weight: bold; margin-bottom: 15px;">{socio.get('cargo', 'AFILIADO')}</div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8em; opacity: 0.8;">
                    <div>DNI: {socio['dni']}</div>
                    <div style="color: #4ade80;">ESTADO: ACTIVO</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Cerrar Sesión"):
        st.session_state["dni_activo"] = None
        st.rerun()

    # Familiares
    st.subheader("Grupo Familiar")
    fams = db_familia[db_familia['dni_titular'].astype(str) == st.session_state["dni_activo"]]
    for _, f in fams.iterrows():
        st.info(f"**{f['nombre']}** - {f.get('parentesco', 'Familiar')}")
