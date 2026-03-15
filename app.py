import streamlit as st
import requests
import json

st.set_page_config(page_title="Asistente E/LE Pro", layout="wide")

st.title("🎓 Asistente E/LE (Versión 2.0)")

with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("API Key de Google AI Studio", type="password")
    nombre_escuela = st.text_input("Escuela", "Mi Escuela de Español")

tema = st.text_input("Tema de la clase (ej: El pretérito indefinido)")
nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
cantidad = st.number_input("Cantidad de ejercicios", min_value=1, value=5)

if st.button("🚀 Generar Material"):
    if not api_key or not tema:
        st.error("Por favor, introduce la API Key y el tema.")
    else:
        # USAMOS EL MODELO QUE TU CUENTA SÍ TIENE: gemini-2.0-flash
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key.strip()}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Actúa como profesor de español experto. Crea {cantidad} ejercicios nivel {nivel} sobre {tema}. Incluye soluciones. Escuela: {nombre_escuela}."
                }]
            }]
        }
        headers = {'Content-Type': 'application/json'}

        with st.spinner("Generando material con Gemini 2.0..."):
            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                res_json = response.json()
                
                # Extraemos el texto de la respuesta siguiendo la estructura de la API
                if "candidates" in res_json:
                    texto_generado = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    st.success("¡Por fin! Material generado correctamente.")
                    st.markdown("---")
                    st.markdown(texto_generado)
                    st.session_state['resultado'] = texto_generado
                else:
                    # Si falla, mostramos el error detallado de Google
                    error_msg = res_json.get('error', {}).get('message', 'Error desconocido')
                    st.error(f"Error de la API: {error_msg}")
                    
            except Exception as e:
                st.error(f"Error de conexión: {e}")

if 'resultado' in st.session_state:
    st.divider()
    st.download_button("📥 Descargar Material (TXT)", st.session_state['resultado'], file_name=f"Clase_{tema}.txt")
