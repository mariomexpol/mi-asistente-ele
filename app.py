 import streamlit as st
from fpdf import FPDF
import google.generativeai as genai

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asistente E/LE Pro", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración del Centro")
    nombre_escuela = st.text_input("Nombre de la Escuela", "Mi Escuela de Español")
    logo_subido = st.file_uploader("Subir Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
    nombre_profe = st.text_input("Profesor/a", "Tu Nombre")
    api_key = st.text_input("Introduce tu API Key de Gemini", type="password")
    st.info("Obtén tu clave en: aistudio.google.com")

# --- INTERFAZ PRINCIPAL ---
st.title("🎓 Generador de Materiales E/LE")
st.markdown("Crea materiales académicos alineados al MCER de forma instantánea.")

col1, col2 = st.columns(2)

with col1:
    modulo = st.selectbox("Módulo", ["Ejercicios Gramaticales", "Comprensión Lectora (A4)"])
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    tema = st.text_input("Tema (ej: El pretérito indefinido)")

with col2:
    cantidad = st.number_input("Cantidad de ejercicios/preguntas", min_value=1, max_value=30, value=10)
    tecnicas = st.multiselect("Técnicas", 
                             ["Rellenar huecos", "Test de Cloze", "Traducción", "Corregir errores", "Relacionar", "Ordenar frases", "Completar diálogo"])

# --- LÓGICA DE GENERACIÓN ---
if st.button("🚀 Generar Material"):
    if not api_key:
        st.error("⚠️ Falta la API Key en la barra lateral.")
    elif not tema:
        st.warning("⚠️ Por favor, indica un tema.")
    else:
        try:
            genai.configure(api_key=api_key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Construcción segura del prompt (sin comillas triples problemáticas)
            p_lineas = [
                f"Actúa como un Coordinador Académico de Español (E/LE) experto.",
                f"Nivel MCER: {nivel}.",
                f"Tema: {tema}.",
                f"Módulo: {modulo}.",
                f"Técnicas: {', '.join(tecnicas)}.",
                f"Cantidad: {cantidad}.",
                "REQUISITOS:",
                "1. Rigor académico según el MCER.",
                "2. Generar ejercicios claros y numerados.",
                "3. Incluir al final una sección de SOLUCIONES y EXPLICACIÓN PEDAGÓGICA.",
                "4. Todo el contenido debe ser en español."
            ]
            prompt_final = "\n".join(p_lineas)

            with st.spinner("Generando contenido..."):
                response = model.generate_content(prompt_final)
                if response.text:
                    st.session_state['contenido'] = response.text
                    st.success("¡Material generado con éxito!")
                else:
                    st.error("El modelo no pudo generar texto.")
        except Exception as e:
            st.error(f"Error técnico: {e}")

# --- VISUALIZACIÓN Y DESCARGA ---
if 'contenido' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['contenido'])
    
    # Función simple para TXT
    st.download_button(
        label="📄 Descargar en TXT",
        data=st.session_state['contenido'],
        file_name=f"Material_{tema}.txt",
        mime="text/plain"
    )
    
    st.info("💡 Para el PDF con logo, puedes copiar el texto a Word/Google Docs. (La librería PDF en la nube requiere configuración de fuentes avanzada para tildes).")
