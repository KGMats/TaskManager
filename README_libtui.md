
# 🖥️ TUI Framework

## 📄 Visão Geral

Este projeto é um **mini-framework para construção de interfaces textuais (TUI)** no terminal. Ele permite criar aplicações interativas usando apenas Python puro, sem dependências externas além da biblioteca `libterm.py`.

### Funcionalidades:
- Componentes visuais: botões, labels, caixas de seleção, inputs, seletores, etc.
- Navegação por teclado e controle de foco.
- Suporte a diálogos modais (alerta e confirmação).
- Estilização com negrito, sublinhado, itálico, brilho, tachado e cores.

---

## 🔥 Estrutura do Framework

### 🏛️ Classes Base

#### `TextStyle`
Define o estilo visual do texto no terminal.

| Atributo       | Tipo  | Descrição                                    |
|----------------|-------|-----------------------------------------------|
| `bold`         | bool  | Negrito                                       |
| `italic`       | bool  | Itálico                                       |
| `underline`    | bool  | Sublinhado                                    |
| `color`        | str   | Cor (ex.: `"RED"`, `"BLUE"`, `"WHITE"`)       |
| `bright`       | bool  | Cor brilhante                                 |
| `strikethrough`| bool  | Tachado                                        |

---

#### `Widget`
Classe base abstrata para todos os componentes visuais.

| Atributo         | Descrição                                |
|------------------|-------------------------------------------|
| `x`, `y`         | Posição no terminal                      |
| `width`, `height`| Tamanho                                  |
| `is_focused`     | Está focado                              |
| `is_focusable`   | Pode receber foco                        |

| Método           | Descrição                                |
|------------------|------------------------------------------|
| `render()`       | Desenha o widget                         |
| `process_input()`| Processa entrada de teclado              |

---

#### `TUIScreen`
Representa uma tela com múltiplos widgets.

| Método                  | Descrição                                         |
|-------------------------|---------------------------------------------------|
| `build()`               | Define os widgets da tela                        |
| `render()`              | Renderiza todos os widgets                       |
| `process_input(key)`    | Processa entrada e gerencia foco                 |
| `move_focus(direction)` | Move o foco entre widgets focáveis               |
| `get_focusable_widgets()`| Retorna os widgets focáveis                     |

---

#### `TUIApplication`
Gerencia a aplicação inteira.

| Método          | Descrição                                         |
|-----------------|---------------------------------------------------|
| `build()`       | Define a tela inicial                             |
| `render()`      | Atualiza a tela atual                             |
| `process_input()`| Encaminha entrada para a tela atual              |
| `run()`         | Loop principal da aplicação                       |

---

## 🧩 Widgets Disponíveis

- **Label** — Rótulo de texto.
- **Frame** — Moldura com título.
- **Button** — Botão interativo.
- **TextInput** — Entrada de texto.
- **DateInput** — Seletor de data.
- **IntInput** — Entrada de número inteiro.
- **Selector** — Seletor de opções (dropdown simples).
- **Checkbox** — Caixa de seleção.
- **VerticalList** — Lista vertical rolável de widgets.

---

## 📦 Diálogos Modais

- **ConfirmationDialog** — Diálogo de confirmação com opções de "OK" e "Cancelar".
- **AlertDialog** — Alerta simples com mensagem.

---

## 🎨 Estilo de Texto

Estilização possível usando a classe `TextStyle`:
- **Negrito**
- **Itálico**
- **Sublinhado**
- **Tachado**
- **Cor padrão ou brilhante** (`"RED"`, `"GREEN"`, `"BLUE"`, etc.)

---

## 🎹 Mapeamento de Teclas

| Tecla         | Ação                               |
|----------------|------------------------------------|
| `TAB`          | Próximo foco                      |
| `SHIFT+TAB`    | Foco anterior                     |
| `ENTER`        | Selecionar / Confirmar / Editar   |
| `ESC`          | Cancelar                          |
| `↑ ↓ ← →`      | Navegação                         |
| `BACKSPACE`    | Apagar                            |
| `F1` a `F12`   | Teclas de função                   |

---

## 🚀 Exemplo de Uso

```python
class MyApp(TUIApplication):
    def build(self):
        screen = TUIScreen()
        screen.children = [
            Label("Hello World", x=2, y=2),
            Button("OK", x=2, y=4, on_click=lambda: print("Clicked!"))
        ]
        self.current_screen = screen

if __name__ == "__main__":
    MyApp().run()
```

---

## 🛠️ Dependências

- Python 3
- `libterm.py` (biblioteca própria incluída no projeto)

---

## 👥 Autoria

- Jeorde Antonio Ribeiro Neto
- Kayky Gibran de Oliveira Matos

---

## 📅 Última Atualização

Junho de 2025

---
