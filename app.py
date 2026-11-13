import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd

# Configuración general de la página en modo ancho
st.set_page_config(
    page_title="Bovi-Fertil-IA — Laboratorio Móvil",
    page_icon="🔬",
    layout="wide"
)

# Estilos CSS avanzados con alto contraste para el modo oscuro de Streamlit
st.markdown("""
    <style>
    .main-title {
        font-size: 2.8rem !important;
        color: #60A5FA !important;
        font-weight: 800 !important;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.2rem !important;
        color: #94A3B8 !important;
        font-weight: 500 !important;
        margin-bottom: 20px;
    }
    p, .stMarkdown, .stAlert {
        font-size: 1.1rem !important;
    }
    /* Tarjetas de métricas estilizadas con alto contraste para modo oscuro */
    div.stMetric {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 15px 10px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    div.stMetric:hover {
        border-color: #60A5FA;
        box-shadow: 0 10px 15px -3px rgba(96, 165, 250, 0.2);
    }
    /* Forzar que los textos dentro de las métricas resalten bien */
    div.stMetric label {
        color: #94A3B8 !important;
    }
    div.stMetric [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar el estado de sesión para el login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.nombre = ""
    st.session_state.apellido = ""
    st.session_state.es_ingeniero = True

# PANTALLA DE INICIO DE SESIÓN
if not st.session_state.logged_in:
    st.markdown('<p class="main-title">🔬 Bovi-Fertil-IA</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Plataforma Inteligente de Análisis Seminal Bovino</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("### 🔐 Identificación de Usuario / Visitante")
        st.write("Por favor, introduce tus datos para acceder al laboratorio móvil.")
        
        with st.form("login_form"):
            nombre_input = st.text_input("Nombre")
            apellido_input = st.text_input("Apellido")
            es_ing_input = st.checkbox("¿Eres Ingeniero / Profesional?", value=True)
            
            submitted = st.form_submit_button("🚀 Entrar al Sistema")
            
            if submitted:
                if nombre_input.strip() and apellido_input.strip():
                    st.session_state.logged_in = True
                    st.session_state.nombre = nombre_input.strip()
                    st.session_state.apellido = apellido_input.strip()
                    st.session_state.es_ingeniero = es_ing_input
                    st.rerun()
                else:
                    st.warning("⚠️ Por favor, ingresa tu nombre y apellido para continuar.")
    
    st.stop()

# ==========================================
# USUARIO LOGUEADO
# ==========================================

prefijo_titulo = "Ing. " if st.session_state.es_ingeniero else ""
nombre_completo = f"{prefijo_titulo}{st.session_state.nombre} {st.session_state.apellido}"

st.markdown('<p class="main-title">🔬 Bovi-Fertil-IA</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Plataforma Inteligente de Análisis Seminal Bovino en Tiempo Real</p>', unsafe_allow_html=True)
st.markdown("---")

menu = st.sidebar.selectbox(
    "📌 Menú de Navegación",
    ["Inicio", "Análisis Microscópico", "Cámara en Vivo (Dashboard)", "Historial y Reportes", "Configuración"]
)

if st.sidebar.button("🔄 Cambiar de Usuario"):
    st.session_state.logged_in = False
    st.rerun()

if menu == "Inicio":
    col_1, col_2 = st.columns([2, 1])
    with col_1:
        st.success(f"👋 ¡Bienvenido al sistema, {nombre_completo}!")
        st.write("""
        **Bovi-Fertil-IA** integra tecnologías web y visión artificial para emular sistemas profesionales de análisis de semen bovino en campo y laboratorio.
        """)
        st.info("👈 Seleccione **Cámara en Vivo (Dashboard)** en el menú lateral para abrir la captura de muestras.")
    with col_2:
        st.markdown("### 📊 Estado del Sistema")
        st.metric(label="Cloud Stream", value="Activo", delta="Web Ready")
        st.metric(label="Plataforma", value="Multi-Dispositivo", delta="Óptimo")

elif menu == "Análisis Microscópico":
    st.header("🔬 Módulo de Análisis por Imagen Estática")
    archivo = st.file_uploader("📂 Cargar microfotografía", type=["jpg", "jpeg", "png"])
    if archivo:
        img = Image.open(archivo)
        st.image(img, caption=f"Muestra analizada por {nombre_completo}", use_container_width=True)

elif menu == "Cámara en Vivo (Dashboard)":
    st.header("📱 Panel de Control en Vivo (Estilo Laboratorio)")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        toro_id = st.text_input("Identificador del Toro", "EQ-24")
    with col_info2:
        raza_val = st.text_input("Raza / Especie", "Holstein")
    with col_info3:
        evaluador_val = st.text_input("Evaluador", nombre_completo)

    st.markdown("---")
    
    st.info("📸 Usa el siguiente componente para capturar la muestra de la cámara web o del microscopio digital.")
    foto_capturada = st.camera_input("📷 Capturar Fotograma de la Muestra Microscópica")

    if foto_capturada is not None:
        bytes_data = foto_capturada.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        cv2_img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

        st.success("✅ ¡Fotograma capturado con éxito!")
        st.image(cv2_img_rgb, channels="RGB", caption=f"Muestra en Directo - Toro: {toro_id} | Evaluador: {nombre_completo}", use_container_width=True)

        # Métricas con el nuevo diseño adaptado para alto contraste en modo oscuro
        st.markdown("### 📊 Resumen de Análisis en Tiempo Real")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(label="Concentración", value="40.39 M/mL", delta="Normal")
        m2.metric(label="Motilidad Total", value="91%", delta="+1.2%")
        m3.metric(label="Progresivos", value="71%", delta="Óptimo")
        m4.metric(label="Anómalos", value="0%", delta="Estable")

        st.markdown("### ⚡ Cinemática Espermática (Sperm Kinetics)")
        k1, k2, k3, k4, k5, k6, k7, k8 = st.columns(8)
        k1.metric("VAP", "88")
        k2.metric("VSL", "183")
        k3.metric("VCL", "46")
        k4.metric("ALH", "06")
        k5.metric("STR", "65")
        k6.metric("LIN", "63")
        k7.metric("BCF", "67")
        k8.metric("MAD", "48")

elif menu == "Historial y Reportes":
    st.header("📋 Historial de Evaluaciones")
    df_demo = pd.DataFrame({
        "Toro": ["EQ-24", "EQ-25", "EQ-26"],
        "Evaluador": [nombre_completo, nombre_completo, nombre_completo],
        "Motilidad (%)": [91, 84, 79],
        "Concentración (M/mL)": [40.39, 35.10, 29.80]
    })
    st.dataframe(df_demo, use_container_width=True)

elif menu == "Configuración":
    st.header("⚙️ Configuración del Sistema")
    st.write(f"**Usuario actual:** {nombre_completo}")
    st.write("Versión del software: Bovi-Fertil-IA Pro v2.6 (High-Contrast)")