import streamlit as st
from datetime import date
import pyrebase
import json

# --- Cargar configuración de Firebase ---
with open("firebase_config.json") as f:
    firebase_config = json.load(f)

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

# --- Configuración inicial ---
st.set_page_config(page_title="Registro de Horas", layout="centered")

# --- Estado de sesión ---
if "user" not in st.session_state:
    st.session_state.user = None
if "login_successful" not in st.session_state:
    st.session_state.login_successful = False

# --- Función de login ---
def login():
    st.title("Iniciar Sesión")

    email = st.text_input("Correo")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.user = user
            st.session_state.login_successful = True
            st.success("Sesión iniciada correctamente.")
            st.experimental_rerun()
        except Exception as e:
            st.error("Error en el correo o contraseña.")

# --- Función principal de registro ---
def registro():
    st.title("Registro de Horas")

    correo = st.session_state.user["email"]
    st.markdown(f"**Usuario conectado:** {correo}")
    st.write("---")

    # --- Obtener proyectos ---
    try:
        proyectos_raw = db.child("proyectos").get().val()
        if isinstance(proyectos_raw, list):
            proyectos = [p for p in proyectos_raw if p]
        elif isinstance(proyectos_raw, dict):
            proyectos = list(proyectos_raw.values())
        else:
            proyectos = []
    except:
        proyectos = []

    if not proyectos:
        st.warning("No hay proyectos disponibles. Contacta al administrador.")
        return

    proyecto = st.selectbox("Selecciona el proyecto", proyectos)
    categoria = st.selectbox("Selecciona tu categoría", ["Ing A", "Ing B", "Ing QP"])
    horas = st.number_input("Horas trabajadas", min_value=0.0, step=0.5)
    fecha = st.date_input("Fecha", value=date.today())

    if st.button("Registrar"):
        data = {
            "usuario": correo,
            "proyecto": proyecto,
            "categoria": categoria,
            "horas": horas,
            "fecha": fecha.strftime('%Y-%m-%d')
        }
        try:
            db.child("registros").push(data)
            st.success("Registro guardado correctamente.")
            st.experimental_rerun()
        except:
            st.error("Error al guardar el registro en Firebase.")

# --- Control de navegación ---
if st.session_state.user is None:
    login()
else:
    registro()

