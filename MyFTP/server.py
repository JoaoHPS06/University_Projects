import socket
import threading
import os
import struct
import tkinter as tk
from tkinter import scrolledtext

# Macros do Protocolo
SERVER_ROOT = os.path.abspath("server_files") # Define o diretório raiz onde o servidor irá operar.
MSG_END_ERROR_NOT_FOUND = b"END_ERROR: Arquivo nao encontrado"
MSG_END_ERROR_INVALID_DIR = b"ERRO: Diretorio invalido ou nao encontrado"
MSG_END = b"END"
MSG_START = b"START"
MSG_PUT_OK = b"PUT_OK"

# Classe principal da GUI do Servidor
class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Servidor MyFTP")

        # Dicionário de usuários e senhas para autenticação.
        self.users = {"joao": "senha1", "camile": "senha2", "aluno": "senha3"}

        # Garante que o diretório raiz do servidor exista.
        if not os.path.exists(SERVER_ROOT):
            os.makedirs(SERVER_ROOT)

        # Construção da Interface Gráfica (GUI)
        tk.Label(root, text="Logs do servidor:").pack()
        self.log_text = scrolledtext.ScrolledText(root, height=20, width=80, state="disabled")
        self.log_text.pack(pady=5, padx=5)

        tk.Label(root, text=f"Arquivos em: {SERVER_ROOT}").pack()
        self.file_listbox = tk.Listbox(root, width=80)
        self.file_listbox.pack(pady=5, padx=5)
        tk.Button(root, text="Atualizar Lista de Arquivos", command=self.update_file_list).pack(pady=5)

        # Configuração do Socket Principal
        # Este socket fica em uma porta fixa (12345) e sua única função é ouvir por novas tentativas de login.
        self.main_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.main_sock.bind(("localhost", 12345))

        self.log("Servidor iniciado. Aguardando logins na porta 12345...")
        self.update_file_list()

        # Inicia a thread que ouve por logins em segundo plano, para não travar a GUI.
        threading.Thread(target=self.listen_for_logins, daemon=True).start()

    # Função para adicionar uma mensagem ao log da GUI.
    def log(self, msg):
        # Usa root.after para garantir que a atualização da GUI seja feita na thread principal (thread-safe).
        self.root.after(0, self._log_thread_safe, msg)

    # Função interna que efetivamente modifica o widget de texto do log.
    def _log_thread_safe(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see(tk.END)

    # Função para solicitar a atualização da lista de arquivos na GUI.
    def update_file_list(self):
        # Também usa root.after para ser thread-safe.
        self.root.after(0, self._update_file_list_thread_safe)

    # Função interna que atualiza a listbox de arquivos.
    def _update_file_list_thread_safe(self):
        self.file_listbox.delete(0, tk.END)
        for f in os.listdir(SERVER_ROOT):
            full_path = os.path.join(SERVER_ROOT, f)
            # Adiciona uma "/" ao final do nome se for um diretório, para diferenciação visual.
            if os.path.isdir(full_path):
                self.file_listbox.insert(tk.END, f + "/")
            else:
                self.file_listbox.insert(tk.END, f)

    # Thread principal que atua como "Porteiro", gerenciando novos logins.
    def listen_for_logins(self):
        while True:
            try:
                # Espera por uma mensagem na porta de login fixa.
                data, addr = self.main_sock.recvfrom(1024)
                username, password = data.decode().split(":", 1)

                # Valida as credenciais do usuário.
                if self.users.get(username) == password:
                    self.log(f"[Porteiro] Login bem-sucedido de {addr}. Alocando porta dedicada...")
                    
                    # Criação da Sessão Dedicada
                    # 1. Cria um NOVO socket para este cliente.
                    session_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    # 2. Faz o bind a uma porta aleatória disponível (porta 0).
                    session_sock.bind(("localhost", 0))
                    session_port = session_sock.getsockname()[1]

                    # 3. Inicia uma NOVA thread para gerenciar a sessão completa deste cliente, usando o novo socket.
                    session_thread = threading.Thread(target=self.client_session_thread, args=(session_sock, addr, username), daemon=True)
                    session_thread.start()
                    
                    # 4. Envia a nova porta de comunicação de volta para o cliente.
                    self.main_sock.sendto(f"SUCCESS:{session_port}".encode(), addr)
                else:
                    self.log(f"[Porteiro] Falha de login de {addr}.")
                    self.main_sock.sendto(b"FAILURE", addr)
            except Exception as e:
                self.log(f"[Porteiro] Erro no processo de login: {e}")

    # Thread de sessão, uma instância desta função roda para cada cliente conectado.
    def client_session_thread(self, session_sock, client_addr, username):
        self.log(f"Sessão iniciada para {username}@{client_addr} na porta {session_sock.getsockname()[1]}")
        # 'current_path' é uma variável local, garantindo que o 'cd' de um cliente não afete os outros.
        current_path = SERVER_ROOT
        session_sock.settimeout(300) # Timeout de 5 minutos de inatividade.

        while True:
            try:
                # Ouve por comandos apenas no socket dedicado desta sessão.
                data, addr = session_sock.recvfrom(1024 + 4)
                if not data: break

                try:
                    # Tenta decodificar o dado como um comando de texto.
                    decoded_command = data.decode()
                    command_parts = decoded_command.split(" ", 1)
                    command = command_parts[0]

                    if command == "ls":
                        items = []
                        for item in os.listdir(current_path):
                            # Adiciona "/" se for diretório.
                            if os.path.isdir(os.path.join(current_path, item)):
                                items.append(item + "/")
                            else:
                                items.append(item)
                        response = "\n".join(items)
                        session_sock.sendto(response.encode() if response else b" ", client_addr)
                    
                    elif command == "ls_dirs":
                        # Lista apenas os diretórios, para a GUI do cliente.
                        dirs = [d for d in os.listdir(current_path) if os.path.isdir(os.path.join(current_path, d))]
                        dir_list = "\n".join(dirs)
                        session_sock.sendto(dir_list.encode() if dir_list else b" ", client_addr)

                    elif command == "cd" and len(command_parts) > 1:
                        requested_path = command_parts[1]
                        
                        # Comando especial para voltar à raiz segura do servidor.
                        if requested_path in ['/', '.']:
                            current_path = SERVER_ROOT
                            session_sock.sendto(b"Retornou para o diretorio raiz do servidor.", client_addr)
                        else:
                            target_dir = os.path.normpath(os.path.join(current_path, requested_path))
                            # CHECAGEM DE SEGURANÇA: Previne ataques de Directory Traversal.
                            # Garante que o caminho final ainda esteja contido dentro do SERVER_ROOT.
                            if os.path.commonpath([SERVER_ROOT]) == os.path.commonpath([SERVER_ROOT, target_dir]) and os.path.isdir(target_dir):
                                current_path = target_dir
                                session_sock.sendto(f"Diretório alterado para: {os.path.relpath(current_path, SERVER_ROOT) or '.'}".encode(), client_addr)
                            else:
                                session_sock.sendto(MSG_END_ERROR_INVALID_DIR, client_addr)

                    elif command == "get" and len(command_parts) > 1:
                        self.handle_get(session_sock, client_addr, current_path, command_parts[1])

                    elif command == "put" and len(command_parts) > 1:
                        self.handle_put(session_sock, client_addr, current_path, command_parts[1])
                    
                    elif command == "mkdir" and len(command_parts) > 1:
                        # Implementa a criação de diretórios, com checagem de segurança.
                        new_dir_path = os.path.normpath(os.path.join(current_path, command_parts[1]))
                        if os.path.commonpath([SERVER_ROOT]) == os.path.commonpath([SERVER_ROOT, new_dir_path]):
                            try:
                                os.mkdir(new_dir_path)
                                session_sock.sendto(f"Diretório '{command_parts[1]}' criado.".encode(), client_addr)
                                self.update_file_list()
                            except FileExistsError:
                                session_sock.sendto(b"ERRO: Diretorio ja existe.", client_addr)
                        else:
                            session_sock.sendto(b"ERRO: Caminho invalido.", client_addr)

                    elif command == "rmdir" and len(command_parts) > 1:
                        # Implementa a remoção de diretórios, com checagem de segurança.
                        dir_to_remove_path = os.path.normpath(os.path.join(current_path, command_parts[1]))
                        if os.path.commonpath([SERVER_ROOT]) == os.path.commonpath([SERVER_ROOT, dir_to_remove_path]):
                            try:
                                # Garante que o diretório esteja vazio antes de remover.
                                if not os.listdir(dir_to_remove_path):
                                    os.rmdir(dir_to_remove_path)
                                    session_sock.sendto(f"Diretório '{command_parts[1]}' removido.".encode(), client_addr)
                                    self.update_file_list()
                                else:
                                    session_sock.sendto(b"ERRO: O diretorio nao esta vazio.", client_addr)
                            except FileNotFoundError:
                                session_sock.sendto(b"ERRO: Diretorio nao encontrado.", client_addr)
                        else:
                            session_sock.sendto(b"ERRO: Caminho invalido.", client_addr)

                    elif command == "quit":
                        break
                
                # Se a decodificação falhar, significa que recebemos um pacote binário inesperado.
                # Em vez de quebrar, o servidor o ignora e continua.
                except UnicodeDecodeError:
                    self.log(f"Recebido pacote binário inesperado de {username}@{client_addr}. Ignorando.")
                    continue

            except socket.timeout:
                self.log(f"Cliente {username}@{client_addr} timed out. Encerrando sessão.")
                break
            except Exception as e:
                self.log(f"Erro na sessão de {username}@{client_addr}: {e}")
                break
        
        session_sock.close()
        self.log(f"Sessão para {username}@{client_addr} encerrada.")

    # Função que gerencia o envio de um arquivo (comando GET).
    def handle_get(self, sock, addr, path, filename):
        filepath = os.path.join(path, filename)
        if not os.path.exists(filepath):
            sock.sendto(MSG_END_ERROR_NOT_FOUND, addr)
            return

        self.log(f"Enviando '{filename}' para {addr}")
        with open(filepath, "rb") as f:
            seq_num = 0
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                
                # Loop de retransmissão: continua enviando o mesmo pacote até o ACK correto chegar.
                ack_ok = False
                while not ack_ok:
                    packet = struct.pack("!I", seq_num) + chunk
                    sock.sendto(packet, addr)
                    try:
                        ack_data, _ = sock.recvfrom(10)
                        if ack_data.decode() == f"ACK{seq_num}":
                            seq_num += 1
                            ack_ok = True # Sucesso, pode enviar o próximo pacote.
                    except socket.timeout:
                        self.log(f"Timeout esperando ACK{seq_num-1} de {addr}. Reenviando.")
        
        sock.sendto(MSG_END, addr)
        self.log(f"Envio de '{filename}' para {addr} concluído.")

    # Função que gerencia o recebimento de um arquivo (comando PUT).
    def handle_put(self, sock, addr, path, filename):
        filepath = os.path.join(path, filename)
        self.log(f"Recebendo '{filename}' de {addr}")
        sock.sendto(MSG_START, addr) # Sinaliza para o cliente que está pronto.
        
        success = False
        with open(filepath, "wb") as f:
            expected_seq_num = 0
            while True:
                try:
                    packet, _ = sock.recvfrom(1024 + 4)
                    if packet == MSG_END:
                        success = True # Transferência concluída com sucesso.
                        break
                    
                    seq_num = struct.unpack("!I", packet[:4])[0]
                    # Se o pacote recebido for o esperado, escreve no arquivo e avança.
                    if seq_num == expected_seq_num:
                        f.write(packet[4:])
                        sock.sendto(f"ACK{seq_num}".encode(), addr)
                        expected_seq_num += 1
                    else:
                        # Se receber um pacote fora de ordem, reenvia o ACK do último pacote correto.
                        sock.sendto(f"ACK{expected_seq_num - 1}".encode(), addr)
                except socket.timeout:
                    self.log(f"Timeout na recepção de {filename} de {addr}. Abortando.")
                    break
        
        if success:
            # Envia a confirmação final para o cliente.
            sock.sendto(MSG_PUT_OK, addr)
            self.log(f"Recepção de '{filename}' de {addr} concluída.")
            self.update_file_list()
        else:
            self.log(f"Falha na recepção de '{filename}' de {addr}.")
            if os.path.exists(filepath):
                os.remove(filepath) # Remove o arquivo incompleto.

# Ponto de entrada do programa servidor.
if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()