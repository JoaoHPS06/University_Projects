import json
import os
import sys

def load_config(file_path='config.json'):
    """
    Função Utilitária: Carrega as configurações de rede.
    Retorna uma tupla contendo:
    1. nodes_config:      {1: ('node1', 5001), ...}
    2. rs_config:         ('resource_server', 6000)
    3. store_nodes_config:{1: ('store1', 7001), 2: ('store2', 7002), 3: ('store3', 7003)}
    """
    if not os.path.exists(file_path):
        print(f"❌ ERRO CRÍTICO: O arquivo '{file_path}' não foi encontrado!")
        sys.exit(1)

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        # --- Nós do Cluster Sync (TP2) ---
        nodes_config = {}
        for key, value in data['nodes'].items():
            nodes_config[int(key)] = (value[0], int(value[1]))

        # --- Resource Server (Auditor) ---
        rs_raw = data['resource_server']
        rs_config = (rs_raw[0], int(rs_raw[1]))

        # --- Nós do Cluster Store (TP3) ---
        # Mesma lógica: chaves string → int, porta forçada como int
        store_config = {}
        for key, value in data['store_nodes'].items():
            store_config[int(key)] = (value[0], int(value[1]))

        return nodes_config, rs_config, store_config

    except Exception as e:
        print(f"❌ ERRO ao ler configuração (JSON inválido?): {e}")
        sys.exit(1)
