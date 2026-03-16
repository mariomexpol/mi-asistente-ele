import streamlit as st
import requests
import io
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Configuración inicial de la página
st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- FUNCIÓN DE LIMPIEZA Y PROCESAMIENTO ---
def limpiar_texto_ele(texto):
    return texto.replace('\\_', '_')

def generar_docx_profesional(texto_ia, escuela, profe, tema, logo_file=None):
    doc = Document()
    section = doc.sections[0]
    header = section.header
    htxt = header.paragraphs[0]
    
    # Logo Institucional
    if logo_file:
        try:
            run_logo = htxt.add_run()
            run_logo.add_picture(logo_file, width=Inches(1.2))
            htxt.alignment = WD_ALIGN_PARAGRAPH.LEFT
        except: pass
    
    # Encabezado con info de la escuela
    info = header.add_paragraph(f"{escuela}\nProf. {profe}")
    info.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Título
    doc.add_paragraph()
    titulo = doc.add_heading(tema.upper(), 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    lineas = limpiar_texto_ele(texto_ia).split('\n')
    for linea in lineas:
        l = linea.strip()
        if not l: continue
        
        # Formato de Títulos y Vocabulario
        if l.startswith('#') or "VOCABULARIO" in l.upper():
            doc.add_heading(l.replace('#', '').strip(), level=1)
            continue
            
        # Generación de Tablas Reales para Ejercicios de Relacionar
        if '|' in l and '---' not in l:
            datos = [c.strip() for c in l.split('|') if c.strip()]
            if len(datos) >= 2:
                tabla = doc.add_table(rows=1, cols=2)
                tabla.style = 'Table Grid'
                cells = tabla.rows[0].cells
                cells[0].text = datos[0]
                cells[1].text = datos[1]
                continue

        # Párrafos con negritas
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
    st.header("🏫 Configuración ELE")
    logo_subido = st.file_uploader("Logo de la escuela", type=["png", "jpg", "jpeg"])
    nombre_escuela = st.text_input("Institución", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("Clave Gemini API", type="password")

# --- INTERFAZ PRINCIPAL ---
st.title("🎓 Generador ELE Pro")

# 1. ELECCIÓN DE MODO (Esto define qué selectores aparecen)
modo_trabajo = st.selectbox("¿Qué deseas generar hoy?", 
                           ["Unidad Completa (Texto + Ejercicios)", "Solo Lista de Ejercicios"])

st.divider()

# 2. SELECTORES DINÁMICOS
col_a, col_b = st.columns(2)

with col_a:
    tema_input = st.text_input("Tema de la clase", placeholder="Ej: La familia o El medio ambiente")
    nivel_mcer = st.selectbox("Nivel de los alumnos", ["A1", "A2", "B1", "B2", "C1", "C2"])
    
    # Solo aparece si es Unidad Completa
    if modo_trabajo == "Unidad Completa (Texto + Ejercicios)":
        extension_texto = st.select_slider("Extensión del texto base", 
                                          options=["Corto", "1 pág", "2 págs", "3 págs (Extenso)"], 
                                          value="3 págs (Extenso)")

with col_b:
    items_cantidad = st.number_input("Cantidad de ejercicios por técnica", 1, 30, 15)
    
    # Selector de técnicas (Aparece en ambos modos)
    selección_tecnicas = st.multiselect("Técnicas pedagógicas", 
                                       ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", "Corregir errores", "Relacionar columnas"],
                                       default=["Test de Cloze", "Relacionar columnas"])
    
    # Selector de gramática y vocabulario
    selección_enfoque = st.multiselect("Enfoque gramatical / léxico", 
                                      ["Vocabulario", "Subjuntivo", "Pretéritos", "Ser/Estar", "Por/Para"],
                                      default=["Vocabulario", "Subjuntivo"])

# --- ACCIÓN DE GENERAR ---
if st.button("🚀 Crear Material Editorial"):
    if not api_key or not tema_input:
        st.error("Faltan datos críticos (API Key o Tema).")
    elif not selección_tecnicas:
        st.warning("Selecciona al menos una técnica de ejercicios.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        # Construcción del Prompt según el modo
        if modo_trabajo == "Unidad Completa (Texto + Ejercicios)":
            detalles = f"Texto de nivel {nivel_mcer} con extensión de {extension_texto} (mínimo 2000 palabras si es extenso)."
        else:
            detalles = f"Genera directamente la lista de ejercicios sin texto de lectura."

        prompt_final = (f"Actúa como autor de {nombre_escuela}. Tema: {tema_input}, Nivel: {nivel_mcer}. "
                       f"Requisitos: {detalles}. Sección '# VOCABULARIO CLAVE' con términos y definiciones. "
                       f"Crea {items_cantidad} ejercicios por cada técnica: {', '.join(selección_tecnicas)}. "
                       f"Enfoque: {', '.join(selección_enfoque)}. Tablas: 'A | B'. Firma: {nombre_profe}.")
        
        with st.spinner("Generando contenido profesional..."):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt_final}]}]})
                st.session_state['material_ia'] = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.success("¡Material generado!")
            except:
                st.error("Error al conectar con la IA. Revisa tu API Key.")

# --- BOTÓN DE DESCARGA ---
if 'material_ia' in st.session_state:
    st.divider()
    docx_ready = generar_docx_profesional(
        st.session_state['material_ia'], 
        nombre_escuela, 
        nombre_profe, 
        tema_input, 
        logo_file=logo_subido
    )
    
    st.download_button("📥 Descargar Word con Logo y Tablas Reales", data=docx_ready, file_name=f"ELE_{tema_input}.docx")
    st.markdown(st.session_state['material_ia'])
