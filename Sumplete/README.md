# Sumplete Game in C

![Language C](https://img.shields.io/badge/Language-C-A8B9CC?style=for-the-badge&logo=c)
![Status](https://img.shields.io/badge/Status-Completed-4CAF50?style=for-the-badge)

A complete implementation of the logic puzzle game Sumplete, developed entirely in the C language. This project was created as part of an academic assignment and runs directly in the terminal, using ANSI colors for an enhanced user experience.

## Academic Context

This project was developed as the final assignment for the **ntroduction to Programming** course. The objective was to apply fundamental C language concepts—such as memory management, pointers, modularization, and file manipulation—to create an interactive application.

## Features

The game includes a comprehensive set of features to ensure a robust experience:

-   **Random Board Generation:** Every new game presents a unique challenge.
-   **Configurable Size and Difficulty:** The player can choose the board size (from 3x3 to 9x9) and the difficulty level (Easy, Medium, Hard).
-   **Save and Load Game:** Progress can be saved to a `.txt` file at any time and loaded later.
-   **Hint System:** The player can request hints to help solve the puzzle.
-   **Auto-Solve Function:** The game can automatically solve the board from its current state.
-   **Time Tracking:** Game time is monitored to encourage fast solutions.
-   **Colorful Terminal Interface:** Uses ANSI escape codes to differentiate between kept, removed, and validated numbers, improving gameplay.

## How to Play

The objective of Sumplete is to eliminate numbers from a grid. The numbers you decide to **keep** in each row and column must sum up to the exact target values shown on the side and bottom of the grid.

### Game Commands

All actions are performed through text commands:

-   `manter [R][C]`: Marks the number at Row `R` and Column `C` to be kept in the sum.
    -   *Example: `manter 12`*
-   `remover [R][C]`: Marks the number at Row `R` and Column `C` to be removed from the sum.
    -   *Example: `remover 34`*
-   `salvar [filename].txt`: Saves the current game state to the specified file.
    -   *Example: `save my_game.txt`*
-   `dica`: Reveals the correct action (keep or remove) for a currently unmarked cell.
-   `resolver`: Automatically solves the rest of the board. **(Function not implemented)**
-   `voltar`: Returns to the main menu, saving the current progress for the "Continue current game" option.

## Project Structure

The code was modularized to ensure organization and clarity by separating responsibilities:

-   `TP_SUMPLETE.c`: The main file (`main`) that manages the menu and the primary game loop.
-   `MYBOOK.h` / `MYBOOK.c`: Contains the core game logic, including matrix creation and manipulation, sum calculations, and move validation.
-   `MYCOMMANDS.h` / `MYCOMMANDS.c`: Responsible for managing the game session, processing user commands, and interacting with the file system to save/load games.
-   `MYCOLORS.h`: A header file with macro definitions for the ANSI colors used in the terminal.

## Technical Details

-   **Language:** C (C99 Standard)
-   **Techniques:** Dynamic memory allocation (`calloc`, `free`), pointer manipulation for matrices, modular design with header files (`.h`), and file I/O (`fopen`, `fprintf`, `fscanf`).

## How to Compile and Run

### Prerequisites
-   A C compiler, such as GCC.

### Steps
1.  Clone the repository:
    ```bash
    git clone https://github.com/JoaoHPS06/University-Projects/tree/main/Sumplete.git
    cd Sumplete
    ```
2.  Compile the source files:
    ```bash
    gcc TP_SUMPLETE.c MYBOOK.c MYCOMMANDS.c -o sumplete
    ```
3.  Run the game:
    ```bash
    ./sumplete
    ```

## Project Evolution

The core logic developed in this C project served as the foundation for a more advanced version featuring a graphical user interface, developed in C++ with the Qt framework. You can see the evolution of this work in my personal projects repository.

➡️ **Check out the C++/Qt version here: SOON**
