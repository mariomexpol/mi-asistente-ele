import streamlit as st
import requests
import json

st.set_page_config(page_title="Asistente E/LE Pro", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración")
    logo_file = st.file_uploader("Subir logo", type=["png", "jpg", "jpeg"])
    if logo_file: st.image(logo_file, width=150)
    
    nombre_escuela = st.text_input("Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("API Key", type="password")

# --- INTERFAZ PRINCIPAL ---
st.title("🎓 Generador de Unidades Didácticas E/LE")

col1, col2 = st.columns(2)

with col1:
    tema_especifico = st.text_input("Tema del texto", placeholder="Ej: La contaminación en las ciudades o Navidad en México")
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    extension = st.select_slider("Extensión del texto base", 
                                options=["Corto (150 palabras)", "Medio (Mitad A4)", "Largo (A4 completo)"])

with col2:
    enfoque = st.multiselect("Gramática a evaluar", 
                            ["Presente", "Pretéritos", "Subjuntivo", "Por/Para", "Ser/Estar"])
    cantidad_ejercicios = st.slider("Número de ejercicios", 1, 10, 5)

if st.button("🚀 Crear Unidad Completa"):
    if not api_key or not tema_especifico:
        st.error("⚠️ Falta la API Key o el Tema del texto.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        # Prompt estructurado para generar primero el texto y luego los ejercicios
        prompt = f"""
        Actúa como un profesor de español de {nombre_escuela}.
        PASO 1: Redacta un texto original para nivel {nivel} sobre el tema '{tema_especifico}'. 
        Extensión aproximada: {extension}. 
        
        PASO 2: Basándote EXCLUSIVAMENTE en el texto redactado, crea {cantidad_ejercicios} actividades:
        - Incluye técnicas como Test de Cloze, preguntas de comprensión y corrección de errores.
        - Enfócate en la gramática: {', '.join(enfoque)}.
        
        PASO 3: Añade las soluciones detalladas al final.
        
        Formatea todo con títulos claros. Firma como el profesor {nombre_profe}.
        """
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        with st.spinner("Redactando texto y diseñando ejercicios..."):
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
