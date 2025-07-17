# Este arquivo e uma biblioteca de manipulação de terminal em modo texto,
# multiplataforma, feita com intuito de facilitar a criacao
# de interfaces bonitas sem uso de bibliotecas externas.
# Normalmente utiliziaria o NCurses, mas como
# Foi proibido o uso de pacotes que necessitem de instalacao via pip,
# Tivemos que implementar algumas das funcoes do ncurses manualmente

# Especificamente essa biblioteca lida com a parte mais "baixo nivel",
# lidando com coisas como escrever no terminal e mover o cursor.
# A implementacao de abstracoes como botoes e textos e feita em outra
# biblioteca, a libTUI.py (Terminal User Interace)

import sys
import os
import time
from typing import List, Any

if sys.platform == 'win32':
    import msvcrt
    import ctypes
else:
    import tty
    import termios
    import fcntl

class Keys:
    """
    Classe de constantes para representar teclas especiais de forma simbólica.

    Inclui:
        - Setas (UP, DOWN, LEFT, RIGHT)
        - Teclas de função (F1 a F12)
        - Controle de navegação (HOME, END, PAGE_UP, PAGE_DOWN, INSERT, DELETE)
        - Teclas comuns (ESC, TAB, SHIFT_TAB, ENTER, BACKSPACE, SPACE)
    """
    UP = 'UP_ARROW'
    DOWN = 'DOWN_ARROW'
    LEFT = 'LEFT_ARROW'
    RIGHT = 'RIGHT_ARROW'
    
    F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12 = ('F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12')
    
    HOME = 'HOME'
    END = 'END'
    PAGE_UP = 'PAGE_UP'
    PAGE_DOWN = 'PAGE_DOWN'
    INSERT = 'INSERT'
    DELETE = 'DELETE'
    
    ESC = 'ESC'
    TAB = 'TAB'
    SHIFT_TAB = 'SHIFT_TAB'
    ENTER = 'ENTER'
    BACKSPACE = 'BACKSPACE'
    SPACE = ' '

class Terminal():
    """
    Classe responsável por fornecer métodos de controle do terminal de texto.

    Funcionalidades principais:
        - Leitura de teclado (incluindo teclas especiais).
        - Controle de cursor (mover, esconder, mostrar).
        - Manipulação de estilos de texto (cores, negrito, sublinhado, etc.).
        - Limpeza de tela.
        - Operação em modo raw (desabilita buffer e eco no terminal).

    Atributos:
        COLUMNS (int): Número de colunas do terminal.
        LINES (int): Número de linhas do terminal.
        raw_mode (bool): Estado atual do modo raw.
    """
    def __init__(self)->None:
        """
        Inicializa o terminal, captura tamanho atual e prepara
        mapeamento de teclas para diferentes plataformas.
        """
        tmp = os.get_terminal_size()
        self.COLUMNS = tmp[0]
        self.LINES = tmp[1]
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.raw_mode = False
        self.old_settings:List[Any]

        if sys.platform == 'win32':
            self._enable_windows_ansi()

        self.escape_sequences = {
            '\x1b[A': Keys.UP, '\x1b[B': Keys.DOWN, '\x1b[C': Keys.RIGHT, '\x1b[D': Keys.LEFT,
            '\x1b[Z': Keys.SHIFT_TAB,
            '\x1bOA': Keys.UP, '\x1bOB': Keys.DOWN, '\x1bOC': Keys.RIGHT, '\x1bOD': Keys.LEFT,
            '\x1bOP': Keys.F1, '\x1bOQ': Keys.F2, '\x1bOR': Keys.F3, '\x1bOS': Keys.F4,
            '\x1b[15~': Keys.F5, '\x1b[17~': Keys.F6, '\x1b[18~': Keys.F7, '\x1b[19~': Keys.F8,
            '\x1b[20~': Keys.F9, '\x1b[21~': Keys.F10, '\x1b[23~': Keys.F11, '\x1b[24~': Keys.F12,
            '\x1b[H': Keys.HOME, '\x1b[F': Keys.END, '\x1b[1~': Keys.HOME, '\x1b[4~': Keys.END,
            '\x1bOH': Keys.HOME, '\x1bOF': Keys.END, '\x1b[5~': Keys.PAGE_UP, '\x1b[6~': Keys.PAGE_DOWN,
            '\x1b[2~': Keys.INSERT, '\x1b[3~': Keys.DELETE,
        }

        self.windows_keys = {
            b'\xe0H': Keys.UP, b'\xe0P': Keys.DOWN, b'\xe0K': Keys.LEFT, b'\xe0M': Keys.RIGHT,
            b'\xe0G': Keys.HOME, b'\xe0O': Keys.END, b'\xe0I': Keys.PAGE_UP, b'\xe0Q': Keys.PAGE_DOWN,
            b'\xe0R': Keys.INSERT, b'\xe0S': Keys.DELETE,
            b'\x00;': Keys.F1, b'\x00<': Keys.F2, b'\x00=': Keys.F3, b'\x00>': Keys.F4, b'\x00?': Keys.F5,
            b'\x00@': Keys.F6, b'\x00A': Keys.F7, b'\x00B': Keys.F8, b'\x00C': Keys.F9, b'\x00D': Keys.F10,
            b'\x00\x85': Keys.F11, b'\x00\x86': Keys.F12,
            b'\x00\x0f': Keys.SHIFT_TAB,
        }

    def _enable_windows_ansi(self)->None:
        """
        (Windows) Ativa o suporte a sequências ANSI VT no terminal,
        permitindo usar códigos de escape para cores e estilos.
        """
        kernel32 = ctypes.windll.kernel32
        STD_OUTPUT_HANDLE = -11
        h_out = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(h_out, ctypes.byref(mode))
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel32.SetConsoleMode(h_out, mode)

    def enable_raw_mode(self)->None:
        """
        Ativa o modo raw no terminal.

        Efeitos:
            - No modo raw, o terminal não faz buffer de linha nem eco dos caracteres.
            - As teclas são capturadas imediatamente sem esperar ENTER.

        Importante:
            - No Windows, o modo raw é simulado via `msvcrt`.
            - No Unix/Linux é implementado via `termios`.
        """
        if sys.platform == 'win32':
            pass
        else:
            stdin = sys.stdin.fileno()
            self.old_settings = termios.tcgetattr(stdin)
            new_settings = termios.tcgetattr(sys.stdin)
            new_settings[3] = new_settings[3] & ~(termios.ICANON | termios.ECHO)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)
            self.orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
            fcntl.fcntl(sys.stdin, fcntl.F_SETFL, self.orig_fl & ~os.O_NONBLOCK)
        self.raw_mode = True

    def disable_raw_mode(self)->None:
        """
        Desativa o modo raw, restaurando as configurações origniais do terminal.
        """
        if sys.platform == 'win32':
            pass
        elif self.old_settings:
            termios.tcsetattr(self.stdin.fileno(), termios.TCSADRAIN, self.old_settings)
        self.raw_mode = False

    def enable_mouse(self)->None:
        #TODO: Implementar suporte ao mouse
        pass

    
    def read_key(self)->str|None:
        """
        Lê uma tecla pressionada, incluindo teclas especiais.

        Returns:
            str:
                - Uma string representando a tecla (como Keys.UP, Keys.ENTER, Keys.F1, etc.)
                - Ou um caractere literal (ex.: 'a', 'b', '1').

        Bloqueia até que uma tecla seja pressionada.
        No caso de sequências de escape, lê toda a sequência e traduz para um nome simbólico.
        """
        if sys.platform == 'win32':
            ch = msvcrt.getch()
            
            if ch in (b'\x00', b'\xe0'):
                ch2 = msvcrt.getch()
                fullcode = ch + ch2
                return self.windows_keys.get(fullcode, None)
            
            if ch == b'\x1b': return Keys.ESC
            if ch == b'\t': return Keys.TAB
            if ch == b'\r': return Keys.ENTER
            if ch == b'\x08': return Keys.BACKSPACE
            try:
                return ch.decode('utf-8')
            except UnicodeDecodeError:
                return None
        else: # Linux/macOS
            ch = self.stdin.read(1)
            if ch == '\x1b':
                # Lendo o resto da escape sequence
                sequence = ch
                fcntl.fcntl(self.stdin, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)
                while True:
                    try:
                        next_char = self.stdin.read(1)
                        if not next_char: break
                        sequence += next_char
                    except (IOError, TypeError):
                        break
                fcntl.fcntl(self.stdin, fcntl.F_SETFL, self.orig_fl & ~os.O_NONBLOCK)

                if sequence == '\x1b': return Keys.ESC
                return self.escape_sequences.get(sequence, sequence)

            if ch == '\x7f': return Keys.BACKSPACE
            if ch == '\n': return Keys.ENTER
            if ch == '\t': return Keys.TAB
            return ch

    def clear_screen(self)->None:
        """
        Limpa completamente o terminal, equivalente a um 'cls' no windows ou 'clear' no linux.
        """
        self.stdout.write(chr(27) + "[2J")
        try: self.stdout.flush()
        except BlockingIOError: pass

    def hide_cursor(self)->None:
        """
        Esconde o cursor do terminal.
        """
        self.stdout.write('\033[?25l')
        try: self.stdout.flush()
        except BlockingIOError: pass

    def show_cursor(self)->None:
        """
        Mostra o cursor do terminal.
        """
        self.stdout.write('\033[?25h')
        try: self.stdout.flush()
        except BlockingIOError: pass

    def move_cursor(self, x:int, y:int)->None:
        """
        Move o cursor para uma posição específica no terminal.

        Args:
            x (int): Coluna (1 é o canto esquerdo).
            y (int): Linha (1 é o topo).
        """
        self.stdout.write(f'\033[{y};{x}H')
        try: self.stdout.flush()
        except BlockingIOError: pass

    def putstr(self, string:str)->None:
        """
        Escreve uma string na posição atual do cursor.

        Args:
            string (str): Texto a ser exibido.
        """
        self.stdout.write(string)
        try: self.stdout.flush()
        except BlockingIOError: pass

    def set_text_style(self, bold:bool=False, italic:bool=False, underline:bool=False, color:str|None=None, bright:bool=False, strikethrough:bool=False)->None:
        """
        Define o estilo do texto que será impresso.

        Args:
            bold (bool): Negrito.
            italic (bool): Itálico.
            underline (bool): Sublinhado.
            color (str): Cor ('RED', 'GREEN', 'BLUE', etc.).
            bright (bool): Usa versão brilhante da cor.
            strikethrough (bool): Tachado.

        Observação:
            A mudança de estilo persiste até que seja chamado `reset_text_style()`.
        """

        RESET, BOLD, ITALIC, UNDERLINE, STRIKETHROUGH = '\033[0m', '\033[1m', '\033[3m', '\033[4m', '\x1b[9m'
        REGULAR = {"BLACK": "\u001b[30m", "RED": "\u001b[31m", "GREEN": "\u001b[32m", "YELLOW": "\u001b[33m", "BLUE": "\u001b[34m", "MAGENTA": "\u001b[35m", "CYAN": "\u001b[36m", "WHITE": "\u001b[37m", "RESET": "\u001b[0m"}
        BRIGHT = {"BLACK": "\u001b[90m", "RED": "\u001b[91m", "GREEN": "\u001b[92m", "YELLOW": "\u001b[93m", "BLUE": "\u001b[94m", "MAGENTA": "\u001b[95m", "CYAN": "\u001b[96m", "WHITE": "\u001b[97m", "RESET": "\u001b[0m"}
        if bold: self.stdout.write(BOLD)
        if underline: self.stdout.write(UNDERLINE)
        if italic: self.stdout.write(ITALIC)
        if strikethrough: self.stdout.write(STRIKETHROUGH)
        if color:
            if bright: self.stdout.write(BRIGHT[color])
            else: self.stdout.write(REGULAR[color])
        else:
            self.stdout.write(REGULAR["WHITE"])
        try: self.stdout.flush()
        except BlockingIOError: pass

    def reset_text_style(self)->None:
        """
        Restaura o estilo do texto para o padrão (sem negrito, sem cores, etc.).
        """
        RESET = '\033[0m'
        self.stdout.write(RESET)
        try: self.stdout.flush()
        except BlockingIOError: pass

