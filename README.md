# TUI To-Do List Manager

A sophisticated, cross-platform To-Do List application that runs entirely in your terminal. Built with Python and a custom-built Terminal User Interface (TUI) framework made from scratch without pip libraries, this project provides a robust and efficient way to manage complex tasks and lists without ever leaving the command line.

The interface is designed to be fast, responsive, and intuitive, relying solely on keyboard navigation. It is optimized for performance with an event-driven model, ensuring it uses no CPU resources while idle.

---

## ✅ Key Features

This application is packed with features to provide a complete task management experience.

### List Management
- [x] **Multiple Task Lists:** Create, rename, and manage separate lists for different projects (e.g., "Work", "Personal", "Shopping").
- [x] **Duplicate Name Prevention:** The application prevents the creation or renaming of lists to a name that already exists.
- [x] **Safe Deletion:** A modal confirmation dialog appears before deleting a list, preventing accidental data loss.
- [x] **Last List Protection:** The application will not allow the user to delete the final remaining list.

### Task Management
- [x] **Create & Edit Tasks:** Add new tasks with detailed attributes or edit existing ones.
- [x] **Task Attributes:**
    - **Title & Notes:** A required title and optional detailed notes.
    - **Due Date:** An optional due date, selected via an interactive calendar widget.
    - **Priority:** Set priority levels: `Alta`, `Média`, `Baixa`, or `Sem Prioridade`.
    - **Tags:** Assign multiple, comma-separated tags for categorization.
    - **Repetition:** Define task frequency (`Diária`, `Semanal`, `Mensal`, etc.).
- [x] **Toggle Completion:** Quickly mark tasks as complete or incomplete directly from the task view.
- [x] **Task Details View:** A dedicated read-only screen to see all information about a single task.

### Viewing & Filtering System
- [x] **Advanced Filtering:** A powerful filtering screen to create custom views of your tasks.
- [x] **Filter by Scope:** View tasks from a single list or from all lists simultaneously.
- [x] **Filter by Time:** View all tasks, only tasks due today, or tasks due within the next 7 days.
- [x] **Filter by Status:** Show all tasks or only the ones that are not yet completed.
- [x] **Dual Sorting Modes:**
    - Sort primarily by **Date**, with Priority as a tie-breaker.
    - Sort primarily by **Priority**, with Date as a tie-breaker.
- [x] **Global Search:** A dedicated search function to find tasks containing a specific term in their title, notes, or tags.

### User Interface & Experience
- [x] **Fully Keyboard-Navigable:** No mouse required. Navigation is handled via `Tab`, `Shift+Tab`, Arrow Keys, `Enter`, and `Esc`.
- [x] **Custom TUI Framework:** Built from the ground up, featuring reusable widgets like Labels, Buttons, Text Inputs, Checkboxes, and modal Dialogs.
- **Performance Optimized:** Uses an event-driven loop that waits for user input, resulting in zero CPU usage when idle.
- **Cross-Platform:** Fully compatible with modern terminals on Windows, macOS, and Linux.

---

## 🏗️ Project Structure

The project is organized into a modular structure that separates concerns. Here is a breakdown of each file:

.
 * **`createlistscreen.py`**: The UI form for creating a new task list.
 * **`createtaskscreen.py`**: The UI form for adding a new task to a specific list.
 * **`editlistscreen.py`**: The UI form for editing the name of an existing task list.
 * **`edittaskscreen.py`**: The UI form for editing the attributes of an existing task.
 * **`filteroptionsscreen.py`**: The screen where the user selects viewing, filtering, and sorting options.
 * **`libgerenciador.py`**: The "brains" of the application. Defines data structures (`Tarefa`, `ListaDeTarefas`) and contains all business logic (creating, editing, filtering, sorting, etc.). It has no knowledge of the UI.
 * **`libterm.py`**: The lowest level of the application. It handles all direct, cross-platform interaction with the terminal (reading keys, moving the cursor, printing colors).
 * **`libtui.py`**: The heart of the UI framework. It contains the base classes for the application (`TUIApplication`), screens (`TUIScreen`), and all reusable widgets (`Button`, `TextInput`, `VerticalList`, etc.).
 * **`lista_de_tarefas.py`**: The main executable file and entry point for the application. It initializes all components and manages the screen stack.
 * **`listselectionscreen.py`**: The main menu screen. It displays all created task lists and provides global actions like viewing or editing them.
 * **`README.md`**: This file.
 * **`screens.py`**: A simple file containing an `Enum` that provides clear, readable constants for all the different UI screens.
 * **`searchinputscreen.py`**: A simple UI form for the user to type their search query.
 * **`taskdetailscreen.py`**: A read-only screen that displays all attributes of a single task in detail.
 * **`taskviewscreen.py`**: A generic, reusable screen that displays any list of tasks passed to it (e.g., from a filter, search, or single list view).
 * **`userdata.json`**: The database file where all user-created lists and tasks are saved in JSON format.

---

## 🚀 How to Run

1.  Ensure you have Python 3 installed.
2.  Navigate to the project directory in your terminal.
3.  Run the main application file:
    ```bash
    python lista_de_tarefas.py
    ```
