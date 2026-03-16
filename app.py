import streamlit as st
import requests
import json

# Configuración de la página
st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- BARRA LATERAL: CONFIGURACIÓN ---
with st.sidebar:
    st.header("🏫 Configuración Institucional")
    nombre_escuela = st.text_input("Nombre de la Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Nombre del Profesor/a", "Mario")
    api_key = st.text_input("API Key (Gemini)", type="password")
    st.info("📋 Instrucciones: Genera el material, descarga el TXT y usa 'Imprimir > PDF' en tu iPad para la versión final.")

# --- INTERFAZ PRINCIPAL ---
st.title("🎓 Generador ELE Pro: Edición Profesional")
modo = st.radio("Modo de trabajo:", ["Unidad Completa (Texto + Ejercicios)", "Solo Ejercicios"], horizontal=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    tema = st.text_input("Tema de la clase", placeholder="Ej: La gastronomía de Oaxaca o El impacto de la tecnología")
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    
    # Selector de extensión recuperado y estable
    opciones_ext = ["Corto (150 palabras)", "Medio (1 página)", "Largo (2 páginas)", "Extenso (3 páginas)"]
    if modo == "Unidad Completa (Texto + Ejercicios)":
        extension = st.select_slider("Selecciona la extensión del texto base", options=opciones_ext, value="Extenso (3 páginas)")
    
    cantidad = st.number_input("Cantidad de ejercicios por técnica", min_value=1, max_value=30, value=15)

with col2:
    # Selector de técnicas pedagógicas
    tecnicas = st.multiselect("Técnicas pedagógicas a incluir", 
                             ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", 
                              "Corregir errores", "Relacionar columnas", "Ordenar frases"],
                             default=["Test de Cloze", "Preguntas de comprensión"])
    
    # Selector de gramática y VOCABULARIO recuperado
    gramatica_vocab = st.multiselect("Enfoque Gramática / Vocabulario", 
                            ["Presente", "Pretéritos", "Subjuntivo", "Ser/Estar", "Por/Para", "Vocabulario"],
                            default=["Subjuntivo", "Vocabulario"])

# --- PROCESO DE GENERACIÓN ---
if st.button("🚀 Generar Material Profesional"):
    if not api_key or not tema:
        st.error("⚠️ Por favor, introduce la API Key y el tema de la clase.")
    elif not tecnicas:
        st.warning("⚠️ Debes seleccionar al menos una técnica pedagógica.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        # Prompt optimizado para TXT de alta calidad y extensión real
        if modo == "Unidad Completa (Texto + Ejercicios)":
            detalles_longitud = "Escribe un artículo de fondo extremadamente detallado de al menos 2000 palabras, dividido en 6 capítulos narrativos."
        else:
            detalles_longitud = "Crea una lista directa de ejercicios sin texto previo."

        prompt = f"""
        Actúa como un autor experto de libros de texto para la escuela {nombre_escuela}.
        Misión: Generar una unidad didáctica de nivel {nivel} sobre '{tema}'.
        
        ESTRUCTURA DEL ARCHIVO TXT PROFESIONAL:
        1. ENCABEZADO:
           ****************************************************
           ESCUELA: {nombre_escuela}
           PROFESOR: {nombre_profe}
           ****************************************************
        
        2. DESARROLLO:
           {detalles_longitud}
           Usa subtítulos en MAYÚSCULAS y líneas divisorias (====================).
        
        3. PRÁCTICA:
           Genera exactamente {cantidad} ejercicios para cada una de estas técnicas: {', '.join(tecnicas)}.
           Asegúrate de evaluar: {', '.join(gramatica_vocab)}.
        
        4. SOLUCIONARIO:
           Incluye todas las respuestas detalladas al final del documento.
        """
        
        with st.spinner("Generando contenido extenso de alta calidad..."):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                res_json = r.json()
                if "candidates" in res_json:
                    st.session_state['material_final'] = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    st.success("¡Material generado correctamente!")
                else:
                    st.error("Hubo un problema con la respuesta de la IA. Revisa tu API Key.")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# --- VISUALIZACIÓN Y DESCARGA ---
if 'material_final' in st.session_state:
    st.divider()
    st.text_area("Vista previa del material (Formato TXT Pro):", st.session_state['material_final'], height=500)
    
    # Descarga de TXT compatible con iPad
    st.download_button(
        label="📥 Descargar TXT Profesional para iPad",
        data=st.session_state['material_final'],
        file_name=f"Clase_ELE_{tema.replace(' ', '_')}.txt",
        mime="text/plain"
    )
