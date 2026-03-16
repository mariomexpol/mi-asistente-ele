import streamlit as st
import requests
import json

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración")
    nombre_escuela = st.text_input("Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("API Key", type="password")
    st.info("💡 El TXT generado está optimizado para convertirse en PDF en iPad.")

# --- INTERFAZ PRINCIPAL ---
st.title("🎓 Generador ELE Pro")
modo = st.radio("Selecciona modo:", ["Unidad Completa (Texto + Ejercicios)", "Solo Ejercicios"], horizontal=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    tema = st.text_input("Tema de la clase", placeholder="Ej: La biodiversidad en México")
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    
    # Opciones fijas para evitar el ValueError
    opciones_ext = ["Corto", "1 página", "2 páginas", "3 páginas (Extenso)"]
    if modo == "Unidad Completa (Texto + Ejercicios)":
        extension = st.select_slider("Extensión del texto base", options=opciones_ext, value="3 páginas (Extenso)")
    
    cantidad = st.number_input("Items por técnica", min_value=1, max_value=30, value=15)

with col2:
    tecnicas = st.multiselect("Técnicas pedagógicas", 
                             ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", 
                              "Corregir errores", "Relacionar columnas", "Ordenar frases", "Traducción"],
                             default=["Test de Cloze", "Preguntas de comprensión"])
    
    gramatica_vocab = st.multiselect("Enfoque Gramática / Vocabulario", 
                            ["Presente", "Pretéritos", "Subjuntivo", "Ser/Estar", "Por/Para", "Vocabulario"],
                            default=["Subjuntivo", "Vocabulario"])

# --- LÓGICA DE GENERACIÓN ---
if st.button("🚀 Generar Material Profesional"):
    if not api_key or not tema:
        st.error("⚠️ Falta la API Key o el Tema.")
    elif not tecnicas:
        st.warning("⚠️ Selecciona al menos una técnica.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        # Prompt diseñado para TXT de alta calidad
        if modo == "Unidad Completa (Texto + Ejercicios)":
            instruccion = f"Redacta un texto de nivel {nivel} sobre '{tema}' con una extensión de {extension} (mínimo 2000 palabras si es extenso). Luego crea exactamente {cantidad} ejercicios por técnica: {', '.join(tecnicas)}."
        else:
            instruccion = f"Crea una lista de {cantidad} ejercicios de nivel {nivel} sobre '{tema}' usando: {', '.join(tecnicas)}."

        prompt = f"""
        Actúa como profesor experto de {nombre_escuela}.
        {instruccion}
        
        REQUISITOS DE FORMATO TXT:
        - Usa '========================================' para separar secciones.
        - Títulos en MAYÚSCULAS.
        - Gramática a evaluar: {', '.join(gramatica_vocab)}.
        - Incluye SOLUCIONES detalladas al final.
        - Firma como el profesor {nombre_profe}.
        """
        
        with st.spinner("Generando material extenso... Por favor espera."):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                res_json = r.json()
                if "candidates" in res_json:
                    st.session_state['material_final'] = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    st.success("¡Material generado!")
                else:
                    st.error("Error en la respuesta de la IA. Revisa tu API Key.")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# --- RESULTADOS Y DESCARGA ---
if 'material_final' in st.session_state:
    st.divider()
    st.markdown(st.session_state['material_final'])
    
    st.download_button(
        label="📥 Descargar TXT Profesional",
        data=st.session_state['material_final'],
        file_name=f"Material_ELE_{tema.replace(' ', '_')}.txt",
        mime="text/plain"
    )
