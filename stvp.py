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

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
    .main { background-color: #0f172a; }
    
    /* Botones de Navegación */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 4.5em;
        background-color: #2563eb; color: white; border: none;
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; line-height: 1.2; padding: 5px;
    }
    .stButton>button p { font-size: 0.75em !important; margin: 0; font-weight: bold; }

    /* Foto Circular */
    .photo-container {
        width: 90px; height: 90px; border-radius: 50%;
        border: 3px solid rgba(255,255,255,0.9); overflow: hidden;
        margin-right: 15px; background-color: #334155; flex-shrink: 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .photo-container img { width: 100%; height: 100%; object-fit: cover; }

    /* Estructura de la Credencial */
    .credential-card {
        border-radius: 20px; padding: 25px; margin-bottom: 20px;
        color: white; box-shadow: 0 12px 30px rgba(0,0,0,0.6);
        position: relative; overflow: hidden; display: flex; flex-direction: column;
        border: 2px solid rgba(255,255,255,0.1);
    }

    /* Brillo para destacar jerarquía */
    .credential-card::after {
        content: ""; position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        pointer-events: none;
    }

    .card-header { display: flex; align-items: center; text-align: left; margin-top: 10px; position: relative; z-index: 10; }

    /* Estilo de Etiquetas de Cargo */
    .cargo-badge {
        padding: 3px 12px; border-radius: 50px; font-weight: bold; 
        font-size: 0.75em; border: 1px solid rgba(255,255,255,0.4);
        display: inline-block; margin-top: 8px; text-transform: uppercase;
        background: rgba(0,0,0,0.3);
    }

    .family-card {
        background-color: #ffffff; border-radius: 12px; padding: 15px;
        margin-bottom: 12px; border-left: 8px solid #3b82f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .family-name { color: #1e293b; font-weight: 800; text-transform: uppercase; }
    .family-tag {
        display: inline-block; background-color: #dbeafe; color: #1e40af;
        padding: 2px 8px; border-radius: 6px; font-size: 0.75em; font-weight: bold;
    }

    .download-btn {
        background: #10b981; color: white; padding: 12px; border-radius: 12px;
        text-align: center; font-weight: bold; cursor: pointer; margin-bottom: 20px;
        border: none; width: 100%;
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
        for df in [df_s, df_f]:
            col = 'dni' if 'dni' in df.columns else 'dni_titular'
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return df_s, df_f
    except: return pd.DataFrame(), pd.DataFrame()

db_socios, db_familia = cargar_datos()

if "dni_activo" not in st.session_state: st.session_state["dni_activo"] = None
if "seccion" not in st.session_state: st.session_state["seccion"] = "credencial"

# --- LOGIN ---
if st.session_state["dni_activo"] is None:
    st.markdown("<h1 style='text-align: center; color: white;'>STVP Digital</h1>", unsafe_allow_html=True)
    dni_input = st.text_input("Ingrese su DNI:")
    if st.button("INGRESAR"):
        dni_clean = str(dni_input).replace(".", "").replace(" ", "").strip()
        if not db_socios.empty and dni_clean in db_socios['dni'].values:
            st.session_state["dni_activo"] = dni_clean
            st.rerun()
        else: st.error("DNI no registrado.")

else:
    socio = db_socios[db_socios['dni'] == st.session_state["dni_activo"]].iloc[0]
    cargo_str = str(socio.get('cargo', 'AFILIADO')).upper()
    
    # --- NAVEGACIÓN ---
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

    # SECCIÓN: CREDENCIAL (Diferenciación de Jerarquías)
    if st.session_state["seccion"] == "credencial":
        
        # LÓGICA DE COLORES SOLICITADA
        # 1. DORADO (Comisión Directiva)
        if any(x in cargo_str for x in ["COMISION", "COMISIÓN", "DIRECTIVA", "SECRETARIO"]):
            bg = "linear-gradient(135deg, #b8860b 0%, #8b6508 50%, #4a3504 100%)"
            border = "#ffd700" # Dorado
            label = "COMISIÓN DIRECTIVA"
        
        # 2. VERDE (Delegados)
        elif "DELEGADO" in cargo_str:
            bg = "linear-gradient(135deg, #065f46 0%, #064e3b 100%)"
            border = "#34d399" # Esmeralda/Verde
            label = "DELEGADO"
        
        # 3. AZUL (Afiliados)
        else:
            bg = "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)"
            border = "#60a5fa" # Azul cielo
            label = "AFILIADO"

        url_foto = socio.get('foto', 'https://www.w3schools.com/howto/img_avatar.png')
        if pd.isna(url_foto) or str(url_foto).strip() == "": url_foto = "https://www.w3schools.com/howto/img_avatar.png"

        st.markdown(f"""
            <div id="digital-credential" class="credential-card" style="background: {bg}; border: 2px solid {border};">
                <p style="font-size: 0.6em; letter-spacing: 2px; opacity: 0.8; margin: 0; font-weight: bold;">SINDICATO STVP</p>
                <div class="card-header">
                    <div class="photo-container" style="border-color: {border};">
                        <img src="{url_foto}">
                    </div>
                    <div>
                        <h2 style="margin: 0; font-size: 1.4em; text-transform: uppercase; letter-spacing: 1px;">{socio['nombre']}</h2>
                        <div class="cargo-badge" style="color: {border};">{label}</div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 30px; font-size: 0.85em; position: relative; z-index: 10;">
                    <div>DNI<br><b style="font-size: 1.1em;">{socio['dni']}</b></div>
                    <div style="text-align: right;">ESTADO<br><b style="color: #4ade80; font-size: 1.1em;">ACTIVO</b></div>
                </div>
            </div>
            <button class="download-btn" onclick="downloadCredential()">⬇️ GUARDAR CREDENCIAL</button>
            <script>
            function downloadCredential() {{
                const element = document.getElementById('digital-credential');
                html2canvas(element, {{ scale: 3, backgroundColor: null }}).then(canvas => {{
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
            st.markdown("<h3 style='color: white; margin-top: 20px;'>👨‍👩‍👧‍👦 Grupo Familiar</h3>", unsafe_allow_html=True)
            for _, f in fams.iterrows():
                st.markdown(f"""
                    <div class="family-card">
                        <div class="family-name">{f['nombre']}</div>
                        <div style="color: #475569; font-size: 0.9em;">DNI: {f.get('dni_familiar', 'N/A')}</div>
                        <div class="family-tag">{str(f.get('parentesco', 'Familiar')).upper()}</div>
                    </div>
                """, unsafe_allow_html=True)

    # OTRAS SECCIONES (BENEFICIOS, ETC.) - Se mantienen igual
    elif st.session_state["seccion"] == "beneficios":
        st.subheader("Beneficios")
        st.markdown('<div class="benefit-card"><h4 style="color:#3b82f6; margin:0;">🏨 Turismo - ROLSOL VALLE</h4><p style="color:#94a3b8; font-size:0.9em;">Paquetes y financiación exclusiva.</p></div>', unsafe_allow_html=True)
        st.link_button("📲 CONTACTO DIRECTO (WHATSAPP)", "https://whatsapp.com/channel/0029VbAua9BJENy8oScpAH2B")

    # BOTÓN SALIR
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("❌ CERRAR SESIÓN"):
        st.session_state["dni_activo"] = None
        st.rerun()
