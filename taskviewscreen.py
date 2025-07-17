from libtui import *
from libterm import Keys
from screens import SCREENS
from libgerenciador import ListaDeTarefas

class TaskViewScreen(TUIScreen):
    """
    Uma tela genérica para exibir uma lista de tarefas filtrada e ordenada.
    
    Esta tela é responsável por buscar seus próprios dados com base nos
    parâmetros de filtro recebidos, e pode se auto-atualizar.
    """
    
    def __init__(self, titulo: str, filtro_tempo: str, filtro_status: str, ordenacao: str, contexto_lista: ListaDeTarefas = None, contexto_tag: str = None):
        """
        Inicializa a tela TaskViewScreen.

        Args:
            titulo (str): O título a ser exibido no frame da tela.
            filtro_tempo (str): O filtro de tempo a ser aplicado ('TODAS', 'HOJE', 'SETE_DIAS').
            filtro_status (str): O filtro de status a ser aplicado ('TODAS', 'COMPLETAS', 'INCOMPLETAS').
            ordenacao (str): O critério de ordenação ('DATA', 'PRIORIDADE').
            contexto_lista (ListaDeTarefas, optional): A lista de tarefas que serve de contexto.
            contexto_tag (str, optional): A tag que serve de contexto.
        """
        super().__init__()
        self.app = TUIApplication.current_application
        self.titulo_tela = titulo
        self.dialog = None 
        
        # Armazena os parâmetros de filtro para poder recarregar os dados
        self.filtro_tempo = filtro_tempo
        self.filtro_status = filtro_status
        self.ordenacao = ordenacao
        self.contexto_lista = contexto_lista
        self.contexto_tag = contexto_tag
        
        # Carrega os dados iniciais
        self.refresh_tasks()

    def _setup_ui(self):
        """Configura ou reconfigura os widgets da UI."""
        self.children.clear()
        t = self.app.terminal
        width, height = t.COLUMNS, t.LINES

        self.frame = Frame(x=1, y=1, width=width, height=height, title=f"{self.titulo_tela} ({len(self.resultados)} tarefas)")
        self.children.append(self.frame)

        self.is_empty_view = not self.resultados
        self.can_create_task = self.contexto_lista is not None

        self.list_widget = VerticalList(x=3, y=3, width=width - 6, height=height - 8)
        self.children.append(self.list_widget)
        
        if self.is_empty_view:
            self.prompt_label = Label("Nenhuma tarefa encontrada para esta visualização.", x=4, y=5, style=TextStyle(italic=True, color="WHITE"))
            self.children.append(self.prompt_label)
        else:
            self.refresh_list_ui()

        action_buttons = []
        if self.can_create_task:
            self.create_button = Button("Criar Tarefa", x=0, y=height-5, on_click=self.push_create_task_screen)
            action_buttons.append(self.create_button)

        if not self.is_empty_view:
            self.details_button = Button("Detalhes", x=0, y=height-5, on_click=self.open_task_details)
            action_buttons.append(self.details_button)
            
            # Renomeia para ser mais claro
            if self.filtro_status == "COMPLETAS":
                self.delete_all_button = Button("Apagar Todas", x=0, y=height-5, on_click=self.confirm_delete_all_completed)
                action_buttons.append(self.delete_all_button)
            
        self.back_button = Button("Voltar", x=0, y=height-5, on_click=self.app.pop_screen_stack)
        action_buttons.append(self.back_button)

        current_x = 3
        for btn in action_buttons:
            btn.x = current_x
            current_x += btn.width + 1
        
        self.children.extend(action_buttons)
        self.set_focus_by_index(0)

    def refresh_tasks(self):
        """Busca novamente os dados do gerenciador e reconfigura a UI."""
        self.resultados = self.app.taskmanager.get_visualizacao_tarefas(
            filtro_tempo=self.filtro_tempo,
            filtro_status=self.filtro_status,
            ordenacao=self.ordenacao,
            contexto_lista=self.contexto_lista,
            contexto_tag=self.contexto_tag
        )
        self._setup_ui()

    def push_create_task_screen(self):
        """Navega para a tela de criação de tarefas."""
        if self.contexto_lista:
            self.app.push_screen_stack(SCREENS.CREATETASK, self.contexto_lista)

    def get_focusable_widgets(self):
        """Retorna a lista dinâmica de widgets focáveis com base no estado da tela."""
        focusable = []
        if not self.is_empty_view:
            focusable.append(self.list_widget)
        
        if self.can_create_task:
            focusable.append(self.create_button)
        
        if not self.is_empty_view:
            focusable.append(self.details_button)
            if self.filtro_status == "COMPLETAS":
                focusable.append(self.delete_all_button)
            
        focusable.append(self.back_button)
        return focusable

    def refresh_list_ui(self):
        """Limpa e repopula o widget da lista com os resultados atuais."""
        self.list_widget.children.clear()
        for tarefa, lista_mae in self.resultados:
            texto_label = f"{tarefa.titulo}  (em: {lista_mae.titulo})"
            label = Label(texto_label)
            if tarefa.concluida:
                label.style = TextStyle(strikethrough=True, color="WHITE")
            label.tarefa_obj = tarefa
            label.lista_mae_obj = lista_mae
            self.list_widget.add_child(label)

    def get_selected_result(self):
        """Obtém a tarefa e a lista mãe atualmente selecionadas na lista."""
        if self.is_empty_view or not self.list_widget.children: return None, None
        selected_widget = self.list_widget.children[self.list_widget.focus_index]
        return selected_widget.tarefa_obj, selected_widget.lista_mae_obj

    def open_task_details(self):
        """Abre a tela de detalhes para a tarefa selecionada."""
        tarefa, lista_mae = self.get_selected_result()
        if tarefa:
            self.app.push_screen_stack(SCREENS.TASK_DETAIL, (tarefa, lista_mae))

    def process_input(self, key):
        """
        Processa a entrada do teclado para a tela, incluindo atalhos e o sinal de REFRESH.
        """
        if self.dialog:
            self.dialog.process_input(key)
            return

        if key == "REFRESH":
            self.refresh_tasks()
            return True

        focused_widget = self.get_focused_widget()
        if focused_widget == self.list_widget and not self.is_empty_view:
            tarefa, lista_mae = self.get_selected_result()
            if key == Keys.ENTER and tarefa:
                self.app.taskmanager.toggle_tarefa_concluida(lista_mae.id, tarefa.id)
                self.refresh_tasks()
                return True
            if key == Keys.DELETE and tarefa:
                self.app.taskmanager.remover_tarefa(lista_mae.id, tarefa.id)
                self.refresh_tasks() # Recarrega tudo para que a tarefa não apareça mais na lista
                return True
        super().process_input(key)

    def confirm_delete_all_completed(self):
        """Exibe um diálogo para confirmar a exclusão de todas as tarefas concluídas."""
        self.dialog = ConfirmationDialog(
            message="Apagar permanentemente todas as tarefas concluídas?",
            on_confirm=self._perform_delete_all_completed,
            on_cancel=lambda: setattr(self, 'dialog', None)
        )

    def _perform_delete_all_completed(self):
        """Executa a ação de exclusão e fecha a tela atual."""
        self.app.taskmanager.remover_tarefas_concluidas()
        self.dialog = None
        self.app.pop_screen_stack()

