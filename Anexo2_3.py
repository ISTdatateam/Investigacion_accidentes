import streamlit as st


class Question:
    TYPE_MAPPING = {
        "segmented": "segmented_control",
        "sino": "radio",
        "select": "selectbox",
        "text": "text_area",
        "pills": "pills",
        "multiselect": "multiselect"
    }

    def __init__(self, key, question, question_type, options=None, default=None, depends_on=None):
        self.key = key
        self.question = question
        self.type = question_type
        self.options = options or []
        self.default = default
        self.depends_on = depends_on

    def render(self):
        if self.depends_on and not self._check_dependency():
            return None

        st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
        st.markdown(f"**{self.question}**")

        render_method = getattr(st, self.TYPE_MAPPING[self.type], None)
        if not render_method:
            raise ValueError(f"Tipo de pregunta no soportado: {self.type}")

        kwargs = {
            "label": self.question,
            "options": self.options,
            "key": self.key,
            "label_visibility": "hidden"
        }

        if self.type == "select":
            kwargs["index"] = self.options.index(self.default) if self.default in self.options else 0
        elif self.type in ["text", "multiselect"]:
            kwargs["default"] = self.default

        return render_method(**kwargs)

    def _check_dependency(self):
        dependency_key, dependency_value = self.depends_on
        return st.session_state.respuestas.get(dependency_key) == dependency_value


class Page:
    def __init__(self, page_id, section, questions, next_pages=None):
        self.page_id = page_id
        self.section = section
        self.questions = questions
        self.next_pages = next_pages or {}

    def render(self):
        st.markdown(f"##### {self.section}")
        responses = {}

        for question in self.questions:
            response = question.render()
            if response is not None:
                responses[question.key] = response

        if self._navigation_controls():
            self._handle_responses(responses)
            return self._get_next_page()
        return None

    def _navigation_controls(self):
        st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
        nav_key = f"nav_{self.page_id}"
        options = ["Continuar ▶"]
        if st.session_state.history:
            options.insert(0, "◀ Regresar")

        action = st.segmented_control(
            label="Navegación",
            options=options,
            key=nav_key,
            label_visibility="collapsed"
        )

        if action == "◀ Regresar":
            st.session_state.current_page = st.session_state.history.pop()
            st.rerun()
        return action == "Continuar ▶"

    def _handle_responses(self, responses):
        for key, value in responses.items():
            if value:  # Solo guardar respuestas no vacías
                st.session_state.respuestas[key] = value

    def _get_next_page(self):
        if self.next_pages:
            for response_value, next_page in self.next_pages.items():
                if st.session_state.respuestas.get(self.questions[0].key) == response_value:
                    return next_page
        return None


class SurveyManager:
    def __init__(self):
        self.pages = {}
        self._initialize_state()
        self._load_pages()

    def _initialize_state(self):
        initial_state = {
            'current_page': '1',
            'respuestas': {},
            'history': []
        }
        for key, value in initial_state.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def _load_pages(self):
        self.pages = {
            '1': Page(
                page_id='1',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p1',
                        question="1. ¿La tarea que desarrollaba en el momento del accidente era propia de su puesto de trabajo?",
                        question_type="segmented",
                        options=["SI", "NO"]
                    )
                ],
                next_pages={'SI': '2', 'NO': '3'}
            ),
            '2': Page(
                page_id='2',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p2',
                        question="2. ¿La tarea que desarrollaba era habitual?",
                        question_type="sino",
                        options=["SI", "NO"]
                    )
                ],
                next_pages={'SI': '2.1', 'NO': '3'}
            ),
            '2.1': Page(
                page_id='2.1',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p2.1',
                        question="2.1. ¿Se realizaba la tarea habitual de la misma manera con la que se venía realizando normalmente?",
                        question_type="segmented",
                        options=["SI", "NO"]
                    )
                ],
                next_pages={'SI': '2.2', 'NO': '2.3'}
            ),
            '2.2': Page(
                page_id='2.2',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p2.2',
                        question="2.2. Desarrollando la tarea de la forma habitual ¿era posible que ocurriera el accidente?",
                        question_type="segmented",
                        options=["SI", "NO"]
                    )
                ],
                next_pages={'SI': '3', 'NO': '3'}
            ),
            '2.3': Page(
                page_id='2.3',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p2.3',
                        question="2.3. ¿Por qué la persona accidentada realizaba la tarea habitual de manera diferente?",
                        question_type="select",
                        options=[
                            "Seleccione...",
                            "No era posible realizarla de la forma habitual.",
                            "Desconocía la forma habitual de realizar la tarea.",
                            "Había recibido instrucciones de realizarla de esta manera.",
                            "Otros (especificar)"
                        ],
                        default="Seleccione..."
                    )
                ],
                next_pages={'Otros (especificar)': '2.3.1', '_default': '3'}
            ),
            '2.3.1': Page(
                page_id='2.3.1',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p2.3.1',
                        question="2.3.1 Especifica por qué la persona accidentada realizaba la tarea habitual de manera diferente",
                        question_type="text"
                    )
                ],
                next_pages={'_default': '3'}
            ),
            '3': Page(
                page_id='3',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p3',
                        question="3. ¿Con qué frecuencia el trabajador había desarrollado esta tarea?",
                        question_type="select",
                        options=[
                            "Seleccione...",
                            "Era la primera vez",
                            "De manera esporádica",
                            "Frecuentemente"
                        ],
                        default="Seleccione..."
                    )
                ],
                next_pages={'_default': '4'}
            ),
            '4': Page(
                page_id='4',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p4',
                        question="4. ¿El trabajador había recibido instrucciones sobre cómo realizar la tarea?",
                        question_type="segmented",
                        options=["SI", "NO"]
                    )
                ],
                next_pages={'SI': '4.1', 'NO': '5'}
            ),
            '4.1': Page(
                page_id='4.1',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p4.1',
                        question="4.1. ¿Qué tipo de instrucciones?",
                        question_type="segmented",
                        options=["Escritas", "Verbales", "Ambas"]
                    )
                ],
                next_pages={'_default': '4.2'}
            ),
            '4.2': Page(
                page_id='4.2',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p4.2',
                        question="4.2. ¿De quién recibió las instrucciones?",
                        question_type="segmented",
                        options=[
                            "Instrucciones del empleador",
                            "Instrucciones del jefe",
                            "Instrucciones del encargado",
                            "Instrucciones de compañeros"
                        ]
                    )
                ],
                next_pages={'_default': '4.3'}
            ),
            '4.3': Page(
                page_id='4.3',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p4.3',
                        question="4.3. ¿Estaba realizando la tarea de acuerdo con esas instrucciones?",
                        question_type="segmented",
                        options=["SI", "NO"]
                    )
                ],
                next_pages={'_default': '5'}
            ),
            '5': Page(
                page_id='5',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p5',
                        question="5. ¿La tarea se realiza con EPP?",
                        question_type="segmented",
                        options=["SI", "NO"]
                    )
                ],
                next_pages={'SI': '5.0.1', 'NO': '6'}
            ),
            '5.0.1': Page(
                page_id='5.0.1',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p5.0.1',
                        question="5.0.1 Especifica los equipos de protección utilizados",
                        question_type="text"
                    )
                ],
                next_pages={'_default': '5.1'}
            ),
            '5.1': Page(
                page_id='5.1',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p5.1',
                        question="5.1. ¿El EPP es adecuado al riesgo?",
                        question_type="segmented",
                        options=["SI", "NO"]
                    )
                ],
                next_pages={'_default': '5.2'}
            ),
            '5.2': Page(
                page_id='5.2',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p5.2',
                        question="5.2. ¿Usaba los EPP en el momento del accidente?",
                        question_type="segmented",
                        options=["SI", "NO"]
                    )
                ],
                next_pages={'_default': '5.3'}
            ),
            '5.3': Page(
                page_id='5.3',
                section='Sección TAREA',
                questions=[
                    Question(
                        key='p5.3',
                        question="5.3. ¿Hubiera evitado el accidente otro EPP?",
                        question_type="segmented",
                        options=["SI", "NO"]
                    )
                ],
                next_pages={'_default': '6'}
            ),
            '6': Page(
                page_id='6',
                section='Sección LUGAR',
                questions=[
                    Question(
                        key='p6',
                        question="6. ¿La tarea se realizaba en el lugar habitual de trabajo?",
                        question_type="segmented",
                        options=["SI", "NO"]
                    )
                ],
                next_pages={'SI': '6.1', 'NO': '6.2'}
            ),
            '6.1': Page(
                page_id='6.1',
                section='Sección LUGAR',
                questions=[
                    Question(
                        key='p6.1',
                        question="6.1. ¿Era posible el accidente en el lugar habitual?",
                        question_type="segmented",
                        options=["SI", "NO"]
                    )
                ],
                next_pages={'_default': '7'}
            ),
            '6.2': Page(
                page_id='6.2',
                section='Sección LUGAR',
                questions=[
                    Question(
                        key='p6.2',
                        question="6.2. ¿Por qué no realizaba la tarea en el lugar habitual?",
                        question_type="select",
                        options=[
                            "Seleccione...",
                            "No era posible realizarla en el lugar habitual.",
                            "Desconocía el lugar habitual.",
                            "Había recibido instrucciones de realizarla en otro lugar.",
                            "Otros (especificar)"
                        ],
                        default="Seleccione..."
                    )
                ],
                next_pages={'Otros (especificar)': '6.2.1', '_default': '7'}
            ),
            '6.2.1': Page(
                page_id='6.2.1',
                section='Sección LUGAR',
                questions=[
                    Question(
                        key='p6.2.1',
                        question="6.2.1 Especifica por qué no se realizaba en el lugar habitual",
                        question_type="text"
                    )
                ],
                next_pages={'_default': '7'}
            )
        }

    def run(self):
        st.subheader("Formulario de Investigación de Accidentes")
        current_page = self.pages.get(st.session_state.current_page)

        if current_page:
            next_page = current_page.render()
            if next_page:
                self._navigate_to(next_page)
        else:
            st.error("Página no encontrada")

    def _navigate_to(self, next_page):
        st.session_state.history.append(st.session_state.current_page)
        st.session_state.current_page = next_page
        st.rerun()


class FinalPage(Page):
    def render(self):
        st.markdown("## Formulario Completo")
        st.success("¡Gracias por completar el formulario!")
        st.write("Resumen de respuestas:", st.session_state.respuestas)

        if st.button("Reiniciar formulario"):
            st.session_state.clear()
            st.rerun()


if __name__ == "__main__":
    survey = SurveyManager()
    survey.run()