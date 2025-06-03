import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("Registro de Horas")

# Datos del formulario
usuario = st.text_input("Correo del trabajador")
proyecto = st.selectbox("Proyecto", ["Proyecto A", "Proyecto B"])
categoria = st.selectbox("Categoría", ["Ing A", "Ing B", "Ing QP"])
horas = st.number_input("Horas trabajadas", min_value=0.0, step=0.5)
fecha = st.date_input("Fecha", value=date.today())

if st.button("Guardar registro"):
    registro = {
        "usuario": usuario,
        "proyecto": proyecto,
        "categoria": categoria,
        "horas": horas,
        "fecha": fecha.strftime('%Y-%m-%d')
    }
    db.collection("registros").add(registro)
    st.success("Registro guardado correctamente.")

