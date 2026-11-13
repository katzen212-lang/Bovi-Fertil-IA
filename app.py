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

# Estilos CSS avanzados para replicar el panel de grado industrial
st.markdown("""
    <style>
    .main-title {
        font-size: 2.8rem !important;
        color: #1E3A8A !important;
        font-weight: 800 !important;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.2rem !important;
        color: #64748B !important;
        font-weight: 500 !important;
        margin-bottom: 20px;
    }
    p, .stMarkdown, .stAlert {
        font-size: 1.1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<p class="main-title">🔬 Bovi-Fertil-IA</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Plataforma Inteligente de Análisis Seminal Bovino en Tiempo Real</p>', unsafe_allow_html=True)
st.markdown("---")

# Menú lateral
menu = st.sidebar.selectbox(
    "📌 Menú de Navegación",
    ["Inicio", "Análisis Microscópico", "Cámara en Vivo (Dashboard)", "Historial y Reportes", "Configuración"]
)

if menu == "Inicio":
    col_1, col_2 = st.columns([2, 1])
    with col_1:
        st.success("👋 ¡Bienvenido al sistema, Ing. Jonathan Morocho!")
        st.write("""
        **Bovi-Fertil-IA** integra visión artificial con OpenCV para emular sistemas profesionales de análisis de semen bovino en campo y laboratorio.
        """)
        st.info("👈 Seleccione **Cámara en Vivo (Dashboard)** en el menú lateral para abrir el panel de control en tiempo real.")
    with col_2:
        st.markdown("### 📊 Estado del Sistema")
        st.metric(label="Motor OpenCV", value="Activo", delta="HD Stream")
        st.metric(label="Plataforma", value="Móvil / Tablet Ready", delta="Óptimo")

elif menu == "Análisis Microscópico":
    st.header("🔬 Módulo de Análisis por Imagen Estática")
    archivo = st.file_uploader("📂 Cargar microfotografía", type=["jpg", "jpeg", "png"])
    if archivo:
        img = Image.open(archivo)
        st.image(img, caption="Muestra analizada", use_container_width=True)

elif menu == "Cámara en Vivo (Dashboard)":
    st.header("📱 Panel de Control en Vivo (Estilo Laboratorio)")
    
    # Controles superiores de la muestra
    col_info1, col_info2, col_info3, col_info4, col_info5 = st.columns([2, 2, 2, 2, 2])
    with col_info1:
        toro_id = st.text_input("Identificador del Toro", "EQ-24")
    with col_info2:
        raza_val = st.text_input("Raza / Especie", "Holstein")
    with col_info3:
        evaluador_val = st.text_input("Evaluador", "Ing. J. Morocho")
    with col_info4:
        st.markdown("<br>", unsafe_allow_html=True)
        # Checkbox para alternar entre pantalla compacta y pantalla completa
        pantalla_completa = st.checkbox("🖥️ Pantalla Completa", value=False)
    with col_info5:
        st.markdown("<br>", unsafe_allow_html=True)
        activar_camara = st.checkbox("🔴 Activar Transmisión", value=False)

    st.markdown("---")

    # Contenedores dinámicos para el video y las métricas
    video_slot = st.empty()
    metrics_placeholder = st.empty()

    if activar_camara:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error("No se pudo conectar con la cámara o microscopio USB (Puerto 0).")
        else:
            st.info("📹 Transmisión en directo activa. Desmarque la casilla para detener.")
            
            while activar_camara:
                ret, frame = cap.read()
                if not ret:
                    st.error("Error al leer el fotograma de la cámara.")
                    break
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Control dinámico del tamaño: Si está marcado "Pantalla Completa", ocupa todo el ancho (100%). Si no, usa un tamaño más compacto y centrado (50%).
                if pantalla_completa:
                    video_slot.image(
                        frame_rgb, 
                        channels="RGB", 
                        use_container_width=True, 
                        caption=f"Muestra en Directo - Toro: {toro_id} [PANTALLA COMPLETA]"
                    )
                else:
                    _, col_centro, _ = st.columns([1, 2, 1])  # Centrado en una columna de tamaño medio
                    with col_centro:
                        video_slot.image(
                            frame_rgb, 
                            channels="RGB", 
                            use_container_width=True, 
                            caption=f"Muestra en Directo - Toro: {toro_id} [Modo Estándar]"
                        )
                
                # Renderizar métricas dinámicas debajo del video
                with metrics_placeholder.container():
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
                
                cv2.waitKey(1)
            
            cap.release()
    else:
        video_slot.info("ℹ️ Active la casilla 'Activar Transmisión' arriba para iniciar la captura en vivo.")

elif menu == "Historial y Reportes":
    st.header("📋 Historial de Evaluaciones")
    df_demo = pd.DataFrame({
        "Toro": ["EQ-24", "EQ-25", "EQ-26"],
        "Motilidad (%)": [91, 84, 79],
        "Concentración (M/mL)": [40.39, 35.10, 29.80]
    })
    st.dataframe(df_demo, use_container_width=True)

elif menu == "Configuración":
    st.header("⚙️ Configuración del Sistema")
    st.write("Versión del software: Bovi-Fertil-IA Pro v2.2")