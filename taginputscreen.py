from libtui import *
from libterm import Keys
from screens import SCREENS

class TagInputScreen(TUIScreen):
    """
    Uma tela que fornece um campo de texto para o usuario inserir a tag pela qual deseja filtrar.

    Esta tela serve como ponto de partida para a funcionalidade de "Visualizar por Tag",
    capturando a entrada do usuário antes de passar para a tela de opções de filtro.

    Atributos:
        app (TUIApplication): A instância principal da aplicação.
        frame (Frame): O widget de frame que desenha a borda da tela.
        prompt_label (Label): O label que indica ao usuário a utilizade do tag input.
        tag_input (TextInput): O campo de texto para a entrada da tag.
        view_button (Button): O botão para prosseguir para a tela de filtros.
        cancel_button (Button): O botão para voltar à tela anterior.
    """
    def __init__(self):
        """
        Inicializa a tela TagInputScreen, configurando todos os seus widgets filhos.
        """
        super().__init__()
        self.app = TUIApplication.current_application
        t = self.app.terminal
        width, height = t.COLUMNS, t.LINES

        self.frame = Frame(x=1, y=1, width=width, height=height, title="Visualizar por Tag")
        self.children.append(self.frame)

        self.prompt_label = Label("Digite a tag para visualizar:", x=4, y=4)
        self.children.append(self.prompt_label)
        
        self.tag_input = TextInput(x=4, y=5, width=width - 8, placeholder="Ex: universidade, trabalho, pessoal...")
        self.children.append(self.tag_input)

        self.view_button = Button("Visualizar", x=4, y=height - 5, on_click=self.view_by_tag)
        self.cancel_button = Button("Cancelar", x=19, y=height - 5, on_click=self.app.pop_screen_stack)
        self.children.extend([self.view_button, self.cancel_button])
        
        self.set_focus_by_index(0)

    def view_by_tag(self):
        """
        Inicia o fluxo de visualização para a tag inserida.
        
        Obtém o texto do campo de entrada e empurra a tela de opções de filtro,
        passando a tag inserida como contexto para a próxima tela.
        """
        tag = self.tag_input.text.strip()
        if tag:
            # Passa a tag para a tela de opções de filtro
            self.app.push_screen_stack(SCREENS.FILTER_OPTIONS, {'contexto_tag': tag})

    def get_focusable_widgets(self):
        """
        Retorna a lista de widgets que podem receber foco para esta tela.

        Returns:
            list: A lista de widgets focáveis, definindo a ordem de navegação.
        """
        return [self.tag_input, self.view_button, self.cancel_button]

