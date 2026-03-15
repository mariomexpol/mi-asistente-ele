import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Asistente E/LE", layout="wide")

st.title("🎓 Generador de Materiales E/LE")

# Barra lateral
with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("API Key", type="password")
    nombre_escuela = st.text_input("Escuela", "Mi Escuela")

# Campos
tema = st.text_input("Tema de la clase")
nivel = st.selectbox("Nivel", ["A1", "A2", "B1", "B2", "C1", "C2"])
cantidad = st.number_input("Cantidad", min_value=1, value=5)

if st.button("🚀 Generar Material"):
    if not api_key or not tema:
        st.error("Falta la llave o el tema")
    else:
        try:
            # Configuración simple
            genai.configure(api_key=api_key.strip())
            
            # Usamos el modelo flash
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"Actúa como profesor de español. Crea {cantidad} ejercicios nivel {nivel} sobre {tema}. Incluye soluciones. Escuela: {nombre_escuela}."
            
            with st.spinner("Generando contenido..."):
                # Llamada estándar sin opciones complejas
                response = model.generate_content(prompt)
                
                if response.text:
                    st.success("¡Logrado!")
                    st.markdown(response.text)
                    st.session_state['resultado'] = response.text
                else:
                    st.error("La IA no devolvió texto.")
                    
        except Exception as e:
            st.error(f"Error: {e}")

if 'resultado' in st.session_state:
    st.download_button("Descargar TXT", st.session_state['resultado'], file_name="material.txt")
