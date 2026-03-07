import socket
import time
import random
import json
import sys
from utils import load_config

def run_client(my_client_id, target_node_id, cluster_config):
    """
    Função principal que simula o comportamento de um cliente.
    """
    
    # 1. Validação: Verifica se o ID do nó que queremos atacar existe no config.json
    if target_node_id not in cluster_config:
        print(f"❌ ERRO: Nó alvo {target_node_id} inválido.")
        return

    # Pega o IP e Porta do nó alvo (Ex: node1, 5001)
    target_address = cluster_config[target_node_id]
    
    # 2. Configuração de Rede (UDP)
    # SOCK_DGRAM indica que estamos usando UDP.
    # O cliente manda a mensagem e "esquece", esperando uma resposta depois.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Timeout de 20 segundos.
    # Se o Nó não responder em 20s (porque caiu ou travou), o cliente desiste desse pedido.
    sock.settimeout(20)

    # Define quantas vezes esse cliente vai tentar escrever no arquivo.
    num_acessos = 20
    
    # --- Loop de Requisições ---
    for i in range(num_acessos):
        
        # Gera o Timestamp atual. 
        # IMPORTANTE: Em Ricart-Agrawala, esse timestamp define a prioridade.
        timestamp = time.time()
        
        # Cria o pacote de dados em formato JSON
        msg = json.dumps({
            'type': 'CLIENT_REQUEST', # Avisa o nó que somos um cliente externo
            'client_id': my_client_id, # Quem sou eu (Ex: Cliente_A)
            'timestamp': timestamp     # Quando eu pedi
        })
        
        # Envia via UDP para o nó alvo
        # .encode() transforma a string JSON em bytes para viajar na rede
        sock.sendto(msg.encode(), target_address)
        
        try:
            # Fica esperando a resposta do nó (Bloqueia aqui até chegar)
            # 1024 é o tamanho máximo do buffer (em bytes)
            data, _ = sock.recvfrom(1024)
            
            # Decodifica a resposta
            resp = json.loads(data.decode())
            
            # Se o nó respondeu COMMITTED, significa que ele conseguiu entrar na Seção Crítica,
            # escreveu no Resource Server e já saiu.
            if resp.get('type') == 'COMMITTED':
                print(f"✅ [{my_client_id}] Pedido {i+1} atendido com sucesso.")
                
        except socket.timeout:
            # Se passou 20s e ninguém respondeu...
            print(f"⚠️ [{my_client_id}] Timeout no pedido {i+1}. O nó pode estar morto ou sobrecarregado.")
        
        # Simula um comportamento humano real.
        # O usuário não clica instantaneamente. Ele espera entre 1 e 5 segundos
        # antes de fazer o próximo pedido. Isso ajuda a variar a carga no sistema.
        time.sleep(random.uniform(1, 5))

if __name__ == "__main__":
    # Validação dos argumentos da linha de comando
    if len(sys.argv) != 3:
        print("Uso: python client.py <NOME> <ID_ALVO>")
        sys.exit(1)

    # Pega os argumentos passados pelo Docker ou Terminal
    # Ex: python client.py Cliente_A 1
    client_id, target_id = sys.argv[1], int(sys.argv[2])
    
    # Carrega a configuração.
    # O "_" (underscore) é usado para ignorar a segunda variável retornada (rs_config).
    # O cliente não precisa saber onde fica o Resource Server, só o Nó precisa.
    nodes_conf, _ , _ = load_config()
    
    # Inicia o ataque!
    run_client(client_id, target_id, nodes_conf)