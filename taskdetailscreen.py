from libtui import *
from libterm import Keys
from screens import SCREENS
# --- ESTA É A CORREÇÃO ---
from libgerenciador import Tarefa, ListaDeTarefas, PRIORIDADE

class TaskDetailScreen(TUIScreen):
    """
    Uma tela de leitura que exibe todos os detalhes de uma tarefa específica.
    
    Esta tela é projetada para ser apenas informativa, mostrando todos os atributos
    de um objeto Tarefa e a lista à qual pertence. Oferece opções para
    editar a tarefa ou voltar para a tela anterior.

    Atributos:
        app (TUIApplication): A instância principal da aplicação.
        tarefa (Tarefa): O objeto da tarefa cujos detalhes estão sendo exibidos.
        lista_mae (ListaDeTarefas): O objeto da lista que contém a tarefa.
        edit_button (Button): O botão para navegar para a tela de edição.
        back_button (Button): O botão para retornar à tela anterior.
    """
    def __init__(self, data: tuple):
        """
        Inicializa a tela TaskDetailScreen.

        Args:
            data (tuple): Uma tupla contendo o objeto Tarefa a ser exibido
                          e o objeto ListaDeTarefas ao qual pertence.
        """
        tarefa, lista_mae = data
        super().__init__()
        self.app = TUIApplication.current_application
        self.tarefa = tarefa
        self.lista_mae = lista_mae
        
        t = self.app.terminal
        width, height = t.COLUMNS, t.LINES

        self.frame = Frame(x=1, y=1, width=width, height=height, title="Detalhes da Tarefa")
        self.children.append(self.frame)

        # Layout dos rótulos para melhor espaçamento e alinhamento
        y = 4
        label_x = 4
        value_x = 18 # Coluna para alinhar os valores
        
        self.children.append(Label(f"ID:", x=label_x, y=y))
        self.children.append(Label(f"{self.tarefa.id}", x=value_x, y=y))
        
        self.children.append(Label(f"Título:", x=label_x, y=y+2))
        self.children.append(Label(f"{self.tarefa.titulo}", x=value_x, y=y+2, style=TextStyle(bold=True)))

        self.children.append(Label(f"Notas:", x=label_x, y=y+4))
        self.children.append(Label(f"{self.tarefa.nota}", x=value_x, y=y+4))

        self.children.append(Label(f"Data:", x=label_x, y=y+6))
        self.children.append(Label(f"{self.tarefa.data.strftime('%d/%m/%Y')}", x=value_x, y=y+6))
        
        priority_style = TextStyle()
        if self.tarefa.prioridade == PRIORIDADE.ALTA: priority_style = TextStyle(color="RED", bright=True, bold=True)
        elif self.tarefa.prioridade == PRIORIDADE.MEDIA: priority_style = TextStyle(color="YELLOW", bright=True)
        self.children.append(Label(f"Prioridade:", x=label_x, y=y+8))
        self.children.append(Label(f"{self.tarefa.prioridade.name}", x=value_x, y=y+8, style=priority_style))

        self.children.append(Label(f"Repetição:", x=label_x, y=y+10))
        self.children.append(Label(f"{self.tarefa.repeticao.name.title()}", x=value_x, y=y+10))
        
        self.children.append(Label(f"Concluída:", x=label_x, y=y+12))
        self.children.append(Label(f"{'Sim' if self.tarefa.concluida else 'Não'}", x=value_x, y=y+12))
        
        self.children.append(Label(f"Tags:", x=label_x, y=y+14))
        self.children.append(Label(f"{', '.join(self.tarefa.tags)}", x=value_x, y=y+14))

        self.children.append(Label(f"Lista:", x=label_x, y=y+16))
        self.children.append(Label(f"{self.lista_mae.titulo}", x=value_x, y=y+16))

        # Botões
        self.edit_button = Button("Editar", x=4, y=height-5, on_click=self.edit_task)
        self.back_button = Button("Voltar", x=15, y=height-5, on_click=self.app.pop_screen_stack)
        self.children.extend([self.edit_button, self.back_button])
        
        self.set_focus_by_index(0)
    
    def edit_task(self):
        """
        Navega para a tela de edição, passando a tarefa e sua lista mãe.
        """
        self.app.push_screen_stack(SCREENS.EDIT_TASK, (self.tarefa, self.lista_mae))

    def get_focusable_widgets(self):
        """
        Retorna a lista de widgets que podem receber foco para esta tela.

        Returns:
            list: A lista de widgets focáveis.
        """
        return [self.edit_button, self.back_button]

    def process_input(self, key):
        """
        Processa as entradas para esta tela. A tecla REFRESH é usada para forçar uma
        atualização da tela ao retornar de uma tela de edição.

        Args:
            key (str): A tecla pressionada pelo utilizador.
        """
        if key == "REFRESH":
            self.app.pop_screen_stack()
            return
            
        super().process_input(key)

