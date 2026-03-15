import streamlit as st
from fpdf import FPDF
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Asistente E/LE Pro", layout="wide")

# --- BARRA LATERAL: CONFIGURACIÓN DE ESCUELA ---
with st.sidebar:
    st.header("🏫 Configuración del Centro")
    nombre_escuela = st.text_input("Nombre de la Escuela", "Mi Escuela de Español")
    logo_subido = st.file_uploader("Subir Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
    nombre_profe = st.text_input("Profesor/a", "Tu Nombre")
    api_key = st.text_input("Introduce tu API Key de Gemini", type="password")

# --- CUERPO PRINCIPAL: PARÁMETROS PEDAGÓGICOS ---
st.title("🎓 Generador de Materiales E/LE (MCER)")
col1, col2 = st.columns(2)

with col1:
    modulo = st.selectbox("Módulo", ["Ejercicios Gramaticales", "Comprensión Lectora (A4)"])
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    tema = st.text_input("Tema (ej: El pretérito imperfecto, La comida)")

with col2:
    cantidad = st.number_input("Cantidad de ítems/preguntas", min_value=1, max_value=50, value=10)
    tecnicas = st.multiselect("Técnicas (puedes elegir varias)", 
                             ["Rellenar huecos", "Test de Cloze", "Traducción", "Corregir errores", "Relacionar", "Ordenar frases"])

# --- LÓGICA DE GENERACIÓN ---
if st.button("🚀 Generar Material"):
    if not api_key:
        st.error("Por favor, introduce tu API Key en la barra lateral.")
    else:
        # Configuración del modelo (Gemini)
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
         # --- LÓGICA DE GENERACIÓN MEJORADA ---
if st.button("🚀 Generar Material"):
    if not api_key:
        st.error("Por favor, introduce tu API Key en la barra lateral.")
    else:
        try:
            # 1. Limpiamos la API Key de posibles espacios accidentales
            genai.configure(api_key=api_key.strip())
            
            # 2. Usamos una configuración de seguridad relajada para temas educativos
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                safety_settings=safety_settings
            )
            
            prompt_final = f"""
            Actúa como un Coordinador Académico de Español (E/LE). 
            Nivel MCER: {nivel}. 
            Tema: {tema}.
            Módulo seleccionado: {modulo}. 
            Técnicas a usar: {', '.join(tecnicas)}. 
            Cantidad de ejercicios: {cantidad}.
            
            INSTRUCCIONES:
            1. Sigue estrictamente el Marco Común Europeo.
            2. Genera los ejercicios de forma clara.
            3. Al final, incluye una sección de 'SOLUCIONES' y 'EXPLICACIÓN PEDAGÓGICA'.
            4. Usa un tono académico profesional.
            """
            
            with st.spinner("Generando contenido académico..."):
                response = model.generate_content(prompt_final)
                
                # Verificamos si la respuesta tiene texto (por si fue bloqueada)
                if response.text:
                    st.session_state['contenido'] = response.text
                    st.markdown(response.text)
                else:
                    st.warning("El modelo no pudo generar una respuesta. Intenta cambiar un poco el tema.")

        except Exception as e:
            st.error(f"Se produjo un error técnico: {e}")
            st.info("💡 Consejo: Revisa que tu API Key sea correcta y que tengas conexión a internet.")
