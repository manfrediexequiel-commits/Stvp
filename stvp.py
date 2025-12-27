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

# --- ESTILOS PERSONALIZADOS (CSS REVISADO) ---
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

    /* Contenedor Foto */
    .photo-container {
        width: 95px; height: 95px; border-radius: 50%;
        border: 3px solid rgba(255,255,255,0.9); overflow: hidden;
        margin-right: 15px; background-color: #334155; flex-shrink: 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3); z-index: 5;
    }
    .photo-container img { width: 100%; height: 100%; object-fit: cover; }

    /* Credencial */
    .credential-card {
        border-radius: 20px; padding: 25px; margin-bottom: 20px;
        color: white; box-shadow: 0 12px 30px rgba(0,0,0,0.6);
        position: relative; overflow: hidden; display: flex; flex-direction: column;
        border: 2px solid rgba(255,255,255,0.1);
        min-height: 220px;
    }

    /* Marca de Agua con Logo */
    .watermark {
        position: absolute; top: 50%; left: 50%;
        transform: translate(-50%, -50%) rotate(-15deg);
        width: 200px; opacity: 0.12; z-index: 0; pointer-events: none;
    }

    .card-content { position: relative; z-index: 2; }
    .card-header { display: flex; align-items: center; text-align: left; margin-top: 10px; }

    .cargo-badge {
        padding: 4px 12px; border-radius: 50px; font-weight: bold; 
        font-size: 0.7em; border: 1px solid rgba(255,255,255,0.4);
        display: inline-block; margin-top: 8px; text-transform: uppercase;
        background: rgba(0,0,0,0.3);
    }

    .download-btn {
        background: #10b981; color: white; padding: 12px; border-radius: 12px;
        text-align: center; font-weight: bold; cursor: pointer; margin-bottom: 20px;
        border: none; width: 100%;
    }

    .family-card {
        background-color: #ffffff; border-radius: 12px; padding: 15px;
        margin-bottom: 12px; border-left: 8px solid #3b82f6;
    }
    </style>
""", unsafe_allow_html=True)

# --- CARGA DE IMÁGENES LOCALES ---
def get_image_base64(path_no_ext):
    for ext in ['png', 'jpg', 'jpeg']:
        full_path = f"{path_no_ext}.{ext}"
        if os.path.exists(full_path):
            with open(full_path, "rb") as img_file:
                return f"data:image/{ext};base64," + base64.b64encode(img_file.read()).decode()
    return ""

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
        for df in [df_s, df_f]:
            col = 'dni' if 'dni' in df.columns else 'dni_titular'
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return df_s, df_f
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame(), pd.DataFrame()

db_socios, db_familia = cargar_datos()

if "dni_activo" not in st.session_state: st.session_state["dni_activo"] = None
if "seccion" not in st.session_state: st.session_state["seccion"] = "credencial"

logo_b64 = get_image_base64("logo_stvp")

# --- FLUJO DE LOGIN ---
if st.session_state["dni_activo"] is None:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if logo_b64: st.image(logo_b64, use_container_width=True)
    st.markdown("<h2 style='text-align: center; color: white;'>Sindicato STVP</h2>", unsafe_allow_html=True)
    dni_input = st.text_input("Ingrese su DNI para acceder:")
    if st.button("INGRESAR"):
        dni_clean = str(dni_input).replace(".", "").replace(" ", "").strip()
        if not db_socios.empty and dni_clean in db_socios['dni'].values:
            st.session_state["dni_activo"] = dni_clean
            st.rerun()
        else: st.error("El DNI ingresado no se encuentra en el padrón.")

else:
    socio = db_socios[db_socios['dni'] == st.session_state["dni_activo"]].iloc[0]
    
    # --- LOGICA DE COLORES POR COLUMNA 'MIEMBRO' ---
    # Usamos .strip() para evitar errores por espacios invisibles en el Excel
    m_tipo = str(socio.get('miembro', 'AFILIADO')).upper().strip()
    
    if any(x in m_tipo for x in ["COMISION", "COMISIÓN", "DIRECTIVA", "SECRETARIO"]):
        bg, border, label = "linear-gradient(135deg, #b8860b 0%, #4a3504 100%)", "#ffd700", "COMISIÓN DIRECTIVA"
    elif "DELEGADO" in m_tipo:
        bg, border, label = "linear-gradient(135deg, #065f46 0%, #064e3b 100%)", "#34d399", "DELEGADO"
    else:
        bg, border, label = "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)", "#60a5fa", "AFILIADO"

    # --- BARRA DE NAVEGACIÓN ---
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

    # SECCIÓN: CREDENCIAL
    if st.session_state["seccion"] == "credencial":
        url_foto = socio.get('foto', '')
        if pd.isna(url_foto) or str(url_foto).strip() == "": 
            url_foto = "https://www.w3schools.com/howto/img_avatar.png"

        st.markdown(f"""
            <div id="digital-credential" class="credential-card" style="background: {bg}; border: 2px solid {border};">
                <img src="{logo_b64}" class="watermark">
                <div class="card-content">
                    <p style="font-size: 0.6em; letter-spacing: 2px; opacity: 0.9; margin: 0; font-weight: bold;">SINDICATO STVP</p>
                    <div class="card-header">
                        <div class="photo-container" style="border-color: {border};">
                            <img src="{url_foto}" crossorigin="anonymous">
                        </div>
                        <div>
                            <h2 style="margin: 0; font-size: 1.3em; text-transform: uppercase; line-height: 1;">{socio['nombre']}</h2>
                            <div class="cargo-badge" style="color: {border};">{label}</div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 35px; font-size: 0.85em;">
                        <div>DNI<br><b style="font-size: 1.1em;">{socio['dni']}</b></div>
                        <div style="text-align: right;">ESTADO<br><b style="color: #4ade80; font-size: 1.1em;">ACTIVO</b></div>
                    </div>
                </div>
            </div>
            <button class="download-btn" onclick="downloadCredential()">⬇️ GUARDAR CREDENCIAL COMO IMAGEN</button>
            <script>
            function downloadCredential() {{
                const element = document.getElementById('digital-credential');
                html2canvas(element, {{ 
                    scale: 3, 
                    backgroundColor: null,
                    useCORS: true,
                    allowTaint: true
                }}).then(canvas => {{
                    const link = document.createElement('a');
                    link.download = 'Credencial_STVP_{socio['dni']}.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                }});
            }}
            </script>
        """, unsafe_allow_html=True)

        # Familiares
        fams = db_familia[db_familia['dni_titular'] == st.session_state["dni_activo"]]
        if not fams.empty:
            st.markdown("<h3 style='color: white;'>👨‍👩‍👧‍👦 Grupo Familiar</h3>", unsafe_allow_html=True)
            for _, f in fams.iterrows():
                st.markdown(f"""
                    <div class="family-card">
                        <div class="family-name">{f['nombre']}</div>
                        <div style="color: #475569; font-size: 0.9em;">DNI: {f.get('dni_familiar','N/A')}</div>
                        <div class="family-tag">{str(f.get('parentesco','Familiar')).upper()}</div>
                    </div>
                """, unsafe_allow_html=True)

    # SECCIÓN: BENEFICIOS
    elif st.session_state["seccion"] == "beneficios":
        st.subheader("Beneficios y Convenios")
        st.markdown("""
            <div style="background:#1e293b; padding:20px; border-radius:15px; border-left: 5px solid #3b82f6;">
                <h4 style="color:#3b82f6; margin:0;">🏨 Turismo - ROLSOL VALLE</h4>
                <p style="color:#94a3b8; font-size:0.95em;">Acceda a hotelería propia y paquetes turísticos exclusivos para el afiliado y su familia.</p>
            </div>
        """, unsafe_allow_html=True)
        st.link_button("📲 VER NOVEDADES EN WHATSAPP", "https://whatsapp.com/channel/0029VbAua9BJENy8oScpAH2B")

    # --- PANEL ADMIN (STVP2026) ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander("🛠️ Configuración de Sistema"):
        pwd = st.text_input("Ingrese clave de administrador:", type="password")
        if pwd == "Stvp2026":
            st.success("Acceso concedido")
            if st.button("🔄 RECARGAR TODA LA BASE DE DATOS"):
                st.cache_data.clear()
                st.toast("Datos actualizados desde Google Sheets")
                st.rerun()
        elif pwd != "":
            st.error("Clave incorrecta")

    if st.button("❌ CERRAR SESIÓN"):
        st.session_state["dni_activo"] = None
        st.rerun()
