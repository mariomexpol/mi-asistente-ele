import streamlit as st
import google.generativeai as genai

# Configuración de la página
st.set_page_config(page_title="Asistente E/LE Pro", layout="wide")

# --- BARRA LATERAL (Logo y Configuración) ---
with st.sidebar:
    st.header("🏫 Mi Institución")
    # Ventana para el LOGO
    logo_file = st.file_uploader("Subir logo de la escuela", type=["png", "jpg", "jpeg"])
    if logo_file:
        st.image(logo_file, width=150)
    
    nombre_escuela = st.text_input("Nombre de la Escuela", "Mi Escuela de Español")
    api_key = st.text_input("API Key de Gemini", type="password")
    st.info("Obtén tu llave en: aistudio.google.com")

# --- INTERFAZ DE GENERACIÓN ---
st.title("🎓 Generador de Materiales Académicos E/LE")

col1, col2 = st.columns(2)

with col1:
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    tema = st.text_input("Tema gramatical o comunicativo")
    modulo = st.radio("Módulo", ["Ejercicios", "Texto con Preguntas"])

with col2:
    cantidad = st.number_input("Cantidad de ítems", min_value=1, value=10)
    # Aquí añadimos TEST DE CLOZE y las demás técnicas
    tecnicas = st.multiselect("Técnicas", 
        ["Test de Cloze", "Rellenar huecos", "Traducción", "Corregir errores", "Ordenar frases", "Relacionar", "Completar diálogo"])

# --- BOTÓN DE ACCIÓN ---
if st.button("🚀 Generar Material"):
    if not api_key:
        st.error("Por favor, introduce tu API Key en la barra lateral.")
    elif not tema:
        st.warning("Escribe un tema para empezar.")
    else:
        try:
            # Configuración para evitar el error 404
            genai.configure(api_key=api_key.strip(), transport='rest')
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Construcción del mensaje para la IA
            prompt = (
                f"Actúa como profesor de español. Crea material nivel {nivel} sobre {tema}. "
                f"Módulo: {modulo}. Técnicas: {', '.join(tecnicas)}. Cantidad: {cantidad}. "
                f"Institución: {nombre_escuela}. "
                "REQUISITO: Incluye soluciones y explicaciones pedagógicas detalladas al final."
            )
            
            with st.spinner("Generando contenido académico..."):
                response = model.generate_content(prompt)
                if response.text:
                    st.session_state['contenido_final'] = response.text
                    st.success("¡Material generado!")
                else:
                    st.error("La IA no devolvió texto. Revisa tu configuración.")
        except Exception as e:
            st.error(f"Error técnico: {e}")
            st.info("Si el error es 404, prueba a generar una nueva API Key en Google AI Studio.")

# --- MOSTRAR RESULTADO Y DESCARGA ---
if 'contenido_final' in st.session_state:
    st.divider()
    # Mostramos el encabezado con el nombre de tu escuela
    st.subheader(f"📄 Material para: {nombre_escuela}")
    st.markdown(st.session_state['contenido_final'])
    
    # Botón de descarga
    st.download_button(
        label="📥 Descargar en TXT",
        data=st.session_state['contenido_final'],
        file_name=f"Material_ELE_{tema}.txt",
        mime="text/plain"
    )
