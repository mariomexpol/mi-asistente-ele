import streamlit as st
import requests
import json

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración")
    logo_file = st.file_uploader("Subir logo", type=["png", "jpg", "jpeg"])
    if logo_file: st.image(logo_file, width=150)
    
    nombre_escuela = st.text_input("Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Profesor/a", "Mario")
    api_key = st.text_input("API Key", type="password")

# --- INTERFAZ PRINCIPAL ---
st.title("🎓 Generador ELE Pro")

modo = st.radio("Selecciona qué deseas generar:", 
                ["Unidad con Texto Base", "Solo Lista de Ejercicios"], 
                horizontal=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    tema_especifico = st.text_input("Tema de la clase", placeholder="Ej: El cambio climático o Leyendas de México")
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    
    if modo == "Unidad con Texto Base":
        # Cambio realizado: Se añade la opción de hasta 3 hojas A4
        extension = st.select_slider("Extensión del texto", 
                                    options=[
                                        "Corto (150 palabras)", 
                                        "Medio (1 página A4)", 
                                        "Largo (2 páginas A4)", 
                                        "Extenso (3 páginas A4)"
                                    ],
                                    value="Medio (1 página A4)")
    
    cantidad_ejercicios = st.number_input("Cantidad de ítems por técnica", min_value=1, max_value=30, value=5)

with col2:
    tecnicas = st.multiselect("Técnicas pedagógicas", 
                             ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", 
                              "Corregir errores", "Relacionar columnas", "Ordenar frases", "Traducción"],
                             default=["Test de Cloze", "Preguntas de comprensión"])
    
    enfoque_gramatical = st.multiselect("Gramática/Vocabulario a evaluar", 
                            ["Presente", "Pretéritos", "Subjuntivo", "Ser/Estar", "Por/Para", "Vocabulario"],
                            default=["Presente"])

if st.button("🚀 Generar Material"):
    if not api_key or not tema_especifico:
        st.error("⚠️ Falta la API Key o el Tema.")
    elif not tecnicas:
        st.warning("⚠️ Selecciona al menos una técnica.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        # Lógica de prompt para la nueva extensión
        if modo == "Unidad con Texto Base":
            instruccion_modo = (
                f"PASO 1: Redacta un texto académico y pedagógico de nivel {nivel} sobre '{tema_especifico}'. "
                f"La extensión DEBE SER de {extension}. Si es 'Extenso', desarrolla profundamente los subtemas, "
                f"usa vocabulario rico y estructura el texto en varios párrafos largos. "
                f"PASO 2: Basándote en ese texto, crea {cantidad_ejercicios} ítems para cada una de estas técnicas: {', '.join(tecnicas)}."
            )
        else:
            instruccion_modo = f"Crea una lista de {cantidad_ejercicios} ejercicios de nivel {nivel} sobre '{tema_especifico}' sin texto previo. Usa las técnicas: {', '.join(tecnicas)}."

        prompt = f"""
        Actúa como un profesor de español de la institución {nombre_escuela}.
        {instruccion_modo}
        
        Asegúrate de que los ejercicios evalúen: {', '.join(enfoque_gramatical)}.
        Incluye siempre las soluciones detalladas al final del documento.
        Firma el material como el profesor {nombre_profe}.
        """
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        with st.spinner("Generando material extenso (esto puede tardar un poco más por el volumen de texto)..."):
            try:
                response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
                res_json = response.json()
                
                if "candidates" in res_json:
                    texto_final = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    st.session_state['material_final'] = texto_final
                    st.success("¡Material Generado con éxito!")
                else:
                    st.error(f"Error de cuota o API: {res_json.get('error', {}).get('message')}")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

if 'material_final' in st.session_state:
    st.divider()
    st.markdown(st.session_state['material_final'])
    st.download_button("📥 Descargar Material (TXT)", st.session_state['material_final'], file_name=f"Material_{tema_especifico}.txt")
