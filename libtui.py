"""
Mini-framework para construção de aplicações em modo texto (TUI) no terminal,
com suporte a widgets, navegação via teclado, estilos visuais e diálogos modais.
API levemente inspirada na API do framework Kivy. Ainda em estágio inicial de
desenvolvimento.

Funcionalidades principais:
- Gerenciamento de telas (screen navigation stack).
- Widgets básicos: Label, Button, TextInput, DateInput, IntInput, Selector, Checkbox, Frame.
- Componentes de lista (VerticalList) com rolagem.
- Diálogos modais: AlertDialog e ConfirmationDialog.
- Sistema de foco entre widgets, navegação com TAB, SHIFT+TAB, setas, Enter e ESC.
- Suporte a estilos de texto com cores, negrito, sublinhado, itálico, tachado e brilho.

Dependências:
- Somente bibliotecas padrão do Python e a libterm.py.
"""

from libterm import Terminal
from typing import List
import time
import datetime
from dataclasses import dataclass
from libterm import Keys


@dataclass
class TextStyle():
    """
    Representa o estilo visual de um texto.

    Atributos:
        bold (bool): Negrito.
        italic (bool): Itálico.
        underline (bool): Sublinhado.
        color (str): Cor do texto (ex.: 'BLACK', 'RED', 'WHITE').
        bright (bool): Alto brilho (texto mais forte).
        strikethrough (bool): Texto "riscado".
    """
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: str = "WHITE"
    bright: bool = False
    strikethrough: bool = False


def apply_style(style: TextStyle)->None:
    """
    Aplica o estilo de texto ao terminal atual.

    Args:
        style (TextStyle): Objeto contendo configurações de estilo.
    """
    terminal:TUIApplication = TUIApplication.current_application.terminal
    terminal.reset_text_style()

    terminal.set_text_style(
        bold=style.bold,
        italic=style.italic,
        underline=style.underline,
        color=style.color,
        bright=style.bright,
        strikethrough=style.strikethrough
    )

class Widget():
    '''Classe abstrata que serve como base para criacao de
    componentes que renderizam na tela, como botoes e labels'''
    def __init__(self):
        self.x: int = None
        self.y: int = None
        self.width: int = None
        self.height: int = None
        self.is_focused:bool = False
        self.is_focusable: bool = True

    def render(self):
        pass

    def process_input(self, key):
        if not key:
            return




class TUIScreen():
    """
    Classe base para representar uma tela (screen) na interface TUI.

    Cada tela possui uma lista de widgets (`children`), gerencia o ciclo de
    foco entre eles e trata eventos de entrada.

    Métodos principais:
    - render(): Desenha todos os widgets da tela.
    - process_input(): Processa teclas para navegação e interação.
    - move_focus(): Alterna foco entre widgets focáveis.
    """
    def __init__(self, *args, **kwargs):
        """
        Inicializa a tela, criando a lista de widgets filhos.
        """
        self.children: List[Widget] = []

    def build(self, *args, **kwargs):
        """
        Método abstrato para construção da tela.

        Deve ser sobrescrito na subclasse para adicionar widgets
        à lista `self.children` e configurar a interface.
        """
        raise NotImplementedError()
    
    def render(self):
        """
        Renderiza todos os widgets presentes na tela.
        """
        for child in self.children:
            child.render()

    def get_focusable_widgets(self):
        """
        Retorna uma lista de widgets que podem receber foco.

        Returns:
            List[Widget]: Lista de widgets com is_focusable == True.
        """
        return [w for w in self.children if w.is_focusable]

    def get_focused_widget(self):
        """
        Obtém o widget atualmente focado.

        Returns:
            Widget | None: Widget focado, ou None se nenhum estiver focado.
        """
        for w in self.get_focusable_widgets():
            if w.is_focused:
                return w

    def set_focus_by_index(self, index):
        """
        Define o foco para o widget na posição `index` da lista de focáveis.

        Args:
            index (int): Índice do widget na lista de focáveis.
        """
        focusable_widgets = self.get_focusable_widgets()
        if not focusable_widgets:
            return

        index_to_focus = max(0,min(index, len(focusable_widgets) - 1))

        current_focused = self.get_focused_widget()
        if current_focused:
            current_focused.is_focused = False

        focusable_widgets[index_to_focus].is_focused = True
        self.focus_index = index_to_focus


    def move_focus(self, direction: int):
        """
        Move o foco para o próximo ou anterior widget focável.

        Args:
            direction (int): +1 para próximo, -1 para anterior.
        """
        focusable_widgets = self.get_focusable_widgets()
        if not focusable_widgets:
            return

        current_focused_widget = self.get_focused_widget()
        try:
            current_index = focusable_widgets.index(current_focused_widget)
            new_index = (current_index + direction) % len(focusable_widgets)
        except ValueError:
            new_index = 0 if direction == 1 else -1

        self.set_focus_by_index(new_index)
   
    def _find_next_widget_in_direction(self, direction: str) -> Widget | None:
        """
        Encontra o widget mais próximo na direção especificada (UP, DOWN, LEFT, RIGHT).

        Args:
            direction (str): A direção da navegação (Keys.UP, etc.).

        Returns:
            Widget | None: O widget mais próximo encontrado, ou None se nenhum for encontrado.
        """
        current_widget = self.get_focused_widget()
        if not current_widget: return None

        focusable = [w for w in self.get_focusable_widgets() if w is not current_widget]
        candidates = []

        for widget in focusable:
            dx = widget.x - current_widget.x
            dy = widget.y - current_widget.y

            if direction == Keys.DOWN and dy > 0: candidates.append((dy, dx, widget))
            elif direction == Keys.UP and dy < 0: candidates.append((dy, dx, widget))
            elif direction == Keys.RIGHT and dx > 0: candidates.append((dx, dy, widget))
            elif direction == Keys.LEFT and dx < 0: candidates.append((dx, dy, widget))
        
        if not candidates: return None

        if direction in [Keys.DOWN, Keys.UP]:
            candidates.sort(key=lambda c: (abs(c[1]), abs(c[0])))
        elif direction in [Keys.LEFT, Keys.RIGHT]:
            candidates.sort(key=lambda c: (abs(c[1]), abs(c[0])))
            
        return candidates[0][2]
    def process_input(self, key):
        """
        Processa a entrada de teclado da tela.

        - Primeiramente, delega a entrada para o widget atualmente focado.
        - Se não for tratada, executa comandos de navegação padrão (TAB, SHIFT+TAB, ESC).

        Args:
            key (str): Tecla pressionada.
        """
        # Tenta processar no widget focado
        focused_widget = self.get_focused_widget()
        if focused_widget:
            if focused_widget.process_input(key):
                return #  A tecla foi tratada pelo widget



        if key in (Keys.UP, Keys.DOWN, Keys.LEFT, Keys.RIGHT):
            next_widget = self._find_next_widget_in_direction(key)
            if next_widget:
                focusable = self.get_focusable_widgets()
                try:
                    idx = focusable.index(next_widget)
                    self.set_focus_by_index(idx)
                except:
                    pass

        # Processa teclas de navegação da interface
        if key == Keys.TAB:
            self.move_focus(1) # Próximo widget
        elif key == Keys.SHIFT_TAB:
            self.move_focus(-1) # Widget anterior
        elif key == Keys.ESC:
            # Por padrão, ESC remove a tela atual da pilha de navegacao de telas (volta para a tela anterior)
            app = TUIApplication.current_application
            app.pop_screen_stack()

    


class TUIApplication():
    """
    Classe principal da aplicação TUI. Gerencia o ciclo de vida da aplicação,
    controle de telas e entrada de teclado.

    Atributos:
        current_application (TUIApplication): Instância global atual da aplicação.
        terminal (Terminal): Interface com o terminal (libterm).
        current_screen (TUIScreen): Tela atualmente ativa.
    """
    current_application = None
    def __init__(self):
        """
        Inicializa a aplicação TUI, configurando o terminal em modo raw
        e definindo a tela inicial através do método build().
        """
        self.terminal: Terminal = Terminal()
        self.terminal.enable_raw_mode()
        self.current_screen = None
        TUIApplication.current_application = self
        self.build()


    def render(self):
        """
        Limpa o terminal e desenha a tela atual.
        """
        self.terminal.clear_screen()
        self.current_screen.render()
    
    def process_input(self, key):
        """
        Encaminha o input para a tela atual.

        Args:
            key (str): Tecla pressionada.
        """
        self.current_screen.process_input(key)


    def build(self):
        """
        Deve ser sobrescrito nas subclasses para construir a tela inicial
        e definir a lógica de inicialização da aplicação.
        """
        raise NotImplementedError("O método build() deve ser implementado pela subclasse.")



    def run(self):
        """
        Loop principal da aplicação. Aguarda eventos de teclado, 
        processa entradas e atualiza a renderização.
        """
        self.render()

        while True:
            key = self.terminal.read_key()

            if not key:
                continue

            self.process_input(key)
            self.render()


class Label(Widget):
    """
    Widget de texto simples para exibir uma string na tela.

    Suporta estilo (cores, negrito, etc.) e posição. Atualmente, a quebra
    de linha automatica (line wrap) ainda não está implementada.

    Args:
        text (str): Texto a ser exibido.
        x (int): Posição X na tela (coluna).
        y (int): Posição Y na tela (linha).
        line_wrap (bool): Se True, quebra linhas automaticamente (não implementado ainda).
        style (TextStyle): Estilo do texto (opcional).
    """
    def __init__(self, text="{empty label}", x=1, y=1, line_wrap=False, style=None):
        super().__init__()
        if type(style) == TextStyle:
            self.style = style
        else:
            self.style = TextStyle()

        self.text: str = text
        self.width: int = len(self.text)
        self.height = 1 if not line_wrap else self.calculate_height()
        self.x = x
        self.y = y
        self.focused_style = TextStyle(True, bright=True, color="YELLOW")
        self.is_focusable = False


    def get_current_style(self):
        """
        Retorna o estilo atual, levando em consideração o foco.

        Returns:
            TextStyle: O estilo a ser aplicado.
        """
        if self.is_focused and self.focused_style:
            return self.focused_style
        return self.style

    def calculate_height(self):
        """
        Calcula a altura da label caso o line_wrap esteja habilitado.

        Returns:
            int: Altura em linhas. (Por enquanto, sempre 1)
        """
        return 1  # TODO: Implementar line wrap

    def render(self):
        """
        Desenha o texto na tela na posição especificada.
        """
        terminal = TUIApplication.current_application.terminal

        apply_style(self.get_current_style())

        terminal.move_cursor(self.x, self.y)
        terminal.putstr(self.text)


class Frame(Widget):
    """
    Widget de moldura com bordas desenhadas, opcionalmente com título.

    Serve para agrupar visualmente outros widgets.

    Args:
        x (int): Posição X (coluna).
        y (int): Posição Y (linha).
        width (int): Largura da moldura.
        height (int): Altura da moldura.
        title (str): Texto opcional exibido no topo da moldura.
        frame_style (TextStyle): Estilo das bordas.
        title_style (TextStyle): Estilo do título.
    """
    def __init__(self, x=1, y=1, width=10, height=5, title=None, 
                 frame_style=None, title_style=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title

        self.frame_style = frame_style or TextStyle()
        self.title_style = title_style or TextStyle(bold=True)
        self.is_focusable = False

    def render(self):
        """
        Desenha a moldura na tela, incluindo título se fornecido.
        """
        terminal = TUIApplication.current_application.terminal

        # Desenha a borda
        terminal.set_text_style(self.frame_style.bold, self.frame_style.italic,
                                self.frame_style.underline, self.frame_style.color,
                                self.frame_style.bright)

        # Parte de cima da borda
        terminal.move_cursor(self.x, self.y)
        terminal.putstr('┌' + '─' * (self.width - 2) + '┐')

        # Laterais
        for i in range(1, self.height - 1):
            terminal.move_cursor(self.x, self.y + i)
            terminal.putstr('│' + ' ' * (self.width - 2) + '│')

        # Parte de baixo da borda
        terminal.move_cursor(self.x, self.y + self.height - 1)
        terminal.putstr('└' + '─' * (self.width - 2) + '┘')

        # Desenha o titulo
        if self.title:
            terminal.set_text_style(self.title_style.bold, self.title_style.italic,
                                    self.title_style.underline, self.title_style.color,
                                    self.title_style.bright)

            title_text = f' {self.title} '
            title_x = self.x + max(2, (self.width - len(title_text)) // 2)

            terminal.move_cursor(title_x, self.y)
            terminal.putstr(title_text)



class Button(Label):
    """
    Widget de botão.

    Herda de Label e adiciona suporte a clique via ENTER.

    Args:
        text (str): Texto exibido no botão.
        x (int): Posição X no terminal.
        y (int): Posição Y no terminal.
        on_click (callable): Função chamada quando o botão é pressionado.
        style (TextStyle): Estilo visual opcional.

    Atributos:
        on_click (callable): Função callback para clique.
    """
    def __init__(self, text="Button", x=1, y=1, on_click=None, style=None):
        super().__init__(text=text, x=x, y=y, style=style)
        self.width = len(text) + 4
        self.height = 3
        self.on_click = on_click
        self.is_focusable = True

        self.focused_style = TextStyle(True, bright=True, color="YELLOW")

    def render(self):
        """
        Renderiza o botão com bordas, texto centralizado
        e destaque se estiver focado.
        """
        terminal = TUIApplication.current_application.terminal


        apply_style(self.get_current_style())

        terminal.move_cursor(self.x, self.y)
        terminal.putstr('┌' + '─' * (self.width - 2) + '┐')

        terminal.move_cursor(self.x, self.y + 1)
        padding = (self.width - 2 - len(self.text)) // 2
        text_line = (
            '│' +
            ' ' * padding +
            self.text +
            ' ' * (self.width - 2 - padding - len(self.text)) +
            '│'
        )
        terminal.putstr(text_line)

        terminal.move_cursor(self.x, self.y + 2)
        terminal.putstr('└' + '─' * (self.width - 2) + '┘')

    def process_input(self, key):
        """
        Processa entrada de teclado. Executa o callback on_click
        quando ENTER é pressionado.

        Args:
            key (str): Tecla pressionada.

        Returns:
            str | None: 'enter' se foi pressionado, None caso contrário.
        """
        if not self.is_focused:
            return

        if key == Keys.ENTER and self.is_focused:
            if self.on_click:
                self.on_click()
            return 'enter'




class TextInput(Label):
    """
    Um widget de campo de texto que permite ao usuário inserir uma única linha de texto.

    Atributos:
        width (int): A largura total do widget, incluindo os parênteses.
        placeholder (str): O texto a ser exibido quando o campo está vazio.
        focused_style (TextStyle): O estilo a ser aplicado quando o widget está focado.
    """
    def __init__(self, x=1, y=1, width=20, placeholder="", initial_text="", style=None):
        """
        Inicializa o widget TextInput.

        Args:
            x (int): A coordenada x inicial do widget.
            y (int): A coordenada y inicial do widget.
            width (int): A largura total do widget.
            placeholder (str): Texto a ser exibido quando o campo está vazio.
            initial_text (str): O texto inicial a ser exibido no campo.
            style (TextStyle): O estilo de texto base para o widget.
        """
        super().__init__(text=initial_text, x=x, y=y, style=style)
        self.width = width
        self.placeholder = placeholder
        self.focused_style = TextStyle(True, bright=True, color="GREEN")

    def render(self):
        """
        Desenha o campo de texto no terminal, incluindo o texto ou placeholder e o cursor.
        """
        terminal = TUIApplication.current_application.terminal

        display_text = self.text if self.text else self.placeholder

        style = TextStyle(**vars(self.style))
        if not self.text:
            style.italic = True
            style.color = "WHITE"

        apply_style(self.get_current_style())

        terminal.move_cursor(self.x, self.y)
        terminal.putstr('[')

        content = display_text[:self.width - 2]
        terminal.putstr(content.ljust(self.width - 2))

        terminal.putstr(']')


        if self.is_focused:
            cursor_pos = self.x + 1 + len(self.text)
            if cursor_pos >= self.x + self.width - 1:
                cursor_pos = self.x + self.width - 2
            terminal.move_cursor(cursor_pos, self.y)

    def process_input(self, key):
        """
        Processa a entrada do teclado para adicionar ou remover caracteres do campo de texto.

        Args:
            key (str): A tecla pressionada pelo utilizador.

        Returns:
            bool: Retorna sempre False para indicar que a tecla não deve impedir a navegação (Tab, etc.).
        """
        if not self.is_focused or not key:
            return False
        if key == Keys.BACKSPACE:
            self.text = self.text[:-1]
        if len(key) > 1:
            return False
        elif key.isprintable() and len(self.text) < self.width - 2:
            self.text += key
        return False


class DateInput(Label):
    """
    Um widget interativo para selecionar uma data (dia, mês, ano).

    Atributos:
        day (int): O dia selecionado.
        month (int): O mês selecionado.
        year (int): O ano selecionado.
        label (str): O texto a ser exibido ao lado da data.
        focus_index (int): O componente da data atualmente em foco (0=dia, 1=mês, 2=ano).
        _being_edited (bool): Uma flag que indica se o modo de edição (setinhas para cima/baixo) está ativo.
    """
    n_dias_mes = [31,28,31,30,31,30,31,31,30,31,30,31]
    siglas_mes = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]

    def __init__(self, label="Date:", x=1, y=1, date=None, style=None):
        """
        Inicializa o widget DateInput.

        Args:
            label (str): O rótulo a ser exibido.
            x (int): A coordenada x inicial.
            y (int): A coordenada y inicial.
            date (tuple): Uma tupla opcional (dia, mês, ano) para definir a data inicial.
            style (TextStyle): O estilo de texto base.
        """
        super().__init__(text=label, x=x, y=y, style=style)
        today = datetime.datetime.today()
        self.day = today.day
        self.month = today.month
        self.year = today.year

        if date:
            self.day, self.month, self.year = date

        self.is_focusable = True
        self.focused_style = TextStyle(bold=True, bright=True, color="WHITE")

        self.label = label
        self.focus_index = 0  # 0 = day, 1 = month, 2 = year
        self._being_edited = False

    def _bissexto(self, year):
        """Verifica se um determinado ano é bissexto."""
        return (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))

    def _max_day_in_month(self, month, year):
        """Retorna o número máximo de dias para um determinado mês e ano."""
        if month == 2:
            return 29 if self._bissexto(year) else 28
        return self.n_dias_mes[month - 1]

    def _format_text(self):
        """Formata a data para exibição, destacando a parte em foco."""
        day_str = f"{self.day:02d}"
        month_str = f"{self.month:02d}"
        year_str = f"{self.year:04d}"

        if self.is_focused and not self._being_edited:
            if self.focus_index == 0:
                day_str = f"[{day_str}]"
            elif self.focus_index == 1:
                month_str = f"[{month_str}]"
            elif self.focus_index == 2:
                year_str = f"[{year_str}]"

        return f"{self.label} {day_str}/{month_str}/{year_str}"

    def render(self):
        """Desenha o widget de data, incluindo indicadores de edição se estiver ativo."""
        self.text = self._format_text()
        super().render()

        if self.is_focused and self._being_edited:
            terminal = TUIApplication.current_application.terminal
            base_x = self.x + len(self.label) + 1
            pos_map = {0: base_x, 1: base_x + 3, 2: base_x + 6}
            col = pos_map[self.focus_index]
            terminal.move_cursor(col, self.y - 1)
            terminal.putstr("▲")
            terminal.move_cursor(col, self.y + 1)
            terminal.putstr("▼")

    def process_input(self, key):
        """
        Processa a entrada do teclado para navegar entre os componentes da data e alterar seus valores.

        Args:
            key (str): A tecla pressionada pelo utilizador.

        Returns:
            bool: True se a tecla foi processada pelo widget, False caso contrário.
        """
        if not self.is_focused:
            return False

        if self._being_edited:
            if key == Keys.UP:
                if self.focus_index == 0:  # Dia
                    self.day += 1
                    max_day = self._max_day_in_month(self.month, self.year)
                    if self.day > max_day:
                        self.day = 1
                elif self.focus_index == 1:  # Mês
                    self.month += 1
                    if self.month > 12:
                        self.month = 1
                    # Ajustando o dia caso ele seja superior ao máximo do mês selecionado
                    max_day = self._max_day_in_month(self.month, self.year)
                    if self.day > max_day:
                        self.day = max_day
                elif self.focus_index == 2:  # Ano
                    self.year += 1
                    # Ajustando o dia caso ele seja superior ao máximo do mês selecionado (Só acontece em fevereiro de ano bissexto)
                    max_day = self._max_day_in_month(self.month, self.year)
                    if self.day > max_day:
                        self.day = max_day
                return True

            elif key == Keys.DOWN:
                if self.focus_index == 0:
                    self.day -= 1
                    if self.day < 1:
                        self.day = self._max_day_in_month(self.month, self.year)
                elif self.focus_index == 1:
                    self.month -= 1
                    if self.month < 1:
                        self.month = 12
                    max_day = self._max_day_in_month(self.month, self.year)
                    if self.day > max_day:
                        self.day = max_day
                elif self.focus_index == 2:
                    self.year -= 1
                    if self.year < 1:
                        self.year = 1  # keep year positive
                    max_day = self._max_day_in_month(self.month, self.year)
                    if self.day > max_day:
                        self.day = max_day
                return True

            elif key == Keys.ESC:
                self._being_edited = False
                return True

            elif key == Keys.ENTER:
                self._being_edited = False
                return True

            else:
                return False

        else:
            if key == Keys.LEFT:
                self.focus_index = (self.focus_index - 1) % 3
                return True
            elif key == Keys.RIGHT:
                self.focus_index = (self.focus_index + 1) % 3
                return True
            elif key == Keys.ENTER:
                self._being_edited = True
                return True
            return False

    def get_date(self):
        """
        Retorna a data selecionada formatada como uma string ISO (AAAA-MM-DD).
        """
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"


class IntInput(Label):
    """
    Um widget interativo para selecionar um valor inteiro, opcionalmente dentro de um intervalo.

    Atributos:
        value (int): O valor inteiro atual.
        min (int | None): O valor mínimo permitido.
        max (int | None): O valor máximo permitido.
        format_str (str): A string de formatação para exibir o número.
        _being_edited (bool): Sinalizador para o modo de edição ativo.
    """
    def __init__(self, value=0, min=None, max=None, x=1, y=1, format_str="01d", style=None):
        """
        Inicializa o widget IntInput.

        Args:
            value (int): O valor inicial.
            min_val (int): O valor mínimo permitido.
            max_val (int): O valor máximo permitido.
            x (int): A coordenada x inicial.
            y (int): A coordenada y inicial.
            format_str (str): A string de formatação para o valor.
            style (TextStyle): O estilo de texto base.
        """
        super().__init__(f"{value:{format_str}}", x, y, style=style)
        self.value = value
        self.min = min
        self.max = max
        self.format_str = format_str
        self.is_focusable = True
        self.focused_style = TextStyle(bold=True, bright=True, color="WHITE")
        self._being_edited = False

    def render(self):
        """Desenha o valor inteiro e os indicadores de edição, se ativos."""
        super().render()
        terminal = TUIApplication.current_application.terminal

        if self._being_edited:
            terminal.move_cursor(self.x, self.y - 1)
            terminal.putstr("▲")
            terminal.move_cursor(self.x, self.y + 1)
            terminal.putstr("▼")

    def update_text(self):
        """Atualiza o texto exibido para o valor atual."""
        self.text = f"{self.value:{self.format_str}}"

    def process_input(self, key):
        """
        Processa a entrada do teclado para alterar o valor inteiro.

        Args:
            key (str): A tecla pressionada pelo utilizador.

        Returns:
            bool: True se a tecla foi processada, False caso contrário.
        """
        if not self.is_focused:
            return False

        if self._being_edited:
            if key == Keys.UP:
                self.value += 1
                if self.max is not None and self.value > self.max:
                    self.value = self.max
                self.update_text()
                return True
            elif key == Keys.DOWN:
                self.value -= 1
                if self.min is not None and self.value < self.min:
                    self.value = self.min
                self.update_text()
                return True
            elif key == Keys.ENTER or key == Keys.ESC:
                self._being_edited = False
                return True
            else:
                return True

        else:
            if key == Keys.ENTER:
                self._being_edited = True
                return True

        return False




class Selector(Label):
    """
    Um widget de seleção que permite ao usuário escolher uma opção de uma lista.

    Atributos:
        options (List[str]): A lista de strings a serem exibidas como opções.
        selected_index (int): O índice da opção atualmente selecionada.
        label (str): O rótulo a ser exibido ao lado do seletor.
        _being_edited (bool): flag que indica s eo modo de edição está ativo.
    """
    def __init__(self, options=None, selected_index=0, x=1, y=1, label="", style=None):
        """
        Inicializa o widget Selector.

        Args:
            options (List[str]): A lista de opções disponíveis.
            selected_index (int): O índice da opção selecionada inicialmente.
            x (int): A coordenada x inicial.
            y (int): A coordenada y inicial.
            label (str): O rótulo a ser exibido.
            style (TextStyle): O estilo de texto base.
        """
        self.options = options or ["Option 1", "Option 2", "Option 3"]
        self.selected_index = max(0, min(selected_index, len(self.options) - 1))
        
        self.label = label
        
        super().__init__(text="", x=x, y=y, style=style)
        
        self.is_focusable = True
        self.focused_style = TextStyle(bold=True, bright=True, color="WHITE")
        self._being_edited = False
        self.update_text()

    def _format_text(self):
        """Formata o texto de exibição, incluindo o rótulo e a opção selecionada."""
        selected_option = self.options[self.selected_index]
        
        display_option = f"[{selected_option}]" if self.is_focused else selected_option
        
        return f"{self.label} {display_option}"

    def render(self):
        """Desenha o seletor e os indicadores de edição, se ativos."""
        self.update_text()
        super().render()
        
        terminal = TUIApplication.current_application.terminal
        if self._being_edited:
            arrow_x = self.x + len(self.label) + 2 
            terminal.move_cursor(arrow_x, self.y - 1)
            terminal.putstr("▲")
            terminal.move_cursor(arrow_x, self.y + 1)
            terminal.putstr("▼")

    def update_text(self):
        """Atualiza o texto exibido para refletir a seleção atual."""
        self.text = self._format_text()

    def get_selected_value(self):
        """
        Retorna a string da opção atualmente selecionada.

        Returns:
            str: O valor do item selecionado.
        """
        return self.options[self.selected_index]

    def get_selected_index(self):
        """
        Retorna o índice da opção atualmente selecionada.

        Returns:
            int: O índice do item selecionado.
        """
        return self.selected_index

    def process_input(self, key):
        """
        Processa a entrada do teclado para navegar pelas opções.

        Args:
            key (str): A tecla pressionada pelo utilizador.

        Returns:
            bool: True se a tecla foi processada, False caso contrário.
        """
        if not self.is_focused:
            return False

        if self._being_edited:
            if key == Keys.UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
                self.update_text()
                return True
            elif key == Keys.DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
                self.update_text()
                return True
            elif key == Keys.ENTER or key == Keys.ESC:
                self._being_edited = False
                return True
            else:
                return True
        else:
            if key == Keys.ENTER:
                self._being_edited = True
                return True
        return False


class Checkbox(Label):
    """
    Um widget que representa uma caixa de seleção que pode ser marcada ou desmarcada.

    Atributos:
        label (str): O texto descritivo exibido ao lado da caixa.
        checked (bool): O estado atual da caixa de seleção (marcada ou não).
    """
    def __init__(self, label="Checkbox", x=1, y=1, checked=False, style=None):
        """
        Inicializa o widget Checkbox.

        Args:
            label (str): O texto descritivo.
            x (int): A coordenada x inicial.
            y (int): A coordenada y inicial.
            checked (bool): O estado inicial da caixa.
            style (TextStyle): O estilo de texto base.
        """
        super().__init__(text=label, x=x, y=y, style=style)
        self.label = label
        self.checked = checked
        self.is_focusable = True
        self.focused_style = TextStyle(True, bright=True, color="WHITE")
        display_text = self._format_text()

    def _format_text(self):
        """Formata a exibição para mostrar [X] ou [ ]."""
        return f"[X] {self.label}" if self.checked else f"[ ] {self.label}"

    def render(self):
        """Desenha a caixa de seleção e seu rótulo no terminal."""
        self.text = self._format_text()
        super().render()

    def process_input(self, key):
        """
        Processa a entrada para alternar o estado da caixa de seleção.

        Args:
            key (str): A tecla pressionada (Enter ou Espaço).
        """
        if not self.is_focused or not key:
            return
        if key in (Keys.ENTER, Keys.SPACE):
            self.checked = not self.checked
            return 'enter'


class VerticalList(Widget):
    """
    Um widget de contêiner que exibe uma lista de widgets filhos verticalmente e permite rolagem e seleção.

    Atributos:
        children (List[Widget]): A lista de widgets contidos na lista.
        scroll_offset (int): O índice do primeiro item visível na lista, para rolagem.
        _focus_index (int): O índice interno do item atualmente selecionado.
    """
    def __init__(self, x=1, y=1, width=20, height=5):
        """
        Inicializa o widget VerticalList.

        Args:
            x (int): A coordenada x inicial.
            y (int): A coordenada y inicial.
            width (int): A largura do contêiner da lista.
            height (int): A altura do contêiner da lista.
        """
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.children: List[Widget] = []
        self.scroll_offset = 0
        self._focus_index = 0
        self.is_focusable = True
        self.is_focused = False

    @property
    def focus_index(self):
        """
        Propriedade para obter com segurança o índice de foco, garantindo que ele esteja sempre dentro dos limites.
        
        Returns:
            int: O índice de foco válido.
        """
        if len(self.children) == 0:
            return 0
        return min(self._focus_index, len(self.children) - 1)

    @focus_index.setter
    def focus_index(self, value):
        """
        Propriedade para definir com segurança o índice de foco, fixando-o a um intervalo válido.

        Args:
            value (int): O novo valor desejado para o índice de foco.
        """
        if len(self.children) == 0:
            self._focus_index = 0
        else:
            self._focus_index = max(0, min(value, len(self.children) - 1))


    def process_input(self, key):
        """
        Processa a navegação para cima/baixo na lista e passa outras teclas para o filho selecionado.

        Args:
            key (str): A tecla pressionada pelo usuário

        Returns:
            bool: True se a tecla de navegação foi processada, False caso contrário.
        """
        if not self.is_focused:
            return False

        if key == Keys.UP:
            self._move_focus(-1)
            return True
        elif key == Keys.DOWN:
            self._move_focus(1)
            return True
        
        if self.children:
            selected_child = self.children[self.focus_index]
            return selected_child.process_input(key)
        
        return False



    def add_child(self, widget: Widget):
        """
        Adiciona um widget filho à lista.

        Args:
            widget (Widget): O widget a ser adicionado.
        """
        self.children.append(widget)

    
    def render(self):
        """Desenha a lista, incluindo a borda, o indicador de seleção e os widgets filhos visíveis."""
        terminal = TUIApplication.current_application.terminal


        visible_children = self.children[self.scroll_offset:self.scroll_offset + self.height - 2]
        
        for i, widget in enumerate(visible_children):
            terminal.reset_text_style()
            
            current_item_index = self.scroll_offset + i
            
            widget.x = self.x + 1
            widget.y = self.y + 1 + i
            
            is_selected = (current_item_index == self.focus_index)
            widget.is_focused = is_selected

            terminal.move_cursor(widget.x, widget.y)
            if is_selected and self.is_focused:
                terminal.set_text_style(color="CYAN", bold=True, bright=True)
                terminal.putstr("> ")
                terminal.reset_text_style()
            else:
                terminal.putstr("  ") # Keep alignment

            widget.x += 2
            widget.render()

    
    def add_child(self, widget: Widget):
        self.children.append(widget)


    def _move_focus(self, delta):
        """Move o foco para o item anterior ou seguinte na lista, ajustando a rolagem."""
        if not self.children:
            return
        
        current_index = self.focus_index
        self.children[current_index].is_focused = False
        
        self.focus_index = (current_index + delta) % len(self.children)
        self.children[self.focus_index].is_focused = True
        
        self._ensure_visible()

    def _ensure_visible(self):
        """Ajusta o `scroll_offset` para garantir que o item focado esteja sempre visível."""
        if self.focus_index < self.scroll_offset:
            self.scroll_offset = self.focus_index
        elif self.focus_index >= self.scroll_offset + self.height - 2:
            self.scroll_offset = self.focus_index - (self.height - 3)


class ConfirmationDialog(Widget):
    """
    Um widget de diálogo modal que sobrepõe a tela para pedir a confirmação do usuário

    Atributos:
        message (str): A mensagem a ser exibida ao usuário.
        on_confirm (callable): A função a ser chamada se o usuário confirmar.
        on_cancel (callable): A função a ser chamada se o usuário cancelar.
        focus_index (int): O botão atualmente selecionado (0=Confirmar, 1=Cancelar).
    """
    def __init__(self, message: str, on_confirm, on_cancel):
        """
        Inicializa o ConfirmationDialog.

        Args:
            message (str): A mensagem de confirmação.
            on_confirm (callable): A função de callback para a confirmação.
            on_cancel (callable): A função de callback para o cancelamento.
        """
        super().__init__()
        self.message = message
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.focus_index = 0 # 0 para Confirmar, 1 para Cancelar

        # Centraliza o diálogo na tela
        t = TUIApplication.current_application.terminal
        self.width = max(len(self.message) + 4, 30)
        self.height = 7
        self.x = (t.COLUMNS - self.width) // 2
        self.y = (t.LINES - self.height) // 2
    
    def render(self):
        """Desenha a caixa de diálogo, a mensagem e os botões Confirmar/Cancelar."""
        # Desenha o frame do diálogo
        frame = Frame(self.x, self.y, self.width, self.height, title="Confirmação")
        frame.frame_style = TextStyle(color="YELLOW", bold=True)
        frame.render()

        # Desenha a mensagem
        msg_label = Label(self.message, x=self.x + 2, y=self.y + 2)
        msg_label.render()

        # Desenha os botões
        confirm_style = TextStyle(bold=True, bright=True, color="RED") if self.focus_index == 0 else TextStyle()
        cancel_style = TextStyle(bold=True, bright=True) if self.focus_index == 1 else TextStyle()

        confirm_button = Button("Confirmar", x=self.x + 3, y=self.y + 4, style=confirm_style)
        cancel_button = Button("Cancelar", x=self.x + self.width - 13, y=self.y + 4, style=cancel_style)
        
        # Define o foco visualmente para os botões internos
        confirm_button.is_focused = self.focus_index == 0
        cancel_button.is_focused = self.focus_index == 1

        confirm_button.render()
        cancel_button.render()

    def process_input(self, key):
        """
        Processa a entrada para navegar entre os botões e executar a ação correspondente.

        Args:
            key (str): A tecla pressionada pelo usuário.

        Returns:
            bool: Retorna sempre True para consumir a tecla e evitar que ela afete a tela por baixo.
        """
        if key == Keys.LEFT or key == Keys.RIGHT or key == Keys.TAB:
            self.focus_index = 1 - self.focus_index # Alterna entre 0 e 1
            return True
        
        if key == Keys.ENTER:
            if self.focus_index == 0:
                self.on_confirm()
            else:
                self.on_cancel()
            return True
        
        if key == Keys.ESC:
            self.on_cancel()
            return True
        
        return True

class AlertDialog(Widget):
    """
    Um widget de diálogo modal que exibe uma mensagem de alerta e espera que o usuário a dispense..

    Atributos:
        message (str): A mensagem de alerta a ser exibida.
        on_dismiss (callable): A função a ser chamada quando o diálogo for dispensado.
    """
    def __init__(self, message: str, on_dismiss):
        """
        Inicializa o AlertDialog.

        Args:
            message (str): A mensagem de alerta.
            on_dismiss (callable): A função de callback para dispensar o diálogo.
        """
        super().__init__()
        self.message = message
        self.on_dismiss = on_dismiss

        # Centraliza o diálogo na tela
        t = TUIApplication.current_application.terminal
        self.width = max(len(self.message) + 4, 20)
        self.height = 6
        self.x = (t.COLUMNS - self.width) // 2
        self.y = (t.LINES - self.height) // 2

    def render(self):
        """Desenha a caixa de diálogo, a mensagem e um único botão OK."""
        # Desenha o frame do diálogo
        frame = Frame(self.x, self.y, self.width, self.height, title="Aviso")
        frame.frame_style = TextStyle(color="YELLOW", bold=True)
        frame.render()

        # Desenha a mensagem
        msg_label = Label(self.message, x=self.x + 2, y=self.y + 2)
        msg_label.render()

        # Desenha um único botão "OK" centrado
        ok_style = TextStyle(bold=True, bright=True)
        button_x = self.x + (self.width - 7) // 2 # Largura de "OK" é 5 + 2 de padding
        ok_button = Button("OK", x=button_x, y=self.y + 3, style=ok_style)
        ok_button.is_focused = True # O botão está sempre focado
        ok_button.render()

    def process_input(self, key):
        """
        Processa qualquer tecla para dispensar o diálogo de alerta.

        Args:
            key (str): A tecla pressionada pelo utilizador.

        Returns:
            bool: Retorna sempre True para consumir a tecla.
        """
        if key in (Keys.ENTER, Keys.ESC, Keys.SPACE):
            self.on_dismiss()
        
        return True # Consome todas as teclas
            
