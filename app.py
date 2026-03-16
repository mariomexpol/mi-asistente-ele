import streamlit as st
import requests
import io
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- FUNCIÓN DE LIMPIEZA DE TEXTO ---
def limpiar_texto_ele(texto):
    # Elimina barras invertidas molestas en los huecos de ejercicios
    return texto.replace('\\_', '_')

# --- GENERADOR DE WORD PROFESIONAL ---
def generar_docx_profesional(texto_ia, escuela, profe, tema, logo_file=None):
    doc = Document()
    
    # Configuración del Encabezado (Logo + Datos)
    section = doc.sections[0]
    header = section.header
    htxt = header.paragraphs[0]
    
    if logo_file:
        try:
            run_logo = htxt.add_run()
            run_logo.add_picture(logo_file, width=Inches(1.2))
            htxt.alignment = WD_ALIGN_PARAGRAPH.LEFT
        except: pass
    
    info_header = header.add_paragraph(f"{escuela}\nProf. {profe}")
    info_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Título de la unidad
    doc.add_paragraph() 
    titulo = doc.add_heading(tema.upper(), 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Procesamiento de líneas
    texto_limpio = limpiar_texto_ele(texto_ia)
    lineas = texto_limpio.split('\n')
    
    for linea in lineas:
        l = linea.strip()
        if not l: continue
            
        # Formato especial para VOCABULARIO y Títulos
        if l.startswith('#') or "VOCABULARIO" in l.upper():
            doc.add_heading(l.replace('#', '').strip(), level=1)
            continue
            
        # Formato de Tablas Reales (Relacionar Columnas)
        if '|' in l and '---' not in l:
            datos = [c.strip() for c in l.split('|') if c.strip()]
            if len(datos) >= 2:
                tabla = doc.add_table(rows=1, cols=2)
                tabla.style = 'Table Grid'
                cells = tabla.rows[0].cells
                cells[0].text = datos[0]
                cells[1].text = datos[1]
                continue

        # Cuerpo de texto con negritas automáticas
        p = doc.add_paragraph()
        partes = l.split('**')
        for i, parte in enumerate(partes):
            run = p.add_run(parte)
            if i % 2 == 1: 
                run.bold = True
                run.font.color.rgb = RGBColor(0, 51, 102) # Azul editorial
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración Escuela")
    logo_img = st.file_uploader("Subir logo institucional", type=["png", "jpg", "jpeg"])
    nombre_escuela = st.text_input("Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("API Key (Gemini)", type="password")

# --- INTERFAZ PRINCIPAL ---
st.title("🎓 Generador ELE Pro: Edición Editorial")

modo_ele = st.selectbox("¿Qué vas a crear hoy?", ["Unidad Completa (Texto + Ejercicios)", "Solo Lista de Ejercicios"])

st.divider()

col_1, col_2 = st.columns(2)

with col_1:
    tema_clase = st.text_input("Tema de la unidad", placeholder="Ej: La familia o El futuro del planeta")
    nivel_clase = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    
    if modo_ele == "Unidad Completa (Texto + Ejercicios)":
        ext_clase = st.select_slider("Extensión", ["Corto", "1 pág", "2 págs", "3 págs (Extenso)"], "3 págs (Extenso)")

with col_2:
    cant_items = st.number_input("Items por técnica", 1, 30, 15)
    tec_pedagogicas = st.multiselect("Técnicas", 
                                    ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", "Corregir errores", "Relacionar columnas"],
                                    default=["Test de Cloze", "Relacionar columnas"])
    
    # NUEVA LISTA DE GRAMÁTICA AMPLIADA
    enfoque_gram = st.multiselect("Enfoque Gramatical / Vocabulario", 
                                 ["Vocabulario", "Presente de Indicativo", "Pretéritos", "Futuros", 
                                  "Presente de Subjuntivo", "Pretérito Imperfecto de Subjuntivo", 
                                  "Condicional Simple", "Condicional Compuesto", "Ser/Estar", "Por/Para"],
                                 default=["Vocabulario", "Presente de Indicativo"])

# --- ACCIÓN DE GENERAR ---
if st.button("🚀 Crear Material Editorial"):
    if not api_key or not tema_clase:
        st.error("⚠️ Falta API Key o el Tema.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        inst_ext = f"Texto de nivel {nivel_clase} de {ext_clase} (2000 palabras si es extenso)." if modo_ele == "Unidad Completa (Texto + Ejercicios)" else "Genera directamente los ejercicios sin texto."
        
        prompt = (f"Actúa como autor experto de {nombre_escuela}. Tema: {tema_clase}, Nivel: {nivel_clase}. "
                  f"Requisitos: {inst_ext}. Sección '# VOCABULARIO CLAVE' con términos y definiciones. "
                  f"Crea {cant_items} ejercicios por técnica: {', '.join(tec_pedagogicas)}. "
                  f"Enfoque: {', '.join(enfoque_gram)}. Tablas: 'A | B'. Firma: {nombre_profe}.")
        
        with st.spinner("Generando y maquetando material profesional..."):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state['material_ia'] = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.success("¡Material generado!")
            except:
                st.error("Error al conectar con la IA.")

# --- DESCARGA ---
if 'material_ia' in st.session_state:
    st.divider()
    docx_bytes = generar_docx_profesional(
        st.session_state['material_ia'], 
        nombre_escuela, 
        nombre_profe, 
        tema_clase, 
        logo_file=logo_img
    )
    
    st.download_button("📥 Descargar Word Profesional", data=docx_bytes, file_name=f"ELE_{tema_clase}.docx")
    st.markdown(st.session_state['material_ia'])
