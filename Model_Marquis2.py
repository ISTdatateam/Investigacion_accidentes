import streamlit as st
from graphviz import Digraph


class TreeNode:
    def __init__(self, cause, level=0):
        self.cause = cause
        self.level = level
        self.children = []
        self.completed = False


def initialize_session():
    if 'root' not in st.session_state:
        st.session_state.root = None
    if 'current_path' not in st.session_state:
        st.session_state.current_path = []
    # Comentar o eliminar la siguiente línea para no sobrescribir el valor del text_input
    # if current_level() < 5:
    #     if current_node() is not None and not current_node().completed:
    #         st.session_state.new_cause = ''
    if 'adding_cause' not in st.session_state:
        st.session_state.adding_cause = False


def current_node():
    return st.session_state.current_path[-1] if st.session_state.current_path else None


def current_level():
    return len(st.session_state.current_path)


def add_cause(cause):
    parent = current_node()
    new_level = parent.level + 1 if parent else 0
    # Validación de profundidad máxima (nivel 5)
    if new_level > 5:
        st.error("¡Se alcanzó el máximo de niveles (5)!")
        return

    new_node = TreeNode(cause, new_level)

    if parent:
        parent.children.append(new_node)
    else:
        st.session_state.root = new_node

    # Depuración: imprimir en terminal
    print(f"Agregando causa: {new_node.cause} en nivel {new_node.level}")
    # Depuración: mostrar en la barra lateral
    st.sidebar.write("Debug - Agregando causa:", new_node.cause, f"(Nivel {new_node.level})")

    # Agregar el nuevo nodo a la ruta actual
    st.session_state.current_path.append(new_node)
    st.session_state.adding_cause = False
    st.rerun()


def finish_branch():
    if current_node():
        current_node().completed = True
    if st.session_state.current_path:
        st.session_state.current_path.pop()
    st.rerun()


def render_tree():
    dot = Digraph()
    # Configurar dirección Top to Bottom (de arriba hacia abajo)
    dot.attr(rankdir='TB', ranksep='0.8', newrank='true')
    dot.attr('edge', arrowhead='none', dir='forward', color='#606060')  # Flechas hacia abajo
    dot.attr('node', shape='ellipse', style='filled', fontname='Arial')

    current = current_node()

    def add_nodes(node, parent=None):
        if node is None:
            return
        node_id = str(id(node))

        # Estilo del nodo actual (nivel 5 sería la raíz)
        if node == current:
            node_style = {'fillcolor': '#FFB74D', 'color': '#BF360C', 'penwidth': '2'}
        else:
            node_style = {'fillcolor': '#E1F5FE', 'color': '#0277BD'}

        if node.level == 5:  # Máximo nivel
            dot.node(node_id, f"Nivel {node.level}\n{node.cause}", color='darkred')


        dot.node(
            node_id,
            f"Nivel {node.level}\n{node.cause}",
            **node_style,
            fontsize='10'
        )

        if parent:
            dot.edge(parent, node_id)  # Conexión padre -> hijo (nivel superior -> inferior)

        # Recorrer hijos manteniendo el orden de causalidad
        for child in reversed(node.children):  # Invertir orden para visualización correcta
            add_nodes(child, node_id)

    add_nodes(st.session_state.root)
    st.graphviz_chart(dot)


# ---------- Modificación en get_all_nodes_hierarchically() ----------
def get_all_nodes_hierarchically(node, nodes_list=None, depth=0):
    if nodes_list is None:
        nodes_list = []
    if node is None:
        return nodes_list

    # Identación con guiones y nivel desde 0
    indent = "--" * depth
    node_label = f"{indent}→ Nivel {node.level}: {node.cause[:25]}..." if len(
        node.cause) > 25 else f"{indent}→ Nivel {node.level}: {node.cause}"

    nodes_list.append((str(id(node)), node_label))

    # Recorrer hijos manteniendo orden original
    for child in node.children:
        get_all_nodes_hierarchically(child, nodes_list, depth + 1)

    return nodes_list


def find_node_by_id(node, target_id):
    if node is None:
        return None
    if str(id(node)) == target_id:
        return node
    for child in node.children:
        found = find_node_by_id(child, target_id)
        if found:
            return found
    return None



def main():
    st.title("Análisis arbol de causas")
    initialize_session()

    # Paso 1: Obtener la lesión inicial
    if not st.session_state.root:
        with st.form("injury_form"):
            injury = st.text_input("Describa la lesión/accidente ocurrido:")
            if st.form_submit_button("Iniciar análisis"):
                add_cause(injury)
        return

    render_tree()

    # Navegación y controles
    current_lvl = current_level()
    node = current_node()

    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        if node and st.button("🔼 No hay más causas", help="Finaliza esta rama y sube un nivel"):
            finish_branch()
    with col2:
        if st.button("🔄 Reiniciar análisis", help="Elimina todo el árbol y comienza de nuevo"):
            st.session_state.clear()
            st.rerun()
    with col3:
        if node and current_lvl < 6 and st.button("➕ Agregar nueva causa", help="Añade otra causa en este mismo nivel"):
            st.session_state.adding_cause = True
            st.rerun()

    # Mostrar formulario solo si hay nodo actual
    if node and (st.session_state.adding_cause or (current_lvl < 6 and not node.completed)):
        with st.form("cause_form"):
            # Lógica de pregunta diferenciada
            if current_lvl == 0:
                pregunta_base = "¿Cuál fue la causa inmediata de"
            else:
                pregunta_base = "¿Qué otra cosa también fue necesaria para que ocurriera:" if node.children else "¿Qué fue necesario para que ocurriera:"

            prompt = f"{pregunta_base} **{node.cause}**?"
            st.write(prompt)

            new_cause = st.text_input("Descripción de la causa:")
            if st.form_submit_button("💾 Guardar causa"):
                if new_cause.strip():
                    add_cause(new_cause.strip())
                else:
                    st.error("¡Debe ingresar una descripción para la causa!")

        # ==============================================
        # Módulo de edición de nodos (añadir esto al final)
        # ==============================================
        st.sidebar.header("Editor de Causas")

        # Obtener lista de nodos con jerarquía visual
        all_nodes = get_all_nodes_hierarchically(st.session_state.root) if st.session_state.root else []

        if all_nodes:
            # Selector de nodo a editar
            selected_node_id = st.sidebar.selectbox(
                "Seleccione un nodo para editar:",
                options=[node[0] for node in all_nodes],
                format_func=lambda x: dict(all_nodes)[x]
            )

            # Buscar el nodo seleccionado
            node_to_edit = find_node_by_id(st.session_state.root, selected_node_id)

            if node_to_edit:
                # Formulario de edición
                with st.sidebar.form("edit_form"):
                    new_cause = st.text_area(
                        "Texto del nodo:",
                        value=node_to_edit.cause,
                        key="edit_cause"
                    )

                    if st.form_submit_button("💾 Guardar cambios"):
                        node_to_edit.cause = new_cause.strip()
                        st.rerun()
        else:
            st.sidebar.info("No hay nodos para editar aún")


if __name__ == "__main__":
    main()
