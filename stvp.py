import streamlit as st
import pandas as pd
import requests
from io import StringIO
import os
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="SINDICATO STVP - Credencial Digital", 
    page_icon="🛡️", 
    layout="centered"
)

# --- ESTILOS PERSONALIZADOS ---
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
    .credential-card {
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
        min-height: 220px;
    }
    /* Estilo para el logo de fondo (Marca de agua) */
    .watermark {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-15deg);
        width: 180px;
        opacity: 0.15;
        pointer-events: none;
        z-index: 0;
    }
    .card-content {
        position: relative;
        z-index: 10;
    }
    .family-card {
        background-color: #1e293b;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #3b82f6;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIÓN PARA OBTENER IMAGEN EN BASE64 ---
def get_image_base64(path_no_ext):
    posibles_ext = ['png', 'jpg', 'jpeg', 'webp']
    for ext in posibles_ext:
        full_path = f"{path_no_ext}.{ext}"
        if os.path.exists(full_path):
            with open(full_path, "rb") as img_file:
                return f"data:image/{ext};base64," + base64.b64encode(img_file.read()).decode()
    return None

# --- FUNCIÓN PARA MOSTRAR EL LOGO SUPERIOR ---
def mostrar_logo_cabecera():
    b64 = get_image_base64("logo_stvp")
    if b64:
        st.image(b64, width=120)
    else:
        st.markdown("""
        <div class="logo-container">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 22C12 22 20 18 20 12V5L12 2L4 5V12C4 18 12 22 12 22Z" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="#2563eb33"/>
                <path d="M9 12L11 14L15 10" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        """, unsafe_allow_html=True)

# --- ENLACES DE GOOGLE SHEETS ---
URL_SOCIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=0&single=true&output=csv"
URL_FAMILIA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRT80rJKxr62o2RBs5PpaCvpWbyH2B14dk1Gv610WH3QPoeQi2akdeu4Kgo97Mtq-QOmB8d3ORap8-n/pub?gid=1889067091&single=true&output=csv"

# --- CARGA DE DATOS ---
@st.cache_data(ttl=600)
def cargar_datos():
    try:
        res_s = requests.get(URL_SOCIOS)
        df_s = pd.read_csv(StringIO(res_s.text))
        df_s.columns = df_s.columns.str.strip().str.lower()
        
        res_f = requests.get(URL_FAMILIA)
        df_f = pd.read_csv(StringIO(res_f.text))
        df_f.columns = df_f.columns.str.strip().str.lower()
        
        return df_s, df_f
    except Exception as e:
        st.error(f"Error al conectar con el Padrón: {e}")
        return pd.DataFrame(), pd.DataFrame()

def get_card_style(miembro):
    m = str(miembro).upper()
    if "COMISIÓN" in m or "DIRECTIVA" in m:
        return "linear-gradient(135deg, #854d0e 0%, #422006 100%)", "#fbbf24"
    elif "DELEGADO" in m:
        return "linear-gradient(135deg, #065f46 0%, #064e3b 100%)", "#6ee7b7"
    else:
        return "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)", "#3b82f6"

# --- INICIO DE APP ---
db_socios, db_familia = cargar_datos()

if "dni_activo" not in st.session_state:
    st.session_state["dni_activo"] = None

# Encabezado
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mostrar_logo_cabecera()

st.markdown("<h1 style='text-align: center; color: white; margin-top: -10px;'>STVP Digital</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Sindicato de Trabajadores de Vigilancia Privada</p>", unsafe_allow_html=True)

if st.session_state["dni_activo"] is None:
    # Vista Login
    with st.container():
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Acceso al Portal")
        dni_input = st.text_input("Ingrese su DNI (sin puntos):", placeholder="Ej: 12345678")
        
        if st.button("Consultar Padrón"):
            if dni_input:
                socio = db_socios[db_socios['dni'].astype(str) == str(dni_input)]
                if not socio.empty:
                    st.session_state["dni_activo"] = str(dni_input)
                    st.rerun()
                else:
                    st.error("DNI no encontrado en el sistema.")
            else:
                st.warning("Por favor, ingrese un número de documento.")
else:
    # Vista Credencial
    dni = st.session_state["dni_activo"]
    socio = db_socios[db_socios['dni'].astype(str) == str(dni)].iloc[0]
    
    bg_color, border_color = get_card_style(socio.get('miembro', socio.get('cargo', 'Afiliado')))
    
    # Preparamos el logo de fondo
    logo_b64 = get_image_base64("logo_stvp")
    watermark_html = f'<img src="{logo_b64}" class="watermark">' if logo_b64 else ''

    # HTML de la Credencial
    st.markdown(f"""
        <div class="credential-card" style="background: {bg_color}; border: 2px solid {border_color};">
            {watermark_html}
            <div class="card-content">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="font-size: 0.7em; font-weight: bold; letter-spacing: 2px; opacity: 0.8;">SINDICATO STVP</div>
                    <div style="font-size: 0.6em; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 5px;">VIGENTE 2025</div>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <h2 style="margin: 0; font-size: 1.8em; text-transform: uppercase; color: white; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);">{socio['nombre']}</h2>
                    <div style="margin-top: 10px; display: inline-block; background: rgba(0,0,0,0.5); padding: 5px 15px; border-radius: 50px; font-size: 0.8em; font-weight: bold; color: {border_color}; border: 1px solid {border_color};">
                        {socio.get('cargo', socio.get('miembro', 'AFILIADO'))}
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8em; opacity: 0.9;">
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
    
    # Grupo Familiar
    st.subheader("👨‍👩‍👧‍👦 Grupo Familiar")
    familiares = db_familia[db_familia['dni_titular'].astype(str) == str(dni)]
    
    if not familiares.empty:
        for _, fam in familiares.iterrows():
            st.markdown(f"""
                <div class="family-card">
                    <div style="font-weight: bold; font-size: 0.9em; color: white;">{fam['nombre']}</div>
                    <div style="font-size: 0.8em; color: #94a3b8;">{fam['parentesco']} • DNI: {fam['dni_familiar']}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No se encuentran familiares vinculados en el padrón.")

    st.write("---")
    if st.button("❌ Cerrar Sesión"):
        st.session_state["dni_activo"] = None
        st.rerun()

# Barra lateral Admin
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
