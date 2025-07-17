# searchinputscreen.py
from libtui import *
from libterm import Keys
from screens import SCREENS

class SearchInputScreen(TUIScreen):
    """
    Uma tela que fornece um campo de texto para o usuário inserir um termo de busca.
    
    Esta tela é usada para capturar a string que será utilizada para procurar tarefas
    em todo o sistema.

    Atributos:
        app (TUIApplication): A instância principal da aplicação.
        frame (Frame): O widget de frame que desenha a borda da tela.
        prompt_label (Label): O texto que instrui o usuário.
        search_input (TextInput): O campo de texto para a entrada do termo de busca.
        search_button (Button): O botão que inicia a busca.
        cancel_button (Button): O botão para voltar à tela anterior.
    """
    def __init__(self):
        """
        Inicializa a tela SearchInputScreen, configurando todos os seus widgets filhos.
        """
        super().__init__()
        self.app = TUIApplication.current_application
        t = self.app.terminal
        width, height = t.COLUMNS, t.LINES

        self.frame = Frame(x=1, y=1, width=width, height=height, title="Buscar Tarefas")
        self.children.append(self.frame)

        self.prompt_label = Label("Digite o termo para buscar:", x=4, y=4)
        self.children.append(self.prompt_label)
        
        self.search_input = TextInput(x=4, y=5, width=width - 8, placeholder="Buscar por título, nota ou tag...")
        self.children.append(self.search_input)

        self.search_button = Button("Buscar", x=4, y=height - 5, on_click=self.perform_search)
        self.cancel_button = Button("Cancelar", x=15, y=height - 5, on_click=self.app.pop_screen_stack)
        self.children.extend([self.search_button, self.cancel_button])
        
        self.set_focus_by_index(0)

    def perform_search(self):
        """
        Executa a busca com o termo inserido pelo usuário.
        
        Este método obtém o texto do campo de entrada, chama o método de busca do
        gestor de tarefas e, em seguida, empurra a tela de visualização de tarefas
        com os resultados encontrados.
        """
        termo = self.search_input.text.strip()
        if termo:
            resultados = self.app.taskmanager.buscar_tarefas(termo)
            # Passa os resultados e o termo de busca para a próxima tela
            dados = {'resultados': resultados, 'termo_busca':termo}
            self.app.push_screen_stack(SCREENS.SEARCH_RESULTS, dados)

    def get_focusable_widgets(self):
        """
        Retorna a lista de widgets que podem receber foco para esta tela.

        Returns:
            list: A lista de widgets focáveis, definindo a ordem de navegação.
        """
        return [self.search_input, self.search_button, self.cancel_button]
