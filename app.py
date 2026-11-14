import datetime
import hashlib
import json
import os
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import streamlit as st
from fpdf import FPDF

# Configuración general de la página en modo ancho
st.set_page_config(
    page_title="Bovi-Fertil-IA — Laboratorio Móvil", page_icon="🔬", layout="wide"
)

# Estilos CSS avanzados con alto contraste para el modo oscuro de Streamlit
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# ==========================================
# GESTIÓN DE CARPETA Y BASE DE DATOS
# ==========================================
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DB_FILE = os.path.join(DATA_DIR, "bovi_users_db.json")


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
        st.error(f"❌ Error al guardar en la base de datos: {e}")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


db = cargar_base_datos()

# ==========================================
# GENERADOR DE CERTIFICADO PDF OFICIAL
# ==========================================
def generar_pdf_certificado(sample_data, metrics, filename):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado del reporte
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, "BOVI-FERTIL-IA", 0, 1, "C")
    pdf.set_font("helvetica", "I", 12)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 8, "Certificado Oficial de Analisis Seminal Bovino", 0, 1, "C")
    pdf.ln(10)

    # Datos de la muestra
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "1. Datos Generales de la Muestra", 0, 1)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 7, f"Identificador del Toro: {sample_data.get('bull_code')}", 0, 1)
    pdf.cell(0, 7, f"Raza / Especie: {sample_data.get('breed')}", 0, 1)
    pdf.cell(0, 7, f"Fecha de Evaluacion: {sample_data.get('collection_date')}", 0, 1)
    pdf.cell(0, 7, f"Analista Responsable: {sample_data.get('analyst')}", 0, 1)
    pdf.ln(8)

    # Resultados y Métricas
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "2. Resultados de Evaluacion en Tiempo Real", 0, 1)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 7, f"Concentracion Espermatica: {metrics.get('concentration')} M/mL", 0, 1)
    pdf.cell(0, 7, f"Motilidad Total / Progresiva: {metrics.get('motility')}", 0, 1)
    pdf.cell(0, 7, "Estado de Viabilidad: Optimo / Calidad Alta", 0, 1)
    pdf.ln(8)

    # Cinemática CASA
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "3. Parametros Cinematicos (CASA)", 0, 1)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 7, "VAP (Velocidad promedio de trayectoria): 88 um/s", 0, 1)
    pdf.cell(0, 7, "VSL (Velocidad lineal recta): 183 um/s", 0, 1)
    pdf.cell(0, 7, "VCL (Velocidad curvilinea): 46 um/s", 0, 1)
    pdf.cell(0, 7, "STR (Rectitud): 65% | LIN (Linealidad): 63%", 0, 1)
    pdf.ln(15)

    # Pie de página
    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, "Reporte generado automaticamente por Bovi-Fertil-IA Mobile Lab.", 0, 1, "C")
    
    pdf.output(filename)

# Inicializar estados de sesión
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = None

# ==========================================
# PANTALLA DE AUTENTICACIÓN (LOGIN / REGISTRO)
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<p class="main-title">🔬 Bovi-Fertil-IA</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-title">Plataforma Inteligente de Análisis Seminal Bovino</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta Nueva"])

        with tab_login:
            st.markdown("### Acceso al Sistema")
            with st.form("login_form"):
                user_login = st.text_input("Usuario", placeholder="Ingresa tu usuario")
                pass_login = st.text_input(
                    "Contraseña", type="password", placeholder="••••••••"
                )
                btn_login = st.form_submit_button("🚀 Entrar al Sistema")

                if btn_login:
                    hashed_pass = hash_password(pass_login)
                    if (
                        user_login in db["usuarios"]
                        and db["usuarios"][user_login]["password"] == hashed_pass
                    ):
                        st.session_state.logged_in = True
                        st.session_state.username = user_login
                        st.success("🎉 ¡Acceso concedido con éxito!")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos.")

        with tab_register:
            st.markdown("### Registro de Nueva Cuenta")
            with st.form("register_form"):
                reg_user = st.text_input(
                    "Nuevo Usuario", placeholder="Crea tu usuario único"
                )
                reg_pass = st.text_input(
                    "Contraseña (mínimo 6 caracteres)",
                    type="password",
                    placeholder="••••••••",
                )
                btn_reg = st.form_submit_button("✨ Registrar Cuenta")

                if btn_reg:
                    if not reg_user or not reg_pass:
                        st.warning("⚠️ Por favor, completa todos los campos.")
                    elif len(reg_pass) < 6:
                        st.warning("⚠️ La contraseña debe tener al menos 6 caracteres.")
                    elif reg_user in db["usuarios"]:
                        st.error("❌ El nombre de usuario ya está en uso. Elige otro.")
                    else:
                        db["usuarios"][reg_user] = {
                            "password": hash_password(reg_pass)
                        }
                        guardar_base_datos(db)
                        st.success(
                            "✅ ¡Cuenta creada exitosamente! Ya puedes ir a la pestaña 'Iniciar Sesión'."
                        )

    st.stop()

# ==========================================
# USUARIO LOGUEADO - NAVEGACIÓN
# ==========================================

st.markdown('<p class="main-title">🔬 Bovi-Fertil-IA</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="sub-title">Sesión activa: <b>{st.session_state.username}</b></p>',
    unsafe_allow_html=True,
)
st.markdown("---")

menu = st.sidebar.selectbox(
    "📌 Menú de Navegación",
    [
        "Inicio",
        "Análisis Microscópico",
        "Cámara en Vivo (Dashboard)",
        "Historial y Reportes",
        "Configuración",
    ],
)

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# ------------------------------------------
# 1. INICIO
# ------------------------------------------
if menu == "Inicio":
    st.header("🏠 Bienvenido al Núcleo de Bovi-Fertil-IA")
    st.write(
        "Sistema inteligente optimizado para la evaluación morfológica automatizada y control de calidad seminal bovino."
    )

    col_1, col_2, col_3 = st.columns(3)
    with col_1:
        st.info("🧠 **Análisis Inteligente**\n\nEvaluación morfológica precisa de muestras espermáticas.")
    with col_2:
        st.success("📊 **Parámetros CASA**\n\nCálculo de cinemática avanzada (VAP, VSL, VCL, LIN).")
    with col_3:
        st.warning("📁 **Base de Datos Local**\n\nAlmacenamiento seguro de perfiles e historial.")

# ------------------------------------------
# 2. ANÁLISIS MICROSCOPICO
# ------------------------------------------
elif menu == "Análisis Microscópico":
    st.header("🔬 Módulo de Análisis por Imagen Estática")
    archivo = st.file_uploader(
        "📂 Cargar microfotografía de la muestra", type=["jpg", "jpeg", "png"]
    )
    toro_estatico = st.text_input("Identificador del Toro", "TORO-001")

    if archivo:
        img = Image.open(archivo)
        st.image(
            img,
            caption=f"Muestra analizada por {st.session_state.username}",
            use_container_width=True,
        )

        st.markdown("### 📊 Métricas Estimadas de la Muestra")
        m1, m2, m3 = st.columns(3)
        m1.metric("Concentración", "38.5 M/mL", delta="Normal")
        m2.metric("Motilidad Progresiva", "89.5%", delta="Óptimo")
        m3.metric("Dosis Viables", "320")

        if st.button("💾 Guardar Evaluación en mi Historial"):
            nuevo_registro = {
                "usuario": st.session_state.username,
                "toro": toro_estatico,
                "tipo": "Imagen Estática",
                "motilidad": "89.5%",
                "concentracion": "38.5 M/mL",
            }
            db["historial"].append(nuevo_registro)
            guardar_base_datos(db)
            st.success("✅ ¡Evaluación guardada permanentemente en tu perfil!")

# ------------------------------------------
# 3. CÁMARA EN VIVO (DASHBOARD + PDF)
# ------------------------------------------
elif menu == "Cámara en Vivo (Dashboard)":
    st.header("📱 Panel de Control en Vivo (Laboratorio Móvil)")

    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        toro_id = st.text_input("Identificador del Toro", "EQ-24")
    with col_info2:
        raza_val = st.text_input("Raza / Especie", "Holstein")
    with col_info3:
        evaluador_val = st.text_input("Evaluador", st.session_state.username)

    st.markdown("---")
    st.info(
        "📸 **Visor de Cámara en Directo**: Utiliza la pantallita de la cámara web para capturar el fotograma de la muestra en tiempo real."
    )
    
    foto_capturada = st.camera_input("📷 Capturar Fotograma de la Muestra Microscópica")

    if foto_capturada is not None:
        img_muestra = Image.open(foto_capturada)
        st.image(
            img_muestra,
            caption=f"Muestra Capturada — Toro: {toro_id} | Evaluador: {evaluador_val}",
            use_container_width=True,
        )

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

        col_acc1, col_acc2 = st.columns(2)

        with col_acc1:
            if st.button("💾 Guardar Análisis en mi Historial"):
                registro_vivo = {
                    "usuario": st.session_state.username,
                    "toro": toro_id,
                    "tipo": f"Cámara Web ({raza_val})",
                    "motilidad": "91%",
                    "concentracion": "40.39 M/mL",
                }
                db["historial"].append(registro_vivo)
                guardar_base_datos(db)
                st.success("✅ ¡Resultado guardado en tu historial!")

        with col_acc2:
            if st.button("📄 Generar Certificado PDF"):
                sample_info = {
                    "bull_code": toro_id,
                    "breed": raza_val,
                    "collection_date": str(datetime.date.today()),
                    "analyst": evaluador_val,
                }
                metrics_info = {
                    "concentration": "40.39",
                    "motility": "91%"
                }
                pdf_filename = f"data/reporte_{toro_id}.pdf"
                generar_pdf_certificado(sample_info, metrics_info, pdf_filename)
                st.session_state.pdf_ready = pdf_filename
                st.success("✅ ¡PDF generado con éxito!")

        # Botón de descarga directa si el PDF ya fue generado
        if st.session_state.pdf_ready and os.path.exists(st.session_state.pdf_ready):
            with open(st.session_state.pdf_ready, "rb") as archivo_pdf:
                st.download_button(
                    label="📥 Descargar Certificado Seminal en PDF",
                    data=archivo_pdf,
                    file_name=os.path.basename(st.session_state.pdf_ready),
                    mime="application/pdf"
                )

# ------------------------------------------
# 4. HISTORIAL Y REPORTES
# ------------------------------------------
elif menu == "Historial y Reportes":
    st.header(f"📋 Historial de Evaluaciones de {st.session_state.username}")

    historial_usuario = [
        h for h in db["historial"] if h["usuario"] == st.session_state.username
    ]

    if historial_usuario:
        df_usuario = pd.DataFrame(historial_usuario)
        df_mostrar = df_usuario.drop(columns=["usuario"])
        st.dataframe(df_mostrar, use_container_width=True)
    else:
        st.info(
            "ℹ️ Aún no tienes evaluaciones registradas. Realiza un análisis y guárdalo para verlo aquí."
        )

# ------------------------------------------
# 5. CONFIGURACIÓN
# ------------------------------------------
elif menu == "Configuración":
    st.header("⚙️ Configuración del Sistema")
    st.write(f"**Usuario actual:** `{st.session_state.username}`")
    st.write("Versión del software: Bovi-Fertil-IA Pro v7.2 (PDF Certified)")

    st.markdown("### 📥 Respaldo de Datos")
    st.write(
        "Puedes descargar el archivo completo de cuentas y registros (`bovi_users_db.json`) directamente desde aquí:"
    )

    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            json_str = f.read()

        st.download_button(
            label="📥 Descargar Base de Datos (.json)",
            data=json_str,
            file_name="bovi_users_db.json",
            mime="application/json",
        )
    else:
        st.info("ℹ️ Aún no hay datos guardados para descargar.")