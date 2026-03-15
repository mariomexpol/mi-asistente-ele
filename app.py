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
        Actúa como un Coordinador Académico E/LE experto. 
        Crea material de nivel {nivel} sobre {tema}.
        Módulo: {modulo}. Técnicas: {tecnicas}. Cantidad: {cantidad}.
        Sigue estrictamente el MCER. Incluye SOLUCIONES y EXPLICACIÓN PEDAGÓGICA al final.
        """
        
        with st.spinner("Generando contenido académico..."):
            response = model.generate_content(prompt)
            contenido = response.text
            st.session_state['contenido'] = contenido
            st.markdown(contenido)

# --- MÓDULO DE EXPORTACIÓN (PDF/TXT) ---
if 'contenido' in st.session_state:
    st.divider()
    
    def generar_pdf(texto, escuela, profe, logo):
        pdf = FPDF()
        pdf.add_page()
        # Aquí la lógica para insertar el LOGO si existe
        if logo:
            pdf.image(logo, 10, 8, 33)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, escuela, ln=True, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, f"Profesor: {profe} | Nivel: {nivel}", ln=True, align='C')
        pdf.ln(10)
        pdf.multi_cell(0, 10, texto.encode('latin-1', 'replace').decode('latin-1'))
        return pdf.output(dest='S').encode('latin-1')

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button("📥 Descargar en PDF", 
                          data=generar_pdf(st.session_state['contenido'], nombre_escuela, nombre_profe, logo_subido),
                          file_name=f"Material_{tema}_{nivel}.pdf")
    with col_btn2:
        st.download_button("📄 Descargar en TXT", 
                          data=st.session_state['contenido'],
                          file_name=f"Material_{tema}_{nivel}.txt")
