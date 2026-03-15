import streamlit as st
import google.generativeai as genai

st.title("Generador E/LE Rápido")

# Campos obligatorios arriba para evitar errores
llave = st.text_input("API Key", type="password")
tema_clase = st.text_input("Tema")
nivel_mcer = st.selectbox("Nivel", ["A1", "A2", "B1", "B2", "C1", "C2"])

if st.button("🚀 Generar Ahora"):
    if not llave or not tema_clase:
        st.error("Rellena la llave y el tema")
    else:
        try:
            # Conexión sin variables intermedias
            genai.configure(api_key=llave.strip())
            modelo = genai.GenerativeModel('gemini-1.5-flash')
            
            # Pedimos algo muy corto para probar
            prompt = f"Crea 3 ejercicios cortos de español nivel {nivel_mcer} sobre {tema_clase} con soluciones."
            
            # Llamada directa sin spinner para ver si hay error inmediato
            respuesta = modelo.generate_content(prompt)
            
            if respuesta.text:
                st.success("¡Logrado!")
                st.markdown(respuesta.text)
                st.download_button("Descargar", respuesta.text, file_name="ejercicios.txt")
            else:
                st.warning("La IA respondió vacío.")
                
        except Exception as e:
            st.error(f"Error detectado: {e}")
