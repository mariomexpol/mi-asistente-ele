import streamlit as st
import requests

st.title("Buscador de Modelos Disponibles")
api_key = st.text_input("Pega tu API Key", type="password")

if st.button("🔍 Ver mis modelos"):
    url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key.strip()}"
    response = requests.get(url)
    modelos = response.json()
    
    if "models" in modelos:
        st.success("Tus modelos disponibles son:")
        for m in modelos["models"]:
            st.code(m["name"]) # Esto te dará la lista real
    else:
        st.error(f"Error: {modelos}")
