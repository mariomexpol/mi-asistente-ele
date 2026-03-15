import streamlit as st
import google.generativeai as genai

st.title("Asistente de Profesor de Español")

# Configuración básica en la página principal (más seguro)
api_key = st.text_input("1. Pega tu API Key de Google AI Studio", type="password")
escuela = st.text_input("2. Nombre de tu Escuela", "Mi Escuela")
tema = st.text_input("3. Tema de la clase (ej. El Subjuntivo)")
nivel = st.selectbox("4. Nivel", ["A1", "A2", "B1", "B2", "C1", "C2"])
cantidad = st.slider("5. Número de ejercicios", 1, 20, 10)

if st.button("🚀 Crear Material"):
    if not api_key or not tema:
        st.error("Faltan datos por rellenar.")
    else:
        try:
            # Conexión limpia
            genai.configure(api_key=api_key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"Actúa como profesor de español. Escuela: {escuela}. Nivel {nivel}. Tema: {tema}. Cantidad: {cantidad}. Incluye ejercicios tipo test de cloze, gramática y soluciones."
            
            with st.spinner("Generando..."):
                response = model.generate_content(prompt)
                st.session_state['resultado'] = response.text
                st.success("¡Hecho!")
        except Exception as e:
            st.error(f"Error: {e}")

if 'resultado' in st.session_state:
    st.markdown("---")
    st.write(f"### Material para {escuela}")
    st.write(st.session_state['resultado'])
    st.download_button("Descargar Material", st.session_state['resultado'], file_name="clase.txt")
