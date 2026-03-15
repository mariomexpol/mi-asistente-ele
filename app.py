import streamlit as st
import google.generativeai as genai

st.title("Generador E/LE (Versión Estable)")

with st.sidebar:
    api_key = st.text_input("API Key", type="password")
    st.info("Asegúrate de que sea de aistudio.google.com")

tema = st.text_input("Tema de la clase")
nivel = st.selectbox("Nivel", ["A1", "A2", "B1", "B2", "C1", "C2"])

if st.button("🚀 Generar Material"):
    if not api_key or not tema:
        st.error("Faltan datos")
    else:
        try:
            genai.configure(api_key=api_key.strip())
            
            # TRUCO FINAL: Usamos la ruta completa del modelo para evitar el error 404
            # Probamos primero con esta ruta específica
            model = genai.GenerativeModel(model_name='models/gemini-1.5-flash-latest')
            
            prompt = f"Crea material de español nivel {nivel} sobre {tema} con soluciones."
            
            with st.spinner("Conectando con el servidor de Google..."):
                response = model.generate_content(prompt)
                
                if response.text:
                    st.success("¡Por fin! Generado con éxito.")
                    st.markdown(response.text)
                    st.session_state['cache'] = response.text
                else:
                    st.warning("Respuesta vacía.")
                    
        except Exception as e:
            # Si el anterior falla, el código intenta la versión Pro automáticamente
            st.warning("Reintentando con modelo de respaldo...")
            try:
                model_alt = genai.GenerativeModel(model_name='models/gemini-1.0-pro')
                response = model_alt.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e2:
                st.error(f"Error persistente: {e2}")

if 'cache' in st.session_state:
    st.download_button("Descargar TXT", st.session_state['cache'], file_name="material.txt")
