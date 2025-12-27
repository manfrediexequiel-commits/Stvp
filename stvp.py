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
    URL_FAMILIA
