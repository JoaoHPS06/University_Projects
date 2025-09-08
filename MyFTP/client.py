import socket
import struct
import os
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD 

# Macros do Protocolo
LOGIN_SERVER_ADDR = ("localhost", 12345) # Endereço do servidor de login
BUFFER_SIZE = 1024 # Tamanho do buffer para envio e recebimento de dados
# Mensagens de controle padronizadas.
MSG_START = b"START"
MSG_END = b"END"
MSG_PUT_OK = b"PUT_OK"

# Classe para criar uma janela de diálogo customizada para selecionar um diretório de uma lista.
class SelectDirectoryDialog(simpledialog.Dialog):
    def __init__(self, parent, title, dir_list):
        self.dir_list = dir_list
        self.result = None
        super().__init__(parent, title)

    # Cria o corpo da janela de diálogo.
    def body(self, master):
        self.listbox = tk.Listbox(master, width=50, height=10)
        self.listbox.pack(padx=5, pady=5)
        for item in self.dir_list:
            self.listbox.insert(tk.END, item)
        return self.listbox

    # Chamado quando o botão "OK" é pressionado. Armazena o item selecionado.
    def apply(self):
        selected_indices = self.listbox.curselection()
        if selected_indices:
            self.result = self.listbox.get(selected_indices[0])

# Classe principal da GUI do cliente.
class ClientGUI:
    def __init__(self, root):
        self.root = root
        # Criação do socket UDP que será usado para toda a comunicação.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5) # Define um timeout para evitar que o programa trave esperando.
        self.session_addr = None # 'session_addr' irá armazenar o endereço da porta dedicada fornecida pelo servidor após o login.
        # Inicia a aplicação mostrando a tela de login.
        self.login_screen()

    # Constrói a tela de login.
    def login_screen(self):
        self.clear_root()
        self.root.title("MyFTP Client - Login")
        tk.Label(self.root, text="Usuário:").pack(pady=5)
        self.username_entry = tk.Entry(self.root, width=30)
        self.username_entry.pack()
        tk.Label(self.root, text="Senha:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*", width=30)
        self.password_entry.pack()
        tk.Button(self.root, text="Login", command=self.try_login).pack(pady=10)

    # Tenta realizar o login no servidor.
    def try_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Erro", "Usuário e senha não podem estar em branco.")
            return
        try:
            # Envia as credenciais para o endereço fixo do "Porteiro".
            self.sock.sendto(f"{username}:{password}".encode(), LOGIN_SERVER_ADDR)
            # Espera pela resposta.
            data, _ = self.sock.recvfrom(1024)
            response = data.decode()
            # Se a resposta for sucesso, extrai a nova porta e armazena em 'session_addr'.
            if response.startswith("SUCCESS:"):
                new_port = int(response.split(":")[1])
                self.session_addr = (LOGIN_SERVER_ADDR[0], new_port)
                self.show_message("info", "Login", "Login realizado com sucesso!")
                self.main_screen() # Muda para a tela principal.
            else:
                self.show_message("error", "Erro", "Login ou senha inválidos.")
        except socket.timeout:
            self.show_message("error", "Erro de Conexão", "O servidor de login não respondeu.")
        except Exception as e:
            self.show_message("error", "Erro", f"Ocorreu um erro: {e}")

    # Constrói a tela principal da aplicação após o login.
    def main_screen(self):
        self.clear_root()
        self.root.title(f"MyFTP Client - Conectado a {self.session_addr}")
        # Organização da janela em dois painéis (esquerda para comandos, direita para arquivos).
        left_frame = tk.Frame(self.root, padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        right_frame = tk.Frame(self.root, padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Botões de Comando (painel esquerdo)
        tk.Button(left_frame, text="Mudar Diretório (cd)", command=self.cd_visual).pack(fill=tk.X, pady=3)
        tk.Button(left_frame, text="Voltar (cd ..)", command=self.cd_back).pack(fill=tk.X, pady=3)
        tk.Button(left_frame, text="Ir para Raiz", command=self.go_to_root).pack(fill=tk.X, pady=3)
        tk.Button(left_frame, text="Criar Diretório (mkdir)", command=self.mkdir).pack(fill=tk.X, pady=3)
        tk.Button(left_frame, text="Remover Diretório (rmdir)", command=self.rmdir_visual).pack(fill=tk.X, pady=3)
        tk.Button(left_frame, text="Sair", command=self.quit_client).pack(fill=tk.X, pady=(20, 3))
        
        # Painel de Arquivos (painel direito)
        tk.Label(right_frame, text="Arquivos no Servidor:").pack()
        self.file_listbox = tk.Listbox(right_frame, width=60, height=15)
        self.file_listbox.pack(pady=5, fill=tk.BOTH, expand=True)
        
        button_frame = tk.Frame(right_frame)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Atualizar Lista (ls)", command=self.list_files).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Baixar Selecionado (get)", command=self.download_file_start).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Enviar Arquivo (put)", command=self.upload_file_dialog_start).pack(side=tk.LEFT, padx=5)
        
        # Área de Arrastar e Soltar
        tk.Label(right_frame, text="Ou arraste arquivos aqui para enviar:").pack(pady=(10, 0))
        drop_area = tk.Label(right_frame, text="Área de Upload", relief="sunken", bg="lightgray", width=50, height=5)
        drop_area.pack(pady=5, fill=tk.X)
        drop_area.drop_target_register(DND_FILES)
        drop_area.dnd_bind("<<Drop>>", self.upload_file_drop_start)
        
        # Carrega a lista de arquivos inicial ao entrar na tela.
        self.list_files()

    # Envia o comando 'ls' e preenche a lista de arquivos com a resposta.
    def list_files(self):
        try:
            self.sock.sendto(b"ls", self.session_addr)
            data, _ = self.sock.recvfrom(4096)
            files = data.decode().split("\n")
            self.file_listbox.delete(0, tk.END)
            for f in sorted(files):
                if f and f.strip(): self.file_listbox.insert(tk.END, f)
        except socket.timeout:
            self.show_message("error", "Erro", "Servidor não respondeu ao comando 'ls'.")

    # Função visual para mudar de diretório.
    def cd_visual(self):
        try:
            # 1. Pede ao servidor a lista de diretórios disponíveis.
            self.sock.sendto(b"ls_dirs", self.session_addr)
            data, _ = self.sock.recvfrom(4096)
            dir_list = [d for d in data.decode().split("\n") if d]
            if not dir_list:
                self.show_message("info", "Mudar Diretório", "Nenhum subdiretório encontrado.")
                return
            # 2. Mostra a janela de diálogo para o usuário escolher.
            dialog = SelectDirectoryDialog(self.root, "Selecione um Diretório para Entrar", dir_list)
            selected_dir = dialog.result
            # 3. Se um diretório foi escolhido, envia o comando 'cd'.
            if selected_dir:
                self._send_simple_command(f"cd {selected_dir}")
        except socket.timeout:
            self.show_message("error", "Erro", "Servidor não respondeu ao pedido de diretórios.")
    
    # Função visual para remover um diretório.
    def rmdir_visual(self):
        try:
            self.sock.sendto(b"ls_dirs", self.session_addr)
            data, _ = self.sock.recvfrom(4096)
            dir_list = [d for d in data.decode().split("\n") if d]
            if not dir_list:
                self.show_message("info", "Remover Diretório", "Nenhum subdiretório para remover.")
                return
            dialog = SelectDirectoryDialog(self.root, "Selecione um Diretório para Remover", dir_list)
            selected_dir = dialog.result
            if selected_dir:
                # Pede uma confirmação extra antes de uma ação destrutiva.
                if messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover o diretório '{selected_dir}'?"):
                    self._send_simple_command(f"rmdir {selected_dir}")
        except socket.timeout:
            self.show_message("error", "Erro", "Servidor não respondeu ao pedido de diretórios.")

    # Funções de atalho para comandos de navegação.
    def cd_back(self):
        self._send_simple_command("cd ..")

    def go_to_root(self):
        self._send_simple_command("cd /")

    # Função para o comando 'mkdir' que pede um input de texto.
    def mkdir(self):
        self._generic_command_with_input("mkdir", "Criar Diretório", "Nome do novo diretório:")

    # Função auxiliar para comandos que precisam de um input de texto simples.
    def _generic_command_with_input(self, cmd, title, prompt):
        param = simpledialog.askstring(title, prompt)
        if param: self._send_simple_command(f"{cmd} {param}")

    # Função auxiliar que encapsula o envio de um comando simples e o recebimento de uma resposta.
    def _send_simple_command(self, command_str):
        try:
            self.sock.sendto(command_str.encode(), self.session_addr)
            data, _ = self.sock.recvfrom(1024)
            response = data.decode()
            if response.startswith("ERRO"):
                self.show_message("error", "Erro do Servidor", response)
            else:
                self.show_message("info", "Resposta do Servidor", response)
            self.list_files() # Atualiza a lista de arquivos após o comando.
        except socket.timeout:
            self.show_message("error", "Erro", f"Servidor não respondeu ao comando '{command_str.split(' ')[0]}'.")

    # Função chamada pelo evento de arrastar e soltar.
    def upload_file_drop_start(self, event):
        filepath = event.data.strip('{}')
        if not os.path.isfile(filepath): return
        # Inicia a thread de upload para não travar a GUI.
        threading.Thread(target=self._threaded_upload, args=(filepath,), daemon=True).start()

    # Função chamada pelo botão "Enviar Arquivo".
    def upload_file_dialog_start(self):
        filepath = filedialog.askopenfilename()
        if not filepath: return
        # Inicia a thread de upload para não travar a GUI.
        threading.Thread(target=self._threaded_upload, args=(filepath,), daemon=True).start()

    # Função que executa em uma thread para fazer o upload de um arquivo.
    def _threaded_upload(self, filepath):
        filename = os.path.basename(filepath)
        try:
            self.sock.sendto(f"put {filename}".encode(), self.session_addr)
            start_signal, _ = self.sock.recvfrom(1024)
            if start_signal != MSG_START:
                self.show_message("error", "Erro", "Servidor não iniciou a recepção.")
                return

            with open(filepath, "rb") as f:
                seq_num = 0
                while True:
                    chunk = f.read(BUFFER_SIZE)
                    if not chunk: break
                    packet = struct.pack("!I", seq_num) + chunk
                    self.sock.sendto(packet, self.session_addr)
                    try:
                        ack, _ = self.sock.recvfrom(1024)
                        if ack.decode() == f"ACK{seq_num}":
                            seq_num += 1
                        else: f.seek(-len(chunk), 1) # Retransmite se o ACK for incorreto.
                    except socket.timeout:
                        f.seek(-len(chunk), 1) # Retransmite em caso de timeout.
            
            self.sock.sendto(MSG_END, self.session_addr)

            # Espera pela confirmação final 'PUT_OK' do servidor.
            try:
                final_ack, _ = self.sock.recvfrom(1024)
                if final_ack == MSG_PUT_OK:
                    self.show_message("info", "Upload", f"Arquivo '{filename}' enviado e confirmado com sucesso!")
                    self.root.after(0, self.list_files)
                else:
                    self.show_message("warning", "Upload", "Arquivo enviado, mas confirmação final do servidor falhou.")
            except socket.timeout:
                self.show_message("error", "Erro de Confirmação", "Arquivo enviado, mas o servidor não confirmou o recebimento.")

        except socket.timeout:
            self.show_message("error", "Erro", "Timeout durante o upload do arquivo.")

    # Função de entrada para iniciar o download.
    def download_file_start(self):
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            self.show_message("warning", "Aviso", "Nenhum arquivo selecionado.")
            return
        filename = self.file_listbox.get(selected_indices[0])
        save_path = filedialog.asksaveasfilename(initialfile=filename)
        if not save_path: return
        # Inicia a thread de download para não travar a GUI.
        threading.Thread(target=self._threaded_download, args=(filename, save_path), daemon=True).start()

    # Função que executa em uma thread para baixar um arquivo.
    def _threaded_download(self, filename, save_path):
        try:
            # Impede o download de um diretório.
            if filename.endswith("/"):
                self.show_message("error", "Erro", "Não é possível baixar um diretório.")
                return
            self.sock.sendto(f"get {filename}".encode(), self.session_addr)
            with open(save_path, "wb") as f:
                expected_seq_num = 0
                while True:
                    packet, _ = self.sock.recvfrom(BUFFER_SIZE + 4)
                    if packet.startswith(b"END_ERROR"):
                        self.show_message("error", "Erro no Servidor", packet.decode().split(":",1)[1])
                        os.remove(save_path)
                        return
                    if packet == MSG_END:
                        break
                    
                    seq_num = struct.unpack("!I", packet[:4])[0]
                    if seq_num == expected_seq_num:
                        f.write(packet[4:])
                        self.sock.sendto(f"ACK{seq_num}".encode(), self.session_addr)
                        expected_seq_num += 1
                    else:
                        self.sock.sendto(f"ACK{expected_seq_num - 1}".encode(), self.session_addr)
            self.show_message("info", "Download", f"Arquivo '{filename}' baixado com sucesso!")
        except socket.timeout:
            self.show_message("error", "Erro", "Timeout durante o download do arquivo.")
            if os.path.exists(save_path): os.remove(save_path)

    # Envia o comando 'quit' e fecha a aplicação.
    def quit_client(self):
        if self.session_addr:
            try: self.sock.sendto(b"quit", self.session_addr)
            except Exception: pass
        self.sock.close()
        self.root.destroy()
    
    # Limpa todos os widgets da janela, usado para trocar de tela.
    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # Função thread-safe para mostrar caixas de mensagem a partir de qualquer thread.
    def show_message(self, mtype, title, message):
        self.root.after(0, lambda: getattr(messagebox, f"show{mtype}")(title, message))

# Ponto de entrada do programa cliente.
if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ClientGUI(root)
    # Garante que a função quit_client seja chamada ao fechar a janela.
    root.protocol("WM_DELETE_WINDOW", app.quit_client)
    root.mainloop()