import streamlit as st
import requests
import json
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- FUNCIÓN PARA GENERAR PDF ---
def crear_pdf(texto, nombre_escuela, logo_path=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Encabezado con Logo
    if logo_path:
        pdf.image(logo_path, 10, 8, 33)
        pdf.set_x(45)
    
    # Nombre de la Escuela
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, nombre_escuela.encode('latin-1', 'replace').decode('latin-1'), ln=True)
    pdf.ln(10)
    
    # Cuerpo del texto
    pdf.set_font("Arial", size=11)
    # Reemplazamos caracteres especiales para evitar errores en PDF básico
    texto_limpio = texto.replace('–', '-').replace('—', '-').replace('“', '"').replace('”', '"')
    
    pdf.multi_cell(0, 10, texto_limpio.encode('latin-1', 'replace').decode('latin-1'))
    
    return pdf.output(dest='S').encode('latin-1')

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración")
    logo_file = st.file_uploader("Subir logo", type=["png", "jpg", "jpeg"])
    logo_path = None
    if logo_file:
        st.image(logo_file, width=150)
        # Guardar logo temporalmente para el PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(logo_file.getvalue())
            logo_path = tmp.name
    
    nombre_escuela = st.text_input("Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("API Key", type="password")

# --- INTERFAZ PRINCIPAL ---
st.title("🎓 Generador ELE Pro")
modo = st.radio("Modo:", ["Unidad con Texto Base", "Solo Lista de Ejercicios"], horizontal=True)

col1, col2 = st.columns(2)
with col1:
    tema_especifico = st.text_input("Tema", placeholder="Ej: La contaminación")
    nivel = st.selectbox("Nivel", ["A1", "A2", "B1", "B2", "C1", "C2"])
    if modo == "Unidad con Texto Base":
        extension = st.select_slider("Extensión", options=["Corto (150 palabras)", "Medio (1 página A4)", "Largo (2 páginas A4)", "Extenso (3 páginas A4)"])
    cantidad_ejercicios = st.number_input("Cantidad de ítems", 1, 30, 5)

with col2:
    tecnicas = st.multiselect("Técnicas", ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", "Corregir errores", "Relacionar columnas", "Ordenar frases"], default=["Test de Cloze"])
    enfoque_gramatical = st.multiselect("Gramática", ["Presente", "Pretéritos", "Subjuntivo", "Ser/Estar", "Vocabulario"], default=["Presente"])

if st.button("🚀 Generar Material"):
    if not api_key or not tema_especifico:
        st.error("⚠️ Falta API Key o Tema.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        prompt = f"Actúa como profesor de {nombre_escuela}. Tema {tema_especifico}, nivel {nivel}. Modo: {modo}. Técnicas: {', '.join(tecnicas)}. Enfoque: {', '.join(enfoque_gramatical)}. Cantidad: {cantidad_ejercicios}. Firma como {nombre_profe}. Incluye soluciones."
        
        with st.spinner("Generando contenido..."):
            try:
                response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}))
                st.session_state['material_final'] = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.success("¡Material Generado!")
            except Exception as e:
                st.error(f"Error: {e}")

# --- BOTONES DE DESCARGA ---
if 'material_final' in st.session_state:
    st.divider()
    st.markdown(st.session_state['material_final'])
    
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button("📥 Descargar TXT", st.session_state['material_final'], file_name=f"Material_{tema_especifico}.txt")
    
    with col_dl2:
        # Generar PDF al momento de hacer clic
        pdf_bytes = crear_pdf(st.session_state['material_final'], nombre_escuela, logo_path)
        st.download_button("📄 Descargar PDF Oficial", data=pdf_bytes, file_name=f"Material_{tema_especifico}.pdf", mime="application/pdf")
