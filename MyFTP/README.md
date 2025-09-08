# MyFTP - Protocolo de Transferência de Arquivos sobre UDP

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Concluído-green?style=for-the-badge)

Um projeto acadêmico de Redes de Computadores que implementa um protocolo de transferência de arquivos (FTP) simplificado, construído do zero sobre o protocolo UDP, com uma interface gráfica para cliente e servidor.

## Visão Geral do Projeto

O MyFTP foi desenvolvido como trabalho prático para a disciplina de Redes de Computadores. O principal objetivo era construir um sistema cliente-servidor para transferência de arquivos que não utilizasse a confiabilidade do protocolo TCP. Em vez disso, o desafio central foi implementar uma camada de confiabilidade sobre o **UDP (User Datagram Protocol)**, que é inerentemente não confiável e não orientado à conexão.

O sistema consiste em duas aplicações com interface gráfica (GUI): um servidor capaz de lidar com múltiplos clientes simultaneamente e um cliente que permite ao usuário interagir com o sistema de arquivos remoto.

## Principais Funcionalidades

-   **Autenticação de Usuário:** Sistema de login com validação de credenciais no servidor.
-   **Navegação no Sistema de Arquivos Remoto:** Comandos `ls`, `cd`, `cd ..` e um botão para voltar à raiz.
-   **Manipulação de Diretórios:** Criação (`mkdir`) e remoção (`rmdir`) de pastas no servidor.
-   **Transferência de Arquivos Bidirecional:**
    -   **Upload (`put`):** Envio de arquivos do cliente para o servidor através de um botão de seleção ou da funcionalidade de arrastar e soltar (Drag and Drop).
    -   **Download (`get`):** Download de arquivos do servidor para o cliente.
-   **Interface Gráfica Intuitiva:** Tanto o cliente quanto o servidor possuem interfaces gráficas construídas com Tkinter, facilitando a interação e o monitoramento.
-   **Suporte Multiplataforma:** O sistema é compatível com Windows, macOS e Linux.

## Tecnologias Utilizadas

-   **Linguagem:** Python 3
-   **Rede:** Biblioteca `socket` para comunicação UDP.
-   **Interface Gráfica (GUI):** `Tkinter` (com `ttk` para um visual aprimorado) e `TkinterDnD2` para a funcionalidade de arrastar e soltar.
-   **Concorrência:** Biblioteca `threading`.
