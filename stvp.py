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
    
    .stButton>button {
        width: 100%; border-radius: 12px; height: 4.5em;
        background-color: #2563eb; color: white; border: none;
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; line-height: 1.2; padding: 5px;
    }
    .stButton>button p { font-size: 0.75em !important; margin: 0; font-weight: bold; }

    .photo-container {
        width: 90px; height: 90px; border-radius: 50%;
        border: 3px solid rgba(255,255,255,0.8); overflow: hidden;
        margin-right: 15px; background-color: #334155; flex-shrink: 0;
    }
    .photo-container img { width: 100%; height: 100%; object-fit: cover; }

    .credential-card {
        border-radius: 20px; padding: 25px; margin-bottom: 20px;
        color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        position: relative; overflow: hidden; display: flex; flex-direction: column;
    }

    .family-card {
        background-color: #ffffff; border-radius: 12px; padding: 15px;
        margin-bottom: 12px; border-left: 8px solid #3b82f6;
    }
    .family-name { color: #1e293b; font-weight: 800; text-transform: uppercase; }
    .family-tag {
        display: inline-block; background-color: #dbeafe; color: #1e40af;
        padding: 2px 8px; border-radius: 6px; font-size: 0.75em; font-weight: bold;
    }

    .benefit-card {
        background-color: #1e293b; border-radius: 15px; padding: 20px;
        margin-bottom: 15px; border: 1px solid rgba(59, 130, 246, 0.3);
    }

    .download-btn {
        background: #059669; color: white; padding: 12px; border-radius: 12px;
        text-align: center; font-weight: bold; cursor: pointer; margin-bottom: 20px;
        border: none; width: 100%; display: block;
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

# --- APP PRINCIPAL ---
else:
    socio = db_socios[db_socios['dni'] == st.session_state["dni_activo"]].iloc[0]
    cargo_str = str(socio.get('cargo', 'AFILIADO')).upper()
    
    # --- MENÚ DE NAVEGACIÓN ---
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
        if any(x in cargo_str for x in ["COMISIÓN", "DIRECTIVA"]):
            bg, border, label = "linear-gradient(135deg, #854d0e 0%, #422006 100%)", "#fbbf24", "COMISIÓN DIRECTIVA"
        elif "DELEGADO" in cargo_str:
            bg, border, label = "linear-gradient(135deg, #064e3b 0%, #022c22 100%)", "#4ade80", "DELEGADO"
        else:
            bg, border, label = "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)", "#3b82f6", "AFILIADO"

        url_foto = socio.get('foto', 'https://www.w3schools.com/howto/img_avatar.png')
        if pd.isna(url_foto) or str(url_foto).strip() == "": url_foto = "https://www.w3schools.com/howto/img_avatar.png"

        st.markdown(f"""
            <div id="digital-credential" class="credential-card" style="background: {bg}; border: 2px solid {border};">
                <p style="font-size: 0.6em; letter-spacing: 2px; opacity: 0.7; margin: 0;">SINDICATO STVP</p>
                <div class="card-header">
                    <div class="photo-container"><img src="{url_foto}"></div>
                    <div>
                        <h2 style="margin: 0; font-size: 1.4em;">{socio['nombre']}</h2>
                        <div style="background: rgba(0,0,0,0.4); padding: 2px 10px; border-radius: 50px; color: {border}; font-weight: bold; font-size: 0.7em; border: 1px solid {border}; margin-top: 5px;">{label}</div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 25px; font-size: 0.85em;">
                    <div>DNI<br><b>{socio['dni']}</b></div>
                    <div style="text-align: right;">ESTADO<br><b style="color: #4ade80;">ACTIVO</b></div>
                </div>
            </div>
            <button class="download-btn" onclick="downloadCredential()">⬇️ GUARDAR CREDENCIAL</button>
            <script>
            function downloadCredential() {{
                const element = document.getElementById('digital-credential');
                html2canvas(element, {{ scale: 3 }}).then(canvas => {{
                    const link = document.createElement('a');
                    link.download = 'Credencial_STVP.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                }});
            }}
            </script>
        """, unsafe_allow_html=True)

        fams = db_familia[db_familia['dni_titular'] == st.session_state["dni_activo"]]
        if not fams.empty:
            st.markdown("<h3 style='color: white;'>👨‍👩‍👧‍👦 Grupo Familiar</h3>", unsafe_allow_html=True)
            for _, f in fams.iterrows():
                st.markdown(f"""
                    <div class="family-card">
                        <div class="family-name">{f['nombre']}</div>
                        <div style="color: #475569; font-size: 0.9em;">DNI: {f.get('dni_familiar', 'N/A')}</div>
                        <div class="family-tag">{str(f.get('parentesco', 'Familiar')).upper()}</div>
                    </div>
                """, unsafe_allow_html=True)

    # SECCIÓN: BENEFICIOS (CON ROLSOL VALLE)
    elif st.session_state["seccion"] == "beneficios":
        st.subheader("Beneficios Exclusivos")
        
        # Tarjeta ROLSOL VALLE
        st.markdown("""
            <div class="benefit-card">
                <h4 style="color: #3b82f6; margin: 0;">🏨 Turismo - ROLSOL VALLE</h4>
                <p style="color: #94a3b8; font-size: 0.9em; margin: 10px 0;">
                    Acceda a las mejores ofertas en hotelería propia y convenios en todo el país.
                </p>
            </div>
        """, unsafe_allow_html=True)
        st.link_button("📲 CONTACTO DIRECTO (WHATSAPP)", "https://whatsapp.com/channel/0029VbAua9BJENy8oScpAH2B")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Otros beneficios
        st.markdown("""
            <div class="benefit-card">
                <h4 style="color: #3b82f6; margin: 0;">📚 Útiles Escolares</h4>
                <p style="color: #94a3b8; font-size: 0.9em; margin: 5px 0;">Entrega de kits escolares anuales para hijos de afiliados.</p>
            </div>
            <div class="benefit-card">
                <h4 style="color: #3b82f6; margin: 0;">👶 Nacimiento</h4>
                <p style="color: #94a3b8; font-size: 0.9em; margin: 5px 0;">Ajuar completo para el recién nacido.</p>
            </div>
        """, unsafe_allow_html=True)

    # SECCIÓN: CONSULTAS
    elif st.session_state["seccion"] in ["gremial", "legal"]:
        st.subheader(f"Asesoría {st.session_state['seccion'].capitalize()}")
        detalle = st.text_area("Describa su inquietud:")
        if st.button("Enviar"):
            mensaje = f"Hola, soy {socio['nombre']}. Consulta {st.session_state['seccion']}: {detalle}"
            url_wa = f"https://wa.me/5491156424903?text={urllib.parse.quote(mensaje)}"
            st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; padding:15px; border-radius:12px; text-align:center;">📲 Enviar por WhatsApp</div></a>', unsafe_allow_html=True)

    # PANEL DELEGADOS
    if any(x in cargo_str for x in ["DELEGADO", "COMISIÓN"]):
        st.markdown("---")
        with st.expander("🛠️ Panel de Gestión (Delegados)"):
            archivo = st.file_uploader("Previsualizar foto de afiliado", type=['jpg', 'png'])
            if archivo: st.image(archivo, width=100)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("❌ CERRAR SESIÓN"):
        st.session_state["dni_activo"] = None
        st.rerun()
