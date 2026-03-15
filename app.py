import streamlit as st
import requests
import json
from fpdf import FPDF
import tempfile
import io

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- CLASE PDF PROFESIONAL ---
class ELE_PDF(FPDF):
    def header(self):
        if hasattr(self, 'logo_path') and self.logo_path:
            self.image(self.logo_path, 10, 8, 30)
        self.set_font('helvetica', 'B', 15)
        self.set_x(45)
        # Codificación segura para el nombre de la escuela
        escuela_safe = self.nombre_escuela.encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 10, escuela_safe, ln=True, align='L')
        self.ln(10)

    def write_markdown(self, txt):
        """Procesa negritas ** y maneja caracteres latinos"""
        parts = txt.split('**')
        for i, part in enumerate(parts):
            if i % 2 == 1:
                self.set_font('helvetica', 'B', 12)
            else:
                self.set_font('helvetica', '', 12)
            
            # Limpieza y codificación para evitar errores de string
            clean_part = part.encode('latin-1', 'replace').decode('latin-1')
            self.write(7, clean_part)

def generar_pdf_profesional(texto, escuela, logo_path):
    # Usamos latin-1 como base para FPDF estándar
    pdf = ELE_PDF()
    pdf.nombre_escuela = escuela
    pdf.logo_path = logo_path
    pdf.add_page()
    
    lineas = texto.split('\n')
    for linea in lineas:
        if linea.strip() == "":
            pdf.ln(5)
        else:
            pdf.write_markdown(linea)
            pdf.ln(7)
    
    # Retornamos los bytes del PDF
    return pdf.output()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración")
    logo_file = st.file_uploader("Subir logo", type=["png", "jpg", "jpeg"])
    logo_path = None
    if logo_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(logo_file.getvalue())
            logo_path = tmp.name
        st.image(logo_file, width=150)
    
    nombre_escuela = st.text_input("Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("API Key", type="password")

# --- INTERFAZ ---
st.title("🎓 Generador ELE Pro")
modo = st.radio("Selecciona:", ["Unidad con Texto Base", "Solo Lista de Ejercicios"], horizontal=True)

col1, col2 = st.columns(2)
with col1:
    tema = st.text_input("Tema de la clase")
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    if modo == "Unidad con Texto Base":
        extension = st.select_slider("Extensión", options=["Corto", "1 página", "2 páginas", "3 páginas (Extenso)"], value="3 páginas (Extenso)")
    cantidad = st.number_input("Cantidad de ejercicios", 1, 30, 15)

with col2:
    tecnicas = st.multiselect("Técnicas", ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", "Corregir errores", "Relacionar columnas", "Ordenar frases"], default=["Test de Cloze", "Preguntas de comprensión"])
    # Recuperada la opción de Vocabulario
    gramatica = st.multiselect("Gramática / Vocabulario", ["Presente", "Pretéritos", "Subjuntivo", "Ser/Estar", "Vocabulario"], default=["Subjuntivo", "Vocabulario"])

if st.button("🚀 Generar Material"):
    if not api_key or not tema:
        st.error("⚠️ Datos incompletos.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        prompt = f"""
        Actúa como profesor de {nombre_escuela}. Crea una unidad de nivel {nivel} sobre '{tema}'.
        REQUISITOS:
        1. TEXTO: Mínimo 2000 palabras, dividido en secciones profundas. Usa subtítulos con **Negrita**.
        2. EJERCICIOS: EXACTAMENTE {cantidad} ítems por técnica: {', '.join(tecnicas)}.
        3. ENFOQUE: {', '.join(gramatica)}.
        Incluye soluciones y firma como {nombre_profe}.
        """
        
        with st.spinner("Generando contenido extenso..."):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state['material_final'] = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.success("¡Material generado!")
            except Exception as e:
                st.error(f"Error: {e}")

# --- DESCARGAS ---
if 'material_final' in st.session_state:
    st.divider()
    st.markdown(st.session_state['material_final'])
    
    col_txt, col_pdf = st.columns(2)
    with col_txt:
        st.download_button("📥 Descargar TXT", data=st.session_state['material_final'], file_name=f"Material_{tema}.txt")
    
    with col_pdf:
        try:
            pdf_output = generar_pdf_profesional(st.session_state['material_final'], nombre_escuela, logo_path)
            st.download_button(
                label="📄 Descargar PDF Profesional",
                data=bytes(pdf_output),
                file_name=f"Material_{tema}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error técnico al preparar el PDF: {e}")
