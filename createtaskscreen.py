from libtui import *
from libterm import Keys
from screens import SCREENS
from libgerenciador import PRIORIDADE, FREQUENCIA, ListaDeTarefas

class CreateTaskScreen(TUIScreen):
    """
    Tela para criação de uma nova tarefa dentro de uma lista específica.

    Permite inserir título, notas, tags, prioridade, data de vencimento e frequência.
    Utiliza widgets customizados para entrada de dados e seleção de opções.
    """
    def __init__(self, task_list: ListaDeTarefas):
        """
        Inicializa a tela com todos os campos necessários para criar uma tarefa.

        Args:
            task_list (ListaDeTarefas): A lista onde a nova tarefa será adicionada.
        """
        super().__init__()
        self.app = TUIApplication.current_application
        self.task_list = task_list
        
        t = self.app.terminal
        width, height = t.COLUMNS, t.LINES

        # Define layout vertical para cada campo e botões
        y_notes = 6
        y_tags = 8
        y_priority = 10
        y_date = 13
        y_freq = 15
        y_buttons = y_freq + 3

        self.frame = Frame(x=1, y=1, width=width, height=height, title="Criando Nova Tarefa")
        self.frame.frame_style.color = "BLUE"
        self.frame.frame_style.bold = True
        self.children.append(self.frame)

        # Definindo os inputs de Titulo
        self.title_input = TextInput(x=4, y=4, width=width - 8, placeholder="Título da tarefa...")
        self.children.append(self.title_input)

        # Definindo os inputs de Titulo
        self.notes_input = TextInput(x=4, y=y_notes, width=width - 8, placeholder="Notas (opcional)...")
        self.children.append(self.notes_input)
        
        # Definindo os inputs de Tags
        self.tags_input = TextInput(x=4, y=y_tags, width=width-8, placeholder="Tags (separadas por vírgula)...")
        self.children.append(self.tags_input)

        # Definindo o seletor de prioridade. Por padrao "Nenhuma" e selecionado
        self.priority_label = Label("Prioridade:", x=4, y=y_priority, style=TextStyle(bold=True))
        self.children.append(self.priority_label)


        self.priority_none = Checkbox(label="Nenhuma", x=4, y=y_priority + 1, checked=True)
        self.priority_low = Checkbox(label="Baixa", x=16, y=y_priority + 1, checked=False, style=TextStyle(color="GREEN"))
        self.priority_medium = Checkbox(label="Média", x=27, y=y_priority + 1, checked=False, style=TextStyle(color="YELLOW"))
        self.priority_high = Checkbox(label="Alta", x=38, y=y_priority + 1, checked=False, style=TextStyle(color="RED"))
        self.children.extend([self.priority_none, self.priority_low, self.priority_medium, self.priority_high])

        # Definindo os inputs de Data
        self.dateinput = DateInput(x=4, y=y_date, style=TextStyle(bold=True), label="Data:")
        self.children.append(self.dateinput)
        
        # Definindo o seletor de recorrencia.
        self.frequence_selector = Selector(['Nenhuma', 'Diaria', 'Semanal', 'Mensal', 'Anual'], x=4, y=y_freq, label="Frequência:")
        self.children.append(self.frequence_selector)
        
        # Botoes
        self.save_button = Button(text="Salvar", x=4, y=y_buttons, on_click=self.save_task)
        self.cancel_button = Button(text="Cancelar", x=15, y=y_buttons, on_click=self.cancel)
        self.children.extend([self.save_button, self.cancel_button])
        
        self.set_focus_by_index(0)

    def get_focusable_widgets(self):
        """
        Retorna a lista dos widgets interativos para navegação por teclado.

        Returns:
            list: Widgets focáveis na ordem do tab.
        """
 
        return [
            self.title_input,
            self.notes_input,
            self.tags_input,
            self.priority_none,
            self.priority_low,
            self.priority_medium,
            self.priority_high,
            self.dateinput,
            self.frequence_selector,
            self.save_button,
            self.cancel_button
        ]

    def update_priority_selection(self, selected_checkbox):
        """
        Garante que apenas um checkbox de prioridade esteja selecionado.

        Args:
            selected_checkbox (Checkbox): Checkbox que foi selecionado.
        """
        priorities = [self.priority_none, self.priority_low, self.priority_medium, self.priority_high]
        for priority_widget in priorities:
            priority_widget.checked = (priority_widget == selected_checkbox)

    def get_task_priority(self):
        """
        Retorna o valor da prioridade da tarefa baseado no checkbox selecionado.

        Returns:
            PRIORIDADE: Enum representando a prioridade selecionada.
        """
        if self.priority_none.checked: return PRIORIDADE.SEM_PRIORIDADE
        if self.priority_low.checked: return PRIORIDADE.BAIXA
        if self.priority_medium.checked: return PRIORIDADE.MEDIA
        if self.priority_high.checked: return PRIORIDADE.ALTA
        return PRIORIDADE.SEM_PRIORIDADE # Default fallback

    def get_task_frequency(self):
        """
        Retorna o valor da frequência da tarefa baseado na seleção do usuário.

        Returns:
            FREQUENCIA: Enum representando a frequência selecionada.
        """
        freq_map = {'Nenhuma': FREQUENCIA.NENHUMA, 'Diaria': FREQUENCIA.DIARIA, 'Semanal': FREQUENCIA.SEMANAL, 'Mensal': FREQUENCIA.MENSAL, 'Anual': FREQUENCIA.ANUAL}
        return freq_map.get(self.frequence_selector.get_selected_value(), FREQUENCIA.NENHUMA)

    def cancel(self):
        """Cancela a criação da tarefa e volta para a tela anterior."""
        self.app.pop_screen_stack()

    def process_input(self, key):
        """
        Processa entrada de teclado, tratando especificamente checkboxes de prioridade.

        Args:
            key (str): Tecla pressionada.
        """
        focused_widget = self.get_focused_widget()
        
        if focused_widget in [self.priority_none, self.priority_low, self.priority_medium, self.priority_high]:
            if key == Keys.ENTER or key == Keys.SPACE:
                focused_widget.process_input(key)
                self.update_priority_selection(focused_widget)
                return
                
        super().process_input(key)
    
    def get_tags_from_input(self) -> list[str]:
        """
        Analisa a string de tags separadas por vírgula e retorna uma lista limpa.

        Returns:
            list[str]: Lista de tags sem espaços em branco.
        """
        tags_string = self.tags_input.text
        if not tags_string:
            return []
        return [tag.strip() for tag in tags_string.split(',') if tag.strip()]

    def save_task(self):
        """
        Coleta os dados dos widgets e cria a nova tarefa na lista.

        Chama o gerenciador de tarefas para adicionar a tarefa e fecha a tela.
        """
        self.app.taskmanager.criar_tarefa(
            lista_id=self.task_list.id,
            titulo=self.title_input.text,
            nota=self.notes_input.text,
            data=self.dateinput.get_date(),
            tags=self.get_tags_from_input(),
            prioridade=self.get_task_priority(),
            repeticao=self.get_task_frequency()
        )
        self.app.pop_screen_stack()

