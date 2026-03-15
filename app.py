import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Asistente E/LE Pro", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración")
    logo_file = st.file_uploader("Subir logo", type=["png", "jpg", "jpeg"])
    if logo_file:
        st.image(logo_file, width=150)
    nombre_escuela = st.text_input("Escuela", "Mi Escuela de Español")
    api_key = st.text_input("API Key de Gemini", type="password")

# --- INTERFAZ ---
st.title("🎓 Generador de Materiales E/LE")

col1, col2 = st.columns(2)
with col1:
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    tema = st.text_input("Tema de la clase")
    modulo = st.radio("Módulo", ["Ejercicios", "Texto con Preguntas"])

with col2:
    cantidad = st.number_input("Cantidad", min_value=1, value=10)
    tecnicas = st.multiselect("Técnicas", 
        ["Test de Cloze", "Rellenar huecos", "Traducción", "Corregir errores", "Ordenar frases", "Relacionar"])

if st.button("🚀 Generar Material"):
    if not api_key:
        st.error("Introduce la API Key")
    else:
        try:
            # Configuración básica sin argumentos extra
            genai.configure(api_key=api_key.strip())
            
            # Usamos el nombre del modelo sin el prefijo 'models/'
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"Profesor de español. Escuela: {nombre_escuela}. Nivel {nivel}. Tema: {tema}. Módulo: {modulo}. Técnicas: {tecnicas}. Cantidad: {cantidad}. Incluye soluciones."
            
            with st.spinner("Generando..."):
                # Llamada directa
                response = model.generate_content(prompt)
                
                # Acceso directo al texto
                st.session_state['contenido'] = response.text
                st.success("¡Generado!")
                
        except Exception as e:
            # Si el anterior falla, intentamos el modelo Pro
            try:
                model_alt = genai.GenerativeModel('gemini-pro')
                response = model_alt.generate_content(prompt)
                st.session_state['contenido'] = response.text
                st.success("¡Generado con modelo Pro!")
            except Exception as e2:
                st.error(f"Error de conexión: {e2}")

# --- RESULTADO ---
if 'contenido' in st.session_state:
    st.divider()
    st.subheader(f"📄 {nombre_escuela}")
    st.markdown(st.session_state['contenido'])
    st.download_button("📥 Descargar TXT", st.session_state['contenido'], file_name="material.txt")
