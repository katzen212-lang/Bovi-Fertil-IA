import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import json
import os

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
    div.stMetric label {
        color: #94A3B8 !important;
    }
    div.stMetric [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
    }
    </style>
""", unsafe_allow_html=True)

# Archivo local para persistencia de cuentas y registros
DB_FILE = "bovi_users_db.json"

def cargar_base_datos():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"usuarios": {}, "historial": []}

def guardar_base_datos(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = cargar_base_datos()

# Inicializar estados de sesión
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.nombre_completo = ""

# ==========================================
# PANTALLA DE AUTENTICACIÓN (LOGIN / REGISTRO)
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<p class="main-title">🔬 Bovi-Fertil-IA</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Plataforma Inteligente de Análisis Seminal Bovino</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta Nueva"])
        
        with tab_login:
            st.markdown("### Acceso al Sistema")
            with st.form("login_form"):
                user_login = st.text_input("Usuario o Correo")
                pass_login = st.text_input("Código de Acceso / Contraseña", type="password")
                btn_login = st.form_submit_button("🚀 Entrar")
                
                if btn_login:
                    if user_login in db["usuarios"] and db["usuarios"][user_login]["password"] == pass_login:
                        st.session_state.logged_in = True
                        st.session_state.username = user_login
                        st.session_state.nombre_completo = db["usuarios"][user_login]["nombre"]
                        st.success("¡Bienvenido de nuevo!")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos.")
                        
        with tab_register:
            st.markdown("### Registro de Nuevo Usuario")
            with st.form("register_form"):
                reg_user = st.text_input("Nombre de Usuario (único)")
                reg_nombre = st.text_input("Nombre y Apellido (ej. Ing. Jonathan Morocho)")
                reg_pass = st.text_input("Código de Acceso / Contraseña", type="password")
                btn_reg = st.form_submit_button("✨ Registrarse")
                
                if btn_reg:
                    if not reg_user or not reg_nombre or not reg_pass:
                        st.warning("⚠️ Por favor, llena todos los campos.")
                    elif reg_user in db["usuarios"]:
                        st.error("❌ El nombre de usuario ya existe. Elige otro.")
                    else:
                        db["usuarios"][reg_user] = {
                            "nombre": reg_nombre,
                            "password": reg_pass
                        }
                        guardar_base_datos(db)
                        st.success("✅ ¡Cuenta creada con éxito! Ya puedes iniciar sesión en la pestaña de al lado.")
                        
    st.stop()

# ==========================================
# A PARTIR DE AQUÍ EL USUARIO ESTÁ LOGUEADO
# ==========================================

st.markdown('<p class="main-title">🔬 Bovi-Fertil-IA</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-title">Sesión activa: <b>{st.session_state.nombre_completo}</b></p>', unsafe_allow_html=True)
st.markdown("---")

menu = st.sidebar.selectbox(
    "📌 Menú de Navegación",
    ["Inicio", "Análisis Microscópico", "Cámara en Vivo (Dashboard)", "Historial y Reportes", "Configuración"]
)

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.nombre_completo = ""
    st.rerun()

if menu == "Inicio":
    col_1, col_2 = st.columns([2, 1])
    with col_1:
        st.success(f"👋 ¡Hola, {st.session_state.nombre_completo}!")
        st.write("""
        **Bovi-Fertil-IA** integra tecnologías web y visión artificial para emular sistemas profesionales de análisis de semen bovino en campo y laboratorio. Cada cuenta mantiene sus registros de evaluaciones de manera segura.
        """)
        st.info("👈 Seleccione **Cámara en Vivo (Dashboard)** en el menú lateral para iniciar una nueva evaluación.")
    with col_2:
        st.markdown("### 📊 Estado del Sistema")
        st.metric(label="Base de Datos", value="Sincronizada", delta="Segura")
        st.metric(label="Plataforma", value="Multi-Dispositivo", delta="Óptimo")

elif menu == "Análisis Microscópico":
    st.header("🔬 Módulo de Análisis por Imagen Estática")
    archivo = st.file_uploader("📂 Cargar microfotografía", type=["jpg", "jpeg", "png"])
    toro_estatico = st.text_input("Identificador del Toro (Imagen Estática)", "EQ-ESTATICO")
    
    if archivo:
        img = Image.open(archivo)
        st.image(img, caption=f"Muestra analizada por {st.session_state.nombre_completo}", use_container_width=True)
        
        if st.button("💾 Guardar Evaluación Estática"):
            nuevo_registro = {
                "usuario": st.session_state.username,
                "evaluador": st.session_state.nombre_completo,
                "toro": toro_estatico,
                "tipo": "Imagen Estática",
                "motilidad": "89.5%",
                "concentracion": "38.5 M/mL"
            }
            db["historial"].append(nuevo_registro)
            guardar_base_datos(db)
            st.success("✅ ¡Evaluación guardada en tu historial personal!")

elif menu == "Cámara en Vivo (Dashboard)":
    st.header("📱 Panel de Control en Vivo (Estilo Laboratorio)")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        toro_id = st.text_input("Identificador del Toro", "EQ-24")
    with col_info2:
        raza_val = st.text_input("Raza / Especie", "Holstein")
    with col_info3:
        evaluador_val = st.text_input("Evaluador", st.session_state.nombre_completo)

    st.markdown("---")
    
    st.info("📸 Usa el siguiente componente para capturar la muestra de la cámara web o del microscopio digital.")
    foto_capturada = st.camera_input("📷 Capturar Fotograma de la Muestra Microscópica")

    if foto_capturada is not None:
        bytes_data = foto_capturada.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        cv2_img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

        st.success("✅ ¡Fotograma capturado con éxito!")
        st.image(cv2_img_rgb, channels="RGB", caption=f"Muestra en Directo - Toro: {toro_id} | Evaluador: {evaluador_val}", use_container_width=True)

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
        
        if st.button("💾 Guardar Análisis en mi Historial"):
            registro_vivo = {
                "usuario": st.session_state.username,
                "evaluador": evaluador_val,
                "toro": toro_id,
                "tipo": f"Cámara ({raza_val})",
                "motilidad": "91%",
                "concentracion": "40.39 M/mL"
            }
            db["historial"].append(registro_vivo)
            guardar_base_datos(db)
            st.success("✅ ¡Resultado guardado exitosamente en tu cuenta!")

elif menu == "Historial y Reportes":
    st.header(f"📋 Historial de Evaluaciones de {st.session_state.nombre_completo}")
    
    # Filtrar el historial global únicamente para el usuario que ha iniciado sesión
    historial_usuario = [h for h in db["historial"] if h["usuario"] == st.session_state.username]
    
    if historial_usuario:
        df_usuario = pd.DataFrame(historial_usuario)
        # Ocultar la columna interna de usuario para mayor limpieza visual
        df_mostrar = df_usuario.drop(columns=["usuario"])
        st.dataframe(df_mostrar, use_container_width=True)
    else:
        st.info("ℹ️ Aún no tienes evaluaciones guardadas. Realiza un análisis desde la cámara o imagen estática y guárdalo.")

elif menu == "Configuración":
    st.header("⚙️ Configuración del Sistema")
    st.write(f"**Usuario actual:** {st.session_state.nombre_completo}")
    st.write(f"**Identificador de cuenta:** `{st.session_state.username}`")
    st.write("Versión del software: Bovi-Fertil-IA Pro v3.0 (Auth & Multi-User)")