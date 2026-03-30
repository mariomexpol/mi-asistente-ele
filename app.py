import streamlit as st
import google.generativeai as genai
import io
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- LIMPIEZA DE FORMATO ---
def limpiar_texto_ele(texto):
    return texto.replace('\\_', '_').replace('\\', '')

# --- CONSTRUCCIÓN DEL WORD ---
def generar_docx_profesional(texto_ia, escuela, profe, tema, logo_file=None):
    doc = Document()
    section = doc.sections[0]
    header = section.header
    htxt = header.paragraphs[0]
    
    if logo_file:
        try:
            run_logo = htxt.add_run()
            run_logo.add_picture(logo_file, width=Inches(1.2))
            htxt.alignment = WD_ALIGN_PARAGRAPH.LEFT
        except: pass
    
    info_h = header.add_paragraph(f"{escuela}\nProf. {profe}")
    info_h.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_paragraph() 
    titulo = doc.add_heading(tema.upper(), 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    lineas = limpiar_texto_ele(texto_ia).split('\n')
    for linea in lineas:
        l = linea.strip()
        if not l: continue
        
        if l.startswith('#') or "VOCABULARIO" in l.upper() or "SOLUCIONARIO" in l.upper() or "EJERCICIOS" in l.upper():
            if "SOLUCIONARIO" in l.upper(): doc.add_page_break()
            doc.add_heading(l.replace('#', '').strip(), level=1)
            continue
            
        if '|' in l and '---' not in l:
            datos = [c.strip() for l_p in l.split('|') if (c := l_p.strip())]
            if len(datos) >= 2:
                tabla = doc.add_table(rows=1, cols=2)
                tabla.style = 'Table Grid'
                cells = tabla.rows[0].cells
                cells[0].text = datos[0]
                cells[1].text = datos[1]
                continue

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
    logo_subido = st.file_uploader("Subir logo", type=["png", "jpg", "jpeg"])
    nombre_escuela = st.text_input("Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("API Key (Gemini)", type="password")

# --- INTERFAZ PRINCIPAL ---
st.title("🎓 Generador ELE Pro")
modo = st.selectbox("Modo de generación", ["Unidad Completa (Texto + Ejercicios)", "Solo Lista de Ejercicios"])

st.divider()

col1, col2 = st.columns(2)
with col1:
    tema_input = st.text_input("Tema de la unidad")
    nivel_mcer = st.selectbox("Nivel", ["A1", "A2", "B1", "B2", "C1", "C2"])
    ext_val = "Corto"
    if modo == "Unidad Completa (Texto + Ejercicios)":
        ext_val = st.select_slider("Extensión", ["Corto", "1 pág", "2 págs", "3 págs (Extenso)"], "3 págs (Extenso)")

with col2:
    items_val = st.number_input("Items por técnica", 1, 30, 15)
    tecs_val = st.multiselect("Técnicas", ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", "Corregir errores", "Relacionar columnas"], default=["Relacionar columnas", "Test de Cloze"])
    gram_val = st.multiselect("Enfoque", ["Vocabulario", "Presente de Indicativo", "Pretéritos", "Futuros", "Subjuntivo", "Ser/Estar", "Por/Para"], default=["Vocabulario", "Presente de Indicativo"])

# ... (Mantén las funciones de limpieza y generación de DOCX iguales al código anterior)

if st.button("🚀 Generar Material Editorial (Adaptado a Polonia)"):
    if not api_key or not tema_input:
        st.error("⚠️ Configuración incompleta.")
    else:
        try:
            genai.configure(api_key=api_key.strip())
            # Usamos Flash por estabilidad, pero con instrucciones de experto
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt_p = (f"Actúa como profesor experto de español para polacos en la escuela {nombre_escuela}. "
                      f"Tema: {tema_input}, Nivel: {nivel_mcer}. "
                      f"IMPORTANTE: Mis alumnos son POLACOS. "
                      f"1. En la sección '# VOCABULARIO CLAVE', incluye la traducción de cada palabra al POLACO.\n"
                      f"2. En el texto, explica brevemente (en español) las diferencias o similitudes con el polaco (ej. el uso de 'się').\n"
                      f"3. Requisitos: Texto de {ext_val} y {items_val} ejercicios por técnica: {', '.join(tecs_val)}.\n"
                      f"4. AÑADE una técnica extra: 'Traducción del polaco al español' con frases típicas del tema.\n"
                      f"5. REGLAS DE FORMATO: Usa '_______' para los huecos. NO pongas respuestas en los ejercicios.\n"
                      f"6. Crea una sección final '# SOLUCIONARIO'.\n"
                      f"Firma: {nombre_profe}.")
            
            with st.spinner("Generando unidad adaptada para alumnos polacos..."):
                response = model.generate_content(prompt_p)
                st.session_state['material_ia'] = response.text
                st.success("¡Material generado con éxito!")
        except Exception as e:
            st.error(f"Error detectado: {e}")

# ... (El resto del código de descarga se mantiene igual)

if 'material_ia' in st.session_state:
    st.divider()
    docx_bytes = generar_docx_profesional(st.session_state['material_ia'], nombre_escuela, nombre_profe, tema_input, logo_file=logo_subido)
    st.download_button("📥 Descargar Word Profesional", data=docx_bytes, file_name=f"ELE_{tema_input}.docx")
    st.markdown(st.session_state['material_ia'])
