# MyFTP - File Transfer Protocol over UDP

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Completed-green?style=for-the-badge)

An academic Computer Networks project that implements a simplified file transfer protocol (FTP), built from scratch over the UDP protocol, with a graphical interface for both client and server.

## Project Overview

MyFTP was developed as a practical assignment for the Computer Networks course.  
The main goal was to build a client-server system for file transfer without relying on the reliability of the TCP protocol.  
Instead, the central challenge was to implement a reliability layer on top of **UDP (User Datagram Protocol)**, which is inherently unreliable and connectionless.

The system consists of two graphical applications (GUI): a server capable of handling multiple clients simultaneously and a client that allows the user to interact with the remote file system.

## Key Features

- **User Authentication:** Login system with credential validation on the server.  
- **Remote File System Navigation:** Commands `ls`, `cd`, `cd ..`, and a button to return to the root directory.  
- **Directory Management:** Create (`mkdir`) and remove (`rmdir`) folders on the server.  
- **Bidirectional File Transfer:**  
  - **Upload (`put`):** Send files from the client to the server through a file selection button or drag-and-drop functionality.  
  - **Download (`get`):** Retrieve files from the server to the client.  
- **Intuitive Graphical Interface:** Both client and server include graphical interfaces built with Tkinter, making interaction and monitoring easier.  
- **Cross-Platform Support:** Compatible with Windows, macOS, and Linux.  

## Technologies Used

- **Language:** Python 3  
- **Networking:** `socket` library for UDP communication.  
- **Graphical Interface (GUI):** `Tkinter` (with `ttk` for enhanced styling) and `TkinterDnD2` for drag-and-drop functionality.  
- **Concurrency:** `threading` library.  
