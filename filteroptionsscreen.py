from libtui import *
from libterm import Keys
from screens import SCREENS
from libgerenciador import ListaDeTarefas

class FilterOptionsScreen(TUIScreen):
    """
    Tela que apresenta opções de filtros para visualização de tarefas.

    Permite aplicar filtros por:
    - Data (todas, até hoje ou próximos 7 dias)
    - Status (todas, concluídas ou não concluídas)
    - Critério de ordenação (data ou prioridade)

    Funciona tanto no contexto de uma lista específica, de uma tag,
    ou globalmente sobre todas as tarefas.
    """
    def __init__(self, contexto_lista: ListaDeTarefas = None, contexto_tag: str = None):
        """"
        Inicializa a tela com filtros de visualização.

        Args:
            contexto_lista (ListaDeTarefas, opcional): Lista de tarefas específica para aplicar os filtros.
            contexto_tag (str, opcional): Tag específica para filtrar tarefas.
        """
        super().__init__()
        self.app = TUIApplication.current_application
        self.contexto_lista = contexto_lista
        self.contexto_tag = contexto_tag
        
        t = self.app.terminal
        width, height = t.COLUMNS, t.LINES

        titulo = "Opções de Visualização"
        if self.contexto_lista:
            titulo = f"Visualizar: {self.contexto_lista.titulo}"
        elif self.contexto_tag:
            titulo = f"Visualizar Tag: '{self.contexto_tag}'"

        self.frame = Frame(x=1, y=1, width=width, height=height, title=titulo)
        self.children.append(self.frame)
        
        y = 4
        # Seletor para filtro de data
        self.filtro_data = Selector(['Todas as Datas', 'Até Hoje', 'Próximos 7 Dias'], x=4, y=y, label="Datas:")
        
        # Seletor para filtro pelo status das tarefas
        self.filtro_status = Selector(['Todas', 'Apenas Não Concluídas', 'Apenas Concluídas'], x=4, y=y+3, label="Status:")

        
        # Seletor para ordenação dos resultados
        self.ordenacao = Selector(['Por Data (Padrão)', 'Por Prioridade'], x=4, y=y+6, label="Ordenar Por:")
        
        # Botões para aplicar ou cancelar filtros
        self.apply_button = Button("Visualizar", x=4, y=height-5, on_click=self.apply_filters)
        self.cancel_button = Button("Cancelar", x=19, y=height-5, on_click=self.app.pop_screen_stack)
        
        self.children.extend([self.filtro_data, self.filtro_status, self.ordenacao, self.apply_button, self.cancel_button])
        self.set_focus_by_index(0)
    
    def get_focusable_widgets(self):
        """
        Retorna a lista de widgets focáveis na ordem de navegação.

        Returns:
            list: Widgets focáveis.
        """
        return [self.filtro_data, self.filtro_status, self.ordenacao, self.apply_button, self.cancel_button]


    def apply_filters(self):
        """
        Aplica os filtros selecionados e abre a tela de visualização das tarefas.

        Converte os valores dos seletores em parâmetros internos e os passa
        para a tela 'TaskViewScreen', que fará a busca.
        """

        # Dicionarios para converter texto UI em parâmetros internos
        map_data = {'Todas as Datas': "TODAS", 'Até Hoje': "HOJE", 'Próximos 7 Dias': "SETE_DIAS"}
        map_ordem = {'Por Data (Padrão)': "DATA", 'Por Prioridade': "PRIORIDADE"}
        map_status = {'Todas': "TODAS", 'Apenas Não Concluídas': "INCOMPLETAS", 'Apenas Concluídas': "COMPLETAS"}

        
        filtro_data_val = map_data[self.filtro_data.get_selected_value()]
        filtro_status_val = map_status[self.filtro_status.get_selected_value()]
        ordenacao_val = map_ordem[self.ordenacao.get_selected_value()]

        # Passa os PARÂMETROS de filtro para a tela de visualização, não os resultados
        dados_para_view = {
            'titulo': self.frame.title,
            'filtro_tempo': filtro_data_val,
            'filtro_status': filtro_status_val,
            'ordenacao': ordenacao_val,
            'contexto_lista': self.contexto_lista,
            'contexto_tag': self.contexto_tag
        }
        # Navega para a TaskViewScreen com os dados para a busca
        self.app.push_screen_stack(SCREENS.TASK_VIEW, dados_para_view)

