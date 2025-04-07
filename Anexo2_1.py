import streamlit as st


# Configuración inicial del estado
def inicializar_estado():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '1'
    if 'respuestas' not in st.session_state:
        st.session_state.respuestas = {}


# Diccionario de páginas
def load_pages():
    return {
        # Sección TAREA
        '1': page_1,
        '2': page_2,
        '2.1': page_2_1,
        '2.2': page_2_2,
        '2.3': page_2_3,
        '2.3.1': page_2_3_1,
        '3': page_3,
        '4': page_4,
        '4.1': page_4_1,
        '4.2': page_4_2,
        '4.3': page_4_3,
        '5': page_5,
        '5.0.1': page_5_0_1,
        '5.1': page_5_1,
        '5.2': page_5_2,
        '5.3': page_5_3,
        # Sección LUGAR
        '6': page_6,
        '6.1': page_6_1,
        '6.2': page_6_2,
        '6.2.1': page_6_2_1,
        '7': page_7
        #'7.1': page_7_1
    }


# Páginas de preguntas
def page_1():
    st.text("Sección TAREA")
    respuesta = st.segmented_control(
        "1. ¿La tarea que desarrollaba en el momento del accidente era propia de su puesto de trabajo?",
        options = ["SI", "NO"],
        default=None,
        )


    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p1'] = respuesta
            st.session_state.current_page = '2' if respuesta == "SI" else '3'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_2():
    st.text("Sección TAREA")
    respuesta = st.segmented_control(
        "2. ¿La tarea que desarrollaba era habitual?",
        ["SI", "NO"],
        default=None,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p2'] = respuesta
            st.session_state.current_page = '2.1' if respuesta == "SI" else '3'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_2_1():
    st.text("Sección TAREA")
    respuesta = st.segmented_control(
        "2.1. ¿Se realizaba la tarea habitual de la misma manera con la que se venía realizando normalmente?",
        ["SI", "NO"],
        default=None,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p2.1'] = respuesta
            st.session_state.current_page = '2.2' if respuesta == "SI" else '2.3'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


# Preguntas 2.2 a 7 (continuación)
def page_2_2():
    st.text("Sección TAREA")
    respuesta = st.segmented_control(
        "2.2. Desarrollando la tarea de la forma habitual ¿era posible que ocurriera el accidente?",
        ["SI", "NO"],
        default=None,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p2.2'] = respuesta
            st.session_state.current_page = '3'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_2_3():
    st.text("Sección TAREA")
    opciones = [
        "No era posible realizarla de la forma habitual.",
        "Desconocía la forma habitual de realizar la tarea.",
        "Había recibido instrucciones de realizarla de esta manera.",
        "Otros (especificar)"
    ]
    respuesta = st.segmented_control(
        "2.3. ¿Por qué la persona accidentada realizaba la tarea habitual de manera diferente?",
        opciones,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p2.3'] = respuesta
            st.session_state.current_page = '2.3.1' if "Otros" in respuesta else '3'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_2_3_1():
    st.text("Sección TAREA")
    respuesta = st.text_input(
        "2.3.1 Especifica por qué la persona accidentada realizaba la tarea habitual de manera diferente",
        value=st.session_state.respuestas.get('p2.3.1', '')
    )
    if st.button("Continuar"):
        if respuesta.strip():
            st.session_state.respuestas['p2.3.1'] = respuesta
            st.session_state.current_page = '3'
            st.rerun()
        else:
            st.warning("Por favor ingresa una especificación")

def page_3():
    st.text("Sección TAREA")
    opciones = ["Seleccione...", "Era la primera vez", "De manera esporádica", "Frecuentemente"]
    respuesta = st.selectbox(
        "3. ¿Con qué frecuencia el trabajador había desarrollado esta tarea?",
        options=opciones,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p3'] = respuesta
            st.session_state.current_page = '4'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_4():
    st.text("Sección TAREA")
    respuesta = st.segmented_control(
        "4. ¿El trabajador había recibido instrucciones sobre cómo realizar la tarea?",
        ["SI", "NO"],
        default=None,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p4'] = respuesta
            st.session_state.current_page = '4.1' if respuesta == "SI" else '5'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_4_1():
    st.text("Sección TAREA")
    opciones = ["Escritas", "Verbales", "Ambas"]
    respuesta = st.segmented_control(
        "4.1. ¿Qué tipo de instrucciones?",
        options=opciones,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p4.1'] = respuesta
            st.session_state.current_page = '4.2'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_4_2():
    st.text("Sección TAREA")
    opciones = [
        "Instrucciones del empleador",
        "Instrucciones del jefe",
        "Instrucciones del encargado",
        "Instrucciones de compañeros"
    ]
    respuesta = st.segmented_control(
        "4.2. ¿De quién recibió las instrucciones?",
        options=opciones,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p4.2'] = respuesta
            st.session_state.current_page = '4.3'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_4_3():
    st.text("Sección TAREA")
    respuesta = st.segmented_control(
        "4.3. ¿Estaba realizando la tarea de acuerdo con esas instrucciones?",
        ["SI", "NO"],
        default=None,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p4.3'] = respuesta
            st.session_state.current_page = '5'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_5():
    st.text("Sección TAREA")
    respuesta = st.segmented_control(
        "5. ¿La tarea se realiza con EPP?",
        ["SI", "NO"],
        default=None,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p5'] = respuesta
            st.session_state.current_page = '5.0.1' if respuesta == "SI" else '6'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_5_0_1():
    st.text("Sección TAREA")
    respuesta = st.text_area(
        "5.0.1 Especifica los equipos de protección utilizados",
        value=st.session_state.respuestas.get('p5.0.1', '')
    )
    if st.button("Continuar"):
        if respuesta.strip():
            st.session_state.respuestas['p5.0.1'] = respuesta
            st.session_state.current_page = '5.1'
            st.rerun()
        else:
            st.warning("Por favor ingresa una especificación")

def page_5_1():
    st.text("Sección TAREA")
    respuesta = st.segmented_control(
        "5.1. ¿El EPP es adecuado al riesgo?",
        ["SI", "NO"],
        default=None,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p5.1'] = respuesta
            st.session_state.current_page = '5.2'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_5_2():
    st.text("Sección TAREA")
    respuesta = st.segmented_control(
        "5.2. ¿Usaba los EPP en el momento del accidente?",
        ["SI", "NO"],
        default=None,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p5.2'] = respuesta
            st.session_state.current_page = '5.3'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_5_3():
    st.text("Sección TAREA")
    respuesta = st.segmented_control(
        "5.3. ¿Hubiera evitado el accidente otro EPP?",
        ["SI", "NO"],
        default=None,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p5.3'] = respuesta
            st.session_state.current_page = '6'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_6():
    st.text("Sección LUGAR")
    respuesta = st.segmented_control(
        "6. ¿La tarea se realizaba en el lugar habitual de trabajo?",
        ["SI", "NO"],
        default=None,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p6'] = respuesta
            st.session_state.current_page = '6.1' if respuesta == "SI" else '6.2'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_6_1():
    st.text("Sección LUGAR")
    respuesta = st.segmented_control(
        "6.1. ¿Era posible el accidente en el lugar habitual?",
        ["SI", "NO"],
        default=None,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p6.1'] = respuesta
            st.session_state.current_page = '7'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_6_2():
    st.text("Sección LUGAR")
    opciones = [
        "No era posible realizarla en el lugar habitual.",
        "Desconocía el lugar habitual.",
        "Había recibido instrucciones de realizarla en otro lugar.",
        "Otros (especificar)"
    ]
    respuesta = st.segmented_control(
        "6.2. ¿Por qué no realizaba la tarea en el lugar habitual?",
        options=opciones,
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p6.2'] = respuesta
            st.session_state.current_page = '6.2.1' if "Otros" in respuesta else '7'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_6_2_1():
    st.text("Sección LUGAR")
    respuesta = st.text_area(
        "6.2.1 Especifica por qué no se realizaba en el lugar habitual",
        value=st.session_state.respuestas.get('p6.2.1', '')
    )
    if st.button("Continuar"):
        if respuesta.strip():
            st.session_state.respuestas['p6.2.1'] = respuesta
            st.session_state.current_page = '7'
            st.rerun()
        else:
            st.warning("Por favor ingresa una especificación")

def page_7():
    st.text("Sección LUGAR")
    opciones = [
        "Protección eléctrica directa defectuosa",
        "Protección eléctrica indirecta defectuosa",
        "Focos de ignición no controlados",
        "Falta de compartimentación de áreas",
        "Compartimentación insuficiente",
        "Sistemas de detección incorrectos",
        "Sistemas de extinción incorrectos",
        "Otros (especificar)"
    ]
    respuesta = st.pills(
        "7. ¿Existe relación entre el accidente y las instalaciones? Seleccione todas las condiciones presentes",
        options=opciones,
        selection_mode="multi",
        default=st.session_state.respuestas.get('p7', [])
    )
    if st.button("Continuar"):
        if respuesta:
            st.session_state.respuestas['p7'] = respuesta
            st.session_state.current_page = '7.1' if "Otros (especificar)" in respuesta else '8'
            st.rerun()
        else:
            st.warning("Por favor selecciona al menos una opción")


def main():
    st.subheader("Formulario de Investigación de Accidentes")
    inicializar_estado()
    pages = load_pages()

    # Mostrar página actual
    pages[st.session_state.current_page]()


    # Sidebar con progreso
    #st.sidebar.subheader("Progreso del formulario")
    #current_index = list(pages.keys()).index(st.session_state.current_page)
    #selected_page = st.sidebar.radio(
    #    "Preguntas completadas:",
    #    options=list(pages.keys()),
    #    index=current_index,
    #    format_func=lambda x: f"Pregunta {x}",
    #    label_visibility="collapsed"
    #)


    # Debug respuestas
    st.sidebar.subheader("Respuestas actuales")
    st.sidebar.write(st.session_state.respuestas)


if __name__ == "__main__":
    main()