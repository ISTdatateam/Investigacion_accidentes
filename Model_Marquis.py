import streamlit as st


def inicializar_estado():
    estados_base = {
        'nivel_actual': 1,
        'rama_actual': [],
        'respuestas': {},
        'historial': [],
        'causas_pendientes': [],
        'max_nivel': 5
    }
    for key, val in estados_base.items():
        if key not in st.session_state:
            st.session_state[key] = val


def generar_clave_actual():
    return '.'.join(['2'] + st.session_state.rama_actual) if st.session_state.rama_actual else '1'


def mostrar_arbol_lateral():
    st.sidebar.header("🌳 Estructura de Causas")

    def construir_nodo(clave, nivel=1):
        if clave not in st.session_state.respuestas:
            return ""

        icono = '🩹' if nivel == 1 else '📌' if nivel == 2 else '🔍'
        texto = f"{icono} {st.session_state.respuestas[clave]}\n"
        subclaves = sorted(
            [k for k in st.session_state.respuestas if k.startswith(f'{clave}.')],
            key=lambda x: [int(n) for n in x.split('.')[1:]]
        )

        for sk in subclaves:
            texto += " " * nivel + construir_nodo(sk, nivel + 1)
        return texto

    if '1' in st.session_state.respuestas:
        st.sidebar.markdown("### Lesión Principal")
        st.sidebar.markdown(construir_nodo('1'))

    if st.session_state.nivel_actual > 1:
        st.sidebar.markdown("### Línea de Investigación")
        st.sidebar.markdown(construir_nodo('.'.join(['2'] + st.session_state.rama_actual[:-1])))


def manejar_agregar_factor(respuesta):
    clave_actual = generar_clave_actual()
    contador = sum(1 for k in st.session_state.respuestas if k.startswith(f'{clave_actual}.')) + 1
    nueva_clave = f'{clave_actual}.{contador}'

    st.session_state.respuestas[nueva_clave] = respuesta
    st.session_state.causas_pendientes.append(nueva_clave)
    st.session_state.historial.append({
        'nivel': st.session_state.nivel_actual,
        'rama': st.session_state.rama_actual.copy(),
        'pendientes': st.session_state.causas_pendientes.copy()
    })


def manejar_completar_nivel():
    if st.session_state.nivel_actual < st.session_state.max_nivel:
        # Avanzar al siguiente nivel para cada causa pendiente
        st.session_state.nivel_actual += 1
        st.session_state.rama_actual = [str(len(st.session_state.causas_pendientes))]
        st.session_state.causas_pendientes = []
    else:
        st.session_state.nivel_actual = 'final'


def mostrar_formulario():
    nivel = st.session_state.nivel_actual
    clave_actual = generar_clave_actual()

    with st.form(key=f"form_{nivel}_{'_'.join(st.session_state.rama_actual)}"):
        if nivel == 1:
            pregunta = "🚑 ¿Cuál fue la lesión principal del trabajador?"
            ayuda = "Describa la lesión o condición médica resultante"
        else:
            padre = '.'.join(['2'] + st.session_state.rama_actual[:-1]) if nivel > 2 else '2'
            contexto = st.session_state.respuestas.get(padre, "el evento anterior")
            pregunta = f"{'🔹' * (nivel - 1)} Nivel {nivel - 1}.{len(st.session_state.rama_actual)}: ¿Qué fue necesario para que ocurra {contexto}?"
            ayuda = "Identifique un factor específico (material, humano u organizacional)"

        respuesta = st.text_input(pregunta, help=ayuda)

        cols = st.columns([3, 1])
        with cols[0]:
            if st.form_submit_button("➕ Agregar Factor" if nivel > 1 else "🚀 Continuar") and respuesta:
                if nivel == 1:
                    st.session_state.respuestas['1'] = respuesta
                    st.session_state.nivel_actual = 2
                else:
                    manejar_agregar_factor(respuesta)
                st.rerun()

        with cols[1]:
            if nivel > 1 and st.form_submit_button("✅ Completar Nivel"):
                manejar_completar_nivel()
                st.rerun()


def mostrar_resultados():
    st.header("📊 Análisis Final de Causas")

    def generar_reporte(clave, nivel=1):
        if clave not in st.session_state.respuestas:
            return ""

        margen = " " * (nivel - 1)
        texto = f"{margen}• {st.session_state.respuestas[clave]}\n"
        subclaves = sorted(
            [k for k in st.session_state.respuestas if k.startswith(f'{clave}.')],
            key=lambda x: [int(n) for n in x.split('.')[1:]]
        )

        for sk in subclaves:
            texto += generar_reporte(sk, nivel + 1)
        return texto

    st.markdown(generar_reporte('1'))

    if st.button("🔄 Nueva Investigación"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def main():
    inicializar_estado()
    mostrar_arbol_lateral()

    if st.session_state.nivel_actual == 'final':
        mostrar_resultados()
    else:
        st.progress((st.session_state.nivel_actual - 1) / st.session_state.max_nivel)
        mostrar_formulario()

        if st.session_state.historial:
            if st.button("↩️ Retroceder"):
                estado_previo = st.session_state.historial.pop()
                st.session_state.nivel_actual = estado_previo['nivel']
                st.session_state.rama_actual = estado_previo['rama']
                st.session_state.causas_pendientes = estado_previo['pendientes']
                st.rerun()


if __name__ == "__main__":
    main()