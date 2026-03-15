import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Asistente E/LE", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración")
    nombre_escuela = st.text_input("Escuela", "Mi Escuela")
    nombre_profe = st.text_input("Profesor/a", "Nombre")
    api_key = st.text_input("API Key de Gemini", type="password")

# --- INTERFAZ ---
st.title("🎓 Generador E/LE")
modulo = st.selectbox("Módulo", ["Ejercicios Gramaticales", "Comprensión Lectora"])
nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
tema = st.text_input("Tema de la clase")
cantidad = st.number_input("Cantidad", min_value=1, value=10)
tecnicas = st.multiselect("Técnicas", ["Rellenar huecos", "Traducción", "Corregir errores", "Ordenar frases"])

if st.button("🚀 Generar"):
    if not api_key:
        st.error("Introduce la API Key")
    else:
        try:
            # Limpiamos la llave
            llave = api_key.strip()
            genai.configure(api_key=llave)
            
            # Usamos el nombre simplificado que funciona en la API v1
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"Actúa como profesor de español experto. Crea material nivel {nivel} sobre {tema}. Módulo: {modulo}. Técnicas: {tecnicas}. Cantidad: {cantidad}. Incluye soluciones y explicaciones pedagógicas."
            
            with st.spinner("Generando contenido pedagógico..."):
                # Forzamos la generación
                response = model.generate_content(prompt)
                
                if response and response.text:
                    st.session_state['texto'] = response.text
                    st.success("¡Material listo!")
                    st.markdown(response.text)
                else:
                    st.error("El modelo respondió pero no contiene texto. Revisa los filtros de seguridad.")
                    
        except Exception as e:
            # Este mensaje nos dirá si es un problema de la LLAVE o del MODELO
            st.error(f"Error técnico: {e}") 
