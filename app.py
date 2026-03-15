import streamlit as st
import google.generativeai as genai
from google.generativeai.types import RequestOptions

st.set_page_config(page_title="Asistente E/LE Pro", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Mi Institución")
    logo_file = st.file_uploader("Subir logo de la escuela", type=["png", "jpg", "jpeg"])
    if logo_file:
        st.image(logo_file, width=150)
    nombre_escuela = st.text_input("Nombre de la Escuela", "Mi Escuela de Español")
    api_key = st.text_input("API Key de Gemini", type="password")

# --- INTERFAZ ---
st.title("🎓 Generador de Materiales E/LE")

col1, col2 = st.columns(2)
with col1:
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    tema = st.text_input("Tema de la clase")
    modulo = st.radio("Módulo", ["Ejercicios", "Texto con Preguntas"])

with col2:
    cantidad = st.number_input("Cantidad de ítems", min_value=1, value=10)
    tecnicas = st.multiselect("Técnicas", 
        ["Test de Cloze", "Rellenar huecos", "Traducción", "Corregir errores", "Ordenar frases", "Relacionar", "Completar diálogo"])

if st.button("🚀 Generar Material"):
    if not api_key:
        st.error("Introduce la API Key")
    else:
        try:
            # CONFIGURACIÓN MAESTRA PARA EVITAR EL 404
            genai.configure(api_key=api_key.strip())
            
            # Forzamos el uso de la API v1 (estable) en lugar de v1beta
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"Profesor de español. Escuela: {nombre_escuela}. Nivel {nivel}. Tema: {tema}. Módulo: {modulo}. Técnicas: {tecnicas}. Cantidad: {cantidad}. Incluye soluciones."
            
            with st.spinner("Conectando con el servidor estable..."):
                # Aquí está el truco: añadimos RequestOptions para forzar la versión de la API
                response = model.generate_content(
                    prompt,
                    request_options=RequestOptions(api_version='v1')
                )
                
                if response.text:
                    st.session_state['contenido'] = response.text
                    st.success("¡Generado correctamente!")
                else:
                    st.error("No se recibió texto.")
        except Exception as e:
            # Si falla el 1.5, intentamos el 1.0 Pro que es el más compatible
            st.warning("Ajustando compatibilidad...")
            try:
                model_alt = genai.GenerativeModel('gemini-pro')
                response = model_alt.generate_content(prompt, request_options=RequestOptions(api_version='v1'))
                st.session_state['contenido'] = response.text
                st.success("¡Generado con modelo de respaldo!")
            except Exception as e2:
                st.error(f"Error final: {e2}")

# --- MOSTRAR ---
if 'contenido' in st.session_state:
    st.divider()
    st.subheader(f"📄 {nombre_escuela}")
    st.markdown(st.session_state['contenido'])
    st.download_button("📥 Descargar TXT", st.session_state['contenido'], file_name="material.txt")
