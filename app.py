import streamlit as st
import requests
import json
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- FUNCIÓN PARA CREAR EL DOCUMENTO WORD ---
def generar_docx(texto_ia, escuela, profe, tema):
    doc = Document()
    
    # Estilo del Encabezado
    header = doc.sections[0].header
    p_header = header.paragraphs[0]
    p_header.text = f"{escuela}\nProfesor: {profe}"
    p_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Título Principal
    t = doc.add_heading(f"Unidad Didáctica: {tema}", 0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Procesar el texto de la IA
    lineas = texto_ia.split('\n')
    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
            
        if linea.startswith('###'): # Títulos de sección
            seccion = doc.add_heading(linea.replace('###', '').strip(), level=1)
        elif linea.startswith('####'): # Subtítulos
            sub = doc.add_heading(linea.replace('####', '').strip(), level=2)
        else:
            p = doc.add_paragraph()
            # Manejo básico de negritas de la IA (**)
            partes = linea.split('**')
            for i, parte in enumerate(partes):
                run = p.add_run(parte)
                if i % 2 == 1:
                    run.bold = True
    
    # Guardar en memoria
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración")
    nombre_escuela = st.text_input("Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("API Key (Gemini)", type="password")

# --- INTERFAZ ---
st.title("🎓 Generador ELE Pro: Edición Word")
modo = st.radio("Modo:", ["Unidad Completa", "Solo Ejercicios"], horizontal=True)

st.divider()

col1, col2 = st.columns(2)
with col1:
    tema = st.text_input("Tema de la clase")
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    
    opciones_ext = ["Corto", "Medio", "Largo (2 págs)", "Extenso (3 págs)"]
    extension = st.select_slider("Extensión del texto", options=opciones_ext, value="Extenso (3 págs)")
    
    cantidad = st.number_input("Cantidad de ejercicios por técnica", 1, 30, 15)

with col2:
    tecnicas = st.multiselect("Técnicas", 
                             ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", 
                              "Corregir errores", "Relacionar columnas", "Ordenar frases"],
                             default=["Test de Cloze", "Preguntas de comprensión"])
    
    gramatica = st.multiselect("Enfoque Gramática / Vocabulario", 
                            ["Presente", "Pretéritos", "Subjuntivo", "Ser/Estar", "Vocabulario"],
                            default=["Subjuntivo", "Vocabulario"])

if st.button("🚀 Generar Material en Word"):
    if not api_key or not tema:
        st.error("⚠️ Datos incompletos.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        prompt = f"""
        Actúa como autor de libros de texto para {nombre_escuela}. Nivel {nivel}, tema '{tema}'.
        1. TEXTO: Mínimo 2000 palabras (3 páginas de contenido). Usa ### para títulos y **negrita** para resaltar.
        2. EJERCICIOS: Exactamente {cantidad} por técnica: {', '.join(tecnicas)}.
        3. ENFOQUE: {', '.join(gramatica)}.
        Firma como {nombre_profe} e incluye soluciones.
        """
        
        with st.spinner("Generando contenido extenso para 3 páginas..."):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state['material_ia'] = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                st.success("¡Material generado!")
            except Exception as e:
                st.error(f"Error: {e}")

if 'material_ia' in st.session_state:
    st.divider()
    st.markdown(st.session_state['material_ia'])
    
    # Generar el archivo Word
    docx_data = generar_docx(st.session_state['material_ia'], nombre_escuela, nombre_profe, tema)
    
    st.download_button(
        label="📥 Descargar Unidad en Word (.docx)",
        data=docx_data,
        file_name=f"Unidad_{tema.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
