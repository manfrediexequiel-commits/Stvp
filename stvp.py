import streamlit as st
import pandas as pd
import requests
from io import StringIO
import os
import base64
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
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        margin-bottom: 10px;
        background-color: #1e293b;
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

# --- UTILIDADES PARA IMÁGENES ---

def format_drive_url(url):
    """Convierte un enlace de compartir de Google Drive en un enlace de visualización directa."""
    if not isinstance(url, str):
        return url
    # Regex para extraer el ID de archivos de Google Drive
    drive_match = re.search(r"(?:https?://)?(?:drive\.google\.com/(?:file/d/|open\?id=)|googledrive\.com/host/)([\w-]+)", url)
    if drive_match:
        file_id = drive_match.group(1)
        # Usamos el servidor de miniaturas de Google para renderizado directo
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
def cargar_datos():
    """Descarga los datos de Google Sheets y limpia las columnas."""
    try:
        res_s = requests.get(URL_SOCIOS)
        df_s = pd.read_csv(StringIO(res_s.text))
        df_s.columns = df_s.columns.str.strip().str.lower()
        
        res_f = requests.get(URL_FAMILIA)
        df_f = pd.read_csv(StringIO(res_f.text))
        df_f.columns = df_f.columns.str.strip().str.lower()
        
        return df_s, df_f
    except Exception as e:
        st.error(f"Error de conexión con el padrón: {e}")
        return pd.DataFrame(), pd.DataFrame()

def get_card_style(miembro):
    """Define los colores de la credencial según el cargo."""
    m = str(miembro).upper()
    if "COMISIÓN" in m or "DIRECTIVA" in m:
        return "linear-gradient(135deg, #854d0e 0%, #422006 100%)", "#fbbf24"
    elif "DELEGADO" in m:
        return "linear-gradient(135deg, #065f46 0%, #064e3b 100%)", "#6ee7b7"
    else:
        return "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)", "#3b82f6"

# --- LÓGICA PRINCIPAL ---
db_socios, db_familia = cargar_datos()

if "dni_activo" not in st.session_state:
    st.session_state["dni_activo"] = None

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
    dni_input = st.text_input("Ingrese su DNI (sin puntos):", placeholder="Ej: 12345678")
    
    if st.button("Consultar Padrón"):
        if dni_input:
            # Buscamos el DNI en la base de socios
            socio = db_socios[db_socios['dni'].astype(str) == str(dni_input)]
            if not socio.empty:
                st.session_state["dni_activo"] = str(dni_input)
                st.rerun()
            else:
                st.error("DNI no encontrado en el sistema.")
        else:
            st.warning("Por favor, ingrese un número de documento.")
else:
    # --- VISTA DE CREDENCIAL ACTIVA ---
    dni = st.session_state["dni_activo"]
    socio = db_socios[db_socios['dni'].astype(str) == str(dni)].iloc[0]
    
    # Colores según cargo
    bg_color, border_color = get_card_style(socio.get('miembro', socio.get('cargo', 'Afiliado')))
    
    # Preparar Logo de Fondo (Marca de Agua)
    logo_b64 = get_image_base64("logo_stvp")
    watermark_html = f'<img src="{logo_b64}" class="watermark">' if logo_b64 else ''
    
    # Procesar URL de foto de Google Drive del Socio
    url_foto_cruda = socio.get('foto', None)
    url_foto_directa = format_drive_url(url_foto_cruda)
    
    foto_html = f'<img src="{url_foto_directa}" class="profile-img">' if pd.notna(url_foto_directa) else '<div style="height:20px"></div>'

    # Renderizado de la Tarjeta HTML
    st.markdown(f"""
        <div class="credential-card" style="background: {bg_color}; border: 2px solid {border_color};">
            {watermark_html}
            <div class="card-content">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="font-size: 0.7em; font-weight: bold; letter-spacing: 2px; opacity: 0.8;">SINDICATO STVP</div>
                    <div style="font-size: 0.6em; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 5px;">VIGENTE 2025</div>
                </div>
                
                <div style="text-align: center; margin: 15px 0;">
                    {foto_html}
                    <h2 style="margin: 5px 0 0 0; font-size: 1.6em; text-transform: uppercase; color: white; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);">{socio['nombre']}</h2>
                    <div style="margin-top: 5px; display: inline-block; background: rgba(0,0,0,0.5); padding: 4px 12px; border-radius: 50px; font-size: 0.75em; font-weight: bold; color: {border_color}; border: 1px solid {border_color};">
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
    
    # --- GRUPO FAMILIAR ---
    st.subheader("👨‍👩‍👧‍👦 Grupo Familiar")
    familiares = db_familia[db_familia['dni_titular'].astype(str) == str(dni)]
    
    if not familiares.empty:
        for _, fam in familiares.iterrows():
            f_url = format_drive_url(fam.get('foto', None))
            f_img_tag = f'<img src="{f_url}" class="family-img">' if pd.notna(f_url) else '<div class="family-img" style="background:#475569; display:flex; align-items:center; justify-content:center;">👤</div>'
            
            st.markdown(f"""
                <div class="family-card">
                    {f_img_tag}
                    <div>
                        <div style="font-weight: bold; font-size: 0.9em; color: white;">{fam['nombre']}</div>
                        <div style="font-size: 0.8em; color: #94a3b8;">{fam['parentesco']} • DNI: {fam['dni_familiar']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No se encuentran familiares vinculados en el padrón actual.")

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
