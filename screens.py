from enum import Enum

class SCREENS(Enum):
    """
    Define constantes para todos os tipos de telas na aplicação.
    
    Esta enumeração é usada para evitar o uso de "números mágicos" ao trabalhar
    com a pilha de telas, tornando o código mais legível e fácil de manter. Cada
    valor representa uma tela única.
    """
    LIST_SELECTION = 0      # A tela principal que exibe todas as listas de tarefas.
    CREATELIST = 1          # A tela para criar uma nova lista de tarefas.
    EDIT_LIST = 2           # A tela para editar o nome de uma lista de tarefas existente.
    CREATETASK = 4          # A tela para criar uma nova tarefa dentro de uma lista.
    TASK_DETAIL = 5         # A tela que exibe todos os detalhes de uma única tarefa.
    EDIT_TASK = 6           # A tela para editar uma tarefa existente.
    SEARCH_INPUT = 7        # A tela para o usuario inserir um termo de busca global. (Não utilizado atualmente)
    SEARCH_RESULTS = 8      # A tela onde o usuario escolhe as opções de visualização e filtro.
    FILTER_OPTIONS = 9      # A tela onde o usuario escolhe as opções de visualização e filtro.
    TASK_VIEW = 10          # A tela genérica que exibe uma lista de tarefas filtrada e ordenada.
    TAG_INPUT = 11          # A tela para o utilizador inserir uma tag para visualização.
