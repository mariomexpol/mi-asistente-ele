import streamlit as st
import requests
import io
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- FUNCIÓN DE LIMPIEZA DE FORMATO ---
def limpiar_texto(texto):
    # Elimina las barras invertidas que rompen el diseño de los huecos
    return texto.replace('\\_', '_')

# --- GENERADOR DE WORD PROFESIONAL ---
def generar_docx_profesional(texto_ia, escuela, profe, tema, logo_file=None):
    doc = Document()
    
    # Configuración de márgenes y encabezado
    section = doc.sections[0]
    header = section.header
    htxt = header.paragraphs[0]
    
    # Inserción del LOGO
    if logo_file:
        try:
            run_logo = htxt.add_run()
            run_logo.add_picture(logo_file, width=Inches(1.2))
            htxt.alignment = WD_ALIGN_PARAGRAPH.LEFT
        except:
            pass
    
    # Información de la escuela (Alineada a la derecha)
    info_header = header.add_paragraph(f"{escuela}\nProf. {profe}")
    info_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Título de la unidad
    doc.add_paragraph() 
    titulo = doc.add_heading(tema.upper(), 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Procesamiento del texto
    texto_procesado = limpiar_texto(texto_ia)
    lineas = texto_procesado.split('\n')
    
    for linea in lineas:
        l = linea.strip()
        if not l: continue
            
        # Formato de Títulos y Vocabulario
        if l.startswith('#') or "VOCABULARIO" in l.upper():
            doc.add_heading(l.replace('#', '').strip(), level=1)
            continue
            
        # Formato de Tablas (Relacionar Columnas)
        if '|' in l and '---' not in l:
            datos = [celda.strip() for celda in l.split('|') if celda.strip()]
            if len(datos) >= 2:
                tabla = doc.add_table(rows=1, cols=2)
                tabla.style = 'Table Grid'
                cells = tabla.rows[0].cells
                cells[0].text = datos[0]
                cells[1].text = datos[1]
                continue

        # Cuerpo de texto con detección de negritas
        p = doc.add_paragraph()
        partes = l.split('**')
        for i, parte in enumerate(partes):
            run = p.add_run(parte)
            if i % 2 == 1: # Texto en negrita
                run.bold = True
                run.font.color.rgb = RGBColor(0, 51, 102)
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- BARRA LATERAL (CONFIGURACIÓN) ---
with st.sidebar:
    st.header("🏫 Configuración Institucional")
    logo_subido = st.file_uploader("Subir logo de la escuela", type=["png", "jpg", "jpeg"])
    nombre_escuela = st.text_input("Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("API Key (Gemini)", type="password")

# --- INTERFAZ DE USUARIO ---
st.title("🎓 Generador ELE Pro: Edición Editorial")

# Agrupación de selectores para evitar que desaparezcan
col_tema, col_nivel = st.columns([2, 1])
with col_tema:
    tema_input = st.text_input("Tema de la clase", placeholder="Ej: La vida en el campo vs la ciudad")
with col_nivel:
    nivel_mcer = st.selectbox("Nivel", ["A1", "A2", "B1", "B2", "C1", "C2"])

st.divider()

col_ext, col_cant = st.columns(2)
with col_ext:
    ext_texto = st.select_slider("Extensión del texto", ["Corto", "1 pág", "2 págs", "3 págs (Extenso)"], "3 págs (Extenso)")
with col_cant:
    cantidad_ej = st.number_input("Ejercicios por técnica", 1, 30, 15)

col_tec, col_gram = st.columns(2)
with col_tec:
    lista_tecnicas = st.multiselect("Técnicas pedagógicas", 
                                   ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", "Corregir errores", "Relacionar columnas"], 
                                   default=["Relacionar columnas", "Test de Cloze"])
with col_gram:
    lista_gramatica = st.multiselect("Enfoque pedagógico", 
                                    ["Vocabulario", "Subjuntivo", "Pretéritos", "Ser/Estar", "Por/Para"], 
                                    default=["Vocabulario", "Subjuntivo"])

# --- GENERACIÓN ---
if st.button("🚀 Crear Material de Alta Calidad"):
    if not api_key or not tema_input:
        st.error("⚠️ Configuración incompleta (Falta API Key o Tema).")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        prompt = (f"Actúa como autor experto de la escuela {nombre_escuela}. Tema: {tema_input}, Nivel: {nivel_mcer}. "
                  f"Requisitos: Sección '# VOCABULARIO CLAVE', texto de {ext_texto} (mínimo 2000 palabras si es extenso), "
                  f"y {cantidad_ej} ejercicios por técnica: {', '.join(lista_tecnicas)}. "
                  f"Enfoque: {', '.join(lista_gramatica)}. Tablas para relacionar: 'A | B'. Firma: {nombre_profe}.")
        
        with st.spinner("Redactando y maquetando material..."):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state['material_ia'] = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.success("¡Material generado con éxito!")
            except:
                st.error("Error al conectar con el servidor de IA.")

# --- DESCARGA ---
if 'material_ia' in st.session_state:
    st.divider()
    docx_bytes = generar_docx_profesional(
        st.session_state['material_ia'], 
        nombre_escuela, 
        nombre_profe, 
        tema_input, 
        logo_file=logo_subido
    )
    
    st.download_button("📥 Descargar Unidad en Word Profesional", data=docx_bytes, file_name=f"ELE_{tema_input}.docx")
    st.markdown(st.session_state['material_ia'])
