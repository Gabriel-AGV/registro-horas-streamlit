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

    # Refrescar el token para evitar errores HTTP
    try:
        user = auth.refresh(st.session_state.user['refreshToken'])
        st.session_state.user['idToken'] = user['idToken']
    except Exception:
        st.error("Tu sesión ha expirado. Por favor, vuelve a iniciar sesión.")
        st.session_state.user = None
        st.stop()

    st.title("Registro de Horas")
    correo = st.session_state.user["email"]
    st.write(f"Sesión activa como: **{correo}**")

    # Obtener lista de proyectos desde Firebase
    try:
        proyectos_raw = db.child("proyectos").get(st.session_state.user['idToken']).val()
        proyectos = list(proyectos_raw.values()) if proyectos_raw else []
    except Exception:
        st.error("Error al cargar proyectos. Verifica tu conexión o reglas de la base de datos.")
        st.stop()

    if not proyectos:
        st.warning("No hay proyectos disponibles.")
        return

    proyecto = st.selectbox("Proyecto", proyectos)
    categoria = st.selectbox("Categoría", ["Ing A", "Ing B", "Ing QP"])
    horas = st.number_input("Horas trabajadas", min_value=0.0, step=0.5)
    fecha = st.date_input("Fecha", value=date.today())

    if st.button("Registrar horas"):
        data = {
            "usuario": correo,
            "proyecto": proyecto,
            "categoria": categoria,
            "horas": horas,
            "fecha": fecha.strftime('%Y-%m-%d')
        }
        try:
            db.child("registros").push(data, st.session_state.user['idToken'])
            st.success("Registro guardado correctamente.")
        except Exception:
            st.error("Error al guardar el registro. Revisa tu conexión o autenticación.")

    # Sección exclusiva del administrador
    if correo == "admin@empresa.cl":
        st.markdown("### 🔧 Agregar nuevo proyecto")
        nuevo = st.text_input("Nuevo nombre de proyecto")
        if st.button("Agregar proyecto"):
            if nuevo:
                try:
                    db.child("proyectos").push(nuevo, st.session_state.user['idToken'])
                    st.success(f"Proyecto '{nuevo}' agregado.")
                    st.experimental_rerun()
                except Exception:
                    st.error("No se pudo agregar el proyecto.")

    # Botón cerrar sesión
    st.markdown("---")
    if st.button("Cerrar sesión"):
        st.session_state.user = None
        st.success("Sesión cerrada.")
        st.experimental_rerun()

