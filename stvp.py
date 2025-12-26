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
    if not isinstance(url, str) or pd.isna(url) or url.strip() == "":
        return None
    # Intenta capturar el ID del archivo de un link de drive
    drive_match = re.search(r"(?:https?://)?(?:drive\.google\.com/(?:file/d/|open\?id=)|googledrive\.com/host/)([\w-]+)", url)
    if drive_match:
        file_id = drive_match.group(1)
        return f"https://lh3.googleusercontent.com/u/0/d/{file_id}"
    return url

def get_image_base64(path_no_ext):
    """Convierte una imagen local a Base64."""
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
        # Normalización de columnas
        df_s.columns = df_s.columns.str.strip().str.lower()
        df_f.columns = df_f.columns.str.strip().str.lower()
        return df_s, df_f
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame(), pd.DataFrame()

def get_style(cargo):
    c = str(cargo).upper()
    if any(x in c for x in ["COMISIÓN", "DIRECTIVA", "SECRETARIO", "SEC."]): 
        return "linear-gradient(135deg, #854d0e 0%, #422006 100%)", "#fbbf24"
    if "DELEGADO" in c:
        return "linear-gradient(135deg, #065f46 0%, #064e3b 100%)", "#6ee7b7"
    return "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)", "#3b82f6"

# --- INICIO DE APLICACIÓN ---
if "dni_activo" not in st.session_state: st.session_state["dni_activo"] = None
if "pantalla" not in st.session_state: st.session_state["pantalla"] = "inicio"

db_socios, db_familia = cargar_datos_reales()

# Encabezado
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mostrar_logo_cabecera()

st.markdown("<h1 style='text-align: center; color: white; margin-top: -10px;'>STVP Digital</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Sindicato de Trabajadores de Vigilancia Privada</p>", unsafe_allow_html=True)

if st.session_state["dni_activo"] is None:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Acceso al Portal")
    dni_in = st.text_input("Ingrese su DNI (sin puntos):", key="login_dni")
    if st.button("Consultar Padrón"):
        if dni_in:
            if not db_socios.empty:
                dni_str = str(dni_in).strip()
                socio_filt = db_socios[db_socios['dni'].astype(str).str.strip() == dni_str]
                if not socio_filt.empty:
                    st.session_state["dni_activo"] = dni_str
                    st.rerun()
                else:
                    st.error("DNI no encontrado en el padrón actual.")
            else:
                st.error("Error al acceder a la base de datos.")
        else:
            st.warning("Por favor, ingrese un número de DNI.")
else:
    # Menú de Navegación
    m1, m2, m3, m4 = st.columns(4)
    with m1: 
        if st.button("🪪 Credencial"): st.session_state["pantalla"] = "inicio"; st.rerun()
    with m2: 
        if st.button("📣 Gremial"): st.session_state["pantalla"] = "gremial"; st.rerun()
    with m3: 
        if st.button("⚖️ Legal"): st.session_state["pantalla"] = "legal"; st.rerun()
    with m4: 
        if st.button("🎁 Beneficios"): st.session_state["pantalla"] = "bonos"; st.rerun()

    # Obtención de datos segura
    try:
        socio_data = db_socios[db_socios['dni'].astype(str).str.strip() == str(st.session_state["dni_activo"])].iloc[0]
    except:
        st.session_state["dni_activo"] = None
        st.rerun()

    if st.session_state["pantalla"] == "inicio":
        # Estilos basados en cargo
        cargo_actual = socio_data.get('cargo', socio_data.get('miembro', 'AFILIADO'))
        bg, brd = get_style(cargo_actual)
        
        # Procesamiento de Foto
        foto_url = format_drive_url(socio_data.get('foto'))
        foto_html = f'<img src="{foto_url}" class="profile-img">' if foto_url else '<div style="height:20px"></div>'
        
        # Marca de agua
        logo_b64 = get_image_base64("logo_stvp")
        watermark_html = f'<img src="{logo_b64}" class="watermark">' if logo_b64 else ''
        
        # RENDERIZADO DE CREDENCIAL SEGÚN EL DISEÑO SOLICITADO
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
                        <h2 style="margin: 5px 0 0 0; font-size: 1.6em; text-transform: uppercase; color: white; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);">
                            {socio_data['nombre']}
                        </h2>
                        <div style="margin-top: 5px; display: inline-block; background: rgba(0,0,0,0.5); padding: 4px 12px; border-radius: 50px; font-size: 0.75em; font-weight: bold; color: {brd}; border: 1px solid {brd};">
                            {cargo_actual}
                        </div>
                    </div>

                    <div style="display: flex; justify-content: space-between; font-size: 0.8em; opacity: 0.9; margin-top: 10px;">
                        <div>
                            <div style="font-size: 0.7em; opacity: 0.6;">DOCUMENTO</div>
                            <div style="font-weight: bold;">{socio_data['dni']}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 0.7em; opacity: 0.6;">ESTADO</div>
                            <div style="font-weight: bold; color: #4ade80;">ACTIVO</div>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Familiares
        fams = db_familia[db_familia['dni_titular'].astype(str).str.strip() == str(st.session_state["dni_activo"])]
        if not fams.empty:
            st.subheader("👨‍👩‍👧‍👦 Grupo Familiar")
            for _, f in fams.iterrows():
                f_url = format_drive_url(f.get('foto'))
                f_tag = f'<img src="{f_url}" class="family-img">' if f_url else '<div class="family-img" style="background:#475569; display:flex; align-items:center; justify-content:center; color:white; font-size:20px;">👤</div>'
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
            st.info("No hay familiares vinculados en el padrón.")

    elif st.session_state["pantalla"] == "bonos":
        st.subheader("🎁 Beneficios")
        beneficios = [
            ("🏨", "Turismo", "Hoteles con convenio."),
            ("💊", "Salud", "Farmacias adheridas."),
            ("📚", "Educación", "Kits escolares.")
        ]
        for icon, title, desc in beneficios:
            st.markdown(f'<div class="benefit-card"><h3>{icon} {title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)

    elif st.session_state["pantalla"] in ["gremial", "legal"]:
        tipo = st.session_state["pantalla"].upper()
        st.subheader(f"Consulta {tipo}")
        msg = st.text_area("Escriba su consulta aquí:")
        if st.button("Enviar por WhatsApp"):
            msg_quote = urllib.parse.quote(f"Consulta {tipo}\nAfiliado: {socio_data['nombre']}\nDNI: {socio_data['dni']}\nConsulta: {msg}")
            st.markdown(f'<a href="https://wa.me/5491156424903?text={msg_quote}" target="_blank" style="display:block; background:#25D366; color:white; text-align:center; padding:10px; border-radius:10px; text-decoration:none; font-weight:bold;">📲 Enviar Mensaje</a>', unsafe_allow_html=True)

    if st.sidebar.button("❌ Cerrar Sesión"):
        st.session_state["dni_activo"] = None
        st.rerun()

with st.sidebar:
    st.markdown("### ⚙️ Administración")
    if st.checkbox("Modo Administrador"):
        pwd = st.text_input("Clave:", type="password")
        if pwd == "stvp2025":
            if st.button("🔄 Refrescar Padrón"):
                st.cache_data.clear()
                st.success("Base de datos actualizada.")
                st.rerun()
import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from fpdf import FPDF
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SINDICATO STVP - Credencial Digital", page_icon="🛡️", layout="centered")

# --- ENLACES DE GOOGLE SHEETS (Reemplaza con tus links de "Publicar en la Web") ---
URL_SOCIOS = "https://drive.google.com/file/d/1j-OZfPahquiCpOVIkys5zYFG5jqwcKVc/view?usp=drivesdk"
URL_FAMILIA = "https://drive.google.com/file/d/1OHbeZDXHZZs6DOGeYJNYTUnyMz8IOgVt/view?usp=drivesdk"

# --- FUNCIONES DE CARGA Y PROCESAMIENTO ---
@st.cache_data(ttl=600)  # Se actualiza cada 10 min
def cargar_datos():
    try:
        df_s = pd.read_csv(URL_SOCIOS, dtype={'DNI': str})
        df_f = pd.read_csv(URL_FAMILIA, dtype={'DNI_Titular': str, 'DNI_Familiar': str})
        return df_s, df_f
    except:
        # Datos de prueba por si los links fallan inicialmente
        df_s = pd.DataFrame([{"DNI": "123", "Nombre": "SOCIO DE PRUEBA", "Vence": "2026-12-31", "Miembro": "AFILIADO ACTIVO", "Cargo": "N/A"}])
        df_f = pd.DataFrame([{"DNI_Titular": "123", "Nombre": "FAMILIAR PRUEBA", "Parentesco": "Hijo", "DNI_Familiar": "456"}])
        return df_s, df_f

def generar_pdf_titular(s, path_logo):
    pdf = FPDF(orientation='L', unit='mm', format=(54, 86))
    pdf.add_page()
    
    # Color según categoría: Dorado para Directiva, Azul para Afiliados
    color = (133, 77, 14) if s['Miembro'] == "COMISIÓN DIRECTIVA" else (30, 58, 138)
    pdf.set_fill_color(*color)
    pdf.rect(0, 0, 86, 54, 'F')
    
    # Logo
    if os.path.exists(path_logo):
        pdf.image(path_logo, 5, 5, 12)
    
    # Encabezado
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_xy(18, 6)
    pdf.cell(0, 5, "SINDICATO STVP", ln=True)
    
    # Nombre
    pdf.set_y(18)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, s['Nombre'].upper(), ln=True, align='C')
    
    # Cargo / Miembro
    pdf.set_font("Arial", 'B', 8)
    pdf.set_text_color(253, 224, 71) # Amarillo
    cargo = s['Cargo'] if s['Miembro'] == "COMISIÓN DIRECTIVA" else s['Miembro']
    pdf.cell(0, 5, cargo, ln=True, align='C')
    
    # Datos Pie
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", '', 7)
    pdf.set_y(42)
    pdf.cell(0, 5, f"DNI: {s['DNI']} | VENCE: {s['Vence']}", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- INICIALIZACIÓN ---
db_socios, db_familia = cargar_datos()
path_logo = "logo_stvp.png"

if "dni_activo" not in st.session_state:
    st.session_state["dni_activo"] = None

# --- INTERFAZ DE USUARIO ---
# Logo superior izquierda
col_l, col_r = st.columns([1, 4])
with col_l:
    if os.path.exists(path_logo):
        st.image(path_logo, width=80)

st.title("🛡️ Credencial Digital STVP")

# FLUJO DE LOGIN / CONSULTA
if st.session_state["dni_activo"] is None:
    st.markdown("### Bienvenido al portal del afiliado")
    dni_input = st.text_input("Ingrese su DNI para validar:")
    if st.button("Consultar Credencial"):
        if dni_input:
            st.session_state["dni_activo"] = dni_input
            st.rerun()
else:
    dni = st.session_state["dni_activo"]
    socio = db_socios[db_socios["DNI"].astype(str) == str(dni)]
    
    if not socio.empty:
        s = socio.iloc[0]
        es_directiva = s['Miembro'] == "COMISIÓN DIRECTIVA"
        
        # Diseño de la tarjeta en pantalla
        bg_card = "linear-gradient(135deg, #854d0e 0%, #422006 100%)" if es_directiva else "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)"
        border_color = "#fbbf24" if es_directiva else "#3b82f6"
        
        st.markdown(f"""
            <div style="background: {bg_card}; color: white; padding: 25px; border-radius: 15px; border: 3px solid {border_color}; text-align: center; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);">
                <p style="text-align: left; font-size: 0.7em; letter-spacing: 2px; margin: 0;">SINDICATO STVP</p>
                <h1 style="margin: 15px 0; font-size: 1.8em;">{s['Nombre']}</h1>
                <p style="background: rgba(255,255,255,0.1); display: inline-block; padding: 5px 15px; border-radius: 5px; font-weight: bold; color: #fde047;">
                    {s['Cargo'] if es_directiva else s['Miembro']}
                </p>
                <hr style="opacity: 0.2; margin: 20px 0;">
                <p style="margin: 0;">DNI: {s['DNI']} | Vencimiento: {s['Vence']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Botones de Acción
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            pdf_bytes = generar_pdf_titular(s, path_logo)
            st.download_button(label="📥 Descargar PDF", data=pdf_bytes, file_name=f"STVP_{dni}.pdf", mime="application/pdf", use_container_width=True)
        with c2:
            if st.button("❌ Cerrar Sesión", use_container_width=True):
                st.session_state["dni_activo"] = None
                st.rerun()
        
        # Grupo Familiar
        st.markdown("---")
        st.subheader("👨‍👩‍👧‍👦 Grupo Familiar Vinculado")
        familiares = db_familia[db_familia["DNI_Titular"].astype(str) == str(dni)]
        if not familiares.empty:
            for _, f in familiares.iterrows():
                st.info(f"**{f['Nombre']}** - {f['Parentesco']} (DNI: {f['DNI_Familiar']})")
        else:
            st.warning("No se encontraron familiares registrados.")
            
    else:
        st.error("DNI no encontrado en el padrón actual.")
        if st.button("Volver a intentar"):
            st.session_state["dni_activo"] = None
            st.rerun()

# --- PANEL DE ADMINISTRACIÓN (OPCIONAL) ---
with st.sidebar:
    st.write("---")
    if st.checkbox("Acceso Administrador"):
        pass_admin = st.text_input("Clave", type="password")
        if pass_admin == "stvp2025":
            st.success("Conectado a Google Sheets")
            st.write("**Resumen de Padrón:**")
            st.write(f"Total Afiliados: {len(db_socios)}")
            if st.button("Forzar Actualización de Datos"):
                st.cache_data.clear()
                st.rerun()
