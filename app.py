import streamlit as st
import pyrebase
from datetime import date
import json

# Cargar configuración Firebase
with open("firebase_config.json") as f:
    config = json.load(f)

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

st.set_page_config(page_title="Control de Horas", layout="centered")

if "user" not in st.session_state:
    st.session_state.user = None

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
        except Exception as e:
            st.error("Correo o contraseña inválidos.")

def formulario():
    st.title("Registro de Horas")
    email = st.session_state.user["email"]
    st.write(f"Sesión activa como: {email}")

    proyectos = db.child("proyectos").get().val()
    proyectos = list(proyectos.values()) if proyectos else []

    if not proyectos:
        st.warning("No hay proyectos disponibles.")
        return

    proyecto = st.selectbox("Proyecto", proyectos)
    categoria = st.selectbox("Categoría", ["Ing A", "Ing B", "Ing QP"])
    horas = st.number_input("Horas trabajadas", min_value=0.0, step=0.5)
    fecha = st.date_input("Fecha", value=date.today())

    if st.button("Registrar"):
        db.child("registros").push({
            "usuario": email,
            "proyecto": proyecto,
            "categoria": categoria,
            "horas": horas,
            "fecha": fecha.strftime('%Y-%m-%d')
        })
        st.success("Registro guardado.")

    if email == "admin@empresa.cl":
        st.markdown("### 🔧 Agregar nuevo proyecto")
        nuevo = st.text_input("Nuevo proyecto")
        if st.button("Agregar proyecto"):
            if nuevo:
                db.child("proyectos").push(nuevo)
                st.success("Proyecto agregado.")
                st.experimental_rerun()

# Lógica principal
if st.session_state.user is None:
    login()
else:
    formulario()

