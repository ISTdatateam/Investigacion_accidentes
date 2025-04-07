import streamlit as st

st.set_page_config(
    page_title="Voice Local App",
    page_icon="🎤",
    layout="centered",
)

# Permisos globales (versión simplificada)
st.markdown("""<meta 
        http-equiv="Permissions-Policy" 
        content="microphone=(self)"
    >""", unsafe_allow_html=True)

audio_value = st.audio_input("Grabar desde móvil", key="local_mic")

