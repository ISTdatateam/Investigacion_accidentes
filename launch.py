import sys
from subprocess import call


def main():
    # Configuración de Streamlit
    streamlit_command = [
        "streamlit",
        "run",
        "Anexo5q_2p.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.enableCORS=true",
        "--server.enableXsrfProtection=false"
    ]

    # Ejecutar con las opciones
    sys.exit(call(streamlit_command))


if __name__ == "__main__":
    main()