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
    }

    .credential-card {
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 20px;
        color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
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
        text-align: center;
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
        transition: transform 0.2s;
    }
    .benefit-item:hover {
        transform: scale(1.02);
        border-color: #3b82f6;
    }
    
    .link-benefit {
        text-decoration: none;
        color: inherit;
    }
    </style>
""", unsafe_allow_html=True)

# --- UTILIDADES PARA IMÁGENES ---
def get_image_base64(path_no_ext):
    """Convierte una imagen local a Base64 para usar en HTML."""
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
        return df_s, df_f
    except:
        return pd.DataFrame(), pd.DataFrame()

# --- LÓGICA DE LA APP ---
db_socios, db_familia = cargar_datos()

if "dni_activo" not in st.session_state:
    st.session_state["dni_activo"] = None
if "seccion" not in st.session_state:
    st.session_state["seccion"] = "credencial"

# Cabecera con logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mostrar_logo_cabecera()

if st.session_state["dni_activo"] is None:
    st.markdown("<h1 style='text-align: center; color: white; margin-top: -10px;'>STVP Digital</h1>", unsafe_allow_html=True)
    st.markdown("### Acceso Afiliados")
    dni_input = st.text_input("Ingrese su DNI:")
    if st.button("Validar"):
        dni_clean = str(dni_input).strip()
        if not db_socios.empty and dni_clean in db_socios['dni'].astype(str).values:
            st.session_state["dni_activo"] = dni_clean
            st.rerun()
        else:
            st.error("DNI no encontrado.")
else:
    # Obtener datos del socio logueado
    socio = db_socios[db_socios['dni'].astype(str) == st.session_state["dni_activo"]].iloc[0]
    
    # Menú de Botones
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        if st.button("🪪 Inicio"): st.session_state["seccion"] = "credencial"; st.rerun()
    with m2:
        if st.button("📣 Gremial"): st.session_state["seccion"] = "gremial"; st.rerun()
    with m3:
        if st.button("⚖️ Legal"): st.session_state["seccion"] = "legal"; st.rerun()
    with m4:
        if st.button("🎁 Beneficios"): st.session_state["seccion"] = "beneficios"; st.rerun()

    st.markdown("---")

    if st.session_state["seccion"] == "credencial":
        cargo_raw = str(socio.get('cargo', 'AFILIADO')).upper()
        
        # --- LÓGICA DE COLORES POR JERARQUÍA ---
        if any(x in cargo_raw for x in ["COMISIÓN", "DIRECTIVA", "SECRETARIO", "SEC."]):
            bg_color = "linear-gradient(135deg, #854d0e 0%, #422006 100%)" # Dorado/Marrón
            border_color = "#fbbf24" # Amarillo/Oro
            label_text = "COMISIÓN DIRECTIVA"
        elif "DELEGADO" in cargo_raw:
            bg_color = "linear-gradient(135deg, #064e3b 0%, #022c22 100%)" # Verde oscuro
            border_color = "#4ade80" # Verde neón
            label_text = "DELEGADO"
        else:
            bg_color = "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)" # Azul profundo
            border_color = "#3b82f6" # Azul claro
            label_text = "AFILIADO"

        # Marca de agua base64
        logo_b64 = get_image_base64("logo_stvp")
        watermark_html = f'<img src="{logo_b64}" class="watermark">' if logo_b64 else ''

        # Credencial Visual
        st.markdown(f"""
            <div class="credential-card" style="background: {bg_color}; border: 2px solid {border_color};">
                {watermark_html}
                <div class="card-content">
                    <p style="text-align: left; font-size: 0.7em; letter-spacing: 2px; opacity: 0.7; margin: 0;">SINDICATO STVP</p>
                    <div style="height: 30px;"></div>
                    <h2 style="margin: 0; font-size: 1.8em; text-transform: uppercase; color: white;">{socio['nombre']}</h2>
                    <div style="background: rgba(0,0,0,0.4); padding: 5px 15px; border-radius: 50px; display: inline-block; margin-top: 15px; color: {border_color}; font-weight: bold; font-size: 0.8em; border: 1px solid {border_color};">
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
        fams = db_familia[db_familia['dni_titular'].astype(str) == st.session_state["dni_activo"]]
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
        titulo = "Consulta Gremial" if st.session_state["seccion"] == "gremial" else "Asesoría Legal"
        st.subheader(titulo)
        st.info("Su consulta será derivada directamente a nuestros secretarios vía WhatsApp.")
        detalle = st.text_area("Describa su inquietud:")
        if st.button("Enviar por WhatsApp"):
            mensaje = f"Hola STVP, soy {socio['nombre']} (DNI {socio['dni']}). Mi consulta {st.session_state['seccion']} es: {detalle}"
            url_wa = f"https://wa.me/5491156424903?text={urllib.parse.quote(mensaje)}"
            st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; padding:15px; border-radius:12px; text-align:center; font-weight:bold;">📲 Abrir WhatsApp</div></a>', unsafe_allow_html=True)

    elif st.session_state["seccion"] == "beneficios":
        st.subheader("🎁 Beneficios Exclusivos")
        items = [
            ("🏨 Turismo - Rolsolviajes", "Hotelería propia y convenios en todo el país. Acceda a las ofertas vigentes.", "https://whatsapp.com/channel/0029VbAua9BJENy8oScpAH2B"),
            ("📚 Útiles", "Entrega de kits escolares anuales.", None),
            ("🎁 Nacimiento", "Ajuar para el recién nacido.", None)
        ]
        for t, d, link in items:
            if link:
                st.markdown(f"""
                    <a href="{link}" target="_blank" class="link-benefit">
                        <div class="benefit-item">
                            <div style="font-weight: bold; color: #3b82f6;">{t} 🔗</div>
                            <div style="font-size: 0.85em; color: #94a3b8;">{d} <br> <span style="color:#25D366; font-size:0.9em;">(Ver canal de WhatsApp)</span></div>
                        </div>
                    </a>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="benefit-item">
                        <div style="font-weight: bold; color: #3b82f6;">{t}</div>
                        <div style="font-size: 0.85em; color: #94a3b8;">{d}</div>
                    </div>
                """, unsafe_allow_html=True)

    if st.sidebar.button("❌ Cerrar Sesión"):
        st.session_state["dni_activo"] = None
        st.session_state["seccion"] = "credencial"
        st.rerun()

# Sidebar Admin
with st.sidebar:
    st.markdown("---")
    if st.checkbox("Admin"):
        if st.text_input("Clave", type="password") == "stvp2025":
            if st.button("Actualizar Padrón"):
                st.cache_data.clear()
                st.success("Datos sincronizados.")
