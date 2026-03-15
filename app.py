import streamlit as st
import requests
import json
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- CLASE PDF PROFESIONAL CON SOPORTE DE CARACTERES ---
class ELE_PDF(FPDF):
    def header(self):
        if hasattr(self, 'logo_path') and self.logo_path:
            self.image(self.logo_path, 10, 8, 30)
        self.set_font('helvetica', 'B', 15)
        self.set_x(45)
        # Limpieza de caracteres para el encabezado
        escuela_txt = self.nombre_escuela.encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 10, escuela_txt, ln=True, align='L')
        self.ln(10)

    def write_markdown(self, txt):
        """Procesa negritas ** y maneja acentos de forma segura"""
        parts = txt.split('**')
        for i, part in enumerate(parts):
            if i % 2 == 1:
                self.set_font('helvetica', 'B', 12)
            else:
                self.set_font('helvetica', '', 12)
            
            # Reemplazos críticos para evitar que el PDF se rompa (0 KB)
            clean = part.replace('–', '-').replace('—', '-').replace('¿', '?').replace('¡', '!')
            # Codificación latin-1 obligatoria para FPDF básico
            pdf_text = clean.encode('latin-1', 'replace').decode('latin-1')
            self.write(7, pdf_text)

def generar_pdf_seguro(texto, escuela, logo_path):
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
    
    # Salida en formato binario puro (bytearray)
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
modo = st.radio("Modo de trabajo:", ["Unidad Completa (Texto + Ejercicios)", "Solo Ejercicios"], horizontal=True)

col1, col2 = st.columns(2)
with col1:
    tema = st.text_input("Tema detallado", placeholder="Ej: Impacto de la IA en la educación")
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    extension = st.select_slider("Extensión del texto base", options=["1 página", "2 páginas", "3 páginas (Extenso)"], value="3 páginas (Extenso)")

with col2:
    cantidad = st.number_input("Cantidad de ítems por técnica", 1, 30, 15)
    tecnicas = st.multiselect("Técnicas", ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", "Corregir errores", "Relacionar columnas"], default=["Test de Cloze", "Preguntas de comprensión"])
    gramatica = st.multiselect("Gramática", ["Presente", "Pretéritos", "Subjuntivo", "Ser/Estar"], default=["Subjuntivo"])

if st.button("🚀 Generar Material"):
    if not api_key or not tema:
        st.error("⚠️ Datos faltantes")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        # PROMPT DE ALTA DENSIDAD: Forzamos la estructura de 3 páginas
        prompt = f"""
        Actúa como profesor de {nombre_escuela}. Genera una unidad ELE nivel {nivel} sobre '{tema}'.
        
        INSTRUCCIONES DE VOLUMEN (CRÍTICO):
        1. TEXTO: Escribe un ensayo de 2000 palabras dividido en: Introducción, Antecedentes, Situación Actual, Impacto Social, Perspectivas Futuras y Conclusión. Cada sección debe ser muy larga.
        2. EJERCICIOS: Crea exactamente {cantidad} ítems numerados para CADA una de estas técnicas: {', '.join(tecnicas)}. No omitas ninguno.
        3. GRAMÁTICA: Aplica {', '.join(gramatica)}.
        
        Soluciones al final. Firma: {nombre_profe}.
        """
        
        with st.spinner("Generando material extenso... Esto puede tardar hasta 90 segundos."):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state['material_final'] = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.success("¡Material generado con éxito!")
            except Exception as e:
                st.error(f"Error en la IA: {e}")

if 'material_final' in st.session_state:
    st.divider()
    st.markdown(st.session_state['material_final'])
    
    # Generamos el PDF capturando la salida binaria
    try:
        pdf_output = generar_pdf_seguro(st.session_state['material_final'], nombre_escuela, logo_path)
        
        col_txt, col_pdf = st.columns(2)
        with col_txt:
            st.download_button("📥 Descargar TXT", data=st.session_state['material_final'], file_name=f"Material_{tema}.txt")
        with col_pdf:
            st.download_button(
                label="📄 Descargar PDF Profesional",
                data=bytes(pdf_output), # Convertimos a bytes explícitamente
                file_name=f"Material_{tema}.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"Error técnico al preparar la descarga: {e}")
