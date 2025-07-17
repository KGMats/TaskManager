from libtui import *
from libterm import Keys
from screens import SCREENS
from libgerenciador import ListaDeTarefas

class EditListScreen(TUIScreen):
    """
    Tela para editar o nome de uma lista de tarefas existente.

    Exibe o nome atual da lista em um campo de texto editável,
    permite modificar e salvar a alteração, ou cancelar.
    """
    def __init__(self, lista_de_tarefas: ListaDeTarefas):
        """
        Inicializa a tela com o nome atual da lista preenchido.

        Args:
            lista_de_tarefas (ListaDeTarefas): A lista a ser editada.
        """
        super().__init__()
        self.app = TUIApplication.current_application
        self.lista_de_tarefas = lista_de_tarefas
        t = self.app.terminal
        width, height = t.COLUMNS, t.LINES

        self.frame = Frame(x=1, y=1, width=width, height=height, title="Editar Nome da Lista")
        self.children.append(self.frame)

        # Campo de texto com o nome atual da lista
        self.title_input = TextInput(x=4, y=4, width=width - 8, initial_text=self.lista_de_tarefas.titulo)
        self.children.append(self.title_input)

        # Label para exibir mensagens de erro, inicialmente vazio
        self.error_label = Label("", x=4, y=6, style=TextStyle(color="RED", bright=True))
        self.children.append(self.error_label)

        # Botões Salvar e Cancelar
        self.save_button = Button("Salvar", x=4, y=height - 5, on_click=self.save_list)
        self.cancel_button = Button("Cancelar", x=15, y=height - 5, on_click=self.app.pop_screen_stack)
        self.children.extend([self.save_button, self.cancel_button])
        
        self.set_focus_by_index(0)

    def save_list(self):
        """
        Tenta salvar o novo nome da lista.

        Valida o título não vazio e chama o gerenciador para editar a lista.
        Caso o nome já exista, exibe uma mensagem de erro.
        """
        novo_titulo = self.title_input.text.strip()
        if not novo_titulo:
            self.error_label.text = "O título não pode estar vazio."
            return

        success = self.app.taskmanager.editar_lista_de_tarefas(
            self.lista_de_tarefas.id,
            novo_titulo
        )

        if success:
            self.app.pop_screen_stack()
        else:
            self.error_label.text = "Já existe uma lista com este nome."

    def get_focusable_widgets(self):
        """
        Retorna a lista dos widgets que podem receber foco para navegação por teclado.

        Returns:
            list: Widgets focáveis na ordem do tab.
        """
        return [self.title_input, self.save_button, self.cancel_button]

