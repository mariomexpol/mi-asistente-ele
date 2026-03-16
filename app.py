import streamlit as st
import requests
import io
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- FUNCIÓN DE LIMPIEZA ---
def limpiar_formato_final(texto):
    return texto.replace('\\_', '_').replace('\\', '')

# --- GENERADOR DOCX ---
def generar_docx_profesional(texto_ia, escuela, profe, tema, logo_file=None):
    doc = Document()
    section = doc.sections[0]
    header = section.header
    htxt = header.paragraphs[0]
    
    # Manejo del Logo
    if logo_file:
        try:
            run_logo = htxt.add_run()
            run_logo.add_picture(logo_file, width=Inches(1.2))
            htxt.alignment = WD_ALIGN_PARAGRAPH.LEFT
        except: pass
    
    info_h = header.add_paragraph(f"{escuela}\nProf. {profe}")
    info_h.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Título Principal
    doc.add_paragraph() 
    titulo = doc.add_heading(tema.upper(), 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    lineas = limpiar_formato_final(texto_ia).split('\n')
    for linea in lineas:
        l = linea.strip()
        if not l: continue
            
        # Detectar Títulos y Secciones
        if l.startswith('#') or "VOCABULARIO" in l.upper() or "SOLUCIONARIO" in l.upper() or "EJERCICIOS" in l.upper():
            if "SOLUCIONARIO" in l.upper():
                doc.add_page_break() # Las soluciones van en página aparte
            doc.add_heading(l.replace('#', '').strip(), level=1)
            continue
            
        # Tablas Reales
        if '|' in l and '---' not in l:
            datos = [c.strip() for c in l.split('|') if c.strip()]
            if len(datos) >= 2:
                tabla = doc.add_table(rows=1, cols=2)
                tabla.style = 'Table Grid'
                cells = tabla.rows[0].cells
                cells[0].text = datos[0]
                cells[1].text = datos[1]
                continue

        # Texto con negritas
        p = doc.add_paragraph()
        partes = l.split('**')
        for i, parte in enumerate(partes):
            run = p.add_run(parte)
            if i % 2 == 1:
                run.bold = True
                run.font.color.rgb = RGBColor(0, 51, 102)
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración")
    logo_subido = st.file_uploader("Subir logo de la escuela", type=["png", "jpg", "jpeg"])
    nombre_escuela = st.text_input("Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("API Key (Gemini)", type="password")

# --- INTERFAZ ---
st.title("🎓 Generador ELE Pro")
modo = st.selectbox("Selecciona modo", ["Unidad Completa (Texto + Ejercicios)", "Solo Lista de Ejercicios"])

st.divider()

col1, col2 = st.columns(2)
with col1:
    tema_input = st.text_input("Tema de la unidad")
    nivel_mcer = st.selectbox("Nivel", ["A1", "A2", "B1", "B2", "C1", "C2"])
    if modo == "Unidad Completa (Texto + Ejercicios)":
        ext = st.select_slider("Extensión", ["Corto", "1 pág", "2 págs", "3 págs (Extenso)"], "3 págs (Extenso)")

with col2:
    items = st.number_input("Items por técnica", 1, 30, 15)
    tecs = st.multiselect("Técnicas", ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", "Corregir errores", "Relacionar columnas"], default=["Relacionar columnas", "Test de Cloze"])
    gram = st.multiselect("Enfoque", ["Vocabulario", "Presente de Indicativo", "Pretéritos", "Futuros", "Presente de Subjuntivo", "Pretérito Imperfecto de Subjuntivo", "Condicional Simple", "Condicional Compuesto", "Ser/Estar", "Por/Para"], default=["Vocabulario", "Presente de Indicativo"])

if st.button("🚀 Generar Material Editorial"):
    if not api_key or not tema_input:
        st.error("⚠️ Configuración incompleta.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        detalles = f"Texto de {ext} (2000 palabras si es extenso)." if modo == "Unidad Completa (Texto + Ejercicios)" else "Genera solo los ejercicios."
        
        prompt = (f"Actúa como autor experto de {nombre_escuela}. Tema: {tema_input}, Nivel: {nivel_mcer}. "
                  f"Requisitos: {detalles}. Sección '# VOCABULARIO CLAVE'. "
                  f"Crea {items} ejercicios por técnica: {', '.join(tecs)}. Enfoque: {', '.join(gram)}. "
                  f"IMPORTANTE: Al final, incluye siempre una sección llamada '# SOLUCIONARIO' con todas las respuestas. "
                  f"Tablas: 'A | B'. Firma: {nombre_profe}.")
        
        with st.spinner("Generando material con soluciones..."):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state['material_ia'] = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.success("¡Material y soluciones generados!")
            except: st.error("Error en la API.")

if 'material_ia' in st.session_state:
    st.divider()
    docx_bytes = generar_docx_profesional(st.session_state['material_ia'], nombre_escuela, nombre_profe, tema_input, logo_file=logo_subido)
    st.download_button("📥 Descargar Word con Logo y Soluciones", data=docx_bytes, file_name=f"ELE_{tema_input}.docx")
    st.markdown(st.session_state['material_ia'])
