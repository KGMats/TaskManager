from libtui import *
from libterm import Keys
from screens import SCREENS
from libgerenciador import PRIORIDADE, FREQUENCIA, Tarefa

from libtui import *
from libterm import Keys
from screens import SCREENS
from libgerenciador import PRIORIDADE, FREQUENCIA, Tarefa, ListaDeTarefas

class EditTaskScreen(TUIScreen):
    """
    Tela para edição de uma tarefa existente.

    Permite modificar todos os atributos da tarefa, inclusive movê-la para outra lista.
    """
    def __init__(self, data: tuple):
        tarefa, lista_mae = data
        super().__init__()
        self.app = TUIApplication.current_application
        self.tarefa = tarefa
        self.lista_mae = lista_mae
        
        t = self.app.terminal
        width, height = t.COLUMNS, t.LINES

        # Define posições Y para os campos
        y_notes, y_tags, y_priority, y_date, y_freq, y_lista, y_buttons = 6, 8, 10, 13, 15, 17, 19

        self.frame = Frame(x=1, y=1, width=width, height=height, title="Editando Tarefa")
        self.children.append(self.frame)

        # Campos de edição preenchidos com valores atuais
        self.title_input = TextInput(x=4, y=4, width=width-8, initial_text=self.tarefa.titulo)
        self.notes_input = TextInput(x=4, y=y_notes, width=width-8, initial_text=self.tarefa.nota)
        tags_str = ", ".join(self.tarefa.tags)
        self.tags_input = TextInput(x=4, y=y_tags, width=width-8, initial_text=tags_str)
        
        self.priority_label = Label("Prioridade:", x=4, y=y_priority, style=TextStyle(bold=True))
        p_none, p_low, p_med, p_high = (self.tarefa.prioridade == p for p in PRIORIDADE)
        self.priority_none = Checkbox("Nenhuma", x=4, y=y_priority+1, checked=p_none)
        self.priority_low = Checkbox("Baixa", x=16, y=y_priority+1, checked=p_low)
        self.priority_medium = Checkbox("Média", x=27, y=y_priority+1, checked=p_med)
        self.priority_high = Checkbox("Alta", x=38, y=y_priority+1, checked=p_high, style=TextStyle(color="RED", bold=True))
        
        self.dateinput = DateInput(x=4, y=y_date, label="Data:")
        self.dateinput.day, self.dateinput.month, self.dateinput.year = self.tarefa.data.day, self.tarefa.data.month, self.tarefa.data.year
        
        freq_options = ['Nenhuma', 'Diaria', 'Semanal', 'Mensal', 'Anual']
        freq_index = freq_options.index(self.tarefa.repeticao.name.title())
        self.frequence_selector = Selector(freq_options, x=4, y=y_freq, label="Frequência:", selected_index=freq_index)

        todas_listas = self.app.taskmanager.get_todas_listas()
        self.lista_options = {lista.titulo: lista for lista in todas_listas}
        lista_titles = list(self.lista_options.keys())
        current_list_index = lista_titles.index(self.lista_mae.titulo)
        self.lista_selector = Selector(lista_titles, x=4, y=y_lista, label="Mover para Lista:", selected_index=current_list_index)

        self.save_button = Button("Salvar", x=4, y=y_buttons, on_click=self.save_changes)
        self.cancel_button = Button("Cancelar", x=15, y=y_buttons, on_click=self.app.pop_screen_stack)

        self.children.extend([
            self.title_input, self.notes_input, self.tags_input, self.priority_label,
            self.priority_none, self.priority_low, self.priority_medium, self.priority_high,
            self.dateinput, self.frequence_selector, self.lista_selector,
            self.save_button, self.cancel_button
        ])
        self.set_focus_by_index(0)

    def save_changes(self):
        """
        Salva as alterações feitas na tarefa.

        Move a tarefa para outra lista, se o usuário selecionou uma diferente,
        e atualiza os atributos da tarefa com os dados do formulário.
        """
        selected_list_title = self.lista_selector.get_selected_value()
        selected_list_obj = self.lista_options[selected_list_title]
        if self.lista_mae.id != selected_list_obj.id:
            self.app.taskmanager.mover_tarefa(self.tarefa.id, self.lista_mae.id, selected_list_obj.id)

        self.app.taskmanager.editar_tarefa(
            tarefa=self.tarefa, titulo=self.title_input.text, nota=self.notes_input.text,
            data=self.dateinput.get_date(), tags=self.get_tags_from_input(),
            prioridade=self.get_task_priority(), repeticao=self.get_task_frequency()
        )
        self.app.pop_screen_stack()
        self.app.pop_screen_stack()

    def get_focusable_widgets(self):
        """
        Retorna os widgets que podem receber foco para navegação.

        Returns:
            list: Widgets focáveis, na ordem do tab.
        """
        return [
            self.title_input, self.notes_input, self.tags_input,
            self.priority_none, self.priority_low, self.priority_medium, self.priority_high,
            self.dateinput, self.frequence_selector, self.lista_selector,
            self.save_button, self.cancel_button
        ]

    def update_priority_selection(self, selected_checkbox):
        """
        Garante que apenas uma checkbox de prioridade esteja selecionada.

        Args:
            selected_checkbox (Checkbox): A checkbox que foi marcada.
        """
        priorities = [self.priority_none, self.priority_low, self.priority_medium, self.priority_high]
        for p in priorities: p.checked = (p == selected_checkbox)
        
    def get_task_priority(self):
        """
        Obtém o valor do enum PRIORIDADE correspondente à checkbox marcada.

        Returns:
            PRIORIDADE: O nível de prioridade selecionado.
        """
        if self.priority_none.checked: return PRIORIDADE.SEM_PRIORIDADE
        if self.priority_low.checked: return PRIORIDADE.BAIXA
        if self.priority_medium.checked: return PRIORIDADE.MEDIA
        if self.priority_high.checked: return PRIORIDADE.ALTA
        return PRIORIDADE.SEM_PRIORIDADE

    def get_task_frequency(self):
        """
        Obtém o valor do enum FREQUENCIA selecionado no seletor.

        Returns:
            FREQUENCIA: A frequência selecionada.
        """
        freq_map = {'Nenhuma': FREQUENCIA.NENHUMA, 'Diaria': FREQUENCIA.DIARIA, 'Semanal': FREQUENCIA.SEMANAL, 'Mensal': FREQUENCIA.MENSAL, 'Anual': FREQUENCIA.ANUAL}
        return freq_map.get(self.frequence_selector.get_selected_value(), FREQUENCIA.NENHUMA)

    def get_tags_from_input(self) -> list[str]:
        """
        Analisa a string de tags separadas por vírgula e retorna uma lista de tags limpas.

        Returns:
            list[str]: Lista de tags sem espaços vazios.
        """
        tags_string = self.tags_input.text
        if not tags_string: return []
        return [tag.strip() for tag in tags_string.split(',') if tag.strip()]

    def process_input(self, key):
        """
        Processa a entrada do usuário para comportamento especial de checkboxes de prioridade.

        Args:
            key: Tecla pressionada.
        """
        focused_widget = self.get_focused_widget()
        if focused_widget in [self.priority_none, self.priority_low, self.priority_medium, self.priority_high]:
            if key in (Keys.ENTER, Keys.SPACE):
                focused_widget.process_input(key)
                self.update_priority_selection(focused_widget)
                return
        super().process_input(key)

