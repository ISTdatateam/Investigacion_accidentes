from openai import OpenAI
import streamlit as st
from io import BytesIO

key= "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"
client = OpenAI(api_key=key)


construir_relato = """
Redacta un reporte de accidente de trabajo utilizando el audio enviado. Asegúrate de cumplir con los siguientes criterios:

1. Organización Cronológica:
   - Estructura el relato en orden cronológico, abarcando los hechos previos, el desarrollo del accidente y las acciones posteriores.

2. Responde a las Preguntas Clave:
   - ¿Quién?: Identifica a las personas involucradas (empleados, testigos, supervisores, etc.).
   - ¿Qué?: Describe detalladamente lo ocurrido, enfocándote en el desarrollo del accidente.
   - ¿Cómo?: Explica el modo en que se produjo el accidente, incluyendo las circunstancias y posibles causas (factores técnicos, ambientales, etc.).
   - ¿Dónde?: Ubica el lugar exacto del incidente.
   - ¿Cuándo?: Indica la fecha y la hora en que ocurrió el accidente.

3. Claridad y Coherencia:
   - Presenta la información de forma fluida y detallada, asegurando que el relato sea coherente y fácil de seguir.

4. Hechos Verificables y Objetividad:
   - Limítate a exponer hechos comprobables, evitando interpretaciones o juicios de valor.
   - Si se incluyen interpretaciones, identifícalas claramente y respáldalas con la información disponible.

5. Tono Profesional:
   - Utiliza un lenguaje claro, formal y adecuado para informes oficiales.

Sigue estas pautas para redactar un reporte completo, objetivo y preciso del accidente de trabajo.
"""

# Interfaz de usuario
audio_value = st.audio_input("Record a voice message")

if audio_value:
    st.audio(audio_value)

    try:
        audio_bytes = audio_value.read()
        #encoded_string = base64.b64encode(audio_bytes).decode('utf-8')
        st.success("Audio codificado correctamente!")

        if st.button("Procesar con IA"):
            try:
                audio_file = BytesIO(audio_bytes)
                audio_file.name = "audio.wav"
                transcript = client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file= audio_file,
                    response_format="text",
                    prompt="El audio corresponde a la descripcion de un accidente del trabajo"
                )

                st.write(transcript)
                prompt2 = transcript

            except Exception as e:
                st.error(f"Error en la transcripción: {str(e)}")

            try:
                razonamiento = client.chat.completions.create(
                    model="o3-mini-2025-01-31",
                    messages=[
                        {
                            "role": "developer",
                            "content": construir_relato
                        },
                        {
                            "role": "user",
                            "content": prompt2
                        },
                    ],
                )

                st.subheader("Reporte generado:")
                st.write(razonamiento.choices[0].message.content)

            except Exception as e:
                st.error(f"Error al construir relato: {str(e)}")

    except Exception as e:
        st.error(f"Error en codificación de audio: {str(e)}")