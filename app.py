import streamlit as st
import requests
import json

st.set_page_config(page_title="Asistente ELE Pro", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏫 Configuración del Centro")
    nombre_escuela = st.text_input("Nombre de la Escuela", "El Sabor de la Lengua")
    nombre_profe = st.text_input("Nombre del Profesor/a", "Mario")
    api_key = st.text_input("API Key", type="password")
    st.info("💡 Tip: Tras descargar el TXT en tu iPad, usa 'Imprimir > Zoom' para crear un PDF perfecto.")

# --- INTERFAZ PRINCIPAL ---
st.title("🎓 Generador ELE Pro (Edición iPad)")
modo = st.radio("Modo de trabajo:", ["Unidad Completa (Texto + Ejercicios)", "Solo Ejercicios"], horizontal=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    tema = st.text_input("Tema de la clase", placeholder="Ej: La vida nocturna en Madrid")
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    
    if modo == "Unidad Completa (Texto + Ejercicios)":
        extension = st.select_slider("Extensión del texto base", 
                                    options=["Corto", "Medio", "Largo (2 págs)", "Extenso (3 págs)"], 
                                    value="Extenso (3 págs)")
    
    cantidad = st.number_input("Cantidad de ejercicios por técnica", min_value=1, max_value=30, value=15)

with col2:
    tecnicas = st.multiselect("Técnicas pedagógicas", 
                             ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", 
                              "Corregir errores", "Relacionar columnas", "Ordenar frases"],
                             default=["Test de Cloze", "Preguntas de comprensión"])
    
    gramatica_vocab = st.multiselect("Enfoque Gramática / Vocabulario", 
                            ["Presente", "Pretéritos", "Subjuntivo", "Ser/Estar", "Vocabulario"],
                            default=["Subjuntivo", "Vocabulario"])

# --- LÓGICA DE GENERACIÓN ---
if st.button("🚀 Generar Material Maquetado"):
    if not api_key or not tema:
        st.error("⚠️ Falta la API Key o el Tema.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        # PROMPT DE DISEÑO ASCII PROFESIONAL
        prompt = f"""
        Actúa como profesor experto de {nombre_escuela}. Genera una unidad ELE de nivel {nivel} sobre '{tema}'.
        
        INSTRUCCIONES DE FORMATO PARA ARCHIVO TXT PROFESIONAL:
        1. ENCABEZADO: Crea un recuadro con asteriscos que contenga el nombre de la escuela: {nombre_escuela}.
        2. TÍTULOS: Usa una línea de símbolos '===' encima y debajo de cada título principal.
        3. SUBTÍTULOS: Usa '---' debajo de cada subtítulo.
        4. TEXTO BASE: Mínimo 2000 palabras si la extensión es extensa. Divide en párrafos claros con sangría (espacios).
        5. EJERCICIOS: Genera exactamente {cantidad} ítems numerados para cada una de estas técnicas: {', '.join(tecnicas)}.
        6. SEPARACIÓN: Usa una línea de '___' (guiones bajos) al final de cada sección de ejercicios.
        7. SOLUCIONES: Ponlas al final bajo el título 'SOLUCIONARIO DETALLADO'.
        
        Firma al final como: {nombre_profe}.
        """
        
        with st.spinner("Diseñando material maquetado..."):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                res_json = r.json()
                if "candidates" in res_json:
                    st.session_state['material_final'] = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    st.success("¡Material maquetado con éxito!")
                else:
                    st.error("Error en la API. Verifica tu clave.")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# --- RESULTADOS Y DESCARGA ---
if 'material_final' in st.session_state:
    st.divider()
    # Mostramos una previsualización
    st.text_area("Previsualización del diseño:", st.session_state['material_final'], height=400)
    
    st.download_button(
        label="📥 Descargar TXT Profesional para iPad",
        data=st.session_state['material_final'],
        file_name=f"ELE_{tema.replace(' ', '_')}.txt",
        mime="text/plain"
    )
