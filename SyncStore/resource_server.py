import socket
import threading
import datetime
import sys
import os  # <--- IMPORTANTE: Biblioteca necessária para interagir com o Sistema Operacional (fsync)
from utils import load_config

# --- Definição de Cores ANSI ---
# Usamos isso para colorir o terminal. Ajuda a identificar erros (Vermelho) rapidamente
# no meio de vários logs do Docker.
RED = "\033[91m"    # Vermelho: Usado para erros críticos e COLISÕES
GREEN = "\033[92m"  # Verde: Usado para sucesso (Entrada autorizada)
YELLOW = "\033[93m" # Amarelo: Avisos de inicialização
RESET = "\033[0m"   # Reseta a cor para o padrão do terminal (branco/cinza)

class ResourceServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
        # Contador vital: rastreia quantos nós estão na Seção Crítica AGORA.
        # Se este número passar de 1, o algoritmo falhou.
        self.active_writers = 0
        
        # Lock (Trava) de Thread:
        # Como o servidor atende vários nós ao mesmo tempo (multithread), precisamos
        # proteger a variável 'active_writers' para que duas threads não a alterem
        # exatamente no mesmo microssegundo, causando erro de contagem.
        self.lock = threading.Lock()
        
        # --- Configuração do Socket TCP ---
        # Usamos TCP (SOCK_STREAM) porque precisamos de uma conexão confiável e duradoura
        # enquanto o nó estiver escrevendo.
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # SO_REUSEADDR: Permite reiniciar o servidor rapidamente sem dar erro de 
        # "Address already in use" (porta presa pelo SO).
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        
        # Bind em '0.0.0.0': Faz o servidor escutar conexões vindas de qualquer lugar 
        # (seja do Docker, da rede local ou VPN).
        self.server_socket.bind(('0.0.0.0', self.port))
        
        # Listen(10): Define o tamanho da fila de espera de conexões.
        self.server_socket.listen(10) 
        
        # --- Inicialização do Arquivo de Log ---
        # O modo "w" (write) limpa o arquivo antigo sempre que o servidor reinicia.
        with open("audit.log", "w") as f:
            f.write("--- INICIO DA AUDITORIA ---\n")
            f.flush()            # Empurra os dados da memória do Python para o Buffer do SO
            os.fsync(f.fileno()) # Força o SO a gravar no Disco Físico agora (segurança contra crash)

        print(f"{YELLOW}👑 RESOURCE SERVER (AUDITOR) ONLINE na porta {self.port}{RESET}")
        print(f"{YELLOW}📝 Gravando logs em 'audit.log' (Modo Sincrono)...{RESET}")

    def start(self):
        # Loop Infinito Principal
        while True:
            # .accept() bloqueia a execução até alguém tentar conectar.
            # Retorna o socket do cliente e o endereço dele.
            client_socket, addr = self.server_socket.accept()
            
            # Cria uma nova Thread para atender esse cliente.
            # Isso é fundamental: libera o loop principal para aceitar novas conexões
            # imediatamente, permitindo concorrência.
            threading.Thread(target=self.handle_connection, args=(client_socket,)).start()

    def handle_connection(self, sock):
        """
        Lida com a sessão de um nó específico.
        """
        try:
            # Recebe a primeira mensagem (espera-se algo como "ACQUIRE 1")
            data = sock.recv(1024).decode().strip()
            if not data: return 
            
            parts = data.split()
            if len(parts) < 2: return # Validação simples para evitar erro
            
            command, node_id = parts[0], parts[1]
            
            if command == "ACQUIRE":
                # Se o comando for ACQUIRE, registramos que o nó ENTROU.
                self.log_access(node_id, "ENTER")
                
                # --- O PULO DO GATO ---
                # O servidor fica travado nesta linha (recv) esperando o nó terminar.
                # Enquanto a conexão estiver aberta aqui, o nó é considerado "ativo".
                # O nó só manda a próxima mensagem quando terminar o trabalho dele.
                data = sock.recv(1024).decode().strip()
                
                if data.startswith("RELEASE"):
                    # Se recebeu RELEASE, registramos que o nó SAIU.
                    self.log_access(node_id, "EXIT")
            
        except Exception as e:
            pass # Ignora erros de desconexão abrupta
        finally:
            # Sempre fecha o socket para liberar recursos do sistema
            sock.close()

    def log_access(self, node_id, action):
        """
        Função central de auditoria. Registra entrada/saída com horário preciso.
        """
        # Usa o Lock para garantir que logs não se misturem
        with self.lock:
            # --- Configuração do Horário (Timezone) ---
            # Cria um fuso horário com deslocamento de -3 horas (Brasília)
            fuso_brasilia = datetime.timezone(datetime.timedelta(hours=-3))
            # Pega a hora atual nesse fuso e formata para string
            now = datetime.datetime.now(fuso_brasilia).strftime("%H:%M:%S.%f")[:-3]
            
            if action == "ENTER":
                self.active_writers += 1 # Incrementa contador de escritores ativos
                status_color = GREEN
                
                # --- DETECÇÃO DE COLISÃO ---
                # Se já havia alguém escrevendo (active_writers > 1), acendemos o alerta vermelho!
                if self.active_writers > 1:
                    status_color = RED + "🚨 COLISÃO DETECTADA! "
                
                msg = f"[{now}] ✅ Nó {node_id} acessou o recurso. (Ativos: {self.active_writers})"
                
            elif action == "EXIT":
                self.active_writers -= 1 # Decrementa contador
                status_color = RESET
                msg = f"[{now}] 🏁 Nó {node_id} liberou o recurso. (Ativos: {self.active_writers})"

            # 1. Mostra no Terminal (Colorido)
            print(f"{status_color}{msg}{RESET}")
            
            # 2. Grava no Arquivo (Síncrono/Seguro)
            try:
                with open("audit.log", "a") as f:
                    f.write(msg + "\n")
                    f.flush()            # Limpa buffer do Python
                    os.fsync(f.fileno()) # Grava no disco físico imediatamente
            except Exception as e:
                print(f"❌ Erro crítico ao gravar arquivo: {e}")

if __name__ == "__main__":
    # Carrega as configurações (IP e Porta do Servidor de Recursos)
    _, rs_config, _ = load_config()
    host, port = rs_config
    
    # Instancia e inicia o servidor
    server = ResourceServer(host, port)
    server.start()