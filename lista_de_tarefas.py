from libtui import *
from libterm import Terminal, Keys
from libgerenciador import GerenciadorTarefas, ListaDeTarefas, Tarefa
from screens import SCREENS
from listselectionscreen import ListSelectionScreen
from createlistscreen import CreateListScreen
from editlistscreen import EditListScreen
from createtaskscreen import CreateTaskScreen
from edittaskscreen import EditTaskScreen
from taskdetailscreen import TaskDetailScreen
from filteroptionsscreen import FilterOptionsScreen
from taskviewscreen import TaskViewScreen
from taginputscreen import TagInputScreen
from searchinputscreen import SearchInputScreen
from searchresultscreen import SearchResultsScreen

class TodoApp(TUIApplication):
    """
    A classe principal da aplicação que gerencia as telas e a lógica de negócios.
    
    Esta classe inicializa a aplicação, gerencia a pilha de navegação de telas,
    e contém o loop principal do programa.

    Atributos:
        screen_stack (List[TUIScreen]): Uma pilha para gerirenciar as telas em uso.
        terminal (Terminal): Uma instância do controlador de terminal.
        taskmanager (GerenciadorTarefas): Uma instância do gerenciador de dados das tarefas.
        current_screen (TUIScreen): A tela em que o usuario está atualmente.
    """
    def build(self):
        """
        Este método é chamado uma vez durante a inicialização para configurar o terminal,
        instanciar o gerenciador de tarefas e colocar a tela inicial para a pilha de navegação.
        """
        self.screen_stack = []
        self.terminal.hide_cursor()
        self.taskmanager = GerenciadorTarefas()
        self.push_screen_stack(SCREENS.LIST_SELECTION)

    def push_screen_stack(self, screen_type: SCREENS, data=None):
        """
        Cria e adiciona uma nova tela à pilha, tornando-a a tela ativa.

        Args:
            screen_type (SCREENS): O tipo de tela a ser criado, a partir do enum SCREENS.
            data (any, optional): Dados opcionais a serem passados para o construtor da nova tela.
        """
        new_screen = None
        if screen_type == SCREENS.LIST_SELECTION: new_screen = ListSelectionScreen()
        elif screen_type == SCREENS.CREATELIST: new_screen = CreateListScreen()
        elif screen_type == SCREENS.SEARCH_INPUT: new_screen = SearchInputScreen()
        elif screen_type == SCREENS.TAG_INPUT: new_screen = TagInputScreen()
        elif screen_type == SCREENS.EDIT_LIST:
            if isinstance(data, ListaDeTarefas): new_screen = EditListScreen(data)
        elif screen_type == SCREENS.FILTER_OPTIONS:
            if data is None: data = {}
            new_screen = FilterOptionsScreen(contexto_lista=data.get('contexto_lista'), contexto_tag=data.get('contexto_tag'))
        elif screen_type == SCREENS.TASK_VIEW:
            if isinstance(data, dict):
                new_screen = TaskViewScreen(data['titulo'], data['filtro_tempo'],
                                            data['filtro_status'], data['ordenacao'],
                                            data['contexto_lista'], data['contexto_tag'])
        elif screen_type == SCREENS.CREATETASK:
             if isinstance(data, ListaDeTarefas): new_screen = CreateTaskScreen(data)
        elif screen_type == SCREENS.TASK_DETAIL:
            if isinstance(data, tuple): new_screen = TaskDetailScreen(data)
        elif screen_type == SCREENS.EDIT_TASK:
            if isinstance(data, tuple): new_screen = EditTaskScreen(data)

        elif screen_type == SCREENS.SEARCH_RESULTS:
            if isinstance(data, dict):
                new_screen = SearchResultsScreen(resultados=data.get('resultados'), termo_busca=data.get('termo_busca'))

        if new_screen:
            self.screen_stack.append(new_screen)
            self.current_screen = self.screen_stack[-1]
    
    def pop_screen_stack(self):
        """
        Remove a tela do topo da pilha e torna a tela anterior.
        
        Se a pilha ficar vazia, a aplicação é encerrada. Após remover uma tela, envia um
        sinal "REFRESH" para a nova tela, permitindo que ele atualize os seus dados.
        """
        self.screen_stack.pop()
        if not self.screen_stack: self.quit_app()
        else:
            self.current_screen = self.screen_stack[-1]
            if hasattr(self.current_screen, 'process_input'): self.current_screen.process_input("REFRESH")

    def quit_app(self):
        """
        Executa os procedimentos de limpeza e encerra a aplicação.
        
        Isso inclui limpar o terminal, mostrar o cursor, guardar os dados e
        restaurar o modo normal do terminal.
        """
        self.terminal.clear_screen()
        self.terminal.move_cursor(1, 1)
        self.terminal.show_cursor()
        self.taskmanager.save_database()
        self.terminal.disable_raw_mode()
        exit()

if __name__ == "__main__":
    app = TodoApp()
    app.run()

