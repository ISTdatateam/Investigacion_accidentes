import streamlit as st
from openai import OpenAI
import ast

gptpreguntas = "gpt-4o-mini-2024-07-18"
#gptpreguntas = "o3-mini-2025-01-31"

gptaudio= "gpt-4o-mini-transcribe"

key = "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"
client = OpenAI(api_key=key)

# Configuración inicial del estado
def inicializar_estado():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'final'
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



# Generación del relato
if "relato" not in st.session_state:
    st.session_state.relato = """El accidente ocurrió el miércoles a las 17:00, al término de la jornada laboral, en la sala de preparación de pan de una instalación de fabricación de productos de panadería. En esta área se encontraba una sobadora, que es un equipo utilizado para amasar y tratar la masa de pan. Este tipo de máquina, debido a su diseño antiguo, estaba adosada a la pared lateral derecha de la sala y carecía de un sistema de bloqueo que impidiera el acceso a los rodillos durante su funcionamiento. Por lo tanto, en condiciones normales, el operador podía acceder a los rodillos desde el costado de la máquina.

En ese momento, el operador de máquina decidió proceder a limpiar los rodillos de la sobadora mientras esta estaba en funcionamiento, bajo la creencia de que se le haría más fácil de esa manera. A pesar de que no existía un procedimiento de seguridad establecido para llevar a cabo la limpieza de la máquina, el trabajador llevó a cabo la actividad sin asegurarse de que el equipo estuviera detenido. Este procedimiento inadecuado y la falta de medidas preventivas, como un protocolo que obligara a detener la máquina antes de realizar cualquier tarea de limpieza, contribuyeron a la generación de un ambiente de riesgo.

Durante la limpieza, el trabajador se colocó por el costado de la sobadora, en un área peligrosa por la cercanía de los rodillos en movimiento. A pesar de que no había testigos presentes en el momento del accidente, el operador sufrió un atrapamiento en alguna de las partes móviles de la máquina. Este incidente evidenció las condiciones inseguras en las que se operaba y la falta de capacitación o de un sistema de trabajo seguro que incluyera medidas adecuadas para la limpieza de la sobadora.

La máquina, al ser muy antigua, no contaba con diseños modernos que incluyeran protecciones adecuadas para evitar el acceso a partes móviles, lo que se tradujo en un incumplimiento de las normas de seguridad que podrían haber prevenido el incidente. En conclusión, el atrapamiento del operador durante la limpieza de la sobadora se debió a una serie de factores, entre los que se incluyen la falta de procedimientos adecuados, el estado de antiquedad del equipo, y la decisión del trabajador de operar la máquina en funcionamiento durante la limpieza."""

def page_final():
    st.markdown("## Generación de árbol de causas")

    if st.session_state.relato:
        with st.expander("relato", expanded=False):
            st.write(st.session_state.relato)

    data_arbol = "Relato accidente: " + str(st.session_state.relato)

    prompt_arbol = """
        - Analiza el relato 100 veces.
        - Identifica la consecuencia (Lesion que sufre el trabajador) como evento final, luego para ese hecho identifica de la información disponible cuales son las causas necesarias para que ocurriera entre los hechos identificados.
        - Luego para cada una de estos hechos (causas de segundo nivel) identifica que causas fueron necesarias para que ocurriera cada una de ellas.
        - En cada nodo se espera que identifiques de 1 a 3 causas.
        - Se espera que el arbol tenga entre 3 a 5 niveles    
        - Bajo el título "Arbol de causas", construye un árbol de causas utilizando el código numérico de ramas.
           - Utiliza la siguiente codificación:
               • "0.0.0.0.0.0.0.0.0" para el evento final.
               • "1.0.0.0.0.0.0.0.0" para la causa inmediata.
               • Las subcausas se representarán añadiendo dígitos en cada nivel, por ejemplo "1.1.0.0.0.0.0.0.0", "1.2.0.0.0.0.0.0.0", etc.
           - Si para que se produzca un evento es necesario que concurran dos o más condiciones (por ejemplo, que un objeto se proyecte y que el trabajador se encuentre en zona de riesgo), representa estas condiciones como ramas paralelas que convergen en ese evento.

        Ejemplo de resultado y formato de salida esperado:

        "0.0.0.0.0.0.0.0.0": "Trauma torácico con resultado fatal",
        "1.0.0.0.0.0.0.0.0": "Trabajador golpeado por eje"
        "1.1.0.0.0.0.0.0.0": "Eje se proyecta hacia el trabajador",
        "1.1.1.0.0.0.0.0.0": "Corte de un estrobo",
        "1.1.2.0.0.0.0.0.0": "Eje choca con embarcación",
        "1.1.2.1.0.0.0.0.0": "Eje realiza movimiento tipo péndulo",
        "1.1.2.1.1.0.0.0.0": "Tecle que soporta extremo trabaja de forma diagonal",
        "1.1.2.1.2.0.0.0.0": "Eje abandona su alojamiento y pierde soporte",
        "1.2.0.0.0.0.0.0.0": "Trabajador permanece a un costado del eje",
        "1.2.1.0.0.0.0.0.0": "Trabajador realizaba limpieza del eje"
         ...
    
        
        Vuelve a analizar tu resultado, ve que tenga una estructura logica, que la causalidad sea demostrable, que solo tome hechos comprobables de la información disponible.
        No incluyas juicios de valor como por ejemplo "Condiciones del equipo inadecuadas", por otro lado un hecho bien identificado seria "Equipo no cuenta con protección"
        Entrega solo los datos en código y su glosa, sin otros comentarios. Cada linea debe tener el codigo entre cremillas dobles ("), dos puntos (:), la glosa entre cremillas dobles y finalizado por coma (,), Similar a la estructura de un diccionario de python
        
        """


    if "arbol" not in st.session_state:
        st.session_state.arbol = {}


    # Generación del árbol de causas
    if st.button("Generar Árbol con IA 🤖"):
        try:
            # Aquí tu lógica para generar el árbol
            arbol = procesar_prompt(key, prompt_arbol, data_arbol, gptpreguntas)
            st.subheader("Árbol de causas:")

            # Envolvemos el texto entre llaves para formar un literal de diccionario válido
            arbol = "{" + arbol + "}"

            # Evaluamos de forma segura el literal y lo convertimos en un diccionario
            st.session_state.arbol = ast.literal_eval(arbol)
            st.write(str(st.session_state.arbol))
            print(st.session_state.arbol)

        except Exception as e:
            st.error(f"Error al generar árbol: {e}")

    if st.session_state.arbol:
        with st.expander("Códigos arbol", expanded=False):
            st.write(st.session_state.arbol)

    if st.button("Visualizar árbol 🤖"):
        try:
            if st.session_state.arbol:
                from pyecharts import options as opts
                from pyecharts.charts import Tree
                import webbrowser
                import os

                # ---------------------------------------------------------
                # Funciones adaptadas para diccionarios
                # ---------------------------------------------------------
                def normalize_code(code_str):
                    """Convierte el código a tupla de 9 segmentos"""
                    parts = code_str.split('.')
                    return tuple(parts + ['0'] * (9 - len(parts)) if len(parts) < 9 else parts)

                def find_parent_code(normalized_code):
                    """Encuentra el código padre basado en la estructura jerárquica"""
                    try:
                        last_non_zero = max(i for i, part in enumerate(normalized_code) if part != '0')
                    except ValueError:
                        return None  # Es la raíz (0.0.0.0.0.0.0.0.0)

                    parent_parts = list(normalized_code)
                    parent_parts[last_non_zero] = '0'
                    return tuple(parent_parts[:last_non_zero + 1] + ['0'] * (9 - (last_non_zero + 1)))

                def build_tree_from_dict(data_dict):
                    """Construye el árbol desde un diccionario"""
                    node_map = {}
                    root = None

                    # Primera pasada: crear todos los nodos
                    for code_str, name in data_dict.items():
                        code = normalize_code(code_str)
                        parent_code = find_parent_code(code)

                        node_map[code] = {
                            "name": name,
                            "children": [],
                            "parent_code": parent_code
                        }

                    # Segunda pasada: vincular padres e hijos
                    for code, node in node_map.items():
                        parent_code = node["parent_code"]
                        if parent_code is None:
                            root = node
                        elif parent_code in node_map:
                            node_map[parent_code]["children"].append(node)
                        else:
                            st.warning(f"Padre no encontrado para: {code}")

                    # --- DEBUG: Mostrar estructura generada ---
                    st.json({
                        k: {"name": v["name"], "children": [c["name"] for c in v["children"]]}
                        for k, v in node_map.items() if v["children"]
                    })
                    # ------------------------------------------

                    return [root] if root else []

                # ---------------------------------------------------------
                # Procesamiento y validación
                # ---------------------------------------------------------
                # Convertir a diccionario si es necesario
                arbol_data = dict(st.session_state.arbol)

                # Validar formato mínimo
                if "0.0.0.0.0.0.0.0.0" not in arbol_data:
                    raise ValueError("Falta el nodo raíz (0.0.0.0.0.0.0.0.0)")

                # Construir árbol
                roots = build_tree_from_dict(arbol_data)

                # Crear gráfico
                tree_chart = Tree(init_opts=opts.InitOpts(width="1200px", height="800px"))
                tree_chart.add(
                    "",
                    roots,
                    orient="LR",
                    label_opts=opts.LabelOpts(
                        position="left",
                        font_size=12,
                        font_style="bold",
                        width=250
                    ),
                    initial_tree_depth=-1  # Expandir todo
                )
                tree_chart.set_global_opts(title_opts=opts.TitleOpts(title="Árbol de Causas desde Diccionario"))

                # Mostrar
                output_file = "arbol_diccionario.html"
                tree_chart.render(output_file)
                webbrowser.open("file://" + os.path.realpath(output_file))

        except Exception as e:
            st.error(f"Error: {str(e)}")

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