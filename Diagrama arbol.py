from pyecharts import options as opts
from pyecharts.charts import Tree
import webbrowser
import os


def build_tree_from_lines_ordered(lines):
    """
    Construye un árbol (lista de nodos) a partir de líneas ordenadas.
    Cada línea tiene el formato:
         <código jerárquico> <descripción>
    Se utiliza un stack para determinar el nivel (basado en la cantidad de dígitos
    significativos, es decir, hasta el primer "0") y se insertan nodos placeholder si es necesario.
    Cada nodo se crea con las claves "name", "children" y, de forma interna, "code".
    """
    roots = []
    stack = []

    for line in lines:
        parts = line.strip().split(maxsplit=1)
        if not parts:
            continue
        code_str = parts[0]
        name = parts[1] if len(parts) > 1 else ""
        # Extraer la parte significativa del código (hasta el primer "0")
        code_parts = code_str.split('.')
        meaningful_parts = []
        if code_parts[0] == "0":
            meaningful_parts = ["0"]
        else:
            for p in code_parts:
                if p == "0":
                    break
                meaningful_parts.append(p)
        new_code = meaningful_parts  # Lista de segmentos
        level = len(new_code)
        new_node = {"name": name, "children": [], "code": new_code}

        if not stack:
            # Primer nodo (raíz)
            roots.append(new_node)
            stack.append(new_node)
        else:
            # Comparar el código del nodo actual (último en el stack) con el nuevo para hallar el prefijo común
            current = stack[-1]["code"]
            common = 0
            for a, b in zip(current, new_code):
                if a == b:
                    common += 1
                else:
                    break
            # Desapilar hasta tener la profundidad igual al prefijo común
            while len(stack) > common:
                stack.pop()
            # Si faltan niveles intermedios, insertar nodos placeholder
            while len(stack) < level - 1:
                placeholder_code = new_code[:len(stack) + 1]
                placeholder = {"name": "", "children": [], "code": placeholder_code}
                if stack:
                    stack[-1]["children"].append(placeholder)
                else:
                    roots.append(placeholder)
                stack.append(placeholder)
            # Agregar el nuevo nodo como hijo del último nodo en el stack
            if stack:
                stack[-1]["children"].append(new_node)
            else:
                roots.append(new_node)
            stack.append(new_node)

    # Eliminar la clave interna "code" de cada nodo
    def remove_code_field(node):
        if "code" in node:
            del node["code"]
        for child in node.get("children", []):
            remove_code_field(child)

    for root in roots:
        remove_code_field(root)

    return roots


# Nuevos datos: cada elemento de la lista es una línea con código y descripción.
data_lines = [
    "0.0.0.0.0.0.0.0.0 Operador sufre atrapamiento en partes móviles de la sobadora",
    "1.0.0.0.0.0.0.0.0 Operador procede a limpiar los rodillos mientras la máquina está en funcionamiento",
    "1.1.0.0.0.0.0.0.0 Ausencia de un procedimiento de seguridad que obligue a detener la máquina antes de la limpieza",
    "1.1.1.0.0.0.0.0.0 Falta de protocolos y medidas preventivas establecidos en la operación de la máquina",
    "1.1.2.0.0.0.0.0.0 Falta de capacitación o concientización en seguridad para la realización de tareas de mantenimiento",
    "1.2.0.0.0.0.0.0.0 Decisión equivocada del operador al creer que limpiar con la máquina en funcionamiento era más fácil",
    "1.2.1.0.0.0.0.0.0 Falta de análisis adecuado de riesgos antes de iniciar la tarea de limpieza",
    "2.0.0.0.0.0.0.0.0 Operador se posiciona en área peligrosa, cerca de los rodillos en movimiento",
    "2.1.0.0.0.0.0.0.0 Diseño de la sobadora que permite el acceso a zonas de riesgo al carecer de sistema de bloqueo y protecciones",
    "2.1.1.0.0.0.0.0.0 Antigüedad del equipo y ausencia de actualizaciones en materia de seguridad",
    "2.1.2.0.0.0.0.0.0 Ubicación adosada a la pared que facilita el acceso a los rodillos en funcionamiento"
]

# Construir la estructura del árbol a partir de las líneas
roots = build_tree_from_lines_ordered(data_lines)

# Si hay más de un nodo raíz, agruparlos bajo un nodo raíz común
if len(roots) > 1:
    tree_data = [{"name": "Accidente", "children": roots}]
else:
    tree_data = roots

# Crear el gráfico de árbol con pyecharts en orientación horizontal ("LR")
tree_chart = Tree(init_opts=opts.InitOpts(width="1200px", height="800px"))
tree_chart.add(
    "",
    tree_data,
    orient="LR",
    label_opts=opts.LabelOpts(
        formatter="{a|{b}}",
        rich={"a": {"width": 150}},  # Ancho máximo de 150px para cada etiqueta
    ),
)
# Configurar para que se muestre completamente desplegado
tree_chart.set_series_opts(initial_tree_depth=-1)
tree_chart.set_global_opts(title_opts=opts.TitleOpts(title="Árbol de Causas - Expandido"))

# Renderizar el archivo HTML y abrirlo automáticamente en el navegador
output_file = "arbol_causas_smartart_horizontal.html"
tree_chart.render(output_file)
webbrowser.open("file://" + os.path.realpath(output_file))
