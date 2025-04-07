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

        # Crear estructura inicial si no existe
        if self.df.empty:
            self.df = pd.DataFrame(columns=[
                'cuv',
                'rut_empresa',
                'nombre_centro',
                'tipo_calle',
                'nombre_calle',
                'numero',
                'resto_direccion',
                'comuna'
            ])

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
    REQUIRED_COLS = [
        'id',
        'fecha',
        'hora',
        'cuv_centro',
        'tipo_accidente',  # Si se usa
        'gravedad',       # Si se usa
        'direccion',      # <--- Añadir
        'descripcion'     # <--- Añadir
    ]

    def __init__(self):
        super().__init__()
        # Forzar recarga completa de datos
        self.df = self.load_data("accidentes.csv", self.REQUIRED_COLS)
        self._procesar_fechas_horas()

        # Asegurar tipos de datos
        if not self.df.empty:
            self.df['cuv_centro'] = self.df['cuv_centro'].astype(str)


    def _procesar_fechas_horas(self):
        """Conversión y validación de fechas/horas"""
        self.df['fecha'] = pd.to_datetime(
            self.df['fecha'],
            format='%Y-%m-%d',
            errors='coerce'
        )

        self.df['hora'] = pd.to_datetime(
            self.df['hora'].astype(str),
            format='%H:%M',
            errors='coerce'
        ).dt.time

        # Eliminar registros inválidos
        self.df = self.df.dropna(subset=['fecha', 'hora'])

    def get_accidentes_centro(self, cuv):
        return self.df[self.df['cuv_centro'].astype(str) == str(cuv)].copy()

    def crear_nuevo(self, datos):
        # Cargar datos existentes ANTES de agregar nuevos
        self.df = self.load_data("accidentes.csv", self.REQUIRED_COLS)  # <--- Faltaba esto

        # Validar campos obligatorios
        for campo in ['fecha', 'hora', 'cuv_centro', 'direccion']:
            if campo not in datos:
                raise ValueError(f"Falta campo obligatorio: {campo}")

        # Generar ID único
        new_id = str(uuid.uuid4())[:8]
        new_row = {
            'id': new_id,
            **datos
        }

        # Validar formato fecha/hora
        try:
            datetime.strptime(new_row['fecha'], '%Y-%m-%d')
            datetime.strptime(new_row['hora'], '%H:%M')
        except ValueError as e:
            raise ValueError(f"Formato inválido: {e}")

        # Asegurar todas las columnas
        for col in self.REQUIRED_COLS:
            new_row.setdefault(col, None)

        # Añadir al DataFrame existente
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)  # <--- Modificado
        self.save_data(self.df, "accidentes.csv")
        return new_id

    def actualizar(self, accidente_id, nuevos_datos):
        # Verificar existencia
        if accidente_id not in self.df['id'].values:
            raise KeyError(f"Accidente {accidente_id} no existe")

        # Validar columnas
        for col in nuevos_datos:
            if col not in self.df.columns:
                raise KeyError(f"Columna inválida: {col}")

        # Actualizar datos
        mask = self.df['id'] == accidente_id
        self.df.loc[mask, list(nuevos_datos.keys())] = list(nuevos_datos.values())
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
        df = self.load_data("trabajadores.csv")
        return df[df['accidente_id'] == accidente_id]

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


def pagina_empresa():
    st.header("Gestión de Empresa")

    # Inicializar estado si no existe
    if 'rut_empresa' not in st.session_state:
        st.session_state.rut_empresa = None
        st.session_state.rut_temp = None

    # Sección de búsqueda
    rut_input = st.text_input("Ingrese RUT de la empresa (formato: 12.345.678-9):", key="rut_input")

    # Botón de búsqueda principal
    if st.button("Buscar empresa"):
        if not re.match(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', rut_input):
            st.error("Formato de RUT inválido. Use formato: 12.345.678-9")
        else:
            empresa = Empresa()
            if empresa.existe(rut_input):
                st.session_state.rut_empresa = rut_input
                st.success("Empresa encontrada")
            else:
                st.session_state.rut_empresa = None
                st.session_state.rut_temp=rut_input
                st.warning("Empresa no registrada")

    # Sección para empresa existente
    if st.session_state.rut_empresa:
        empresa = Empresa()
        empresa_data = empresa.df[empresa.df['rut'] == st.session_state.rut_empresa]

        if not empresa_data.empty:
            empresa_data = empresa_data.iloc[0]

            with st.expander("Datos de la empresa", expanded=True):
                st.write(f"**Nombre Legal:** {empresa_data['nombre']}")
                st.write(f"**Dirección Legal:** {empresa_data['direccion']}")
                st.write(f"**Giro Comercial:** {empresa_data['giro']}")
                st.write(f"**Fecha de Registro:** {empresa_data['fecha_registro']}")

                # Botones de acción en columnas
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Editar datos de la empresa"):
                        st.session_state.pagina = "editar_empresa"
                        st.rerun()

            if st.button("Ir a centros de trabajo"):
                st.session_state.pagina = "centros_trabajo"
                st.rerun()

    if not st.session_state.rut_empresa and st.session_state.rut_temp:
        if st.button("Registrar nueva empresa con este RUT"):
            st.session_state.pagina = "nueva_empresa"
            st.rerun()


def pagina_nueva_empresa():
    st.header("Registro de Nueva Empresa")

    with st.form("nueva_empresa"):
        st.write(f"RUT: {st.session_state.rut_temp}")
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

    if st.button("Cancelar"):
        st.session_state.pagina = "inicio"



def pagina_editar_empresa():
    st.header("Editar Datos de Empresa")

    if 'rut_empresa' not in st.session_state or not st.session_state.rut_empresa:
        st.error("No hay empresa seleccionada")
        st.session_state.pagina = "inicio"
        st.rerun()

    empresa = Empresa()
    empresa_data = empresa.df[empresa.df['rut'] == st.session_state.rut_empresa].iloc[0]

    with st.form("editar_empresa_form"):
        nombre = st.text_input("Nombre Legal", value=empresa_data['nombre'])
        direccion = st.text_input("Dirección Legal", value=empresa_data['direccion'])
        giro = st.text_input("Giro Comercial", value=empresa_data['giro'])

        if st.form_submit_button("Guardar cambios"):
            empresa.df.loc[empresa.df['rut'] == st.session_state.rut_empresa, 'nombre'] = nombre
            empresa.df.loc[empresa.df['rut'] == st.session_state.rut_empresa, 'direccion'] = direccion
            empresa.df.loc[empresa.df['rut'] == st.session_state.rut_empresa, 'giro'] = giro
            empresa.save_data(empresa.df, "empresas.csv")
            st.success("Datos actualizados correctamente")
            st.session_state.pagina = "inicio"
            st.rerun()

    if st.button("Cancelar y volver"):
        st.session_state.pagina = "inicio"
        st.rerun()

def pagina_centros_trabajo():
    st.header("Gestión de Centros de Trabajo")

    if 'rut_empresa' not in st.session_state or not st.session_state.rut_empresa:
        st.error("Primero debe seleccionar una empresa")
        st.session_state.pagina = "inicio"
        st.rerun()

    empresa = Empresa()
    empresa_data = empresa.df[empresa.df['rut'] == st.session_state.rut_empresa]
    centros = empresa.get_centros_trabajo(st.session_state.rut_empresa)

    if not empresa_data.empty:
        empresa_data = empresa_data.iloc[0]

        with st.expander("Datos de la empresa", expanded=True):
            st.write(f"**RUT:** {empresa_data['rut']}")
            st.write(f"**Nombre Legal:** {empresa_data['nombre']}")
            st.write(f"**Dirección Legal:** {empresa_data['direccion']}")
            st.write(f"**Giro Comercial:** {empresa_data['giro']}")
            st.write(f"**Fecha de Registro:** {empresa_data['fecha_registro']}")


    if not centros.empty:
        selected_centro = st.selectbox(
            "Centros existentes:",
            centros['nombre_centro'],
            key="select_centro"
        )

        with st.expander("Vista previa del centro"):
            centro_data = centros[centros['nombre_centro'] == selected_centro].iloc[0]
            st.write(f"**Nombre:** {centro_data['nombre_centro']}")
            st.write(
                f"**Dirección:** {centro_data['tipo_calle']} {centro_data['nombre_calle']} {centro_data['numero']}")
            st.write(f"**Comuna:** {centro_data['comuna']}")
            if st.button("Editar este centro"):
                st.session_state.pagina = "editar_centro"
                st.rerun()

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if centros.empty:
            st.info("No hay centros registrados")
        else:
            if st.button("Usar Centro Seleccionado"):
                st.session_state.cuv = centros[centros['nombre_centro'] == selected_centro]['cuv'].values[0]
                st.session_state.pagina = "accidentes"
                st.rerun()
    with col2:
        if st.button("Crear Nuevo Centro"):
            st.session_state.pagina = "nuevo_centro"
            st.rerun()
    with col3:
        if st.button("Volver a empresa"):
            st.session_state.pagina = "inicio"
            st.rerun()


def pagina_nuevo_centro():
    st.header("Nuevo Centro de Trabajo")

    empresa = Empresa()
    empresa_data = empresa.df[empresa.df['rut'] == st.session_state.rut_empresa]

    if not empresa_data.empty:
        empresa_data = empresa_data.iloc[0]
        with st.expander("Datos de la empresa", expanded=False):
            st.write(f"**RUT:** {empresa_data['rut']}")
            st.write(f"**Nombre Legal:** {empresa_data['nombre']}")
            st.write(f"**Dirección Legal:** {empresa_data['direccion']}")
            st.write(f"**Giro Comercial:** {empresa_data['giro']}")
            st.write(f"**Fecha de Registro:** {empresa_data['fecha_registro']}")

    with st.form("nuevo_centro"):
        nombre = st.text_input("Nombre del Centro*")

        # Sección de dirección desglosada
        st.write("Dirección del Centro")
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            tipo_calle = st.selectbox(
                "Tipo de calle*",
                options=["Calle", "Avenida", "Pasaje", "Camino", "Ruta", "Otro"],
                index=0
            )
        with col2:
            nombre_calle = st.text_input("Nombre de la calle*")
        with col3:
            numero = st.text_input("Número*", help="Ej: 123, S/N, 456-B")

        resto_direccion = st.text_input("Resto de dirección",
                                        help="Ej: Piso 5, Oficina 203, Sector Norte")

        comuna = st.text_input("Comuna*")

        if st.form_submit_button("Guardar Centro"):
            # Validación básica
            if not all([nombre, nombre_calle, numero, comuna]):
                st.error("Por favor complete los campos obligatorios (*)")
            else:
                try:
                    centro = CentroTrabajo()
                    cuv = centro.crear_nuevo(st.session_state.rut_empresa, {
                        'nombre_centro': nombre,
                        'tipo_calle': tipo_calle,
                        'nombre_calle': nombre_calle,
                        'numero': numero,
                        'resto_direccion': resto_direccion if resto_direccion else None,
                        'comuna': comuna
                    })
                    st.session_state.cuv = cuv
                    st.session_state.pagina = "accidentes"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al crear centro: {str(e)}")

    if st.button("Cancelar"):
        st.session_state.pagina = "centros_trabajo"
        st.rerun()


def pagina_editar_centro():
    st.header("Editar Centro de Trabajo")

    # Verificar empresa seleccionada
    if 'rut_empresa' not in st.session_state or not st.session_state.rut_empresa:
        st.error("Primero debe seleccionar una empresa")
        st.session_state.pagina = "inicio"
        st.rerun()

    # Cargar datos
    empresa = Empresa()
    centro_model = CentroTrabajo()
    centros = empresa.get_centros_trabajo(st.session_state.rut_empresa)

    # Mostrar datos de la empresa
    empresa_data = empresa.df[empresa.df['rut'] == st.session_state.rut_empresa].iloc[0]
    with st.expander("Datos de la empresa", expanded=True):
        st.write(f"**RUT:** {empresa_data['rut']}")
        st.write(f"**Nombre Legal:** {empresa_data['nombre']}")
        st.write(f"**Dirección Legal:** {empresa_data['direccion']}")
        st.write(f"**Giro Comercial:** {empresa_data['giro']}")

    if not centros.empty:
        # Selección de centro
        selected_centro = st.selectbox(
            "Seleccione centro a editar:",
            centros['nombre_centro'],
            key="select_centro_editar"
        )

        # Obtener datos del centro seleccionado
        centro_data = centros[centros['nombre_centro'] == selected_centro].iloc[0]

        with st.form("editar_centro_form"):
            st.subheader("Editar Datos del Centro")

            # Campos editables
            nuevo_nombre = st.text_input("Nombre del Centro*", value=centro_data['nombre_centro'])

            st.subheader("Dirección")
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                # Tipo de calle con selección predefinida
                current_tipo = centro_data['tipo_calle']
                options_tipo = ["Calle", "Avenida", "Pasaje", "Camino", "Ruta", "Otro"]
                default_index = options_tipo.index(current_tipo) if current_tipo in options_tipo else 0
                tipo_calle = st.selectbox(
                    "Tipo de calle*",
                    options=options_tipo,
                    index=default_index
                )
            with col2:
                nombre_calle = st.text_input("Nombre de la calle*", value=centro_data['nombre_calle'])
            with col3:
                numero = st.text_input("Número*", value=centro_data['numero'], help="Ej: 123, S/N, 456-B")

            resto_direccion = st.text_input(
                "Resto de dirección",
                value=centro_data.get('resto_direccion', ''),
                help="Ej: Piso 5, Oficina 203, Sector Norte"
            )

            comuna = st.text_input("Comuna*", value=centro_data['comuna'])

            if st.form_submit_button("Guardar Cambios"):
                # Validar campos obligatorios
                if not all([nuevo_nombre, nombre_calle, numero, comuna]):
                    st.error("Por favor complete los campos obligatorios (*)")
                else:
                    # Actualizar datos
                    centro_model.df.loc[centro_model.df['cuv'] == centro_data['cuv'], [
                        'nombre_centro',
                        'tipo_calle',
                        'nombre_calle',
                        'numero',
                        'resto_direccion',
                        'comuna'
                    ]] = [nuevo_nombre, tipo_calle, nombre_calle, numero, resto_direccion, comuna]

                    # Guardar cambios
                    centro_model.save_data(centro_model.df, "centros_trabajo.csv")
                    st.success("¡Centro actualizado correctamente!")
                    st.session_state.pagina = "centros_trabajo"
                    st.rerun()

        if st.button("Cancelar y volver"):
            st.session_state.pagina = "centros_trabajo"
            st.rerun()

    else:
        st.warning("No hay centros registrados para esta empresa")
        if st.button("Crear nuevo centro"):
            st.session_state.pagina = "nuevo_centro"
            st.rerun()




def pagina_accidentes():
    st.header("Gestión de Accidentes")
    accidente_model = Accidente()
    accidentes = accidente_model.get_accidentes_centro(st.session_state.cuv)

    # Sección Empresa
    empresa = Empresa()
    empresa_data = empresa.df[empresa.df['rut'] == st.session_state.rut_empresa]

    # Sección Centro
    centro_model = CentroTrabajo()  # Crear instancia de CentroTrabajo
    centros = centro_model.df  # Obtener el DataFrame de centros

    if not empresa_data.empty:
        empresa_data = empresa_data.iloc[0]
        with st.expander("Datos de la empresa", expanded=False):
            st.write(f"**Nombre Legal:** {empresa_data['nombre']}")
            st.write(f"**Dirección Legal:** {empresa_data['direccion']}")
            st.write(f"**Giro Comercial:** {empresa_data['giro']}")
            st.write(f"**Fecha de Registro:** {empresa_data['fecha_registro']}")

    # Sección Centro (corregido)
    centro_data = centros[centros['cuv'] == st.session_state.cuv]
    if not centro_data.empty:
        centro_data = centro_data.iloc[0]  # Tomar el primer registro
        with st.expander("Datos del centro", expanded=False):
            st.write(f"**Nombre:** {centro_data['nombre_centro']}")
            st.write(
                f"**Dirección:** {centro_data['tipo_calle']} {centro_data['nombre_calle']} {centro_data['numero']}")
            st.write(f"**Comuna:** {centro_data['comuna']}")


    if not accidentes.empty:
        accidentes = accidentes.sort_values('fecha', ascending=False)
        opciones = [
            f"{row['id']} - {row['fecha'].strftime('%d/%m/%Y')} {row['hora']}"
            for _, row in accidentes.iterrows()
        ]

        selected = st.selectbox("Accidentes existentes:", opciones)
        st.session_state.accidente_id = selected.split(" - ")[0]

        # Obtener datos del accidente seleccionado
        accidente_sel = accidentes[accidentes['id'] == st.session_state.accidente_id].iloc[0]

        # Previsualización del accidente
        with st.expander("Previsualización del Accidente", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Fecha:** {accidente_sel['fecha'].strftime('%d/%m/%Y')}")
            with col2:
                st.write(f"**Hora:** {accidente_sel['hora'].strftime('%H:%M')}")
            st.write(f"**Dirección:** {accidente_sel['direccion']}")
            st.write(f"**Descripción inicial:** {accidente_sel['descripcion']}")

            if st.button("Editar Accidentes Seleccionado"):
                st.session_state.pagina = "editar_accidente"

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("Volver"):
            st.session_state.pagina = "centros_trabajo"
            st.rerun()

    with col2:
        if not accidentes.empty:
            if st.button("Asociar trabajadores al accidente"):
                st.session_state.pagina = "trabajadores"
                st.rerun()

    with col3:
        if st.button("Nuevo Accidente"):
            st.session_state.pagina = "nuevo_accidente"
            st.rerun()


def pagina_editar_accidente():
    st.header("Editar Accidente")

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

    if st.button("Volver"):
        st.session_state.pagina = "accidentes"


# Página para crear/editar accidentes
def pagina_nuevo_accidente():
    st.header("Nuevo Accidente")

    # Sección Empresa
    empresa = Empresa()
    empresa_data = empresa.df[empresa.df['rut'] == st.session_state.rut_empresa]

    # Sección Centro
    centro_model = CentroTrabajo()  # Crear instancia de CentroTrabajo
    centros = centro_model.df  # Obtener el DataFrame de centros

    if not empresa_data.empty:
        empresa_data = empresa_data.iloc[0]
        with st.expander("Datos de la empresa", expanded=False):
            st.write(f"**Nombre Legal:** {empresa_data['nombre']}")
            st.write(f"**Dirección Legal:** {empresa_data['direccion']}")
            st.write(f"**Giro Comercial:** {empresa_data['giro']}")
            st.write(f"**Fecha de Registro:** {empresa_data['fecha_registro']}")

    # Sección Centro (corregido)
    centro_data = centros[centros['cuv'] == st.session_state.cuv]
    if not centro_data.empty:
        centro_data = centro_data.iloc[0]  # Tomar el primer registro
        with st.expander("Datos del centro", expanded=False):
            st.write(f"**Nombre:** {centro_data['nombre_centro']}")
            st.write(
                f"**Dirección:** {centro_data['tipo_calle']} {centro_data['nombre_calle']} {centro_data['numero']}")
            st.write(f"**Comuna:** {centro_data['comuna']}")



    with st.form("nuevo_accidente"):
        fecha = st.date_input("Fecha del accidente")
        hora = st.time_input("Hora del accidente")
        direccion = st.text_input("Dirección del accidente")
        descripcion = st.text_area("Descripción inicial")

        if st.form_submit_button("Guardar Accidente"):
            accidente = Accidente()  # Cargar instancia FRESCA con todos los datos
            nuevo_accidente = {
                'cuv_centro': st.session_state.cuv,
                'fecha': fecha.strftime("%Y-%m-%d"),
                'hora': hora.strftime("%H:%M"),
                'direccion': direccion,
                'descripcion': descripcion,
                'tipo_accidente': 'Por definir',  # Valores por defecto
                'gravedad': 'Leve'
            }
            try:
                nuevo_id = accidente.crear_nuevo(nuevo_accidente)  # Usar el método de la clase
                st.session_state.accidente_id = nuevo_id
                st.success("Accidente registrado exitosamente!")
                st.session_state.pagina = "accidentes"
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")


# Página de gestión de trabajadores
def pagina_trabajadores():
    st.header("Gestión de Trabajadores Involucrados")

    trabajador_model = Trabajador()
    trabajadores_df = trabajador_model.get_by_accidente(st.session_state.accidente_id)

    # Crear lista de nombres segura
    lista_trabajadores = ["Nuevo Trabajador"]  # Siempre incluir la opción de nuevo
    if not trabajadores_df.empty and 'nombres' in trabajadores_df.columns:
        lista_trabajadores = trabajadores_df['nombres'].tolist() + lista_trabajadores

    selected = st.selectbox("Trabajadores registrados:", lista_trabajadores)

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

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Volver al accidente"):
            st.session_state.pagina = "accidentes"
            st.rerun()
    with col2:
        if st.button("Ir a Investigación"):
            st.session_state.pagina = "investigacion"



# Página de investigación
def pagina_investigacion():
    st.header("Datos de la Investigación")

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
    st.header("Árbol de Causas")

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
    st.header("Documentos Anexos")

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

    st.markdown("""
        <style>
            .stButton>button {min-width: 120px;}
            .stSelectbox {min-width: 300px;}
            .stAlert {border-left: 4px solid #FF4B4B; padding: 1rem;}
        </style>
    """, unsafe_allow_html=True)


    paginas = {
        "inicio": pagina_empresa,
        "nueva_empresa": pagina_nueva_empresa,
        "editar_empresa": pagina_editar_empresa,
        "centros_trabajo": pagina_centros_trabajo,
        "nuevo_centro": pagina_nuevo_centro,
        "editar_centro": pagina_editar_centro,
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