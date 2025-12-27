import streamlit as st
import pandas as pd
import requests
from io import StringIO
import os
import base64
import urllib.parse
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="SINDICATO STVP - Credencial Digital", 
    page_icon="🛡️", 
    layout="centered"
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
    .main { background-color: #0f172a; }
    
    /* Botones Navegación */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 4.5em;
        background-color: #2563eb; color: white; border: none;
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; line-height: 1.2; padding: 5px;
    }
    .stButton>button p { font-size: 0.75em !important; margin: 0; font-weight: bold; }

    /* Credencial */
    .credential-card {
        border-radius: 20px; padding: 25px; margin-bottom: 20px;
        color: white; box-shadow: 0 12px 30px rgba(0,0,0,0.6);
        position: relative; overflow: hidden; display: flex; flex-direction: column;
        border: 2px solid rgba(255,255,255,0.1);
    }

    .watermark {
        position: absolute; top: 50%; left: 50%;
        transform: translate(-50%, -50%) rotate(-15deg);
        width: 200px; opacity: 0.12; z-index: 0; pointer-events: none;
    }

    .photo-container {
        width: 95px; height: 95px; border-radius: 50%;
        border: 3px solid rgba(255,255,255,0.9); overflow: hidden;
        margin-right: 15px; background-color: #334155; flex-shrink: 0;
        z-index: 5;
    }
    .photo-container img { width: 100%; height: 100%; object-fit: cover; }

    /* Estilo Botón WhatsApp Corregido */
    .wa-link {
        display: block;
        background-color: #25D366;
        color: white !important;
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        font-weight: bold;
        text-decoration: none;
        margin-bottom: 10px;
        border: 1px solid #128C7E;
    }
    .wa-link:hover {
        background-color: #128C7E;
    }
    </style>
""", unsafe_allow_html=True)

# --- UTILIDADES ---
def get_image_base64(path_no_ext):
    for ext in ['png', 'jpg', 'jpeg']:
        full_path = f"{path_no_ext}.{ext}"
        if os.path.exists(full_path):
            with open(full_path, "rb") as img_file:
                return f"data:image/{ext};base64," + base64.b64encode(img_file.read()).decode()
    return ""

logo_b64 = get_image_base64("logo_stvp")

@st.cache_data(ttl=300)
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
if "seccion" not in st.session_state: st.session_state["seccion"] = "credencial"

# --- LOGO SUPERIOR ---
if logo_b64:
    st.markdown(f'<div style="text-align: center;"><img src="{logo_b64}" width="120"></div>', unsafe_allow_html=True)

# --- LOGIN ---
if st.session_state["dni_activo"] is None:
    st.markdown("<h2 style='text-align: center; color: white;'>Sindicato STVP</h2>", unsafe_allow_html=True)
    dni_input = st.text_input("Ingrese su DNI:")
    if st.button("INGRESAR"):
        dni_clean = str(dni_input).replace(".", "").replace(" ", "").strip()
        if not db_socios.empty and dni_clean in db_socios['dni'].values:
            st.session_state["dni_activo"] = dni_clean
            st.rerun()
        else: st.error("DNI no registrado.")

# --- APP ---
else:
    socio = db_socios[db_socios['dni'] == st.session_state["dni_activo"]].iloc[0]
    
    # Navegación
    m1, m2, m3, m4 = st.columns(4)
    with m1: 
        if st.button("🪪\nINICIO"): st.session_state["seccion"] = "credencial"
    with m2: 
        if st.button("📣\nGREMIAL"): st.session_state["seccion"] = "gremial"
    with m3: 
        if st.button("⚖️\nLEGAL"): st.session_state["seccion"] = "legal"
    with m4: 
        if st.button("🎁\nBENEF."): st.session_state["seccion"] = "beneficios"

    st.markdown("---")

    # SECCIÓN: INICIO / CREDENCIAL
    if st.session_state["seccion"] == "credencial":
        m_tipo = str(socio.get('miembro', 'AFILIADO')).upper().strip()
        if any(x in m_tipo for x in ["COMISION", "COMISIÓN", "DIRECTIVA"]):
            bg, border, label = "linear-gradient(135deg, #b8860b 0%, #4a3504 100%)", "#ffd700", "COMISIÓN DIRECTIVA"
        elif "DELEGADO" in m_tipo:
            bg, border, label = "linear-gradient(135deg, #065f46 0%, #064e3b 100%)", "#34d399", "DELEGADO"
        else:
            bg, border, label = "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)", "#60a5fa", "AFILIADO"

        url_foto = socio.get('foto', 'https://www.w3schools.com/howto/img_avatar.png')
        
        st.markdown(f"""
            <div id="digital-credential" class="credential-card" style="background: {bg}; border: 2px solid {border};">
                <img src="{logo_b64}" class="watermark">
                <div style="position: relative; z-index: 10;">
                    <p style="font-size: 0.6em; letter-spacing: 2px; opacity: 0.9; margin: 0; font-weight: bold;">SINDICATO STVP</p>
                    <div style="display: flex; align-items: center; margin-top: 10px;">
                        <div class="photo-container" style="border-color: {border};"><img src="{url_foto}"></div>
                        <div>
                            <h2 style="margin: 0; font-size: 1.3em; text-transform: uppercase;">{socio['nombre']}</h2>
                            <div style="color: {border}; font-weight: bold; font-size: 0.75em; border: 1px solid {border}; padding: 2px 10px; border-radius: 50px; display: inline-block; margin-top: 5px;">{label}</div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 35px; font-size: 0.85em;">
                        <div>DNI<br><b>{socio['dni']}</b></div>
                        <div style="text-align: right;">ESTADO<br><b style="color: #4ade80;">ACTIVO</b></div>
                    </div>
                </div>
            </div>
            <button class="download-btn" onclick="downloadCredential()" style="width:100%; padding:10px; border-radius:10px; background:#10b981; color:white; border:none; font-weight:bold;">⬇️ GUARDAR IMAGEN</button>
            <script>
            function downloadCredential() {{
                html2canvas(document.getElementById('digital-credential'), {{ scale: 3, useCORS: true }}).then(canvas => {{
                    const link = document.createElement('a');
                    link.download = 'Credencial_STVP_{socio['dni']}.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                }});
            }}
            </script>
        """, unsafe_allow_html=True)

    # SECCIÓN: GREMIAL Y LEGAL (BOTONES CORREGIDOS)
    elif st.session_state["seccion"] in ["gremial", "legal"]:
        tipo_header = "Gremial" if st.session_state["seccion"] == "gremial" else "Legal"
        st.subheader(f"Asesoría {tipo_header}")
        
        st.info("Seleccione un representante para iniciar la consulta por WhatsApp:")
        
        # Preparamos el mensaje
        nombre_afiliado = socio['nombre']
        msg = urllib.parse.quote(f"Hola, mi nombre es {nombre_afiliado}. Necesito realizar una consulta {tipo_header.lower()}.")
        
        # Link 1: Gremial
        st.markdown(f"""<a class="wa-link" href="https://wa.me/5491161080024?text={msg}" target="_blank">📲 Contactar Gremial (+54 9 11 6108-0024)</a>""", unsafe_allow_html=True)
        
        # Link 2: Soporte
        st.markdown(f"""<a class="wa-link" href="https://wa.me/5491156424903?text={msg}" target="_blank">📲 Contactar Soporte (+54 9 11 5642-4903)</a>""", unsafe_allow_html=True)

    # SECCIÓN: BENEFICIOS
    elif st.session_state["seccion"] == "beneficios":
        st.subheader("Beneficios")
        st.markdown("""
            <div style="background:#1e293b; padding:15px; border-radius:15px; border-left: 5px solid #3b82f6; margin-bottom:15px;">
                <h4 style="color:#3b82f6; margin:0;">🏨 Turismo - ROLSOL VALLE</h4>
                <p style="color:#94a3b8; font-size:0.9em;">Acceso a paquetes turísticos exclusivos.</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""<a class="wa-link" href="https://whatsapp.com/channel/0029VbAua9BJENy8oScpAH2B" target="_blank">📲 VER NOVEDADES EN WHATSAPP</a>""", unsafe_allow_html=True)

    # PANEL ADMIN
    st.markdown("---")
    with st.expander("🛠️ Admin"):
        pwd = st.text_input("Clave:", type="password")
        if pwd == "Stvp2026":
            if st.button("🔄 ACTUALIZAR DATOS"):
                st.cache_data.clear()
                st.rerun()

    if st.button("❌ SALIR"):
        st.session_state["dni_activo"] = None
        st.rerun()
