import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SINDICATO STVP - Credencial Digital", page_icon="🛡️", layout="centered")

# --- ENLACES DE GOOGLE SHEETS (Convertidos a exportación directa CSV) ---
ID_SOCIOS = "1j-OZfPahquiCpOVIkys5zYFG5jqwcKVc"
ID_FAMILIA = "1OHbeZDXHZZs6DOGeYJNYTUnyMz8IOgVt"

URL_SOCIOS = f"https://docs.google.com/spreadsheets/d/{ID_SOCIOS}/export?format=csv"
URL_FAMILIA = f"https://docs.google.com/spreadsheets/d/{ID_FAMILIA}/export?format=csv"

# --- FUNCIONES DE CARGA ---
@st.cache_data(ttl=600)
def cargar_datos():
    try:
        df_s = pd.read_csv(URL_SOCIOS, dtype={'DNI': str})
        df_f = pd.read_csv(URL_FAMILIA, dtype={'DNI_Titular': str, 'DNI_Familiar': str})
        return df_s, df_f
    except Exception as e:
        # Datos de respaldo si la conexión falla
        return pd.DataFrame(), pd.DataFrame()

def generar_pdf_titular(s, path_logo):
    pdf = FPDF(orientation='L', unit='mm', format=(54, 86))
    pdf.add_page()
    
    # Lógica de colores para el PDF
    if s['Miembro'] == "COMISIÓN DIRECTIVA":
        color = (133, 77, 14) # Dorado/Marrón
    elif s['Miembro'] == "DELEGADO":
        color = (6, 78, 59) # Verde Oscuro
    else:
        color = (30, 58, 138) # Azul
        
    pdf.set_fill_color(*color)
    pdf.rect(0, 0, 86, 54, 'F')
    if os.path.exists(path_logo):
        pdf.image(path_logo, 5, 5, 12)
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_xy(18, 6)
    pdf.cell(0, 5, "SINDICATO STVP", ln=True)
    
    pdf.set_y(18)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, str(s['Nombre']).upper(), ln=True, align='C')
    
    pdf.set_font("Arial", 'B', 8)
    pdf.set_text_color(253, 224, 71)
    cargo = s['Cargo'] if s['Miembro'] == "COMISIÓN DIRECTIVA" else s['Miembro']
    pdf.cell(0, 5, str(cargo), ln=True, align='C')
    
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

# --- INTERFAZ ---
col_l, col_r = st.columns([1, 4])
with col_l:
    if os.path.exists(path_logo):
        st.image(path_logo, width=80)

st.title("🛡️ Credencial Digital STVP")

if st.session_state["dni_activo"] is None:
    st.markdown("### Bienvenido al portal del afiliado")
    dni_input = st.text_input("Ingrese su DNI:")
    if st.button("Consultar"):
        st.session_state["dni_activo"] = dni_input
        st.rerun()
else:
    dni = st.session_state["dni_activo"]
    socio = db_socios[db_socios["DNI"].astype(str) == str(dni)]
    
    if not socio.empty:
        s = socio.iloc[0]
        
        # Definición de colores según jerarquía
        if s['Miembro'] == "COMISIÓN DIRECTIVA":
            bg_card = "linear-gradient(135deg, #854d0e 0%, #422006 100%)"
            border = "#fbbf24"
        elif s['Miembro'] == "DELEGADO":
            bg_card = "linear-gradient(135deg, #065f46 0%, #064e3b 100%)"
            border = "#6ee7b7"
        else:
            bg_card = "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)"
            border = "#3b82f6"

        st.markdown(f"""
            <div style="background: {bg_card}; color: white; padding: 25px; border-radius: 15px; border: 3px solid {border}; text-align: center;">
                <p style="text-align: left; font-size: 0.7em; letter-spacing: 2px; margin: 0;">SINDICATO STVP</p>
                <h1 style="margin: 15px 0; font-size: 1.8em;">{s['Nombre']}</h1>
                <p style="background: rgba(255,255,255,0.1); display: inline-block; padding: 5px 15px; border-radius: 5px; font-weight: bold; color: #fde047;">
                    {s['Cargo'] if s['Miembro'] == "COMISIÓN DIRECTIVA" else s['Miembro']}
                </p>
                <p style="margin-top: 20px; font-size: 0.9em;">DNI: {s['DNI']} | Vence: {s['Vence']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            pdf_bytes = generar_pdf_titular(s, path_logo)
            st.download_button("📥 Descargar PDF", pdf_bytes, f"STVP_{dni}.pdf", "application/pdf", use_container_width=True)
        with col2:
            if st.button("❌ Cerrar Sesión", use_container_width=True):
                st.session_state["dni_activo"] = None
                st.rerun()
        
        st.markdown("---")
        st.subheader("👨‍👩‍👧‍👦 Grupo Familiar")
        familiares = db_familia[db_familia["DNI_Titular"].astype(str) == str(dni)]
        if not familiares.empty:
            for _, f in familiares.iterrows():
                st.info(f"**{f['Nombre']}** - {f['Parentesco']} (DNI: {f['DNI_Familiar']})")
        else:
            st.warning("No hay familiares vinculados.")
    else:
        st.error("DNI no encontrado.")
        if st.button("Reintentar"):
            st.session_state["dni_activo"] = None
            st.rerun()

# Panel Admin en Sidebar
with st.sidebar:
    if st.checkbox("Admin"):
        if st.text_input("Clave", type="password") == "stvp2025":
            if st.button("Actualizar Datos"):
                st.cache_data.clear()
                st.rerun()
