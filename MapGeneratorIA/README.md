# Map Generator with Backtracking for 2D Game

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![PyGame](https://img.shields.io/badge/PyGame-2.5%2B-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Completed-green?style=for-the-badge)

This project presents a map generator for a 2D RPG exploration game, developed as part of the Artificial Intelligence course.  
The main feature of this system is the use of a backtracking algorithm to ensure that each procedurally generated map is not only random but also valid, playable, and fair, according to a predefined set of rules.

<div align="center">
  <img src="https://github.com/user-attachments/assets/98a0122f-c698-423e-928b-e9cf834c4b32" alt="Game Gameplay" width="600"/>
</div>

## About the Project
A central challenge in many games that use procedural generation is creating levels that make sense.  
A random map may, by chance, be unsolvable (e.g., the key being placed in an inaccessible location).

This project addresses this issue by treating map generation as a **Constraint Satisfaction Problem (CSP)**.  
Instead of simply scattering items, the algorithm actively searches for a configuration that respects all rules, such as:

- **Minimum Distance**: Enemies, treasures, and traps cannot be placed too close to each other or to the player.  
- **Connectivity and Playability**: The map must have a logical path. The player must be able to reach the key and, from there, reach the exit.  
- **Balanced Distribution**: Items are distributed across the map to encourage exploration.  

## Features
- **Procedural Map Generation**: Creates a new map layout on each execution.  
- **Backtracking Algorithm**: Ensures that 100% of generated maps are valid and solvable.  
- **Configurable Constraints**: Generation rules (distance, number of items) can be easily adjusted in the code.  
- **Simple Graphical Interface**: A playable interface built with Pygame to test and visualize generated maps.  
- **Basic Game Mechanics**: Includes player movement, item collection (key, sword), simple combat, and traps.  

## Technologies Used
- **Python 3**: Main language of the project.  
- **Pygame**: Library used for window creation, map rendering, and keyboard event handling.  

## How to Run
To run this project on your local machine, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JoaoHPS06/University-Projects/tree/main/MapGeneratorIA.git
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd MapGeneratorIA
    ```
3.  **Install dependencies:**
    ```bash
    pip install pygame
    ```
4.  **Run the main script:**
    ```bash
    python jogo.py
    ```
    
## Controls
Arrow Keys (Up, Down, Left, Right): Move the player across the map.

## academic_context
This project was developed as the final assessment for the course: BCC325 - Artificial Intelligence at the Federal University of Ouro Preto (UFOP), in the first semester of 2025, taught by Prof. Jadson Castro Gertrudes.
The goal of the project was to apply AI concepts and techniques to solve a practical problem, and the chosen technique was Constraint Satisfaction Algorithms. 

## Team Members
[Camile Reis](https://github.com/camile16)

[Gabriel Vilas](https://github.com/vilas000)

[Gustavo Ferreira](https://github.com/gusthcf)

[João Henrique](https://github.com/JoaoHPS06)

[Marcus Vinicius](https://github.com/MarcusViniAraujo)


