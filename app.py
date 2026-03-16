import streamlit as st
import requests
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

def generar_docx_profesional(texto_ia, escuela, profe, tema):
    doc = Document()
    
    # Encabezado estilo membrete
    header = doc.sections[0].header
    htxt = header.paragraphs[0]
    htxt.text = f"{escuela}\nMaterial Pedagógico - Prof. {profe}"
    htxt.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Título de la Unidad
    titulo = doc.add_heading(tema.upper(), 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    lineas = texto_ia.split('\n')
    for linea in lineas:
        l = linea.strip()
        if not l: continue
            
        # Detectar Títulos principales
        if l.startswith('# ') or l.startswith('###'):
            h = doc.add_heading(l.replace('#', '').strip(), level=1)
            continue
            
        # LÓGICA ESPECIAL PARA TABLAS (Relacionar Columnas)
        if '|' in l and '---' not in l:
            datos = [celda.strip() for celda in l.split('|') if celda.strip()]
            if len(datos) >= 2:
                tabla = doc.add_table(rows=1, cols=2)
                tabla.style = 'Table Grid'
                cells = tabla.rows[0].cells
                cells[0].text = datos[0]
                cells[1].text = datos[1]
                continue

        # Párrafos normales con negritas
        p = doc.add_paragraph()
        partes = l.split('**')
        for i, parte in enumerate(partes):
            run = p.add_run(parte)
            if i % 2 == 1:
                run.bold = True
                run.font.color.rgb = RGBColor(0, 51, 102) # Azul oscuro para resaltar
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- INTERFAZ ---
with st.sidebar:
    st.header("🏫 Configuración")
    nombre_escuela = st.text_input("Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("API Key", type="password")

st.title("🎓 Generador ELE Pro: Calidad Editorial")

col1, col2 = st.columns(2)
with col1:
    tema = st.text_input("Tema de la unidad")
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    extension = st.select_slider("Extensión", ["Corto", "1 pág", "2 págs", "3 págs (Extenso)"], "3 págs (Extenso)")
with col2:
    cantidad = st.number_input("Ejercicios por técnica", 1, 30, 15)
    tecnicas = st.multiselect("Técnicas", ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", "Corregir errores", "Relacionar columnas"], default=["Relacionar columnas", "Test de Cloze"])
    gramatica = st.multiselect("Enfoque", ["Subjuntivo", "Pretéritos", "Vocabulario", "Ser/Estar"], default=["Vocabulario", "Subjuntivo"])

if st.button("🚀 Generar Material Word Profesional"):
    if not api_key or not tema:
        st.error("Faltan datos.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        prompt = f"""
        Actúa como autor experto de {nombre_escuela}. Tema: {tema}, Nivel: {nivel}.
        REQUISITOS OBLIGATORIOS:
        1. VOCABULARIO: Crea una sección llamada '# VOCABULARIO CLAVE' con una lista de 20 términos y definiciones.
        2. TEXTO: Mínimo 2000 palabras (3 páginas). Usa títulos con '#'.
        3. EJERCICIOS: Exactamente {cantidad} por cada técnica: {', '.join(tecnicas)}.
        4. TABLAS: Para la técnica 'Relacionar columnas', genera el contenido usando este formato exactamente: 'Término A | Definición B' (una por línea).
        Firma: {nombre_profe}.
        """
        
        with st.spinner("Generando y maquetando..."):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state['material_ia'] = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.success("¡Material generado!")
            except: st.error("Error en la API")

if 'material_ia' in st.session_state:
    st.divider()
    docx_data = generar_docx_profesional(st.session_state['material_ia'], nombre_escuela, nombre_profe, tema)
    st.download_button("📥 Descargar Word con Tablas Reales", data=docx_data, file_name=f"ELE_{tema}.docx")
    st.markdown(st.session_state['material_ia'])
