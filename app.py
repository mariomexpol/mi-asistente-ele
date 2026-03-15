import streamlit as st
import requests
import json

# Cambio realizado: E/LE -> ELE
st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración")
    logo_file = st.file_uploader("Subir logo", type=["png", "jpg", "jpeg"])
    if logo_file: st.image(logo_file, width=150)
    
    nombre_escuela = st.text_input("Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("API Key", type="password")

# Cambio realizado: E/LE -> ELE
st.title("🎓 Generador de Unidades Didácticas ELE")

col1, col2 = st.columns(2)

with col1:
    tema_especifico = st.text_input("Tema del texto", placeholder="Ej: La contaminación o Navidad en México")
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    extension = st.select_slider("Extensión del texto base", 
                                options=["Corto (150 palabras)", "Medio (Mitad A4)", "Largo (A4 completo)"])

with col2:
    tecnicas = st.multiselect("Selecciona los tipos de ejercicios", 
                             ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", 
                              "Corregir errores", "Relacionar columnas", "Ordenar frases"],
                             default=["Test de Cloze", "Preguntas de comprensión"])
    
    enfoque_gramatical = st.multiselect("Enfoque gramatical", 
                            ["Presente", "Pretéritos", "Subjuntivo", "Ser/Estar", "Vocabulario específico"],
                            default=["Presente"])

if st.button("🚀 Crear Unidad Completa"):
    if not api_key or not tema_especifico:
        st.error("⚠️ Falta la API Key o el Tema del texto.")
    elif not tecnicas:
        st.warning("⚠️ Selecciona al menos un tipo de ejercicio.")
    else:
        # Usamos Gemini 2.5 Pro que es el que te dio éxito
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        prompt = f"""
        Actúa como un profesor de español de {nombre_escuela}.
        
        PASO 1: Redacta un texto de nivel {nivel} sobre '{tema_especifico}'. 
        Extensión: {extension}.
        
        PASO 2: Basándote en ese texto, crea los siguientes tipos de ejercicios:
        {', '.join(tecnicas)}.
        
        Asegúrate de que los ejercicios practiquen: {', '.join(enfoque_gramatical)}.
        
        PASO 3: Incluye las soluciones detalladas.
        
        Firma como el profesor {nombre_profe}.
        """
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        with st.spinner("Generando unidad didáctica..."):
            try:
                response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
                res_json = response.json()
                texto_final = res_json["candidates"][0]["content"]["parts"][0]["text"]
                st.session_state['unidad_didactica'] = texto_final
                st.success("¡Unidad Generada!")
            except Exception as e:
                st.error(f"Error: {e}")

if 'unidad_didactica' in st.session_state:
    st.divider()
    st.markdown(st.session_state['unidad_didactica'])
    st.download_button("📥 Descargar Unidad (TXT)", st.session_state['unidad_didactica'], file_name=f"Unidad_{tema_especifico}.txt")
