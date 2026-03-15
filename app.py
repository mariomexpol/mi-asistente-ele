import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Asistente ELE")

st.title("🎓 Asistente para Profesores de Español")

# Sidebar para configuración
with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("API Key de Gemini", type="password")
    escuela = st.text_input("Nombre de la Escuela", "Mi Escuela")

# Cuerpo principal
tema = st.text_input("Tema de la clase")
nivel = st.selectbox("Nivel", ["A1", "A2", "B1", "B2", "C1", "C2"])
cantidad = st.number_input("Cantidad de ejercicios", min_value=1, value=10)

if st.button("🚀 Generar Material"):
    if not api_key:
        st.error("Por favor, introduce tu API Key.")
    elif not tema:
        st.error("Introduce un tema.")
    else:
        try:
            genai.configure(api_key=api_key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"Crea material de español nivel {nivel} sobre {tema}. Cantidad: {cantidad}. Incluye soluciones. Escuela: {escuela}"
            
            with st.spinner("Generando..."):
                response = model.generate_content(prompt)
                st.session_state['material'] = response.text
                st.success("¡Generado!")
        except Exception as e:
            st.error(f"Error: {e}")

if 'material' in st.session_state:
    st.divider()
    st.markdown(st.session_state['material'])
    st.download_button("📥 Descargar TXT", st.session_state['material'], file_name="clase.txt")
