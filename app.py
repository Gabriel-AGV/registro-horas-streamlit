import streamlit as st
from streamlit_calendar import calendar
from datetime import date, timedelta, datetime
import pyrebase
import json
import calendar as cal

# --- Cargar configuración de Firebase ---
with open("firebase_config.json") as f:
    firebase_config = json.load(f)

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

# --- Configuración de Streamlit ---
st.set_page_config(page_title="Registro de Horas", layout="centered")

# --- Estado de sesión ---
if "user" not in st.session_state:
    st.session_state.user = None
if "login_successful" not in st.session_state:
    st.session_state.login_successful = False

# --- Login ---
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
            st.rerun()
        except:
            st.error("Error en el correo o contraseña.")

# --- Generar eventos del calendario ---
def generar_eventos(usuario):
    hoy = date.today()
    inicio = hoy.replace(day=1)
    ultimo = date(hoy.year, hoy.month, cal.monthrange(hoy.year, hoy.month)[1])

    registros = db.child("registros").get().val()
    registros_usuario = [r for r in registros.values() if r['usuario'] == usuario] if registros else []

    eventos = []
    dia = inicio
    while dia <= ultimo:
        if dia.weekday() < 5:  # Lunes a Viernes
            esperado = 9 if dia.weekday() < 4 else 7.5
            entrada = next((r for r in registros_usuario if r['fecha'] == dia.strftime('%Y-%m-%d')), None)

            if entrada:
                horas = float(entrada['horas'])
                color = "green" if horas >= esperado else "orange"
                titulo = f"{entrada['proyecto']} ({horas} h)"
            else:
                color = "white"
                titulo = "Sin registro"
        else:
            color = "red"
            titulo = "Feriado o fin de semana"

        eventos.append({
            "title": titulo,
            "start": dia.isoformat(),
            "allDay": True,
            "color": color
        })
        dia += timedelta(days=1)

    return eventos

# --- Registro de horas ---
def registro():
    st.title("Registro de Horas")

    correo = st.session_state.user["email"]
    st.markdown(f"**Usuario conectado:** {correo}")
    st.write("---")

    proyectos = ["Proyecto A", "Proyecto B", "Proyecto C"]
    proyecto = st.selectbox("Selecciona el proyecto", proyectos)
    categoria = st.selectbox("Selecciona tu categoría", ["Ing A", "Ing B", "Ing QP"])
    horas = st.number_input("Horas trabajadas", min_value=0.0, step=0.5)
    fecha = st.date_input("Selecciona la fecha", value=date.today())

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
            st.rerun()
        except:
            st.error("Error al guardar el registro.")

    # --- Calendario con colores ---
    st.write("---")
    st.subheader("Calendario de actividades")

    eventos = generar_eventos(correo)

    calendar(
        options={"initialView": "dayGridMonth", "selectable": False},
        events={"events": eventos},
        key="calendar"
    )

# --- Control de navegación ---
if st.session_state.user is None:
    login()
else:
    registro()

