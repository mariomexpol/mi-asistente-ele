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
    st.info("Nota: El archivo TXT está diseñado para ser convertido a PDF en tu iPad.")

# --- INTERFAZ ---
st.title("🎓 Generador ELE Pro")
modo = st.radio("Modo de trabajo:", ["Unidad Completa (Texto + Ejercicios)", "Solo Ejercicios"], horizontal=True)

st.divider()

col1, col2 = st.columns(2)
with col1:
    tema = st.text_input("Tema de la clase", placeholder="Ej: Tradiciones mexicanas")
    nivel = st.selectbox("Nivel MCER", ["A1", "A2", "B1", "B2", "C1", "C2"])
    if modo == "Unidad Completa (Texto + Ejercicios)":
        extension = st.select_slider("Extensión del texto", 
                                    options=["Corto", "Medio", "Largo (2 págs)", "Extenso (3 págs)"], 
                                    value="3 páginas (Extenso)")
    cantidad = st.number_input("Cantidad de ejercicios por técnica", 1, 30, 15)

with col2:
    tecnicas = st.multiselect("Técnicas pedagógicas", 
                             ["Test de Cloze", "Preguntas de comprensión", "Verdadero o Falso", 
                              "Corregir errores", "Relacionar columnas", "Ordenar frases"],
                             default=["Test de Cloze", "Preguntas de comprensión"])
    
    gramatica = st.multiselect("Enfoque Gramática / Vocabulario", 
                            ["Presente", "Pretéritos", "Subjuntivo", "Ser/Estar", "Vocabulario"],
                            default=["Subjuntivo", "Vocabulario"])

if st.button("🚀 Generar Material Profesional"):
    if not api_key or not tema:
        st.error("⚠️ Por favor, introduce la API Key y el tema.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key.strip()}"
        
        # PROMPT REFORZADO PARA TXT ESTRUCTURADO
        prompt = f"""
        Actúa como profesor de {nombre_escuela}. Genera una unidad ELE de nivel {nivel} sobre '{tema}'.
        
        ESTRUCTURA DEL TXT (MUY IMPORTANTE):
        1. Encabezado: Nombre de la escuela y Profesor {nombre_profe}.
        2. Texto Base: Mínimo 2000 palabras si es 'Extenso', dividido en secciones con títulos claros en MAYÚSCULAS.
        3. Ejercicios: EXACTAMENTE {cantidad} ítems por técnica: {', '.join(tecnicas)}.
        4. Gramática/Vocabulario: {', '.join(gramatica)}.
        5. Soluciones: Al final del documento.
        
        Usa separadores como '====================================' entre secciones para que se vea profesional al imprimir.
        """
        
        with st.spinner("Generando material extenso... (Puede tardar 1 minuto)"):
            try:
                r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                res_json = r.json()
                st.session_state['material_final'] = res_json["candidates"][0]["content"]["parts"][0]["text"]
                st.success("¡Material generado!")
            except Exception as e:
                st.error(f"Error en la generación: {e}")

if 'material_final' in st.session_state:
    st.divider()
    st.markdown(st.session_state['material_final'])
    
    # Botón de descarga TXT (Fiable al 100%)
    st.download_button(
        label="📥 Descargar Material Profesional (TXT)",
        data=st.session_state['material_final'],
        file_name=f"Unidad_ELE_{tema.replace(' ', '_')}.txt",
        mime="text/plain"
    )
