import streamlit as st
import pyrebase
from datetime import date
import json

# Leer configuración Firebase
with open("firebase_config.json") as f:
    config = json.load(f)

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

st.set_page_config(page_title="Control de Horas", layout="centered")

# Inicializar estado
if "user" not in st.session_state:
    st.session_state.user = None

# Función de inicio de sesión
def login():
    st.title("Iniciar sesión")
    email = st.text_input("Correo")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Entrar"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.user = user
            st.success("Sesión iniciada correctamente.")
            st.experimental_rerun()
            return  # Evita seguir ejecutando después de login
        except Exception as e:
            st.error("Correo o contraseña inválidos.")

# Función principal con el formulario
def formulario():
    if not st.session_state.user:
        st.warning("Por favor inicia sesión.")
        st.stop()

    st.title("Registro de Horas")
    correo = st.session_state.user["email"]
    st.write(f"Sesión activa como: **{correo}**")

    # Obtener lista de proyectos desde Firebase
    proyectos_raw = db.child("proyectos").get().val()
    proyectos = list(proyectos_raw.values()) if proyectos_raw else []

    if not proyectos:
        st.warning("No hay proyectos disponibles. Contacta al administrador.")
        return

    proyecto = st.selectbox("Proyecto", proyectos)
    categoria = st.selectbox("Categoría", ["Ing A", "Ing B", "Ing QP"])
    horas = st.number_input("Horas trabajadas", min_value=0.0, step=0.5)
    fecha = st.date_input("Fecha", value=date.today())

    if st.button("Registrar horas"):
        db.child("registros").push({
            "usuario": correo,
            "proyecto": proyecto,
            "categoria": categoria,
            "horas": horas,
            "fecha": fecha.strftime('%Y-%m-%d')
        })
        st.success("Registro guardado correctamente.")

    # Zona para administrador
    if correo == "admin@empresa.cl":
        st.markdown("### 🔧 Agregar nuevo proyecto")
        nuevo = st.text_input("Nuevo nombre de proyecto")
        if st.button("Agregar proyecto"):
            if nuevo:
                db.child("proyectos").push(nuevo)
                st.success(f"Proyecto '{nuevo}' agregado.")
                st.experimental_rerun()

    # Cerrar sesión
    st.markdown("---")
    if st.button("Cerrar sesión"):
        st.session_state.user = None
        st.success("Sesión cerrada.")
        st.experimental_rerun()

# Control de flujo
if st.session_state.user is None:
    login()
else:
    formulario()

