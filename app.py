import streamlit as st
import requests
import json

st.set_page_config(page_title="Asistente E/LE Pro", layout="wide")

st.title("🎓 Generador de Materiales E/LE")

with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("API Key de Google AI Studio", type="password")
    nombre_escuela = st.text_input("Escuela", "Mi Escuela")

tema = st.text_input("Tema de la clase (ej: El pretérito imperfecto)")
nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
cantidad = st.number_input("Cantidad de ejercicios", min_value=1, value=5)

if st.button("🚀 Generar Material"):
    if not api_key or not tema:
        st.error("Por favor, introduce la API Key y el tema.")
    else:
        # CONEXIÓN DIRECTA POR HTTP (Evita el error 404 v1beta)
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key.strip()}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Actúa como profesor de español experto. Crea {cantidad} ejercicios nivel {nivel} sobre {tema}. Incluye soluciones. Escuela: {nombre_escuela}."
                }]
            }]
        }
        headers = {'Content-Type': 'application/json'}

        with st.spinner("Generando material (Conexión Directa)..."):
            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                res_json = response.json()
                
                # Extraemos el texto de la respuesta de Google
                if "candidates" in res_json:
                    texto_generado = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    st.success("¡Logrado! Material generado.")
                    st.markdown(texto_generado)
                    st.session_state['resultado'] = texto_generado
                else:
                    st.error(f"Error de la API: {res_json.get('error', {}).get('message', 'Error desconocido')}")
                    
            except Exception as e:
                st.error(f"Error de conexión: {e}")

if 'resultado' in st.session_state:
    st.download_button("📥 Descargar TXT", st.session_state['resultado'], file_name="material_ele.txt")
