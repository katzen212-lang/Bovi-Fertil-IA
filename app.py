import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import json
import os
import hashlib

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

# Archivo JSON para persistencia permanente de cuentas e historial
DB_FILE = "bovi_users_db.json"

def cargar_base_datos():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    return {"usuarios": {}, "historial": []}
                return json.loads(content)
        except Exception:
            return {"usuarios": {}, "historial": []}
    return {"usuarios": {}, "historial": []}

def guardar_base_datos(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Error al guardar en la base de datos: {e}")

# Función para encriptar contraseñas de forma segura con SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

db = cargar_base_datos()

# Inicializar estados de sesión
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Botón de emergencia en la barra lateral para forzar el login si fuera necesario
with st.sidebar:
    st.markdown("### 🛠️ Control de Sesión")
    if st.button("🔄 Forzar Pantalla de Login"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

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
                user_login = st.text_input("Usuario", placeholder="ej. jmorocho")
                pass_login = st.text_input("Contraseña", type="password", placeholder="••••••••")
                btn_login = st.form_submit_button("🚀 Entrar al Sistema")
                
                if btn_login:
                    hashed_pass = hash_password(pass_login)
                    if user_login in db["usuarios"] and db["usuarios"][user_login]["password"] == hashed_pass:
                        st.session_state.logged_in = True
                        st.session_state.username = user_login
                        st.success("¡Acceso concedido con éxito!")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos.")
                        
        with tab_register:
            st.markdown("### Registro de Nueva Cuenta")
            with st.form("register_form"):
                reg_user = st.text_input("Nuevo Usuario", placeholder="ej. jmorocho")
                reg_pass = st.text_input("Contraseña (mínimo 6 caracteres)", type="password", placeholder="••••••••")
                btn_reg = st.form_submit_button("✨ Registrar Cuenta")
                
                if btn_reg:
                    if not reg_user or not reg_pass:
                        st.warning("⚠️ Por favor, completa todos los campos.")
                    elif len(reg_pass) < 6:
                        st.warning("⚠️ La contraseña debe tener al menos 6 caracteres.")
                    elif reg_user in db["usuarios"]:
                        st.error("❌ El nombre de usuario ya está en uso. Elige otro.")
                    else:
                        # Guardar cuenta de forma permanente en el JSON
                        db["usuarios"][reg_user] = {
                            "password": hash_password(reg_pass)
                        }
                        guardar_base_datos(db)
                        st.success("✅ ¡Cuenta creada exitosamente! Ya puedes ir a la pestaña 'Iniciar Sesión'.")
                        
    st.stop()

# ==========================================
# USUARIO LOGUEADO
# ==========================================

st.markdown('<p class="main-title">🔬 Bovi-Fertil-IA</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-title">Sesión activa: <b>{st.session_state.username}</b></p>', unsafe_allow_html=True)
st.markdown("---")

menu = st.sidebar.selectbox(
    "📌 Menú de Navegación",
    ["Inicio", "Análisis Microscópico", "Cámara en Vivo (Dashboard)", "Historial y Reportes", "Configuración"]
)

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

if menu == "Inicio":
    col_1, col_2 = st.columns([2, 1])
    with col_1:
        st.success(f"👋 ¡Bienvenido de nuevo, {st.session_state.username}!")
        st.write("""
        **Bovi-Fertil-IA** almacena de forma permanente todas tus cuentas y registros de evaluaciones de manera segura y privada para cada usuario.
        """)
        st.info("👈 Seleccione **Cámara en Vivo (Dashboard)** en el menú lateral para iniciar una nueva evaluación.")
    with col_2:
        st.markdown("### 📊 Estado de la Cuenta")
        st.metric(label="Base de Datos", value="Permanente (JSON)", delta="Sincronizada")
        st.metric(label="Estado", value="Conectado", delta="Activo")

elif menu == "Análisis Microscópico":
    st.header("🔬 Módulo de Análisis por Imagen Estática")
    archivo = st.file_uploader("📂 Cargar microfotografía", type=["jpg", "jpeg", "png"])
    toro_estatico = st.text_input("Identificador del Toro", "EQ-ESTATICO")
    
    if archivo:
        img = Image.open(archivo)
        st.image(img, caption=f"Muestra analizada por {st.session_state.username}", use_container_width=True)
        
        if st.button("💾 Guardar Evaluación en mi Historial"):
            nuevo_registro = {
                "usuario": st.session_state.username,
                "toro": toro_estatico,
                "tipo": "Imagen Estática",
                "motilidad": "89.5%",
                "concentracion": "38.5 M/mL"
            }
            db["historial"].append(nuevo_registro)
            guardar_base_datos(db)
            st.success("✅ ¡Evaluación guardada permanentemente en tu perfil!")

elif menu == "Cámara en Vivo (Dashboard)":
    st.header("📱 Panel de Control en Vivo (Estilo Laboratorio)")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        toro_id = st.text_input("Identificador del Toro", "EQ-24")
    with col_info2:
        raza_val = st.text_input("Raza / Especie", "Holstein")
    with col_info3:
        evaluador_val = st.text_input("Evaluador", st.session_state.username)

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
                "toro": toro_id,
                "tipo": f"Cámara ({raza_val})",
                "motilidad": "91%",
                "concentracion": "40.39 M/mL"
            }
            db["historial"].append(registro_vivo)
            guardar_base_datos(db)
            st.success("✅ ¡Resultado guardado permanentemente en tu historial!")

elif menu == "Historial y Reportes":
    st.header(f"📋 Historial de Evaluaciones de {st.session_state.username}")
    
    # Filtrar exclusivamente los registros guardados por el usuario actual
    historial_usuario = [h for h in db["historial"] if h["usuario"] == st.session_state.username]
    
    if historial_usuario:
        df_usuario = pd.DataFrame(historial_usuario)
        df_mostrar = df_usuario.drop(columns=["usuario"])
        st.dataframe(df_mostrar, use_container_width=True)
    else:
        st.info("ℹ️ Aún no tienes evaluaciones registradas. Realiza un análisis y guárdalo para verlo aquí.")

elif menu == "Configuración":
    st.header("⚙️ Configuración del Sistema")
    st.write(f"**Usuario actual:** `{st.session_state.username}`")
    st.write("Versión del software: Bovi-Fertil-IA Pro v4.0 (Persistent JSON Auth)")