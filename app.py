import streamlit as st
import requests
import json

# Configuración de página
st.set_page_config(page_title="Asistente E/LE Pro", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración del Centro")
    
    # Ventana para el LOGO
    logo_file = st.file_uploader("Subir logo de la escuela", type=["png", "jpg", "jpeg"])
    if logo_file:
        st.image(logo_file, width=150)
    
    nombre_escuela = st.text_input("Nombre de la Escuela", "Mi Escuela de Español")
    nombre_profe = st.text_input("Nombre del Profesor/a", "Tu Nombre")
    api_key = st.text_input("API Key (Gemini 2.5 Pro)", type="password")
    st.info("Obtén tu clave en: aistudio.google.com")

# --- INTERFAZ PRINCIPAL ---
st.title("🎓 Generador de Materiales E/LE")
st.markdown("Crea materiales académicos personalizados y listos para usar.")

col1, col2 = st.columns(2)

with col1:
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    tema = st.text_input("Tema de la clase", placeholder="Ej: El pretérito indefinido")
    modulo = st.radio("Tipo de material", ["Ejercicios Gramaticales", "Comprensión Lectora"])

with col2:
    cantidad = st.number_input("Cantidad de ejercicios/preguntas", min_value=1, max_value=20, value=5)
    tecnicas = st.multiselect("Técnicas pedagógicas", 
                             ["Test de Cloze", "Rellenar huecos", "Traducción", "Corregir errores", "Relacionar", "Ordenar frases"])

# --- LÓGICA DE GENERACIÓN ---
if st.button("🚀 Generar Material"):
    if not api_key or not tema:
        st.error("⚠️ Por favor, introduce la API Key y el tema en la barra lateral.")
    else:
        # URL forzada al modelo que te funcionó: Gemini 2.5 Pro
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        cuerpo_prompt = (
            f"Actúa como un profesor de español experto de la institución {nombre_escuela}. "
            f"Crea material de nivel {nivel} sobre el tema: {tema}. "
            f"Módulo: {modulo}. Técnicas a usar: {', '.join(tecnicas)}. "
            f"Cantidad: {cantidad} ejercicios. "
            f"Firma el documento como el profesor/a {nombre_profe}. "
            f"IMPORTANTE: Incluye siempre una sección final con las SOLUCIONES detalladas."
        )
        
        payload = {
            "contents": [{"parts": [{"text": cuerpo_prompt}]}]
        }
        headers = {'Content-Type': 'application/json'}

        with st.spinner("Conectando con Gemini 2.5 Pro..."):
            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                res_json = response.json()
                
                if "candidates" in res_json:
                    texto_final = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    st.session_state['material_generado'] = texto_final
                    st.success("¡Material generado con éxito!")
                else:
                    st.error(f"Error de la API: {res_json.get('error', {}).get('message', 'Error desconocido')}")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# --- MOSTRAR RESULTADOS ---
if 'material_generado' in st.session_state:
    st.divider()
    
    # Encabezado visual en la app
    if logo_file:
        st.image(logo_file, width=100)
    st.subheader(f"📄 Material: {tema} - {nombre_escuela}")
    st.info(f"Profesor/a: {nombre_profe}")
    
    st.markdown(st.session_state['material_generado'])
    
    # Descarga
    st.download_button(
        label="📥 Descargar Material (TXT)",
        data=st.session_state['material_generado'],
        file_name=f"Clase_{tema.replace(' ', '_')}.txt",
        mime="text/plain"
    )
