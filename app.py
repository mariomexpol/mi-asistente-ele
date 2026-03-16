import streamlit as st
import requests
import json
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- CLASE PDF PROFESIONAL REFORZADA ---
class ELE_PDF(FPDF):
    def header(self):
        # Logo institucional (si existe)
        if hasattr(self, 'logo_path') and self.logo_path:
            self.image(self.logo_path, 10, 8, 30)
        
        # Membrete de la Escuela
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(44, 62, 80) # Azul oscuro profesional
        self.set_x(45)
        self.cell(0, 10, self.nombre_escuela, ln=True, align='L')
        
        self.set_font('helvetica', 'I', 10)
        self.set_x(45)
        self.cell(0, 5, "Material Didáctico de Español", ln=True, align='L')
        self.ln(10)
        self.line(10, 35, 200, 35) # Línea divisoria decorativa
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()} | Generado por Asistente ELE Pro', align='C')

    def chapter_title(self, label):
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(192, 57, 43) # Rojo elegante para títulos
        self.cell(0, 10, label.upper(), ln=True)
        self.ln(4)

    def write_body(self, text):
        self.set_font('helvetica', '', 11)
        self.set_text_color(0, 0, 0)
        # Procesamiento de negritas reales para el PDF
        parts = text.split('**')
        for i, part in enumerate(parts):
            if i % 2 == 1:
                self.set_font('helvetica', 'B', 11)
            else:
                self.set_font('helvetica', '', 11)
            
            clean_text = part.encode('latin-1', 'replace').decode('latin-1')
            self.write(7, clean_text)

def generar_pdf_editorial(texto, escuela, logo_path):
    pdf = ELE_PDF()
    pdf.nombre_escuela = escuela
    pdf.logo_path = logo_path
    pdf.add_page()
    
    lineas = texto.split('\n')
    for linea in lineas:
        if linea.startswith('###'):
            pdf.ln(5)
            pdf.chapter_title(linea.replace('###', '').strip())
        elif linea.strip() == "":
            pdf.ln(4)
        else:
            pdf.write_body(linea)
            pdf.ln(7)
            
    return pdf.output()

# --- INTERFAZ STREAMLIT (SECCIÓN DE CONFIGURACIÓN) ---
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

st.title("🎓 Generador ELE Pro: Edición Editorial")

# ... (Mantenemos los selectores de Tema, Nivel y Extensión anteriores) ...

if st.button("🚀 Crear Material de Alta Calidad"):
    # ... (Mismo flujo de llamada a la API de Gemini) ...
    pass

if 'material_final' in st.session_state:
    st.divider()
    # Generamos los bytes del PDF profesional
    pdf_bytes = generar_pdf_editorial(st.session_state['material_final'], nombre_escuela, logo_path)
    
    st.download_button(
        label="📄 Descargar PDF de Calidad Editorial",
        data=pdf_bytes,
        file_name=f"Clase_ELE_{nombre_profe}.pdf",
        mime="application/pdf"
    )
