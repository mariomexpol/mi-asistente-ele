import streamlit as st
import requests
import io
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- FUNCIÓN DE LIMPIEZA DE CARACTERES ---
def limpiar_formato(texto):
    # Elimina las barras invertidas que la IA pone antes de los guiones bajos
    return texto.replace('\\_', '_')

def generar_docx_profesional(texto_ia, escuela, profe, tema, logo_file=None):
    doc = Document()
    
    # --- CONFIGURACIÓN DEL ENCABEZADO ---
    section = doc.sections[0]
    header = section.header
    htxt = header.paragraphs[0]
    
    # Insertar Logo
    if logo_file:
        try:
            run_logo = htxt.add_run()
            # Ajuste de tamaño profesional para el logo
            run_logo.add_picture(logo_file, width=Inches(1.3))
            htxt.alignment = WD_ALIGN_PARAGRAPH.LEFT
        except:
            pass # Si falla el logo, continúa con el texto
    
    # Añadir Info de la escuela y profesor (alineada a la derecha)
    info_p = header.add_paragraph(f"{escuela}\nProf. {profe}")
    info_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # --- TÍTULO ---
    doc.add_paragraph() 
    titulo = doc.add_heading(tema.upper(), 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Limpiar el texto de la IA antes de procesar
    texto_limpio = limpiar_formato(texto_ia)
    
    lineas = texto_limpio.split('\n')
    for linea in lineas:
        l = linea.strip()
        if not l: continue
            
        # Detectar Títulos
        if l.startswith('#') or "VOCABULARIO" in l.upper():
            h = doc.add_heading(l.replace('#', '').strip(), level=1)
            continue
            
        # Lógica de Tablas para 'Relacionar Columnas'
        if '|' in l and '---' not in l:
            datos = [celda.strip() for celda in l.split('|') if celda.strip()]
            if len(datos) >= 2:
                tabla = doc.add_table(rows=1, cols=2)
                tabla.style = 'Table Grid'
                cells = tabla.rows[0].cells
                cells[0].text = datos[0]
                cells[1].text = datos[1]
                continue

        # Párrafos con negritas reales
        p = doc.add_paragraph()
        partes = l.split('**')
        for i, parte in enumerate(partes):
            run = p.add_run(parte)
            if i % 2 == 1:
                run.bold = True
                run.font.color.rgb = RGBColor(0, 51, 102) # Azul institucional
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- INTERFAZ DE USUARIO ---
with st.sidebar:
    st.header("🏫 Configuración")
    logo_subido = st.file_uploader("Subir logo institucional", type=["png", "jpg", "jpeg"])
    nombre_escuela = st.text_input("Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("API Key", type="password")

st.title("🎓 Generador ELE Pro: Edición Editorial")

# Agrupamos los selectores para que no desaparezcan
col1, col2 = st.columns(2)
with col1:
    tema_clase = st.text_input("Tema de la unidad", placeholder="Ej: La gastronomía mexicana")
    nivel_mcer = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    ext = st.select_slider("Extensión del texto", ["Corto", "1 pág", "2 págs", "3 págs (Extenso)"], "3 págs (Extenso)")

with col2:
    n_ejercicios = st.number_input("Items por técnica", 1, 30, 15)
    tec = st.multiselect("Técnicas de ejercicios", 
                         ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", "Corregir errores", "Relacionar columnas"], 
                         default=["Relacionar columnas", "Test de Cloze"])
    gram = st.multiselect("Enfoque pedagógico", 
                          ["Vocabulario", "Subjuntivo", "Pretéritos", "Ser/Estar", "Por/Para"], 
                          default=["Vocabulario", "Pretéritos"])

if st.button("🚀 Generar Material Editorial"):
    if not api_key or not tema_clase:
        st.error("⚠️ Configuración incompleta.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        prompt = (f"Actúa como autor de {nombre_escuela}. Tema: {tema_clase}, Nivel: {nivel_mcer}. "
                  f"Requisitos: Sección '# VOCABULARIO CLAVE', texto de {ext}, y {n_ejercicios} ejercicios por técnica: {', '.join(tec)}. "
                  f"Enfoque: {', '.join(gram)}. Tablas: 'A | B'. Firma: {nombre_profe}.")
        
        with st.spinner("Generando contenido y procesando diseño..."):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state['material_ia'] = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.success("¡Material generado!")
            except:
                st.error("Error al conectar con la IA.")

if 'material_ia' in st.session_state:
    st.divider()
    # Generar DOCX con el logo y limpieza de caracteres
    docx_bytes = generar_docx_profesional(
        st.session_state['material_ia'], 
        nombre_escuela, 
        nombre_profe, 
        tema_clase, 
        logo_file=logo_subido
    )
    
    st.download_button("📥 Descargar Word Profesional (.docx)", data=docx_bytes, file_name=f"ELE_{tema_clase}.docx")
    st.markdown(st.session_state['material_ia'])
