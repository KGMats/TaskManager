from libtui import *
from libterm import Keys
from screens import SCREENS
from libgerenciador import ListaDeTarefas

class ListSelectionScreen(TUIScreen):
    """
    A tela principal da aplicação, que exibe todas as listas de tarefas criadas.

    Esta tela serve como o menu principal, permitindo que o usuario navegue
    para outras partes da aplicação, como a visualização de tarefas, edição de listas,
    ou a criação de novas listas etc.

    Atributos:
        app (TUIApplication): A instância principal da aplicação.
        dialog (Widget | None): Um placeholder para diálogos modais (Confirmação, Alerta).
        frame (Frame): O widget de frame que desenha a borda da tela.
        list_widget (VerticalList): O widget que exibe as listas de tarefas.
        view_list_button (Button): O botão para visualizar a lista selecionada.
        view_all_button (Button): O botão para visualizar todas as tarefas de todas as listas.
        edit_list_button (Button): O botão para editar o nome da lista selecionada.
    """
    def __init__(self):
        """
        Inicializa a tela ListSelectionScreen, configurando todos os seus widgets filhos.
        """
        super().__init__()
        self.app = TUIApplication.current_application
        t = self.app.terminal
        width, height = t.COLUMNS, t.LINES
        
        self.dialog = None
        
        self.frame = Frame(x=1, y=1, width=width, height=height, title="Minhas Listas de Tarefas 📝")
        self.frame.frame_style.color = "GREEN"
        self.frame.frame_style.bold = True
        
        self.list_widget = VerticalList(x=3, y=3, width=width - 6, height=height - 8)

        self.view_list_button = Button("Ver Lista", x=3, y=height-5, on_click=self.view_selected_list_tasks)
        self.view_all_button = Button("Ver Todas", x=17, y=height-5, on_click=self.view_all_tasks)
        self.create_list_button = Button("Criar Lista", x=31, y=height-5, on_click=self.create_new_list)
        self.edit_list_button = Button("Editar Lista", x=47, y=height-5, on_click=self.edit_selected_list)
        self.search_button = Button("Buscar", x=64, y=height-5, on_click=self.search_tasks)
        
        self.children.extend([
            self.frame, self.list_widget,
            self.view_list_button, self.view_all_button, 
            self.create_list_button, self.edit_list_button,
            self.search_button
        ])
        self.refresh_lists()
        self.set_focus_by_index(0)

    def render(self):
        """
        Desenha a tela e, se um diálogo estiver ativo, desenha o dialogo por cima de tudo.
        """
        super().render()
        if self.dialog:
            self.dialog.render()
    
    def delete_selected_list(self):
        selected = self.get_selected_list_obj()
        if not selected:
            return

        # Verifica se é a última lista e usa o novo AlertDialog
        if len(self.app.taskmanager.listas) <= 1:
            self.dialog = AlertDialog(
                message="Não é possível excluir a última lista.",
                on_dismiss=self._cancel_delete
            )
            return

        # Se a validação passar, mostra o diálogo de confirmação como antes
        self.dialog = ConfirmationDialog(
            message=f"Apagar '{selected.titulo}' e todas as suas tarefas?",
            on_confirm=self._perform_actual_delete,
            on_cancel=self._cancel_delete
        )


    def _cancel_delete(self):
        self.dialog = None


    def _perform_actual_delete(self):
        selected = self.get_selected_list_obj()
        if selected:
            self.app.taskmanager.remover_lista_de_tarefas(selected.id)
            self.refresh_lists()
        self.dialog = None
            
    def process_input(self, key):
        """
        Processa a entrada do teclado. Dá prioridade ao diálogo, se ativo.

        Args:
            key (str): A tecla pressionada pelo utilizador.
        """
        if self.dialog:
            self.dialog.process_input(key)
            return
        if key == "REFRESH":
            self.refresh_lists()
            return
        if key == Keys.DELETE:
            self.delete_selected_list()
        super().process_input(key)

    def create_new_list(self):
        self.app.push_screen_stack(SCREENS.CREATELIST)


    def view_selected_list_tasks(self):
        """
        Abre a tela de opções de filtro para a lista de tarefas atualmente selecionada.
        """
        selected = self.get_selected_list_obj()
        if selected:
            self.app.push_screen_stack(SCREENS.FILTER_OPTIONS, {'contexto_lista': selected})

    def view_all_tasks(self):
        """
        Abre a tela de opções de filtro sem um contexto de lista, que tem como resultado visualização de todas as tarefas.
        """
        self.app.push_screen_stack(SCREENS.FILTER_OPTIONS, {})

    def edit_selected_list(self):
        """
        Abre a tela de edição para a lista de tarefas atualmente selecionada.
        """
        selected = self.get_selected_list_obj()
        if selected:
            self.app.push_screen_stack(SCREENS.EDIT_LIST, selected)
        
    def get_selected_list_obj(self):
        """
        Obtém o objeto ListaDeTarefas completo que está atualmente selecionado no list_widget.

        Returns:
            ListaDeTarefas | None: O objeto da lista selecionada, ou None se nenhuma estiver selecionada.
        """
        if not self.list_widget.children: return None
        selected_widget = self.list_widget.children[self.list_widget.focus_index]
        return selected_widget.task_list_obj

    def refresh_lists(self):
        """
        Limpa e repopula o list_widget com os dados mais recentes do gestor de tarefas.
        """
        self.list_widget.children.clear()
        for task_list in self.app.taskmanager.listas:
            label = Label(f"  {task_list.titulo}")
            label.task_list_obj = task_list
            self.list_widget.add_child(label)
            
    def get_focusable_widgets(self):
        """
        Retorna a lista de widgets que podem receber foco, definindo a ordem de navegação (Tab).

        Returns:
            list: Uma lista de widgets focáveis.
        """
        return [self.list_widget, self.view_list_button, self.view_all_button,
                self.create_list_button, self.edit_list_button, self.search_button]


    def search_tasks(self):
        """
        Leva o usuario para a tela de busca de tarefas
        """

        self.app.push_screen_stack(SCREENS.SEARCH_INPUT)

