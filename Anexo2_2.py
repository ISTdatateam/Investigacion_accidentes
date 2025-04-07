import streamlit as st
from numpy.ma.core import concatenate
from openai import OpenAI

gptmodel = "gpt-4o-mini-2024-07-18"
key = "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"




# Configuración inicial del estado
def inicializar_estado():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '0'
    if 'respuestas' not in st.session_state:
        st.session_state.respuestas = {}
    if 'history' not in st.session_state:  # Nuevo historial de navegación
        st.session_state.history = []


# Diccionario de páginas (sin cambios)
def load_pages():
    return {
        # Sección TAREA
        '0': page_0,
        '0.1': page_0_1,
        '0.2': page_0_2,
        '0.3': page_0_3,
        '0.4': page_0_4,
        '0.5': page_0_5,
        '0.6': page_0_6,
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
        '7': page_7,
        '7.1': page_7_1,
        '8': page_8,
        '8.1': page_8_1,
        '8.2': page_8_2,
        '8.2.1': page_8_2_1,
        '9': page_9,
        '10': page_10,
        '10.05': page_10_05,
        '10.1': page_10_1,
        '10.2': page_10_2,
        '10.3': page_10_3,
        '10.3.1': page_10_3_1,
        '11': page_11,
        '12': page_12,
        '12.1': page_12_1,
        '12.2': page_12_2,
        '12.3': page_12_3,
        '12.3.1': page_12_3_1,
        '13': page_13,
        '14': page_14,
        '15': page_15,
        '16': page_16,
        'final': page_final
    }


# Función para crear preguntas con formato
def crear_pregunta(pregunta, tipo="segmented", opciones=None, default=None, key=None):
    # Mostrar pregunta con formato
    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
    st.markdown(f"**{pregunta}**")

    if tipo == "segmented":
        return st.pills(
            label= pregunta,
            options=opciones,
            default=default,
            key=key,
            label_visibility="hidden"
        )

    elif tipo == "select":
        return st.selectbox(
            label= pregunta,
            options=opciones,
            index=opciones.index(default) if default in opciones else 0,
            key=key,
            label_visibility="hidden"
        )


    elif tipo == "text":
        return st.text_area(
            label= pregunta,
            value=default,
            key=key,
            label_visibility="hidden"
        )

    elif tipo == "pills":
        return st.pills(
            label= pregunta,
            options=opciones,
            default=default,
            selection_mode="multi",
            key=key,
            label_visibility="hidden"
        )


def botones_navegacion():
    # Generar una clave única basada en la página actual
    nav_key = f"nav_{st.session_state.current_page}"

    # Determinar opciones disponibles
    opciones = []
    if st.session_state.history:
        opciones.append("◀ Regresar")
    opciones.append("Continuar ▶")

    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

    # Mostrar controles de navegación
    accion = st.segmented_control(
        label="Navegación",
        options=opciones,
        key=nav_key,
        label_visibility="collapsed"
    )

    # Manejar acciones
    if accion == "◀ Regresar":
        st.session_state.current_page = st.session_state.history.pop()
        st.rerun()
    elif accion == "Continuar ▶":
        return True

    return False

def page_0():
    st.markdown("##### Relato inicial")

    respuesta = crear_pregunta(
        pregunta="Realiza una primera descripción del accidente",
        tipo="text",
        default=st.session_state.respuestas.get('p0', ''),
        key="p0"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p0'] = respuesta
            st.session_state.current_page = '0.1'
            st.rerun()
        else:
            st.warning("Por favor completa el relato")


def page_0_1():
    st.markdown("##### Relato inicial")

    quien = ("Analiza el relato entregado sobre el accidente y formula exactamente 3 preguntas concretas orientadas exclusivamente"
             " a identificar con claridad a QUIÉN o quiénes estuvieron involucrados en los hechos"
             " (afectados, testigos o personas relacionadas directa o indirectamente), facilitando así la posterior elaboración de un relato lógico,"
             " coherente y preciso, en tercera persona, sin interpretaciones ni suposiciones."
             " Las preguntas deben contribuir a explicitar claramente la identidad, el rol y la participación específica de cada persona en el accidente."
             " Entrega tus preguntas separadas únicamente por punto y coma (';')."
             " No abordes aspectos relacionados con Qué, Cuándo, Dónde, Por qué ni Cómo, ya que serán analizados posteriormente")

    if 'relato_accidente' not in st.session_state:
        st.session_state['relato_accidente'] =  st.session_state.respuestas['p0']

    if "preguntas_quien" not in st.session_state:
        try:
            # Se ejecuta solo la primera vez y se guarda en session_state
            st.session_state.preguntas_quien = procesar_prompt(key, quien, st.session_state.relato_accidente, gptmodel)
            st.write("**Preguntas complementarias:**")
        except Exception as e:
            st.error(f"Error al procesar la solicitud: {e}")

    lista_quien = [elemento.strip(" ") for elemento in st.session_state.preguntas_quien.split(";")]

    respuesta_a = crear_pregunta(
        pregunta=lista_quien[0],
        tipo="text",
        default=st.session_state.respuestas.get('p0_1_a', ''),
        key="p0_1_a"
    )

    respuesta_b = crear_pregunta(
        pregunta=lista_quien[1],
        tipo="text",
        default=st.session_state.respuestas.get('p0_1_b', ''),
        key="p0_1_b"
    )

    respuesta_c = crear_pregunta(
        pregunta=lista_quien[2],
        tipo="text",
        default=st.session_state.respuestas.get('p0_1_c', ''),
        key="p0_1_c"
    )

    if botones_navegacion():
        if respuesta_a and respuesta_b and respuesta_c:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p0_1_a'] = lista_quien[0] + respuesta_a
            st.session_state.respuestas['p0_1_b'] = lista_quien[1] + respuesta_b
            st.session_state.respuestas['p0_1_c'] = lista_quien[2] + respuesta_c
            st.session_state.current_page = '0.2'
            st.rerun()
        else:
            st.warning("Por favor completa el relato")

    print("RELATO: " + st.session_state['relato_accidente'])

def page_0_2():
    st.markdown("##### Relato inicial")

    que = ("Analiza el relato entregado sobre el accidente y formula exactamente 3 preguntas concretas orientadas"
           " exclusivamente a identificar con claridad QUÉ ocurrió en el accidente. Las preguntas deben contribuir"
           " directamente a precisar qué acción, evento u objeto estuvo involucrado específicamente en los hechos,"
           " permitiendo construir posteriormente un relato lógico, coherente y preciso, en tercera persona,"
           " sin interpretaciones ni suposiciones. Entrega tus preguntas separadas únicamente por punto y coma (';')."
           " No abordes aspectos relacionados con Quién, Cuándo, Dónde, Por qué ni Cómo, ya que serán analizados posteriormente.")

    st.session_state.relato_accidente = st.session_state.relato_accidente + ". " + st.session_state.respuestas['p0_1_a'] + ". " + st.session_state.respuestas['p0_1_b'] + \
                       ". " + st.session_state.respuestas['p0_1_c']


    print("RELATO: " + st.session_state['relato_accidente'])

    if "preguntas_que" not in st.session_state:
        try:
            # Se ejecuta solo la primera vez y se guarda en session_state
            st.session_state.preguntas_que = procesar_prompt(key, que, st.session_state.relato_accidente, gptmodel)
            st.write("**Preguntas complementarias:**")
        except Exception as e:
            st.error(f"Error al procesar la solicitud: {e}")

    lista_que = [elemento.strip(" ") for elemento in st.session_state.preguntas_que.split(";")]

    respuesta_a = crear_pregunta(
        pregunta=lista_que[0],
        tipo="text",
        default=st.session_state.respuestas.get('p0_2_a', ''),
        key="p0_2_a"
    )

    respuesta_b = crear_pregunta(
        pregunta=lista_que[1],
        tipo="text",
        default=st.session_state.respuestas.get('p0_2_b', ''),
        key="p0_2_b"
    )

    respuesta_c = crear_pregunta(
        pregunta=lista_que[2],
        tipo="text",
        default=st.session_state.respuestas.get('p0_2_c', ''),
        key="p0_2_c"
    )

    if botones_navegacion():
        if respuesta_a and respuesta_b and respuesta_c:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p0_2_a'] = lista_que[0] + respuesta_a
            st.session_state.respuestas['p0_2_b'] = lista_que[1] + respuesta_b
            st.session_state.respuestas['p0_2_c'] = lista_que[2] + respuesta_c
            st.session_state.current_page = '0.3'
            st.rerun()
        else:
            st.warning("Por favor completa el relato")


def page_0_3():
    st.markdown("##### Relato inicial")

    cuando = ("Analiza el relato entregado sobre el accidente y formula exactamente 3 preguntas concretas orientadas exclusivamente"
              " a identificar con claridad CUÁNDO ocurrió el accidente. Las preguntas deben contribuir directamente a precisar"
              " los momentos o secuencias temporales involucradas en los hechos, permitiendo construir posteriormente un relato"
              " lógico, coherente y preciso, en tercera persona, sin interpretaciones ni suposiciones. Entrega tus preguntas"
              " separadas únicamente por punto y coma (';'). No abordes aspectos relacionados con Quién, Qué, Dónde, Por qué ni"
              " Cómo, ya que serán analizados posteriormente.")

    st.session_state.relato_accidente += ". " + st.session_state.respuestas['p0_2_a'] + ". " + st.session_state.respuestas['p0_2_b'] + \
                       ". " + st.session_state.respuestas['p0_2_c']

    print("RELATO: " + st.session_state['relato_accidente'])

    if "preguntas_cuando" not in st.session_state:
        try:
            st.session_state.preguntas_cuando = procesar_prompt(key, cuando, st.session_state.relato_accidente, gptmodel)
            st.write("**Preguntas complementarias:**")
        except Exception as e:
            st.error(f"Error al procesar la solicitud: {e}")

    lista_cuando = [elemento.strip(" ") for elemento in st.session_state.preguntas_cuando.split(";")]

    respuesta_a = crear_pregunta(
        pregunta=lista_cuando[0],
        tipo="text",
        default=st.session_state.respuestas.get('p0_3_a', ''),
        key="p0_3_a"
    )

    respuesta_b = crear_pregunta(
        pregunta=lista_cuando[1],
        tipo="text",
        default=st.session_state.respuestas.get('p0_3_b', ''),
        key="p0_3_b"
    )

    respuesta_c = crear_pregunta(
        pregunta=lista_cuando[2],
        tipo="text",
        default=st.session_state.respuestas.get('p0_3_c', ''),
        key="p0_3_c"
    )

    if botones_navegacion():
        if respuesta_a and respuesta_b and respuesta_c:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p0_3_a'] = lista_cuando[0] + respuesta_a
            st.session_state.respuestas['p0_3_b'] = lista_cuando[1] + respuesta_b
            st.session_state.respuestas['p0_3_c'] = lista_cuando[2] + respuesta_c
            st.session_state.current_page = '0.4'
            st.rerun()
        else:
            st.warning("Por favor completa el relato")

def page_0_4():
    st.markdown("##### Relato inicial")

    donde = ("Analiza el relato entregado sobre el accidente y formula exactamente 3 preguntas concretas orientadas exclusivamente"
             " a identificar con claridad DÓNDE ocurrió el accidente. Las preguntas deben contribuir directamente a precisar"
             " el lugar exacto, ambiente físico o espacio específico involucrado en los hechos, permitiendo construir posteriormente"
             " un relato lógico, coherente y preciso, en tercera persona, sin interpretaciones ni suposiciones. Entrega tus preguntas"
             " separadas únicamente por punto y coma (';'). No abordes aspectos relacionados con Quién, Qué, Cuándo, Por qué ni Cómo,"
             " ya que serán analizados posteriormente.")

    st.session_state.relato_accidente += ". " + st.session_state.respuestas['p0_3_a'] + ". " + st.session_state.respuestas['p0_3_b'] + \
                       ". " + st.session_state.respuestas['p0_3_c']

    print("RELATO: " + st.session_state['relato_accidente'])

    if "preguntas_donde" not in st.session_state:
        try:
            st.session_state.preguntas_donde = procesar_prompt(key, donde, st.session_state.relato_accidente, gptmodel)
            st.write("**Preguntas complementarias:**")
        except Exception as e:
            st.error(f"Error al procesar la solicitud: {e}")

    lista_donde = [elemento.strip(" ") for elemento in st.session_state.preguntas_donde.split(";")]

    respuesta_a = crear_pregunta(
        pregunta=lista_donde[0],
        tipo="text",
        default=st.session_state.respuestas.get('p0_4_a', ''),
        key="p0_4_a"
    )

    respuesta_b = crear_pregunta(
        pregunta=lista_donde[1],
        tipo="text",
        default=st.session_state.respuestas.get('p0_4_b', ''),
        key="p0_4_b"
    )

    respuesta_c = crear_pregunta(
        pregunta=lista_donde[2],
        tipo="text",
        default=st.session_state.respuestas.get('p0_4_c', ''),
        key="p0_4_c"
    )

    if botones_navegacion():
        if respuesta_a and respuesta_b and respuesta_c:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p0_4_a'] = lista_donde[0] + respuesta_a
            st.session_state.respuestas['p0_4_b'] = lista_donde[1] + respuesta_b
            st.session_state.respuestas['p0_4_c'] = lista_donde[2] + respuesta_c
            st.session_state.current_page = '0.5'
            st.rerun()
        else:
            st.warning("Por favor completa el relato")

def page_0_5():
    st.markdown("##### Relato inicial")

    porque = ("Analiza el relato entregado sobre el accidente y formula exactamente 3 preguntas concretas orientadas exclusivamente"
              " a identificar con claridad POR QUÉ ocurrió el accidente. Las preguntas deben contribuir directamente a precisar"
              " las razones, causas o factores causales que intervinieron en los hechos, permitiendo construir posteriormente"
              " un relato lógico, coherente y preciso, en tercera persona, sin interpretaciones ni suposiciones. Entrega tus"
              " preguntas separadas únicamente por punto y coma (';'). No abordes aspectos relacionados con Quién, Qué, Cuándo,"
              " Dónde ni Cómo, ya que serán analizados posteriormente.")

    st.session_state.relato_accidente += ". " + st.session_state.respuestas['p0_4_a'] + ". " + st.session_state.respuestas['p0_4_b'] + \
                       ". " + st.session_state.respuestas['p0_4_c']

    print("RELATO: " + st.session_state['relato_accidente'])

    if "preguntas_porque" not in st.session_state:
        try:
            st.session_state.preguntas_porque = procesar_prompt(key, porque, st.session_state.relato_accidente, gptmodel)
            st.write("**Preguntas complementarias:**")
        except Exception as e:
            st.error(f"Error al procesar la solicitud: {e}")

    lista_porque = [elemento.strip(" ") for elemento in st.session_state.preguntas_porque.split(";")]

    respuesta_a = crear_pregunta(
        pregunta=lista_porque[0],
        tipo="text",
        default=st.session_state.respuestas.get('p0_5_a', ''),
        key="p0_5_a"
    )

    respuesta_b = crear_pregunta(
        pregunta=lista_porque[1],
        tipo="text",
        default=st.session_state.respuestas.get('p0_5_b', ''),
        key="p0_5_b"
    )

    respuesta_c = crear_pregunta(
        pregunta=lista_porque[2],
        tipo="text",
        default=st.session_state.respuestas.get('p0_5_c', ''),
        key="p0_5_c"
    )

    if botones_navegacion():
        if respuesta_a and respuesta_b and respuesta_c:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p0_5_a'] = lista_porque[0] + respuesta_a
            st.session_state.respuestas['p0_5_b'] = lista_porque[1] + respuesta_b
            st.session_state.respuestas['p0_5_c'] = lista_porque[2] + respuesta_c
            st.session_state.current_page = '0.6'
            st.rerun()
        else:
            st.warning("Por favor completa el relato")

def page_0_6():
    st.markdown("##### Relato inicial")

    como = ("Analiza el relato entregado sobre el accidente y formula exactamente 3 preguntas concretas orientadas exclusivamente"
            " a identificar con claridad CÓMO ocurrió el accidente. Las preguntas deben contribuir directamente a precisar"
            " la forma, procedimiento o mecanismo exacto a través del cual se desarrollaron los hechos, permitiendo construir"
            " posteriormente un relato lógico, coherente y preciso, en tercera persona, sin interpretaciones ni suposiciones."
            " Entrega tus preguntas separadas únicamente por punto y coma (';'). No abordes aspectos relacionados con Quién,"
            " Qué, Cuándo, Dónde ni Por qué, ya que serán analizados posteriormente.")

    st.session_state.relato_accidente += ". " + st.session_state.respuestas['p0_5_a'] + ". " + st.session_state.respuestas['p0_5_b'] + \
                       ". " + st.session_state.respuestas['p0_5_c']

    print("RELATO: " + st.session_state['relato_accidente'])

    if "preguntas_como" not in st.session_state:
        try:
            st.session_state.preguntas_como = procesar_prompt(key, como, st.session_state.relato_accidente, gptmodel)
            st.write("**Preguntas complementarias:**")
        except Exception as e:
            st.error(f"Error al procesar la solicitud: {e}")

    lista_como = [elemento.strip(" ") for elemento in st.session_state.preguntas_como.split(";")]

    respuesta_a = crear_pregunta(
        pregunta=lista_como[0],
        tipo="text",
        default=st.session_state.respuestas.get('p0_6_a', ''),
        key="p0_6_a"
    )

    respuesta_b = crear_pregunta(
        pregunta=lista_como[1],
        tipo="text",
        default=st.session_state.respuestas.get('p0_6_b', ''),
        key="p0_6_b"
    )

    respuesta_c = crear_pregunta(
        pregunta=lista_como[2],
        tipo="text",
        default=st.session_state.respuestas.get('p0_6_c', ''),
        key="p0_6_c"
    )

    if botones_navegacion():
        if respuesta_a and respuesta_b and respuesta_c:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p0_6_a'] = lista_como[0] + respuesta_a
            st.session_state.respuestas['p0_6_b'] = lista_como[1] + respuesta_b
            st.session_state.respuestas['p0_6_c'] = lista_como[2] + respuesta_c
            st.session_state.current_page = '1'  # Ajustar siguiente página según flujo
            st.rerun()
        else:
            st.warning("Por favor completa el relato")


def page_1():
    st.markdown("##### Sección TAREA")

    respuesta = crear_pregunta(
        pregunta="1. ¿La tarea que desarrollaba en el momento del accidente era propia de su puesto de trabajo?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p1'),
        key="p1"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p1'] = respuesta
            st.session_state.current_page = '2' if respuesta == "SI" else '3'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_2():
    st.markdown("##### Sección TAREA")

    respuesta = crear_pregunta(
        pregunta="2. ¿La tarea que desarrollaba era habitual?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p2'),
        key="p2"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p2'] = respuesta
            st.session_state.current_page = '2.1' if respuesta == "SI" else '3'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_2_1():
    st.markdown("##### Sección TAREA")

    respuesta = crear_pregunta(
        pregunta="2.1. ¿Se realizaba la tarea habitual de la misma manera con la que se venía realizando normalmente?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p2.1'),
        key="p2.1"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p2.1'] = respuesta
            st.session_state.current_page = '2.2' if respuesta == "SI" else '2.3'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_2_2():
    st.markdown("##### Sección TAREA")

    respuesta = crear_pregunta(
        pregunta="2.2. Desarrollando la tarea de la forma habitual ¿era posible que ocurriera el accidente?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p2.2'),
        key="p2.2"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p2.2'] = respuesta
            st.session_state.current_page = '3'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_2_3():
    st.markdown("##### Sección TAREA")

    opciones = [
        "Seleccione...",
        "No era posible realizarla de la forma habitual.",
        "Desconocía la forma habitual de realizar la tarea.",
        "Había recibido instrucciones de realizarla de esta manera.",
        "Otros (especificar)"
    ]

    respuesta = crear_pregunta(
        pregunta="2.3. ¿Por qué la persona accidentada realizaba la tarea habitual de manera diferente?",
        opciones=opciones,
        default= st.session_state.respuestas.get('p2.3') if st.session_state.respuestas.get('p2.3') else "Seleccione...",
        key="p2.3",
        tipo = "select"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p2.3'] = respuesta
            st.session_state.current_page = '2.3.1' if "Otros" in respuesta else '3'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_2_3_1():
    st.markdown("##### Sección TAREA")

    respuesta = crear_pregunta(
        pregunta="2.3.1 Especifica por qué la persona accidentada realizaba la tarea habitual de manera diferente",
        tipo="text",
        default=st.session_state.respuestas.get('p2.3.1', ''),
        key="p2.3.1"
    )

    if botones_navegacion():
        if respuesta.strip():
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p2.3.1'] = respuesta
            st.session_state.current_page = '3'
            st.rerun()
        else:
            st.warning("Por favor ingresa una especificación")


def page_3():
    st.markdown("##### Sección TAREA")

    opciones = [
        "Seleccione...",
        "Era la primera vez",
        "De manera esporádica",
        "Frecuentemente"
    ]

    respuesta = crear_pregunta(
        pregunta="3. ¿Con qué frecuencia el trabajador había desarrollado esta tarea?",
        tipo="select",
        opciones=opciones,
        default=st.session_state.respuestas.get('p3') if st.session_state.respuestas.get('p3') else "Seleccione...",
        key="p3"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p3'] = respuesta
            st.session_state.current_page = '4'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_4():
    st.markdown("##### Sección TAREA")

    respuesta = crear_pregunta(
        pregunta="4. ¿El trabajador había recibido instrucciones sobre cómo realizar la tarea?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p4'),
        key="p4"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p4'] = respuesta
            st.session_state.current_page = '4.1' if respuesta == "SI" else '5'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_4_1():
    st.markdown("##### Sección TAREA")

    opciones = ["Escritas", "Verbales", "Ambas"]

    respuesta = crear_pregunta(
        pregunta="4.1. ¿Qué tipo de instrucciones?",
        opciones=opciones,
        default=st.session_state.respuestas.get('p4.1'),
        key="p4.1"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p4.1'] = respuesta
            st.session_state.current_page = '4.2'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_4_2():
    st.markdown("##### Sección TAREA")

    opciones = [
        "Instrucciones del empleador",
        "Instrucciones del jefe",
        "Instrucciones del encargado",
        "Instrucciones de compañeros"
    ]

    respuesta = crear_pregunta(
        pregunta="4.2. ¿De quién recibió las instrucciones?",
        opciones=opciones,
        default=st.session_state.respuestas.get('p4.2'),
        key="p4.2"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p4.2'] = respuesta
            st.session_state.current_page = '4.3'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_4_3():
    st.markdown("##### Sección TAREA")

    respuesta = crear_pregunta(
        pregunta="4.3. ¿Estaba realizando la tarea de acuerdo con esas instrucciones?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p4.3'),
        key="p4.3"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p4.3'] = respuesta
            st.session_state.current_page = '5'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_5():
    st.markdown("##### Sección TAREA")

    respuesta = crear_pregunta(
        pregunta="5. ¿La tarea se realiza con EPP?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p5'),
        key="p5"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p5'] = respuesta
            st.session_state.current_page = '5.0.1' if respuesta == "SI" else '6'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_5_0_1():
    st.markdown("##### Sección TAREA")

    respuesta = crear_pregunta(
        pregunta="5.0.1 Especifica los equipos de protección que se utilizan para la tarea",
        tipo="text",
        default=st.session_state.respuestas.get('p5.0.1', ''),
        key="p5.0.1"
    )

    if botones_navegacion():
        if respuesta.strip():
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p5.0.1'] = respuesta
            st.session_state.current_page = '5.1'
            st.rerun()
        else:
            st.warning("Por favor ingresa una especificación")


def page_5_1():
    st.markdown("##### Sección TAREA")

    respuesta = crear_pregunta(
        pregunta="5.1. ¿El EPP es adecuado al riesgo?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p5.1'),
        key="p5.1"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p5.1'] = respuesta
            st.session_state.current_page = '5.2'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_5_2():
    st.markdown("##### Sección TAREA")

    respuesta = crear_pregunta(
        pregunta="5.2. ¿Usaba los EPP en el momento del accidente?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p5.2'),
        key="p5.2"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p5.2'] = respuesta
            st.session_state.current_page = '5.3'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_5_3():
    st.markdown("##### Sección TAREA")

    respuesta = crear_pregunta(
        pregunta="5.3. ¿Hubiera evitado el accidente otro EPP?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p5.3'),
        key="p5.3"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p5.3'] = respuesta
            st.session_state.current_page = '6'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_6():
    st.markdown("##### Sección LUGAR")

    respuesta = crear_pregunta(
        pregunta="6. ¿La tarea se realizaba en el lugar habitual de trabajo?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p6'),
        key="p6"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p6'] = respuesta
            st.session_state.current_page = '6.1' if respuesta == "SI" else '6.2'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_6_1():
    st.markdown("##### Sección LUGAR")

    respuesta = crear_pregunta(
        pregunta="6.1. ¿Era posible el accidente en el lugar habitual?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p6.1'),
        key="p6.1"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p6.1'] = respuesta
            st.session_state.current_page = '7'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_6_2():
    st.markdown("##### Sección LUGAR")

    opciones = [
        "Seleccione...",
        "No era posible realizarla en el lugar habitual.",
        "Desconocía el lugar habitual.",
        "Había recibido instrucciones de realizarla en otro lugar.",
        "Otros (especificar)"
    ]

    respuesta = crear_pregunta(
        pregunta="6.2. ¿Por qué no realizaba la tarea en el lugar habitual?",
        opciones=opciones,
        tipo="select",
        default= "Seleccione...",
        key="p6.2"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p6.2'] = respuesta
            st.session_state.current_page = '6.2.1' if "Otros (especificar)" in respuesta else '7'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")


def page_6_2_1():
    st.markdown("##### Sección LUGAR")

    respuesta = crear_pregunta(
        pregunta="6.2.1 Especifica por qué no se realizaba en el lugar habitual",
        tipo="text",
        default=st.session_state.respuestas.get('p6.2.1', ''),
        key="p6.2.1"
    )

    if botones_navegacion():
        if respuesta.strip():
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p6.2.1'] = respuesta
            st.session_state.current_page = '7'
            st.rerun()
        else:
            st.warning("Por favor ingresa una especificación")


def page_7():
    st.markdown("##### Sección LUGAR")

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

    respuesta = crear_pregunta(
        pregunta="7. Especifica la relación existente entre el accidente ocurrido y alguna de las circunstancias siguientes asociadas a las instalaciones existentes en el lugar en donde sucedió el accidente.",
        tipo="pills",
        opciones=opciones,
        default=st.session_state.respuestas.get('p7', []),
        key="p7"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p7'] = respuesta
            st.session_state.current_page = '7.1' if "Otros (especificar)" in respuesta else '8'
            st.rerun()
        else:
            st.warning("Por favor selecciona una opción")

def page_7_1():
    st.markdown("##### Sección LUGAR")

    respuesta = crear_pregunta(
        pregunta="7.1 Especifica la relación existente entre el accidente ocurrido y otra circunstancia asociada a las instalaciones existentes en el lugar en donde sucedió el accidente.",
        tipo="text",
        default=st.session_state.respuestas.get('p7.1',''),
        key="p7.1"
    )

    if botones_navegacion():
        if respuesta.strip():
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p7.1'] = respuesta
            st.session_state.current_page = '8'
            st.rerun()
        else:
            st.warning("Por favor ingresa una especificación")


# Sección TIEMPO
def page_8():
    st.markdown("##### Sección TIEMPO")

    respuesta = crear_pregunta(
        pregunta="8. ¿La tarea relacionada con el accidente se estaba realizando en el momento habitual?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p8'),
        key="p8"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p8'] = respuesta
            st.session_state.current_page = '8.1' if respuesta == "SI" else '8.2'
            st.rerun()

def page_8_1():
    st.markdown("##### Sección TIEMPO")

    respuesta = crear_pregunta(
        pregunta="8.1. ¿Era posible el accidente en el momento habitual?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p8.1'),
        key="p8.1"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p8.1'] = respuesta
            st.session_state.current_page = '9'
            st.rerun()

def page_8_2():
    st.markdown("##### Sección TIEMPO")

    opciones = [
        "Había surgido algún imprevisto",
        "Había recibido instrucciones",
        "Otros (especificar)"
    ]

    respuesta = crear_pregunta(
        pregunta="8.2. ¿Por qué no se realizaba en el momento habitual?",
        opciones=opciones,
        default=st.session_state.respuestas.get('p8.2'),
        key="p8.2"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p8.2'] = respuesta
            st.session_state.current_page = '8.2.1' if "Otros" in respuesta else '9'
            st.rerun()

def page_8_2_1():
    st.markdown("##### Sección TIEMPO")

    respuesta = crear_pregunta(
        pregunta="8.2.1 Especificar motivo",
        tipo="text",
        default=st.session_state.respuestas.get('p8.2.1', ''),
        key="p8.2.1"
    )

    if botones_navegacion():
        if respuesta.strip():
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p8.2.1'] = respuesta
            st.session_state.current_page = '9'
            st.rerun()

def page_9():
    st.markdown("##### Sección TIEMPO")

    opciones = [
        "Realizando horas extra",
        "Doblando un turno",
        "Jornada superior a la ordinaria",
        "Después de una pausa",
        "Otros (especificar)"
    ]

    respuesta = crear_pregunta(
        pregunta="9. ¿Relación con estas circunstancias?",
        tipo="pills",
        opciones=opciones,
        default=st.session_state.respuestas.get('p9', []),
        key="p9"
    )

    if botones_navegacion():
        st.session_state.history.append(st.session_state.current_page)
        st.session_state.respuestas['p9'] = respuesta
        st.session_state.current_page = '10'
        st.rerun()

# Sección EQUIPO DE TRABAJO
def page_10():
    st.markdown("##### Sección EQUIPO DE TRABAJO")

    respuesta = crear_pregunta(
        pregunta="10. ¿Se utilizaba equipo de trabajo?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p10'),
        key="p10"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p10'] = respuesta
            st.session_state.current_page = '10.05' if respuesta == "SI" else '11'
            st.rerun()

def page_10_05():
    st.markdown("##### Sección EQUIPO DE TRABAJO")

    respuesta = crear_pregunta(
        pregunta="10.05. Equipos utilizados",
        tipo="text",
        default=st.session_state.respuestas.get('p10.05', ''),
        key="p10.05"
    )

    if botones_navegacion():
        if respuesta.strip():
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p10.05'] = respuesta
            st.session_state.current_page = '10.1'
            st.rerun()

# Sección EQUIPO DE TRABAJO (continuación)
def page_10_1():
    st.markdown("##### Sección EQUIPO DE TRABAJO")

    respuesta = crear_pregunta(
        pregunta="10.1. ¿El equipo utilizado era el habitual?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p10.1'),
        key="p10.1"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p10.1'] = respuesta
            st.session_state.current_page = '10.2' if respuesta == "SI" else '10.3'
            st.rerun()

def page_10_2():
    st.markdown("##### Sección EQUIPO DE TRABAJO")

    respuesta = crear_pregunta(
        pregunta="10.2. ¿Era posible el accidente con el equipo habitual?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p10.2'),
        key="p10.2"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p10.2'] = respuesta
            st.session_state.current_page = '11'
            st.rerun()

def page_10_3():
    st.markdown("##### Sección EQUIPO DE TRABAJO")

    opciones = [
        "Desconocía la existencia del equipo habitual",
        "Equipo habitual en uso por otra persona",
        "Equipo habitual en mal estado",
        "Otros (especificar)"
    ]

    respuesta = crear_pregunta(
        pregunta="10.3. ¿Por qué no usó el equipo habitual?",
        opciones=opciones,
        default=st.session_state.respuestas.get('p10.3'),
        key="p10.3"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p10.3'] = respuesta
            st.session_state.current_page = '10.3.1' if "Otros" in respuesta else '11'
            st.rerun()

def page_10_3_1():
    st.markdown("##### Sección EQUIPO DE TRABAJO")

    respuesta = crear_pregunta(
        pregunta="10.3.1 Especificar motivo",
        tipo="text",
        default=st.session_state.respuestas.get('p10.3.1', ''),
        key="p10.3.1"
    )

    if botones_navegacion():
        if respuesta.strip():
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p10.3.1'] = respuesta
            st.session_state.current_page = '11'
            st.rerun()

def page_11():
    st.markdown("##### Sección EQUIPO DE TRABAJO")

    opciones = [
        "Órganos móviles accesibles",
        "Zona operación desprotegida",
        "Arranque intempestivo",
        "Anulación de protectores",
        "Falta dispositivos control",
        "Ausencia alarmas",
        "Paro emergencia inexistente",
        "Paro emergencia inaccesible",
        "Falta medios consignación",
        "Falta protecciones antivuelco",
        "Deficiencia protecciones antivuelco",
        "Ausencia pantallas protección",
        "Deficiencia cabinas protección",
        "Otros (especificar)"
    ]

    respuesta = crear_pregunta(
        pregunta="11. ¿El accidente tuvo relación con alguna de estas circunstancias?",
        tipo="pills",
        opciones=opciones,
        default=st.session_state.respuestas.get('p11', []),
        key="p11"
    )

    if botones_navegacion():
        st.session_state.history.append(st.session_state.current_page)
        st.session_state.respuestas['p11'] = respuesta
        st.session_state.current_page = '12'
        st.rerun()

# Sección MATERIALES, SUSTANCIAS Y/O PRODUCTOS
def page_12():
    st.markdown("##### Sección MATERIALES")

    respuesta = crear_pregunta(
        pregunta="12. ¿Hubo sustancias/productos involucrados?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p12'),
        key="p12"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p12'] = respuesta
            st.session_state.current_page = '12.1' if respuesta == "SI" else '13'
            st.rerun()

def page_12_1():
    st.markdown("##### Sección MATERIALES")

    opciones = [
        "Explosivo",
        "Inflamable",
        "Tóxico",
        "Corrosivo",
        "Irritante",
        "Sensibilizante",
        "Reactivo con agua",
        "Otros (especificar)"
    ]

    respuesta = crear_pregunta(
        pregunta="12.1. Tipo de sustancia/producto",
        tipo="pills",
        opciones=opciones,
        default=st.session_state.respuestas.get('p12.1', []),
        key="p12.1"
    )

    if botones_navegacion():
        st.session_state.history.append(st.session_state.current_page)
        st.session_state.respuestas['p12.1'] = respuesta
        st.session_state.current_page = '12.2'
        st.rerun()

def page_12_2():
    st.markdown("##### Sección MATERIALES")

    respuesta = crear_pregunta(
        pregunta="12.2. ¿Era de uso habitual esta sustancia?",
        opciones=["SI","NO"],
        default=st.session_state.respuestas.get('p12.2'),
        key="p12.2"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p12.2'] = respuesta
            st.session_state.current_page = '13' if respuesta == "SI" else '12.3'
            st.rerun()

def page_12_3():
    st.markdown("##### Sección MATERIALES")

    opciones = [
        "Sustancia habitual agotada",
        "Uso excepcional",
        "Otros (especificar)"
    ]

    respuesta = crear_pregunta(
        pregunta="12.3. ¿Por qué se usó sustancia no habitual?",
        opciones=opciones,
        default=st.session_state.respuestas.get('p12.3'),
        key="p12.3"
    )

    if botones_navegacion():
        if respuesta:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p12.3'] = respuesta
            st.session_state.current_page = '12.3.1' if "Otros" in respuesta else '13'
            st.rerun()

def page_12_3_1():
    st.markdown("##### Sección MATERIALES")

    respuesta = crear_pregunta(
        pregunta="12.3.1 Especificar motivo",
        tipo="text",
        default=st.session_state.respuestas.get('p12.3.1', ''),
        key="p12.3.1"
    )

    if botones_navegacion():
        if respuesta.strip():
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p12.3.1'] = respuesta
            st.session_state.current_page = '13'
            st.rerun()

def page_13():
    st.markdown("##### Sección MATERIALES")

    opciones = [
        "Materiales muy pesados",
        "Materiales con aristas cortantes",
        "Inestabilidad en almacenamiento",
        "Manipulación manual de cargas",
        "Otros (especificar)"
    ]

    respuesta = crear_pregunta(
        pregunta="13. ¿Relación con estas circunstancias?",
        tipo="pills",
        opciones=opciones,
        default=st.session_state.respuestas.get('p13', []),
        key="p13"
    )

    if botones_navegacion():
        st.session_state.history.append(st.session_state.current_page)
        st.session_state.respuestas['p13'] = respuesta
        st.session_state.current_page = '14'
        st.rerun()

# Función genérica para secciones con preguntas A/B
def crear_seccion_ab(pregunta_num, titulo_seccion, factores, key_base):
    st.markdown(f"##### {titulo_seccion}")
    respuestas = {}

    for factor in factores:
        st.markdown(f"**{factor}**")
        col1, col2 = st.columns(2)

        with col1:
            a_key = f"{key_base}_{factor}_A"
            a_resp = st.radio(
                "A. Presencia durante el accidente",
                ["NO","SI"],
                horizontal=True,
                key=a_key,
                index=0 if st.session_state.respuestas.get(a_key) is None else ["SI","NO"].index(
                    st.session_state.respuestas.get(a_key))
            )

        with col2:
            b_key = f"{key_base}_{factor}_B"
            if a_resp == "SI":
                b_resp = st.radio(
                    "B. Presencia habitual",
                    ["NO","SI"],
                    horizontal=True,
                    key=b_key,
                    index=0 if st.session_state.respuestas.get(b_key) is None else ["SI","NO"].index(
                        st.session_state.respuestas.get(b_key))
                )
            else:
                b_resp = None
                if st.session_state.respuestas.get(b_key):
                    del st.session_state.respuestas[b_key]

        respuestas[factor] = {"Presencia durante el accidente": a_resp, "Presencia habitual": b_resp}

    return respuestas

# Sección AMBIENTE DE TRABAJO
def page_14():
    factores = [
        "Agresión térmica por frío/calor",
        "Nivel de ruido elevado",
        "Iluminación incorrecta",
        "Nivel de vibración elevado",
        "Exposición a tóxicos",
        "Contaminantes biológicos",
        "Agresiones por seres vivos",
        "Otros"
    ]

    respuestas = crear_seccion_ab(
        pregunta_num=14,
        titulo_seccion="AMBIENTE DE TRABAJO",
        factores=factores,
        key_base="p14"
    )

    if botones_navegacion():
        st.session_state.history.append(st.session_state.current_page)
        st.session_state.respuestas['p14'] = respuestas
        st.session_state.current_page = '15'
        st.rerun()

# Sección FACTORES MÚSCULO ESQUELÉTICOS
def page_15():
    factores = [
        "Exceso de esfuerzo físico",
        "Manipulación de cargas",
        "Posturas forzadas",
        "Movimientos repetitivos",
        "Otros"
    ]

    respuestas = crear_seccion_ab(
        pregunta_num=15,
        titulo_seccion="FACTORES MÚSCULO ESQUELÉTICOS",
        factores=factores,
        key_base="p15"
    )

    if botones_navegacion():
        st.session_state.history.append(st.session_state.current_page)
        st.session_state.respuestas['p15'] = respuestas
        st.session_state.current_page = '16'
        st.rerun()

# Sección ORGANIZACIÓN DEL TRABAJO
def page_16():
    factores = [
        "Simultaneidad de tareas",
        "Ritmo elevado",
        "Primas por productividad",
        "Trabajo monótono",
        "Trabajo aislado",
        "Falta de supervisión",
        "Trabajo a turnos",
        "Trabajo nocturno",
        "Trabajo temporal",
        "Exceso de horas",
        "Esfuerzo mental excesivo",
        "Otros"
    ]

    respuestas = crear_seccion_ab(
        pregunta_num=16,
        titulo_seccion="ORGANIZACIÓN DEL TRABAJO",
        factores=factores,
        key_base="p16"
    )

    if botones_navegacion():
        st.session_state.history.append(st.session_state.current_page)
        st.session_state.respuestas['p16'] = respuestas
        st.session_state.current_page = 'final'
        st.rerun()



questions = {
    # Sección TAREA
    "p0":"Relato inicial del accidente",
    "p1": "1. ¿La tarea que desarrollaba en el momento del accidente era propia de su puesto de trabajo?",
    "p2": "2. ¿La tarea que desarrollaba era habitual?",
    "p2.1": "2.1. ¿Se realizaba la tarea habitual de la misma manera con la que se venía realizando normalmente?",
    "p2.2": "2.2. Desarrollando la tarea de la forma habitual ¿era posible que ocurriera el accidente?",
    "p2.3": "2.3. ¿Por qué la persona accidentada realizaba la tarea habitual de manera diferente?",
    "p2.3.1": "2.3.1 Especifica por qué la persona accidentada realizaba la tarea habitual de manera diferente",
    "p3": "3. ¿Con qué frecuencia el trabajador había desarrollado esta tarea?",
    "p4": "4. ¿El trabajador había recibido instrucciones sobre cómo realizar la tarea?",
    "p4.1": "4.1. ¿Qué tipo de instrucciones?",
    "p4.2": "4.2. ¿De quién recibió las instrucciones?",
    "p4.3": "4.3. ¿Estaba realizando la tarea de acuerdo con esas instrucciones?",
    "p5": "5. ¿La tarea se realiza con EPP?",
    "p5.0.1": "5.0.1 Especifica los equipos de protección utilizados",
    "p5.1": "5.1. ¿El EPP es adecuado al riesgo?",
    "p5.2": "5.2. ¿Usaba los EPP en el momento del accidente?",
    "p5.3": "5.3. ¿Hubiera evitado el accidente otro EPP?",
    "p6": "6. ¿La tarea se realizaba en el lugar habitual de trabajo?",
    "p6.1": "6.1. ¿Era posible el accidente en el lugar habitual?",
    "p6.2": "6.2. ¿Por qué no realizaba la tarea en el lugar habitual?",
    "p6.2.1": "6.2.1 Especifica por qué no se realizaba en el lugar habitual",
    "p7": "7. Especifica la relación existente entre el accidente ocurrido y alguna de las circunstancias siguientes asociadas a las instalaciones existentes en el lugar en donde sucedió el accidente.",
    "p7.1": "7.1 Especifica la relación existente entre el accidente ocurrido y otra circunstancia asociada a las instalaciones existentes en el lugar en donde sucedió el accidente.",
    "p8": "8. ¿La tarea relacionada con el accidente se estaba realizando en el momento habitual?",
    "p8.1": "8.1. ¿Era posible el accidente en el momento habitual?",
    "p8.2": "8.2. ¿Por qué no se realizaba en el momento habitual?",
    "p8.2.1": "8.2.1 Especificar motivo",
    "p9": "9. ¿Relación con estas circunstancias?",
    "p10": "10. ¿Se utilizaba equipo de trabajo?",
    "p10.05": "10.05. Equipos utilizados",
    "p10.1": "10.1. ¿El equipo utilizado era el habitual?",
    "p10.2": "10.2. ¿Era posible el accidente con el equipo habitual?",
    "p10.3": "10.3. ¿Por qué no usó el equipo habitual?",
    "p10.3.1": "10.3.1 Especificar motivo",
    "p11": "11. ¿Relación con estas circunstancias?",
    "p12": "12. ¿Hubo sustancias/productos involucrados?",
    "p12.1": "12.1. Tipo de sustancia/producto",
    "p12.2": "12.2. ¿Era de uso habitual esta sustancia?",
    "p12.3": "12.3. ¿Por qué se usó sustancia no habitual?",
    "p12.3.1": "12.3.1 Especificar motivo",
    "p13": "13. ¿Relación con estas circunstancias?"}



# Página final

def reemplazar_claves(respuestas, questions):
    respuestas_modificadas = {}
    for key, valor in respuestas.items():
        # Se obtiene el texto de la pregunta; si no se encuentra, se mantiene la clave original
        texto_pregunta = questions.get(key, key)
        respuestas_modificadas[texto_pregunta] = valor
    return respuestas_modificadas



def procesar_prompt(api_key: str, instruccion: str, prompt: str, model: str) -> str:
    """
    Procesa el prompt utilizando la API de OpenAI.

    :param api_key: API key para autenticarse en OpenAI.
    :param instruccion: Instrucción predefinida para guiar la respuesta.
    :param prompt: Texto del prompt ingresado por el usuario.
    :param model: Modelo a utilizar (por defecto "gpt-4o-mini-2024-07-18").
    :return: Respuesta generada por la API.
    """
    client = OpenAI(api_key=api_key)
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "developer", "content": instruccion},
                {"role": "user", "content": prompt},
            ],
        )
        answer = completion.choices[0].message.content
        return answer
    except Exception as e:
        return f"Error al procesar la solicitud: {e}"

def page_final():
    st.markdown("## Formulario Completo")
    st.success("¡Gracias por completar el formulario!")
    respuestas_con_texto = reemplazar_claves(st.session_state.respuestas, questions)
    with st.expander("Resumen de respuestas", expanded=False):
        st.write(respuestas_con_texto)

    construir_relato = """Utilizando la información de la encuesta semiestructurada, redacta un relato de hechos objetivo y cronológico del accidente. El relato debe integrar y responder de manera clara a cada uno de los siguientes aspectos basados en la encuesta:

    1. Descripción y Contexto Inicial:
       - Comienza con el "Relato inicial del accidente" (por ejemplo, "Juanito se cayó mientras arreglaba unas cajas").
       - Responde las siguientes preguntas:
         - ¿La tarea desarrollada era propia del puesto de trabajo? (Pregunta 1)
         - ¿La tarea era habitual? (Pregunta 2)
         - ¿Con qué frecuencia se realizaba la tarea? (Pregunta 3, ej.: "De manera esporádica")
         - ¿El trabajador había recibido instrucciones sobre cómo realizar la tarea? (Pregunta 4)
         - ¿Se realizaba la tarea utilizando EPP? (Pregunta 5)

    2. Lugar y Condiciones del Trabajo:
       - ¿La tarea se realizaba en el lugar habitual de trabajo? (Pregunta 6)
       - ¿Era posible que ocurriera el accidente en ese lugar? (Pregunta 6.1)
       - ¿La tarea se desarrollaba en el momento habitual? (Pregunta 8)
       - ¿Era posible el accidente en ese momento? (Pregunta 8.1)
       - Menciona cualquier circunstancia relacionada, como la realización de horas extra (Pregunta 9).

    3. Instalaciones y Equipos:
       - Describe la relación del accidente con las condiciones de las instalaciones, por ejemplo: "Focos de ignición no controlados" o "Protección eléctrica indirecta defectuosa" (Pregunta 7).
       - Indica si se utilizaba equipo de trabajo (Pregunta 10) y, en su caso, especifica circunstancias relacionadas, como "Órganos móviles accesibles" o "Paro de emergencia inaccesible" (Pregunta 11).

    4. Sustancias y Materiales:
       - Señala si hubo sustancias o productos involucrados (Pregunta 12).
       - Especifica detalles relevantes como "Materiales muy pesados" (Pregunta 13).

    5. Condiciones Ambientales y Organizacionales (p14, p15, p16):
       - p14: Detalla las condiciones ambientales, por ejemplo, la presencia de "Nivel de ruido elevado" o "Contaminantes biológicos" durante y de forma habitual.
       - p15: Explica condiciones físicas como "Manipulación de cargas" y "Movimientos repetitivos", indicando su presencia durante el accidente y en la rutina.
       - p16: Describe factores de organización y modalidad de trabajo, tales como "Trabajo aislado", "Trabajo a turnos", "Esfuerzo mental excesivo" o "Primas por productividad".

    6. Estructura y Objetividad:
       - Organiza el relato de forma cronológica, respondiendo claramente quién, qué, cómo, dónde y cuándo.
       - Limítate a exponer hechos verificables basados en las respuestas de la encuesta, evitando interpretaciones o juicios de valor. Si se presentan interpretaciones, identifícalas y respáldalas con la información disponible.

    Utiliza esta guía para construir un relato conciso, riguroso y fundamentado que permita identificar las causas y condiciones del accidente integrando toda la información entregada."""

    # Área de texto para el prompt
    datos_respuesta = str(respuestas_con_texto)

    if st.button("Procesar con IA"):
        if not datos_respuesta:
            st.warning("Por favor, ingresa un prompt.")
        else:
            try:
                respuesta = procesar_prompt(key, construir_relato, datos_respuesta, gptmodel)
                st.subheader("Respuesta:")
                st.write(respuesta)
            except Exception as e:
                st.error(f"Error al procesar la solicitud: {e}")


    if st.button("Reiniciar formulario"):
        st.session_state.clear()
        st.rerun()

def main():
    st.subheader("Formulario de Investigación de Accidentes")
    inicializar_estado()
    pages = load_pages()

    # Mostrar página actual
    pages[st.session_state.current_page]()

    # Debug respuestas
    st.sidebar.subheader("Respuestas actuales")
    respuestas_con_texto = reemplazar_claves(st.session_state.respuestas, questions)
    st.sidebar.write(respuestas_con_texto)
    st.sidebar.subheader("Historial de navegación")
    st.sidebar.write(st.session_state.history)

if __name__ == "__main__":
    main()