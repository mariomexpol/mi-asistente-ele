import streamlit as st
import requests
import json
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- CLASE PDF PROFESIONAL (Soporta Negritas y Logo) ---
class ELE_PDF(FPDF):
    def header(self):
        if hasattr(self, 'logo_path') and self.logo_path:
            self.image(self.logo_path, 10, 8, 30)
        self.set_font('helvetica', 'B', 15)
        self.set_x(45)
        self.cell(0, 10, self.nombre_escuela, ln=True, align='L')
        self.ln(10)

    def write_markdown(self, txt):
        """Convierte texto con ** en negritas dentro del PDF"""
        parts = txt.split('**')
        for i, part in enumerate(parts):
            if i % 2 == 1:
                self.set_font('helvetica', 'B', 12)
            else:
                self.set_font('helvetica', '', 12)
            self.write(7, part.replace('–', '-').replace('—', '-'))

def generar_pdf_profesional(texto, escuela, logo_path):
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
    tema = st.text_input("Tema", placeholder="Ej: Gastronomía Mexicana")
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    if modo == "Unidad con Texto Base":
        extension = st.select_slider("Extensión", options=["Corto", "Medio", "Largo (2 págs)", "Extenso (3 págs)"], value="Extenso (3 págs)")
    cantidad = st.number_input("Cantidad exacta de ejercicios por técnica", 1, 30, 15)

with col2:
    tecnicas = st.multiselect("Técnicas", ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", "Corregir errores", "Relacionar columnas", "Ordenar frases"], default=["Test de Cloze", "Preguntas de comprensión"])
    gramatica = st.multiselect("Gramática", ["Presente", "Pretéritos", "Subjuntivo", "Ser/Estar", "Vocabulario"], default=["Subjuntivo", "Pretéritos"])

if st.button("🚀 Generar Material de Alta Calidad"):
    if not api_key or not tema:
        st.error("⚠️ Datos incompletos.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        # PROMPT DE "FORZADO" DE LONGITUD
        prompt = f"""
        Como profesor experto de {nombre_escuela}, crea una unidad ELE de nivel {nivel} sobre '{tema}'.
        
        REQUISITOS CRÍTICOS DE VOLUMEN:
        1. TEXTO BASE: Debe ser muy extenso (mínimo 1500 palabras). Desarrolla 5 secciones detalladas. 
           Usa subtítulos con **Negrita**.
        2. EJERCICIOS: Genera EXACTAMENTE {cantidad} ítems numerados para CADA técnica: {', '.join(tecnicas)}. 
           No resumas. Si pides {cantidad}, escribe los {cantidad}.
        3. ENFOQUE: Usa {', '.join(gramatica)}.
        
        Incluye soluciones y firma como {nombre_profe}.
        """
        
        with st.spinner("Generando contenido extenso (3 páginas)... Esto puede tardar 60 segundos."):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state['material_final'] = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.success("¡Material generado!")
            except Exception as e:
                st.error(f"Error: {e}")

if 'material_final' in st.session_state:
    st.divider()
    st.markdown(st.session_state['material_final'])
    pdf_data = generar_pdf_profesional(st.session_state['material_final'], nombre_escuela, logo_path)
    st.download_button("📄 Descargar PDF Profesional (con Logo y Negritas)", data=bytes(pdf_data), file_name=f"Unidad_{tema}.pdf", mime="application/pdf")
