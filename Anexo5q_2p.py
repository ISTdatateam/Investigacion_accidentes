import streamlit as st
from openai import OpenAI
from io import BytesIO

gptpreguntas = "gpt-4o-mini-2024-07-18"
gptaudio= "gpt-4o-mini-transcribe"

key = "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"
client = OpenAI(api_key=key)

# Configuración inicial del estado
def inicializar_estado():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '0'
    if 'respuestas' not in st.session_state:
        st.session_state.respuestas = {}
    if 'history' not in st.session_state:  # Nuevo historial de navegación
        st.session_state.history = []
    if 'hechos' not in st.session_state:
        st.session_state.hechos = {}
    if 'arbol' not in st.session_state:
        st.session_state.arbol = {}


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
        'semifinal': page_semifinal,
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

    if 'respuestas' not in st.session_state:
        st.session_state['respuestas'] = {}

    respuesta = crear_pregunta(
        pregunta="Realiza una primera descripción del accidente",
        tipo="text",
        default=st.session_state.respuestas.get('p0', ''),
        key="p0"
    )

    # Navegación
    if botones_navegacion():
        if respuesta.strip():
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p0'] = respuesta
            st.session_state.current_page = '0.1'
            st.rerun()
        else:
            st.warning("Por favor completa el relato")



def page_0_1():
    st.markdown("##### Relato inicial")

    quien = ("Analiza el relato entregado sobre el accidente y formula exactamente 2 preguntas concretas orientadas exclusivamente"
             " a identificar con claridad a QUIÉN o quiénes estuvieron involucrados en los hechos"
             " (afectados, testigos o personas relacionadas directa o indirectamente)."
             " Entrega tus preguntas separadas únicamente por punto y coma (';').")

    if 'relato_accidente' not in st.session_state:
        st.session_state['relato_accidente'] =  st.session_state.respuestas['p0']

    if "preguntas_quien" not in st.session_state:
        try:
            st.session_state.preguntas_quien = procesar_prompt(key, quien, st.session_state.relato_accidente, gptpreguntas)
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

    if botones_navegacion():
        if respuesta_a and respuesta_b:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p0_1_a'] = lista_quien[0] + " " + respuesta_a
            st.session_state.respuestas['p0_1_b'] = lista_quien[1] + " " + respuesta_b
            st.session_state.current_page = '0.2'
            st.rerun()
        else:
            st.warning("Por favor completa el relato")



def page_0_2():
    st.markdown("##### Relato inicial")

    que = ("Analiza el relato entregado sobre el accidente y formula exactamente 2 preguntas concretas orientadas"
           " exclusivamente a identificar con claridad QUÉ ocurrió en el accidente."
           " Entrega tus preguntas separadas únicamente por punto y coma (';').")

    st.session_state.relato_accidente += ". " + st.session_state.respuestas['p0_1_a'] + ". " + st.session_state.respuestas['p0_1_b']

    if "preguntas_que" not in st.session_state:
        try:
            st.session_state.preguntas_que = procesar_prompt(key, que, st.session_state.relato_accidente, gptpreguntas)
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

    if botones_navegacion():
        if respuesta_a and respuesta_b:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p0_2_a'] = lista_que[0] + " " + respuesta_a
            st.session_state.respuestas['p0_2_b'] = lista_que[1] + " " + respuesta_b
            st.session_state.current_page = '0.3'
            st.rerun()
        else:
            st.warning("Por favor completa el relato")

    print(st.session_state.respuestas)

def page_0_3():
    st.markdown("##### Relato inicial")

    cuando = ("Analiza el relato entregado sobre el accidente y formula exactamente 2 preguntas concretas orientadas"
              " exclusivamente a identificar con claridad CUÁNDO ocurrió el accidente."
              " Entrega tus preguntas separadas únicamente por punto y coma (';').")

    st.session_state.relato_accidente += ". " + st.session_state.respuestas['p0_2_a'] + ". " + st.session_state.respuestas['p0_2_b']

    if "preguntas_cuando" not in st.session_state:
        try:
            st.session_state.preguntas_cuando = procesar_prompt(key, cuando, st.session_state.relato_accidente, gptpreguntas)
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

    if botones_navegacion():
        if respuesta_a and respuesta_b:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p0_3_a'] = lista_cuando[0] + " " + respuesta_a
            st.session_state.respuestas['p0_3_b'] = lista_cuando[1] + " " + respuesta_b
            st.session_state.current_page = '0.4'
            st.rerun()
        else:
            st.warning("Por favor completa el relato")

    print(st.session_state.respuestas)

def page_0_4():
    st.markdown("##### Relato inicial")

    donde = ("Analiza el relato entregado sobre el accidente y formula exactamente 2 preguntas concretas orientadas"
             " exclusivamente a identificar con claridad DÓNDE ocurrió el accidente."
             " Entrega tus preguntas separadas únicamente por punto y coma (';').")

    st.session_state.relato_accidente += ". " + st.session_state.respuestas['p0_3_a'] + ". " + st.session_state.respuestas['p0_3_b']

    if "preguntas_donde" not in st.session_state:
        try:
            st.session_state.preguntas_donde = procesar_prompt(key, donde, st.session_state.relato_accidente, gptpreguntas)
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

    if botones_navegacion():
        if respuesta_a and respuesta_b:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p0_4_a'] = lista_donde[0] + " " + respuesta_a
            st.session_state.respuestas['p0_4_b'] = lista_donde[1] + " " + respuesta_b
            st.session_state.current_page = '0.5'
            st.rerun()
        else:
            st.warning("Por favor completa el relato")

    print(st.session_state.respuestas)

def page_0_5():
    st.markdown("##### Relato inicial")

    porque = ("Analiza el relato entregado sobre el accidente y formula exactamente 2 preguntas concretas orientadas"
              " exclusivamente a identificar con claridad POR QUÉ ocurrió el accidente."
              " Entrega tus preguntas separadas únicamente por punto y coma (';').")

    st.session_state.relato_accidente += ". " + st.session_state.respuestas['p0_4_a'] + ". " + st.session_state.respuestas['p0_4_b']

    if "preguntas_porque" not in st.session_state:
        try:
            st.session_state.preguntas_porque = procesar_prompt(key, porque, st.session_state.relato_accidente, gptpreguntas)
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

    if botones_navegacion():
        if respuesta_a and respuesta_b:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p0_5_a'] = lista_porque[0] + " " + respuesta_a
            st.session_state.respuestas['p0_5_b'] = lista_porque[1] + " " + respuesta_b
            st.session_state.current_page = '0.6'
            st.rerun()
        else:
            st.warning("Por favor completa el relato")

    print(st.session_state.respuestas)

def page_0_6():
    st.markdown("##### Relato inicial")

    como = ("Analiza el relato entregado sobre el accidente y formula exactamente 2 preguntas concretas orientadas"
            " exclusivamente a identificar con claridad CÓMO ocurrió el accidente."
            " Entrega tus preguntas separadas únicamente por punto y coma (';').")

    st.session_state.relato_accidente += ". " + st.session_state.respuestas['p0_5_a'] + ". " + st.session_state.respuestas['p0_5_b']

    if "preguntas_como" not in st.session_state:
        try:
            st.session_state.preguntas_como = procesar_prompt(key, como, st.session_state.relato_accidente, gptpreguntas)
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

    if botones_navegacion():
        if respuesta_a and respuesta_b:
            st.session_state.history.append(st.session_state.current_page)
            st.session_state.respuestas['p0_6_a'] = lista_como[0] + " " + respuesta_a
            st.session_state.respuestas['p0_6_b'] = lista_como[1] + " " + respuesta_b
            st.session_state.current_page = 'semifinal'
            st.rerun()
        else:
            st.warning("Por favor completa el relato")

    print(st.session_state.respuestas)

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


def page_semifinal():
    st.markdown("## Generación de relato")
    st.success("¡Gracias por completar el formulario!")
    respuestas_con_texto = st.session_state.respuestas

    with st.expander("Resumen de respuestas", expanded=False):
        st.write(respuestas_con_texto)

    prompt_relato = """
    Genera un relato de accidente que cumpla las siguientes indicaciones:

    1. El relato debe estar escrito en prosa, estructurado en párrafos fluidos sin el uso de subtítulos, divisiones o encabezados. Debe leerse como una narrativa continua.
    2. La narrativa debe ser clara y objetiva, describiendo los eventos y actividades en orden cronológico y secuencial, sin incluir juicios, opiniones o interpretaciones subjetivas.
    3. Proporciona antecedentes y contexto suficiente: describe el entorno, las condiciones de trabajo, el equipo utilizado y los procedimientos seguidos, incluyendo detalles técnicos y operativos relevantes.
    4. Asegúrate de que cada hecho o evento relevante esté expresado de forma concreta y observable, NO INVENTES NADA!, se debe identificar de forma objetiva los hechos para su posterior análisis.
    5. El relato debe incluir la secuencia de eventos y condiciones que conducen al accidente, de manera que se puedan identificar las relaciones de causa y efecto necesarias para la generación de un árbol de causas.
    6. La narrativa debe incorporar todos los elementos esenciales sin dividirse en secciones; por ejemplo, debe incluir una introducción con el contexto, seguida de la descripción detallada del desarrollo del accidente y la secuencia de acciones y fallos que permitieron que ocurriera el suceso.
    7. Una vez finalices una version preliminar del relato, vuelve a revisarlo para corroborar que todos los hechos sean contrastables en la información existente, retirando las partes que no tienen sustento.
    Utiliza estos lineamientos para generar un relato de accidente lo suficientemente detallado y estructurado, que facilite la extracción de un listado de hechos ordenado cronológicamente y la construcción de un árbol de causas basado en la relación causa-efecto.
    """

    # Generación del relato
    if "relato" not in st.session_state:
        st.session_state.relato = ""

    if st.button("Genera el relato con IA"):
        if not respuestas_con_texto:
            st.warning("Por favor completa el formulario primero")
        else:
            try:
                # Aquí tu lógica para generar el relato
                relato = procesar_prompt(key, prompt_relato, str(respuestas_con_texto), gptpreguntas)
                st.session_state.relato = str(relato)
                st.success("Relato generado correctamente")
            except Exception as e:
                st.error(f"Error al generar relato: {e}")

    # Mostrar relato generado
    if st.session_state.relato:
        with st.expander("Relato generado", expanded=True):
            st.write(st.session_state.relato)

        # Botón de navegación mejorado
        col1, col2 = st.columns([1, 2])
        with col2:
            if st.button("Continuar a Árbol de Causas ➡️"):
                st.session_state.current_page = 'final'
                st.rerun()


def page_final():
    st.markdown("## Generación de árbol de causas")

    prompt_hechos = """
    Dado el siguiente relato de accidente, realiza lo siguiente:

    1. Listado de hechos:
       - Analiza todo el relato, leelo 100 veces.
       - Identifica los hechos dentro del relato, lo cual debe basarse únicamente en la información objetiva y observable presente en el relato, sin incluir juicios, opiniones o interpretaciones subjetivas.
       - Razonar para la identificación de hechos implica analizar el relato para distinguir entre:
           - Datos o eventos concretos (por ejemplo, "la viga se desliza", "el trabajador se encontraba en la zona de riesgo").
           - Condiciones o circunstancias que se expresan de forma clara.
           - No se deben incluir interpretaciones, suposiciones o valoraciones personales.
       - La redacción de los hechos debe ser breve, muy concisa sobre la información que se quiere aportar.
       - Extrae y ordena cronológicamente el listado de hechos identificados en el relato.
       - Cada hecho debe estar numerado de forma cronológica, comenzando en 1.

    Formato de salida esperado:

    Listado de hechos:
    1. [Hecho 1]
    2. [Hecho 2]
    ...
    """

    if st.session_state.relato:
        with st.expander("relato", expanded=False):
            st.write(st.session_state.relato)

    if "hechos" not in st.session_state:
        st.session_state.hechos = ""

    st.markdown("## Generación listado de hechos")

    # Generación del árbol de causas
    if st.button("Identificar listado de hechos con IA 🤖"):
        try:
            # Aquí tu lógica para generar el árbol
            hechos = procesar_prompt(key, prompt_hechos, st.session_state.relato, gptpreguntas)
            st.session_state.hechos = str(hechos)
            st.success("Listado de hechos generado correctamente")
            st.subheader("Listado de hechos:")
            st.write(hechos)
        except Exception as e:
            st.error(f"Error al generar listado de hechos: {e}")

    st.markdown("## Generación de árbol de causas")

    data_arbol = "Relato accidente: " + str(st.session_state.relato) + "/n/n/n" + "Hechos identificados: " + str(
        st.session_state.hechos)

    prompt_arbol = """
        Dado el siguiente relato y listado de hechos identificados, analiza como cada uno de los hechos se ordena por su relaciones de causa y consecuencias,
        y construye un Árbol de causas, es importante que TODOS los hechos se encuentren representados en el arbol de causas.
           - Bajo el título "Arbol de causas", construye un árbol de causas utilizando el código numérico de ramas.
           - Utiliza la siguiente codificación:
               • "0.0.0.0.0.0.0.0.0" para el evento final.
               • "1.0.0.0.0.0.0.0.0" para la causa inmediata.
               • Las subcausas se representarán añadiendo dígitos en cada nivel, por ejemplo "1.1.0.0.0.0.0.0.0", "1.2.0.0.0.0.0.0.0", etc.
           - Si para que se produzca un evento es necesario que concurran dos o más condiciones (por ejemplo, que un objeto se proyecte y que el trabajador se encuentre en zona de riesgo), representa estas condiciones como ramas paralelas que convergen en ese evento.

        Formato de salida esperado:

        Arbol de causas:
        0.0.0.0.0.0.0.0.0  [Evento final]/n
        1.0.0.0.0.0.0.0.0  [Causa inmediata]/n
        1.1.0.0.0.0.0.0.0  [Condición necesaria]/n
        1.2.0.0.0.0.0.0.0  [Otra condición necesaria]/n
        1.1.1.0.0.0.0.0.0  [Condición necesaria para que ocurriera 1.1]/n
        1.1.2.0.0.0.0.0.0  [Otra Condición necesaria para que ocurriera 1.1]/n
        ...

        Cada nodo puede tener una o mas condiciones necesarias (causas), recuerda que todos los hechos tienen que representarse en el arbol de causas
        """

    # Generación del árbol de causas
    if st.button("Generar Árbol con IA 🤖"):
        try:
            # Aquí tu lógica para generar el árbol
            arbol = procesar_prompt(key, prompt_arbol, st.session_state.hechos, gptpreguntas)
            st.subheader("Árbol de causas:")
            st.write(arbol)
        except Exception as e:
            st.error(f"Error al generar árbol: {e}")

    # Botón de reinicio
    if st.button("Reiniciar formulario ♻️"):
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