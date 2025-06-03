import streamlit as st
from datetime import date
import pyrebase
import json

# Cargar configuración de Firebase
with open("firebase_config.json") as f:
    firebase_config = json.load(f)

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

st.set_page_config(page_title="Registro de Horas", layout="centered")

# Estado de sesión
if "user" not in st.session_state:
    st.session_state.user = None

# Función login
def login():
    st.title("Iniciar Sesión")
    email = st.text_input("Correo")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.user = user
            st.success("Sesión iniciada correctamente.")
            st.experimental_rerun()
            return  # Evita que el bloque siga corriendo
        except:
            st.error("Error en el correo o contraseña.")

# Función principal
def registro():
    st.title("Registro de Horas")

    correo = st.session_state.user["email"]
    st.markdown(f"**Usuario conectado:** {correo}")
    st.write("---")

    # Obtener proyectos desde Firebase
    try:
        proyectos_raw = db.child("proyectos").get().val()
        proyectos = list(proyectos_raw.values()) if proyectos_raw else []
    except:
        st.error("Error al cargar los proyectos.")
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
        except:
            st.error("No se pudo guardar el registro. Verifica la conexión o permisos.")

    # Sección de administración
    if correo == "admin@empresa.cl":
        st.markdown("### 🔧 Agregar nuevo proyecto")
        nuevo_proyecto = st.text_input("Nombre del nuevo proyecto")
        if st.button("Agregar proyecto"):
            if nuevo_proyecto:
                try:
                    db.child("proyectos").push(nuevo_proyecto)
                    st.success(f"Proyecto '{nuevo_proyecto}' agregado.")
                    st.experimental_rerun()
                except:
                    st.error("Error al agregar el proyecto.")

    # Cerrar sesión
    st.markdown("---")
    if st.button("Cerrar sesión"):
        st.session_state.user = None
        st.success("Sesión cerrada.")
        st.experimental_rerun()

# Lógica principal
if st.session_state.user is None:
    login()
else:
    registro()


