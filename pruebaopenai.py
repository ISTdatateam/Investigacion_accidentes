import streamlit as st
import os
from openai import OpenAI

key= "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"

client = OpenAI(api_key= key)


# Configuración de la página
st.set_page_config(page_title="Interfaz con OpenAI GPT", layout="wide")

st.title("Interfaz con OpenAI GPT")

# Área de texto para el prompt
prompt = st.text_area("Ingresa tu pregunta o solicitud", "")

if st.button("Enviar"):
    if not prompt:
        st.warning("Por favor, ingresa un prompt.")
    else:
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                messages=[
                    {"role": "developer", "content": "Genera respuestas breves y en bullet points"},
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

            # Mostrar la respuesta en pantalla
            answer = completion.choices[0].message.content
            st.subheader("Respuesta:")
            st.write(answer)
        except Exception as e:
            st.error(f"Error al procesar la solicitud: {e}")
