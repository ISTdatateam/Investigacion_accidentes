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
            st.session_state.current_page = 'final'  # Ajustar siguiente página según flujo
            st.rerun()
        else:
            st.warning("Por favor completa el relato")


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
    respuestas_con_texto = st.session_state.respuestas
    with st.expander("Resumen de respuestas", expanded=False):
        st.write(respuestas_con_texto)

    construir_relato = """Utilizando la información de la encuesta semiestructurada, redacta un relato de hechos objetivo y cronológico del accidente. El relato debe integrar y responder de manera clara a cada uno de los siguientes aspectos:

    1. Descripción y Contexto Inicial
    2. Lugar y Condiciones del Trabajo
    3. Instalaciones y Equipos
    4. Sustancias y Materiales
    5. Condiciones Ambientales y Organizacionales
    
    Con respecto a la Estructura y Objetividad son muy importantes, por lo cual:
       - Organiza el relato de forma cronológica, respondiendo claramente quién, qué, cómo, dónde y cuándo.
       - Limítate a exponer hechos verificables basados en las respuestas, evitando interpretaciones o juicios de valor. Si se presentan interpretaciones, identifícalas y respáldalas con la información disponible.

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
    st.subheader("Formulario de Investigación de Accidentes 5Q")
    inicializar_estado()
    pages = load_pages()

    # Mostrar página actual
    pages[st.session_state.current_page]()

    # Debug respuestas
    st.sidebar.subheader("Respuestas actuales")
    respuestas_con_texto = st.session_state.respuestas
    st.sidebar.write(respuestas_con_texto)
    st.sidebar.subheader("Historial de navegación")
    st.sidebar.write(st.session_state.history)

if __name__ == "__main__":
    main()