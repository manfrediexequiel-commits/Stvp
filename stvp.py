import streamlit as st
import pandas as pd
import base64
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Simulador STVP", page_icon="🛡️", layout="centered")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.2em;
        background-color: #2563eb; color: white; font-weight: bold; border: none;
    }
    .nav-button>button { background-color: #1e293b; border: 1px solid #3b82f6; }
    .credential-card {
        border-radius: 20px; padding: 25px; margin-bottom: 20px; color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1);
        position: relative; overflow: hidden; min-height: 250px;
    }
    .profile-img {
        width: 110px; height: 110px; border-radius: 50%; object-fit: cover;
        border: 3px solid white; margin-bottom: 10px; background-color: #334155;
    }
    .benefit-card {
        background-color: #1e293b; border-radius: 15px; padding: 20px;
        margin-bottom: 15px; border: 1px solid rgba(59, 130, 246, 0.3); text-align: center;
    }
    .family-card {
        background-color: #1e293b; border-radius: 15px; padding: 15px;
        margin-bottom: 10px; border-left: 5px solid #3b82f6; display: flex; align-items: center; gap: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATOS DE PRUEBA (MOCK DATA) ---
mock_socios = pd.DataFrame([
    {"dni": "12345678", "nombre": "JUAN PÉREZ", "cargo": "AFILIADO", "foto": "https://www.w3schools.com/howto/img_avatar.png"},
    {"dni": "87654321", "nombre": "ANA GARCÍA", "cargo": "COMISIÓN DIRECTIVA", "foto": "https://www.w3schools.com/howto/img_avatar2.png"}
])

mock_familia = pd.DataFrame([
    {"dni_titular": "12345678", "nombre": "MARTA PÉREZ", "parentesco": "Hija", "dni_familiar": "45667788"},
    {"dni_titular": "12345678", "nombre": "ROBERTO PÉREZ", "parentesco": "Hijo", "dni_familiar": "49001122"}
])

# --- NAVEGACIÓN ---
if "dni_demo" not in st.session_state: st.session_state["dni_demo"] = None
if "pantalla_demo" not in st.session_state: st.session_state["pantalla_demo"] = "inicio"

def get_style(cargo):
    if "COMISIÓN" in cargo: return "linear-gradient(135deg, #854d0e 0%, #422006 100%)", "#fbbf24"
    return "linear-gradient(135deg, #1e3a8a 0%, #172554 100%)", "#3b82f6"

# --- RENDER ---
st.markdown("<h1 style='text-align:center; color:#2563eb;'>STVP DIGITAL</h1>", unsafe_allow_html=True)

if st.session_state["dni_demo"] is None:
    st.info("PRUEBA: Use DNI 12345678 para ver un afiliado o 87654321 para directivo.")
    dni_in = st.text_input("DNI:")
    if st.button("Ingresar"):
        if dni_in in mock_socios['dni'].values:
            st.session_state["dni_demo"] = dni_in
            st.rerun()
        else: st.error("DNI no encontrado.")

else:
    # Menú
    st.markdown('<div class="nav-button">', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1: 
        if st.button("🪪 Credencial"): st.session_state["pantalla_demo"] = "inicio"; st.rerun()
    with m2: 
        if st.button("📣 Gremial"): st.session_state["pantalla_demo"] = "gremial"; st.rerun()
    with m3: 
        if st.button("⚖️ Legal"): st.session_state["pantalla_demo"] = "legal"; st.rerun()
    with m4: 
        if st.button("🎁 Bonos"): st.session_state["pantalla_demo"] = "bonos"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    socio = mock_socios[mock_socios['dni'] == st.session_state["dni_demo"]].iloc[0]

    if st.session_state["pantalla_demo"] == "inicio":
        bg, brd = get_style(socio['cargo'])
        st.markdown(f"""
            <div class="credential-card" style="background: {bg}; border: 2px solid {brd};">
                <div style="text-align: center;">
                    <img src="{socio['foto']}" class="profile-img">
                    <h2 style="margin:0;">{socio['nombre']}</h2>
                    <small style="color:{brd}; font-weight:bold;">{socio['cargo']}</small>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:20px; font-size:0.8em;">
                    <div>DNI<br><b>{socio['dni']}</b></div>
                    <div style="text-align:right;">ESTADO<br><b style="color:#4ade80;">ACTIVO</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        fams = mock_familia[mock_familia['dni_titular'] == socio['dni']]
        if not fams.empty:
            st.subheader("Familiares")
            for _, f in fams.iterrows():
                st.markdown(f'<div class="family-card">👤 <div><b>{f["nombre"]}</b><br><small>{f["parentesco"]}</small></div></div>', unsafe_allow_html=True)

    elif st.session_state["pantalla_demo"] in ["gremial", "legal"]:
        tipo = "GREMIAL" if st.session_state["pantalla_demo"] == "gremial" else "LEGAL"
        st.subheader(f"Consulta {tipo}")
        msg = st.text_area("Mensaje:")
        if st.button("Enviar"):
            t_url = urllib.parse.quote(f"*{tipo}*\nSocio: {socio['nombre']}\n\n{msg}")
            st.markdown(f'<a href="https://wa.me/5491156424903?text={t_url}" target="_blank" style="display:block; background:#25D366; color:white; padding:10px; border-radius:10px; text-align:center; text-decoration:none; font-weight:bold;">📲 Enviar WhatsApp</a>', unsafe_allow_html=True)

    elif st.session_state["pantalla_demo"] == "bonos":
        st.subheader("Beneficios Activos")
        st.markdown('<div class="benefit-card">🏨 <b>Turismo</b><br>Hoteles en MDQ</div>', unsafe_allow_html=True)
        st.markdown('<div class="benefit-card">💊 <b>Farmacia</b><br>Descuentos 40%</div>', unsafe_allow_html=True)

    if st.button("Cerrar Sesión"):
        st.session_state["dni_demo"] = None
        st.rerun()
