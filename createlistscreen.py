from libtui import *
from libterm import Keys
from screens import SCREENS

class CreateListScreen(TUIScreen):
    """
    Tela para criação de uma nova lista de tarefas.

    Permite ao usuário digitar o título da nova lista, validar o nome,
    e salvar a lista através do gerenciador de tarefas da aplicação.
    Caso o título já exista, exibe uma mensagem de erro.
    """
    def __init__(self)->None:
        """
        Inicializa a tela de criação de lista.

        Configura a interface com:
        - Um frame principal com título.
        - Um campo de entrada para o título da lista.
        - Um label para exibição de mensagens de erro.
        - Botões Salvar e Cancelar.
        """
        super().__init__()
        self.app = TUIApplication.current_application
        t = self.app.terminal
        width, height = t.COLUMNS, t.LINES

        self.frame = Frame(x=1, y=1, width=width, height=height, title="Criar Nova Lista")
        self.children.append(self.frame)

        self.title_input = TextInput(x=4, y=4, width=width - 8, placeholder="Título da nova lista...")
        self.children.append(self.title_input)

        # Label de erro inicialmente vazio e invisível
        self.error_label = Label("", x=4, y=6, style=TextStyle(color="RED", bright=True))
        self.children.append(self.error_label)

        # Botões Salvar e Cancelar
        self.save_button = Button("Salvar", x=4, y=height - 5, on_click=self.save_list)
        self.cancel_button = Button("Cancelar", x=15, y=height - 5, on_click=self.app.pop_screen_stack)
        self.children.extend([self.save_button, self.cancel_button])
        
        self.set_focus_by_index(0)

    def save_list(self):
        """
        Tenta salvar uma nova lista de tarefas com o título informado.

        Valida se o título não está vazio.
        Utiliza o método do gerenciador de tarefas para criar a lista.
        Exibe mensagem de erro caso o título seja duplicado.
        Fecha a tela após criação bem-sucedida.
        """
        titulo = self.title_input.text.strip()
        if not titulo:
            self.error_label.text = "O título não pode estar vazio."
            return

        created_list = self.app.taskmanager.criar_lista_de_tarefas(titulo)

        if created_list:
            self.app.pop_screen_stack()
        else:
            self.error_label.text = "Já existe uma lista com este nome."

    
    def get_focusable_widgets(self):
        """
        Retorna a lista de widgets focáveis na tela, para navegação por teclado.

        Returns:
            list: Widgets focáveis na ordem de navegação.
        """
        return [self.title_input, self.save_button, self.cancel_button]
