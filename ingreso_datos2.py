from email.policy import default
import streamlit as st
import pandas as pd
from pathlib import Path
import uuid
import re
from datetime import datetime


class DataModel:
    DATA_DIR = Path("data")
    DEFAULT_COLS = {}  # Definir en clases hijas

    def __init__(self):
        self.DATA_DIR.mkdir(exist_ok=True)
        self.df = pd.DataFrame()

    def load_data(self, filename, required_columns=None):
        try:
            filepath = self.DATA_DIR / filename
            df = pd.read_csv(filepath)
            # Agregar columnas faltantes
            if required_columns:
                for col in required_columns:
                    if col not in df.columns:
                        df[col] = None
            return df
        except FileNotFoundError:
            return self.initialize_csv_structure(filename, required_columns)

    def save_data(self, df, filename):
        """Guarda datos preservando el formato correcto"""
        filepath = self.DATA_DIR / filename
        # Crear directorio si no existe
        filepath.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(filepath, index=False)

    def initialize_csv_structure(self, filename, columns=None):
        """Crea un CSV con estructura inicial si no existe"""
        columns = columns or self.DEFAULT_COLS.get(filename, [])
        df = pd.DataFrame(columns=columns)
        self.save_data(df, filename)
        return df

    def generate_id(self):
        """Genera un ID único para registros"""
        return str(uuid.uuid4())[:8]

    def check_duplicates(self, df, field, value):
        """Verifica si ya existe un registro con el mismo valor"""
        return not df[df[field] == value].empty

    def validate_rut(self, rut):
        """Valida formato de RUT chileno"""
        pattern = r'^0*(\d{1,3}(\.?\d{3}){2}-[\dkK])$'
        return re.match(pattern, rut) is not None

    def basic_cleanup(self, df):
        """Limpieza básica de datos"""
        # Eliminar duplicados
        df = df.drop_duplicates()
        # Eliminar filas completamente vacías
        df = df.dropna(how='all')
        return df


class Empresa(DataModel):
    REQUIRED_COLS = ['rut', 'nombre', 'direccion', 'giro', 'fecha_registro']

    def __init__(self):
        super().__init__()
        self.df = self.load_data("empresas.csv", self.REQUIRED_COLS)
        self.df = self.basic_cleanup(self.df)

    # Añadir este método
    def existe(self, rut):
        """Verifica si una empresa existe por su RUT"""
        if self.df.empty:
            return False
        return rut in self.df['rut'].values

    def crear_nueva(self, rut, datos):  # <--- Mantener esta firma
        """Crea nueva empresa con validaciones"""
        if not self.validate_rut(rut):  # Usar el rut del parámetro
            raise ValueError("RUT inválido")

        if self.check_duplicates(self.df, 'rut', rut):
            raise ValueError("Empresa ya existe")

        new_row = {
            'rut': rut,  # Usar el rut del parámetro
            'nombre': datos.get('nombre', ''),
            'direccion': datos.get('direccion', ''),
            'giro': datos.get('giro', ''),
            'fecha_registro': pd.Timestamp.now().strftime('%Y-%m-%d')
        }

        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        self.save_data(self.df, "empresas.csv")
        return new_row

    def get_centros_trabajo(self, rut):
        centro_model = CentroTrabajo()
        centros = centro_model.df

        # Filtrar y asegurar columnas
        if not centros.empty and 'rut_empresa' in centros.columns:
            return centros[centros['rut_empresa'] == rut]
        return pd.DataFrame(columns=CentroTrabajo.REQUIRED_COLS)


class CentroTrabajo(DataModel):
    REQUIRED_COLS = [
        'cuv',
        'rut_empresa',
        'nombre_centro',
        'tipo_calle',
        'nombre_calle',
        'numero',
        'resto_direccion',
        'comuna'
    ]

    def __init__(self):
        super().__init__()
        self.df = self.load_data("centros_trabajo.csv", self.REQUIRED_COLS)

        # Asegurar columnas si el DataFrame está vacío
        if self.df.empty:
            self.df = pd.DataFrame(columns=self.REQUIRED_COLS)

    def crear_nuevo(self, rut_empresa, datos):
        new_id = str(uuid.uuid4())[:8]
        new_row = {
            'cuv': new_id,
            'rut_empresa': rut_empresa,
            **datos
        }

        # Asegurar todas las columnas
        for col in self.df.columns:
            if col not in new_row:
                new_row[col] = None

        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        self.save_data(self.df, "centros_trabajo.csv")
        return new_id


class Accidente(DataModel):
    def __init__(self):
        super().__init__()
        self.df = self.load_data("accidentes.csv")

        if not self.df.empty:
            # Convertir fecha usando formato específico
            self.df['fecha'] = pd.to_datetime(
                self.df['fecha'],
                format='%Y-%m-%d',  # Formato solo fecha
                errors='coerce'  # Manejar valores inválidos como NaT
            )

            # Convertir hora usando formato específico
            self.df['hora'] = pd.to_datetime(
                self.df['hora'],
                format='%H:%M',  # Formato solo hora
                errors='coerce'
            ).dt.time  # Extraer solo el componente de tiempo

            # Eliminar filas con fechas/horas inválidas
            self.df = self.df.dropna(subset=['fecha', 'hora'])

    def get_accidentes_centro(self, cuv):
        return self.df[self.df['cuv_centro'] == cuv]

    def actualizar(self, accidente_id, nuevos_datos):
        for col, valor in nuevos_datos.items():
            self.df.loc[self.df['id'] == accidente_id, col] = valor
        self.save_data(self.df, "accidentes.csv")


class Trabajador(DataModel):
    REQUIRED_COLS = [
        'id',
        'accidente_id',
        'ap_paterno',
        'ap_materno',
        'nombres',
        'origen_doc',
        'id_doc',
        'fecha_nacimiento',
        'sexo',
        'hora_ingreso',
        'hora_salida',
        'jornada',
        'jornada_otro'
    ]

    def __init__(self):
        super().__init__()
        self.df = self.load_data("trabajadores.csv", self.REQUIRED_COLS)

    def get_by_accidente(self, accidente_id):
        return self.df[self.df['accidente_id'] == accidente_id]

    def agregar(self, datos):
        """Agrega un nuevo trabajador con validación"""
        if self.check_duplicates(self.df, 'id_doc', datos['id_doc']):
            raise ValueError("Documento de identidad ya registrado")

        self.df = pd.concat([self.df, pd.DataFrame([datos])], ignore_index=True)
        self.save_data(self.df, "trabajadores.csv")


class Causa(DataModel):
    def __init__(self):
        super().__init__()
        self.df = self.load_data("causas.csv")  # Solo nombre de archivo

    def get_by_accidente(self, accidente_id):
        return self.df[self.df['accidente_id'] == accidente_id]

    def guardar_masivo(self, accidente_id, causas):
        # Convertir a DataFrame
        nuevas_causas = pd.DataFrame([{
            'accidente_id': accidente_id,
            'ubicacion': causa['ubicacion'],
            'codigo': causa['codigo'],
            'glosa': causa['glosa']
        } for causa in causas])

        # Combinar con existentes
        self.df = pd.concat([self.df, nuevas_causas], ignore_index=True)
        self.save_data(self.df, "causas.csv")  # Guardar en data/causas.csv





# Funciones de paginación
def pagina_inicio():
    st.header("Investigación de Accidentes Laborales")

    # Inicializar variables de sesión si no existen
    if 'rut_empresa' not in st.session_state:
        st.session_state.rut_empresa = None
    if 'cuv' not in st.session_state:
        st.session_state.cuv = None

    # Widget para entrada del RUT
    rut_input = st.text_input("Ingrese RUT de la empresa (formato: 81.537.600-5):", key="rut_input")

    # Botón para iniciar la búsqueda
    if st.button("Buscar Empresa"):
        if not rut_input:
            st.error("Por favor ingrese un RUT")
            return

        # Validación básica de formato RUT
        import re
        if not re.match(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', rut_input):
            st.error("Formato de RUT inválido. Use formato: 12.345.678-9")
            return

        empresa = Empresa()

        # Verificar si la empresa existe
        if not empresa.existe(rut_input):
            st.warning("Empresa no registrada")
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("Registrar Nueva Empresa"):
                    st.session_state.rut_temp = rut_input
                    st.session_state.pagina = "nueva_empresa"
                    st.rerun()
            with col2:
                if st.button("Reintentar con otro RUT"):
                    st.session_state.rut_empresa = None
                    st.rerun()
            return
        else:
            st.session_state.rut_empresa = rut_input
            st.success("Empresa encontrada en nuestros registros")

            # Mostrar datos de la empresa
            empresa_data = empresa.df[empresa.df['rut'] == rut_input].iloc[0]
            st.write("**Nombre Legal:**", empresa_data['nombre'])
            st.write("**Dirección Legal:**", empresa_data['direccion'])
            st.write("**Giro Comercial:**", empresa_data['giro'])
            st.write("**Fecha de Registro:**", empresa_data['fecha_registro'])

            # Cargar centros de trabajo
            centros = empresa.get_centros_trabajo(rut_input)

            if not centros.empty:
                st.subheader("Centros de Trabajo Registrados")

                selected_centro = st.selectbox(
                    "Seleccione un centro existente:",
                    centros['nombre_centro'],
                    key="select_centro"
                )

                with st.expander("Vista previa del centro seleccionado"):
                    centro_data = centros[centros['nombre_centro'] == selected_centro].iloc[0]
                    st.write(f"**Nombre:** {centro_data['nombre_centro']}")
                    st.write(f"**Dirección:** {centro_data['tipo_calle']} {centro_data['nombre_calle']} {centro_data['numero']}")
                    st.write(f"**Comuna:** {centro_data['comuna']}")

                col1, col2 = st.columns([1, 1])

                with col1:
                    if st.button("Usar Centro Seleccionado"):
                        cuv_seleccionado = centros[centros['nombre_centro'] == selected_centro]['cuv'].values[0]
                        st.session_state.cuv = cuv_seleccionado
                        st.session_state.pagina = "accidentes"
                        st.rerun()

                with col2:
                    if st.button("Crear Nuevo Centro"):
                        st.session_state.pagina = "nuevo_centro"
                        st.rerun()


            else:
                st.info("Esta empresa no tiene centros registrados")
                if st.button("Crear Primer Centro de Trabajo"):
                    st.session_state.pagina = "nuevo_centro"
                    st.rerun()


def pagina_nueva_empresa():
    st.title("Registro de Nueva Empresa")

    with st.form("nueva_empresa"):
        nombre = st.text_input("Nombre Legal de la Empresa")
        direccion = st.text_input("Dirección Legal")
        giro = st.text_input("Giro Comercial")

        if st.form_submit_button("Guardar Empresa"):
            empresa = Empresa()
            try:
                # Pasar el RUT como primer parámetro y los datos como dict
                empresa.crear_nueva(
                    st.session_state.rut_temp,  # Primer parámetro (rut)
                    {  # Segundo parámetro (datos)
                        'nombre': nombre,
                        'direccion': direccion,
                        'giro': giro
                    }
                )
                st.session_state.rut_empresa = st.session_state.rut_temp
                del st.session_state.rut_temp
                st.session_state.pagina = "inicio"
                st.rerun()

            except ValueError as e:
                st.error(str(e))


def pagina_nuevo_centro():
    st.title("Nuevo Centro de Trabajo")
    with st.form("nuevo_centro"):
        nombre = st.text_input("Nombre Centro")
        direccion = st.text_input("Dirección")
        comuna = st.text_input("Comuna")

        if st.form_submit_button("Guardar"):
            centro = CentroTrabajo()
            cuv = centro.crear_nuevo(st.session_state.rut_empresa, {
                'nombre_centro': nombre,
                'direccion': direccion,
                'comuna': comuna
            })
            st.session_state.cuv = cuv
            st.session_state.pagina = "accidentes"



def pagina_accidentes():
    st.title("Gestión de Accidentes")
    accidente_model = Accidente()
    accidentes = accidente_model.get_accidentes_centro(st.session_state.cuv)

    col1, col2 = st.columns([3, 1])
    with col1:
        if not accidentes.empty:
            # Crear lista de accidentes con ID y fecha
            opciones = [f"{row['id']} - {row['fecha'].strftime('%Y-%m-%d')}"
                        for _, row in accidentes.iterrows()]

            selected = st.selectbox("Accidentes existentes:", opciones)
            st.session_state.accidente_id = selected.split(" - ")[0]  # Extraer el ID
    with col2:
        if st.button("Nuevo Accidente"):
            st.session_state.pagina = "nuevo_accidente"

    if st.button("Editar Accidentes Seleccionado"):
        st.session_state.pagina = "editar_accidente"


def pagina_editar_accidente():
    st.title("Editar Accidente")

    if 'accidente_id' not in st.session_state or not st.session_state.accidente_id:
        st.error("No se ha seleccionado ningún accidente")
        st.session_state.pagina = "accidentes"
        st.rerun()

    accidente_model = Accidente()
    accidentes = accidente_model.get_accidentes_centro(st.session_state.cuv)

    # Filtrar por ID y verificar existencia
    accidente_sel = accidentes[accidentes['id'] == st.session_state.accidente_id]

    if accidente_sel.empty:
        st.error("Accidente no encontrado")
        st.session_state.pagina = "accidentes"
        st.rerun()
    else:
        accidente_sel = accidente_sel.iloc[0]

    with st.form("editar_accidente_form"):
        # Convertir fecha y hora de manera segura
        try:
            fecha_val = pd.to_datetime(accidente_sel['fecha']).date()
        except:
            fecha_val = pd.to_datetime('today').date()

        try:
            hora_val = pd.to_datetime(accidente_sel['hora'], format='%H:%M').time()
        except:
            hora_val = datetime.now().time()

        fecha = st.date_input("Fecha del accidente", value=fecha_val)
        hora = st.time_input("Hora del accidente", value=hora_val)
        direccion = st.text_input("Dirección del accidente", value=accidente_sel.get('direccion', ''))
        descripcion = st.text_area("Descripción inicial", value=accidente_sel.get('descripcion', ''))

        submitted = st.form_submit_button("Guardar Cambios")

        if submitted:
            # Actualizar los datos
            accidente_model.df.loc[accidente_model.df['id'] == st.session_state.accidente_id, 'fecha'] = fecha.strftime(
                "%Y-%m-%d")
            accidente_model.df.loc[accidente_model.df['id'] == st.session_state.accidente_id, 'hora'] = hora.strftime(
                "%H:%M")
            accidente_model.df.loc[accidente_model.df['id'] == st.session_state.accidente_id, 'direccion'] = direccion
            accidente_model.df.loc[
                accidente_model.df['id'] == st.session_state.accidente_id, 'descripcion'] = descripcion

            # Guardar cambios
            accidente_model.save_data(accidente_model.df, "accidentes.csv")
            st.success("¡Cambios guardados exitosamente!")
            st.session_state.pagina = "accidentes"

    if st.button("Volver sin guardar"):
        st.session_state.pagina = "accidentes"


def pagina_nuevo_accidente():
    st.title("Nuevo Accidente")
    with st.form("nuevo_accidente"):
        fecha = st.date_input("Fecha del accidente")
        hora = st.time_input("Hora del accidente")
        direccion = st.text_input("Dirección del accidente")
        descripcion = st.text_area("Descripción inicial")

        if st.form_submit_button("Guardar Accidente"):
            nuevo_id = str(uuid.uuid4())[:8]
            nuevo_accidente = {
                'id': nuevo_id,
                'cuv_centro': st.session_state.cuv,
                'fecha': fecha.strftime("%Y-%m-%d"),  # Formato ISO
                'hora': hora.strftime("%H:%M"),  # Formato 24h
                'direccion': direccion,
                'descripcion': descripcion
            }
            accidente = Accidente()
            accidente.df = pd.concat([accidente.df, pd.DataFrame([nuevo_accidente])], ignore_index=True)
            accidente.save_data(accidente.df, "accidentes.csv")
            st.session_state.accidente_id = nuevo_id
            st.session_state.pagina = "trabajadores"


def pagina_trabajadores():
    st.title("Gestión de Trabajadores Involucrados")

    trabajador_model = Trabajador()
    trabajadores_df = trabajador_model.get_by_accidente(st.session_state.accidente_id)

    # Crear lista de nombres segura
    lista_trabajadores = ["Nuevo Trabajador"]  # Siempre incluir la opción de nuevo
    if not trabajadores_df.empty and 'nombres' in trabajadores_df.columns:
        lista_trabajadores = trabajadores_df['nombres'].tolist() + lista_trabajadores

    col1, col2 = st.columns([4, 1])
    with col1:
        selected = st.selectbox("Trabajadores registrados:", lista_trabajadores)
    with col2:
        if st.button("Ir a Investigación"):
            st.session_state.pagina = "investigacion"

    if selected == "Nuevo Trabajador":
        with st.form("nuevo_trabajador"):
            st.subheader("Datos Personales")
            col1, col2 = st.columns(2)
            ap_paterno = col1.text_input("Apellido Paterno*")
            ap_materno = col2.text_input("Apellido Materno")
            nombres = st.text_input("Nombres*")

            st.subheader("Documento de Identidad")
            col1, col2 = st.columns(2)
            origen_doc = col1.selectbox("Origen Documento*",
                                        options=[1, 2],
                                        format_func=lambda x: "Nacional" if x == 1 else "Extranjero")
            id_doc = col2.text_input("Número Documento*")

            st.subheader("Datos Adicionales")
            col1, col2, col3 = st.columns(3)
            fecha_nacimiento = col1.date_input("Fecha de Nacimiento*")
            sexo = col2.radio("Sexo*", options=["Masculino", "Femenino", "Otro"])

            st.subheader("Datos Relacionados al Accidente")
            col1, col2 = st.columns(2)
            hora_ingreso = col1.time_input("Hora de Ingreso*")
            hora_salida = col2.time_input("Hora de Salida*")
            jornada = st.selectbox("Jornada*", ["Diurna", "Nocturna", "Mixta", "Otro"])

            if jornada == "Otro":
                jornada_otro = st.text_input("Especificar jornada")
            else:
                jornada_otro = None

            if st.form_submit_button("Guardar Trabajador"):
                if not all([ap_paterno, nombres, id_doc]):
                    st.error("Campos obligatorios (*) deben ser completados")
                else:
                    nuevo_id = trabajador_model.generate_id()
                    nuevo_trabajador = {
                        'id': nuevo_id,
                        'accidente_id': st.session_state.accidente_id,
                        'ap_paterno': ap_paterno,
                        'ap_materno': ap_materno or None,
                        'nombres': nombres,
                        'origen_doc': origen_doc,
                        'id_doc': id_doc,
                        'fecha_nacimiento': fecha_nacimiento.strftime("%Y-%m-%d"),
                        'sexo': sexo,
                        'hora_ingreso': hora_ingreso.strftime("%H:%M"),
                        'hora_salida': hora_salida.strftime("%H:%M"),
                        'jornada': jornada,
                        'jornada_otro': jornada_otro
                    }
                    try:
                        trabajador_model.agregar(nuevo_trabajador)
                        st.success("Trabajador registrado exitosamente!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {str(e)}")

    else:
        # Lógica para edición de trabajador existente
        pass  # Implementar similar al formulario nuevo con valores iniciales


# Página de investigación
def pagina_investigacion():
    st.title("Datos de la Investigación")

    with st.form("datos_investigacion"):
        fecha_inicio = st.date_input("Fecha inicio investigación")
        fecha_termino = st.date_input("Fecha término investigación")

        st.subheader("Datos del Investigador")
        inv_paterno = st.text_input("Apellido Paterno Investigador")
        inv_materno = st.text_input("Apellido Materno Investigador")
        inv_nombres = st.text_input("Nombres Investigador")

        if st.form_submit_button("Guardar Investigación"):
            st.session_state.pagina = "arbol_causas"


# Página del árbol de causas
def pagina_arbol_causas():
    st.title("Árbol de Causas")

    if 'causas' not in st.session_state:
        causas = Causa().get_by_accidente(st.session_state.accidente_id)
        st.session_state.causas = causas.to_dict('records')

    # Grilla editable
    for idx, causa in enumerate(st.session_state.causas):
        with st.expander(f"Causa {idx + 1}"):
            cols = st.columns([1, 2, 3, 1])
            with cols[0]:
                ubicacion = st.text_input(f"Ubicación {idx}", value=causa['ubicacion'])
            with cols[1]:
                codigo = st.text_input(f"Código {idx}", value=causa['codigo'])
            with cols[2]:
                glosa = st.text_area(f"Glosa {idx}", value=causa['glosa'])
            with cols[3]:
                if st.button(f"❌ Eliminar {idx}"):
                    del st.session_state.causas[idx]
                    st.rerun()

    if st.button("➕ Agregar Nueva Causa"):
        st.session_state.causas.append({
            'ubicacion': '',
            'codigo': '',
            'glosa': ''
        })
        st.rerun()

    if st.button("Guardar Todas las Causas"):
        Causa().guardar_masivo(st.session_state.accidente_id, st.session_state.causas)
        st.session_state.pagina = "documentos"


# Página de documentos
def pagina_documentos():
    st.title("Documentos Anexos")

    docs_requeridos = [
        "Matriz de riesgos",
        "Evaluaciones de riesgos",
        "Plan de prevención",
        # ... resto de documentos
    ]

    for doc in docs_requeridos:
        st.subheader(doc)
        st.file_uploader(f"Subir {doc}", key=f"doc_{doc}")

    st.subheader("Otros Documentos")
    otros_docs = st.file_uploader("Subir documentos adicionales",
                                  accept_multiple_files=True,
                                  key="otros_docs")

    if st.button("Finalizar Reporte"):
        # Lógica para guardar documentos
        st.success("Reporte completado exitosamente!")
        st.session_state.pagina = "inicio"


def main():
    st.set_page_config(layout="wide")
    paginas = {
        "inicio": pagina_inicio,
        "nueva_empresa": pagina_nueva_empresa,
        "nuevo_centro": pagina_nuevo_centro,
        "accidentes": pagina_accidentes,
        "nuevo_accidente": pagina_nuevo_accidente,
        "editar_accidente": pagina_editar_accidente,
        "trabajadores": pagina_trabajadores,
        "investigacion": pagina_investigacion,
        "arbol_causas": pagina_arbol_causas,
        "documentos": pagina_documentos
    }

    if "pagina" not in st.session_state:
        st.session_state.pagina = "inicio"

    paginas[st.session_state.pagina]()


if __name__ == "__main__":
    main()