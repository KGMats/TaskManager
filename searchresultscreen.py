from libtui import *
from libterm import Keys
from screens import SCREENS
from libgerenciador import Tarefa, ListaDeTarefas

class SearchResultsScreen(TUIScreen):
    """
    Tela para exibir os resultados de uma busca por tarefas.

    Exibe uma lista de tarefas que correspondem a um termo de busca e permite
    ao usuário interagir com elas (ver detalhes, marcar como concluída, apagar).
    """
    def __init__(self, resultados: list, termo_busca: str):
        """
        Inicializa a tela de resultados da busca.

        Args:
            resultados (list): A lista de tuplas (Tarefa, ListaDeTarefas) para exibir.
            termo_busca (str): O termo que foi utilizado na busca.
        """
        super().__init__()
        self.app = TUIApplication.current_application
        self.resultados = resultados
        self.termo_busca = termo_busca
        
        t = self.app.terminal
        width, height = t.COLUMNS, t.LINES

        self.frame = Frame(x=1, y=1, width=width, height=height, title=f"Resultados para '{self.termo_busca}' ({len(self.resultados)} encontrados)")
        self.children.append(self.frame)

        self.is_empty_view = not self.resultados
        
        self.list_widget = VerticalList(x=3, y=3, width=width - 6, height=height - 8)
        self.children.append(self.list_widget)
        
        if self.is_empty_view:
            self.prompt_label = Label("Nenhuma tarefa encontrada.", x=4, y=5, style=TextStyle(italic=True, color="WHITE"))
            self.children.append(self.prompt_label)
        else:
            self.refresh_list_ui()

        action_buttons = []
        if not self.is_empty_view:
            self.details_button = Button("Detalhes", x=0, y=height-5, on_click=self.open_task_details)
            action_buttons.append(self.details_button)
            
        self.back_button = Button("Voltar", x=0, y=height-5, on_click=self.app.pop_screen_stack)
        action_buttons.append(self.back_button)

        current_x = 3
        for btn in action_buttons:
            btn.x = current_x
            current_x += btn.width + 1
        
        self.children.extend(action_buttons)
        self.set_focus_by_index(0)

    def get_focusable_widgets(self):
        """Retorna a lista de widgets focáveis."""
        focusable = []
        if not self.is_empty_view:
            focusable.append(self.list_widget)
            focusable.append(self.details_button)
        focusable.append(self.back_button)
        return focusable

    def refresh_list_ui(self):
        """Atualiza a lista de widgets com os resultados."""
        self.list_widget.children.clear()
        for tarefa, lista_mae in self.resultados:
            # Mostra a qual lista a tarefa pertence, pois é um resultado de busca global
            texto_label = f"{tarefa.titulo} (em: {lista_mae.titulo})"
            label = Label(texto_label)
            if tarefa.concluida:
                label.style = TextStyle(strikethrough=True, color="WHITE")
            # Armazena os objetos para fácil acesso
            label.tarefa_obj = tarefa
            label.lista_mae_obj = lista_mae
            self.list_widget.add_child(label)

    def get_selected_result(self):
        """Retorna a tarefa e a lista selecionadas."""
        if self.is_empty_view or not self.list_widget.children:
            return None, None
        selected_widget = self.list_widget.children[self.list_widget.focus_index]
        return selected_widget.tarefa_obj, selected_widget.lista_mae_obj

    def open_task_details(self):
        """Abre a tela de detalhes para a tarefa selecionada."""
        tarefa, lista_mae = self.get_selected_result()
        if tarefa:
            self.app.push_screen_stack(SCREENS.TASK_DETAIL, (tarefa, lista_mae))

    def process_input(self, key):
        """Processa a entrada do teclado para interagir com a lista."""
        focused_widget = self.get_focused_widget()
        if focused_widget == self.list_widget and not self.is_empty_view:
            tarefa, lista_mae = self.get_selected_result()
            if key == Keys.ENTER and tarefa:
                self.app.taskmanager.toggle_tarefa_concluida(lista_mae.id, tarefa.id)
                self.refresh_list_ui()
                return True
            if key == Keys.DELETE and tarefa:
                self.app.taskmanager.remover_tarefa(lista_mae.id, tarefa.id)
                self.resultados.pop(self.list_widget.focus_index)
                self.frame.title = f"Resultados para '{self.termo_busca}' ({len(self.resultados)} encontrados)"
                self.refresh_list_ui()
                return True
        super().process_input(key)
