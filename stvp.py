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
