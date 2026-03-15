import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Asistente E/LE", layout="wide")

st.title("🎓 Generador de Materiales E/LE")

with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("API Key", type="password")
    nombre_escuela = st.text_input("Escuela", "Mi Escuela")

tema = st.text_input("Tema de la clase")
nivel = st.selectbox("Nivel", ["A1", "A2", "B1", "B2", "C1", "C2"])
cantidad = st.number_input("Cantidad de ejercicios", min_value=1, value=5)

if st.button("🚀 Generar Material"):
    if not api_key or not tema:
        st.error("Falta la llave o el tema")
    else:
        try:
            # --- CONFIGURACIÓN PARA EVITAR EL ERROR 404 ---
            # Forzamos al cliente a usar la versión 'v1' en lugar de 'v1beta'
            from google.api_core import client_options
            options = client_options.ClientOptions(api_endpoint="generativelanguage.googleapis.com")
            
            genai.configure(api_key=api_key.strip(), client_options=options)
            
            # Usamos el nombre del modelo sin prefijos extraños
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"Profesor de español. Escuela: {nombre_escuela}. Nivel {nivel}. Tema: {tema}. Cantidad: {cantidad}. Incluye soluciones."
            
            with st.spinner("Generando contenido pedagógico..."):
                # Realizamos la llamada
                response = model.generate_content(prompt)
                
                if response.text:
                    st.success("¡Conexión exitosa!")
                    st.markdown(response.text)
                    st.session_state['resultado'] = response.text
                else:
                    st.error("La IA no devolvió texto.")
                    
        except Exception as e:
            # Si el error persiste, probamos el último recurso: gemini-pro (v1)
            st.warning("Ajustando ruta de conexión...")
            try:
                model_alt = genai.GenerativeModel('gemini-pro')
                response = model_alt.generate_content(prompt)
                st.session_state['resultado'] = response.text
                st.markdown(response.text)
            except Exception as e2:
                st.error(f"Error técnico: {e2}")

if 'resultado' in st.session_state:
    st.download_button("📥 Descargar TXT", st.session_state['resultado'], file_name="material.txt")
