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
         # --- LÓGICA DE GENERACIÓN (VERSIÓN CORREGIDA) ---
if st.button("🚀 Generar Material"):
    if not api_key:
        st.error("Por favor, introduce tu API Key en la barra lateral.")
    else:
        try:
            # 1. Configuración del motor
            genai.configure(api_key=api_key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 2. Definición del Prompt (Alineación corregida)
            # Nota: El uso de f-strings con triples comillas debe estar pegado al margen del código
            prompt_final = f"""Actúa como un Coordinador Académico de Español (E/LE) experto.
Nivel MCER: {nivel}.
Tema: {tema}.
Módulo: {modulo}.
Técnicas: {', '.join(tecnicas)}.
Cantidad: {cantidad}.

INSTRUCCIONES:
1. Sigue estrictamente el Marco Común Europeo.
2. Genera los ejercicios de forma clara.
3. Al final, incluye 'SOLUCIONES' y 'EXPLICACIÓN PEDAGÓGICA'.
4. Usa un tono académico profesional."""

            with st.spinner("Generando contenido académico..."):
                response = model.generate_content(prompt_final)
                
                if response.text:
                    st.session_state['contenido'] = response.text
                    st.markdown(response.text)
                else:
                    st.warning("El modelo no devolvió texto. Revisa tu cuota de API.")

        except Exception as e:
            st.error(f"Error técnico: {e}") 
