import streamlit as st
import requests
import io
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

def generar_docx_profesional(texto_ia, escuela, profe, tema, logo_file=None):
    doc = Document()
    
    # --- CONFIGURACIÓN DEL ENCABEZADO (Logo + Info) ---
    section = doc.sections[0]
    header = section.header
    
    # Fila superior: Logo a la izquierda, Escuela/Profe a la derecha
    htxt = header.paragraphs[0]
    if logo_file:
        run_logo = htxt.add_run()
        run_logo.add_picture(logo_file, width=Inches(1.2))
    
    # Añadimos la información de la escuela y profesor alineada a la derecha
    info_profe = header.add_paragraph(f"{escuela}\nProf. {profe}")
    info_profe.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # --- TÍTULO DE LA UNIDAD ---
    doc.add_paragraph() # Espacio
    titulo = doc.add_heading(tema.upper(), 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    lineas = texto_ia.split('\n')
    for linea in lineas:
        l = linea.strip()
        if not l: continue
            
        # --- DETECTAR Y FORMATEAR VOCABULARIO ---
        if "VOCABULARIO" in l.upper() or l.startswith('# '):
            h = doc.add_heading(l.replace('#', '').strip(), level=1)
            continue
            
        # --- LÓGICA DE TABLAS (Relacionar Columnas) ---
        if '|' in l and '---' not in l:
            datos = [celda.strip() for celda in l.split('|') if celda.strip()]
            if len(datos) >= 2:
                tabla = doc.add_table(rows=1, cols=2)
                tabla.style = 'Table Grid'
                cells = tabla.rows[0].cells
                cells[0].text = datos[0]
                cells[1].text = datos[1]
                continue

        # --- CUERPO DEL TEXTO CON NEGRITAS ---
        p = doc.add_paragraph()
        partes = l.split('**')
        for i, parte in enumerate(partes):
            run = p.add_run(parte)
            if i % 2 == 1: # Es texto entre asteriscos
                run.bold = True
                run.font.color.rgb = RGBColor(0, 51, 102) # Azul profesional
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración")
    logo_subido = st.file_uploader("Subir logo de la escuela", type=["png", "jpg", "jpeg"])
    nombre_escuela = st.text_input("Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("API Key", type="password")

# --- INTERFAZ DE GENERACIÓN ---
st.title("🎓 Generador ELE Pro: Edición Editorial")

col1, col2 = st.columns(2)
with col1:
    tema_clase = st.text_input("Tema de la unidad")
    nivel_mcer = st.selectbox("Nivel", ["A1", "A2", "B1", "B2", "C1", "C2"])
    ext = st.select_slider("Extensión", ["Corto", "1 pág", "2 págs", "3 págs (Extenso)"], "3 págs (Extenso)")
with col2:
    n_ejercicios = st.number_input("Ejercicios por técnica", 1, 30, 15)
    tec = st.multiselect("Técnicas", ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", "Corregir errores", "Relacionar columnas"], default=["Relacionar columnas", "Test de Cloze"])
    gram = st.multiselect("Enfoque", ["Vocabulario", "Subjuntivo", "Pretéritos", "Ser/Estar"], default=["Vocabulario", "Pretéritos"])

if st.button("🚀 Generar Material Editorial"):
    if not api_key or not tema_clase:
        st.error("Por favor, completa la configuración.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        prompt = f"Actúa como autor experto de {nombre_escuela}. Tema: {tema_clase}, Nivel: {nivel_mcer}. Requisitos: Sección '# VOCABULARIO CLAVE' con términos y definiciones, texto de {ext} (mínimo 2000 palabras si es extenso), y {n_ejercicios} ejercicios por técnica: {', '.join(tec)}. Formato tablas: 'Término | Definición'. Firma: {nombre_profe}."
        
        with st.spinner("Generando contenido..."):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state['material_ia'] = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.success("¡Contenido generado!")
            except: st.error("Error en la conexión con la IA.")

if 'material_ia' in st.session_state:
    st.divider()
    # Pasamos el logo subido directamente a la función
    docx_bytes = generar_docx_profesional(st.session_state['material_ia'], nombre_escuela, nombre_profe, tema_clase, logo_file=logo_subido)
    
    st.download_button("📥 Descargar Word con Logo y Tablas", data=docx_bytes, file_name=f"ELE_{tema_clase}.docx")
    st.markdown(st.session_state['material_ia'])
