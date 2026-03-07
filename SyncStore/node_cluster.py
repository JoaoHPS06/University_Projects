"""
node_cluster.py — Cluster Sync (Ricart-Agrawala, TP2 base)

Mudança em relação ao TP2:
  - A "seção crítica simulada" (time.sleep) foi substituída por acesso REAL
    ao Cluster Store via _write_to_store().
  - O nó tenta escrever no primário atual do Cluster Store.
  - Em caso de falha ou REDIRECT, ele retenta até MAX_STORE_RETRIES vezes,
    percorrendo os nós do Store em ordem de prioridade.

Todo o resto (Ricart-Agrawala, comunicação com clientes, UDP) é idêntico ao TP2.
"""

import socket
import threading
import time
import json
import sys
from utils import load_config
from logger import (init_log, sync_client_request, sync_ra_request_sent,
                    sync_ra_deferred, sync_ra_approved, sync_critical_enter,
                    sync_critical_exit, sync_store_attempt, sync_store_ok,
                    sync_store_fail, sync_store_redirect, sync_store_exhausted,
                    sync_ra_ok_received)

# --- CORES PARA O TERMINAL ---
RESET   = "\033[0m"
BOLD    = "\033[1m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"

# Quantas vezes o Sync Node tenta escrever no Store antes de desistir
MAX_STORE_RETRIES = 3
# Timeout (segundos) ao conectar/escrever no Store
STORE_TIMEOUT = 2


class RicartAgrawalaNode:
    def __init__(self, my_id, cluster_config, rs_config, store_config):
        self.id           = my_id
        self.cluster_nodes = cluster_config
        self.rs_host, self.rs_port = rs_config
        self.store_nodes  = store_config   # {1:('store1',7001), ...}

        # Cached: qual nó Store o Sync acredita ser o primário.
        # Começa pelo menor ID (convenção). Atualizado via REDIRECT.
        self.store_primary_id = min(store_config.keys())

        my_ip, my_port = self.cluster_nodes[my_id]

        # --- ESTADOS RICART-AGRAWALA ---
        self.state       = 'RELEASED'
        self.my_timestamp = 0
        self.num_oks     = 0
        self.defer_queue = []
        self.lock        = threading.Lock()
        self.reply_event = threading.Event()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('0.0.0.0', my_port))

        print(f"{BOLD}✅ Node {self.id} online! Porta {my_port}{RESET}")
        init_log()

    # =========================================================================
    # CICLO DE VIDA
    # =========================================================================

    def start(self):
        threading.Thread(target=self.listen_messages, daemon=True).start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def listen_messages(self):
        while True:
            try:
                data, addr = self.server_socket.recvfrom(2048)
                msg = json.loads(data.decode())

                if   msg['type'] == 'CLIENT_REQUEST':
                    threading.Thread(
                        target=self.handle_client_request, args=(msg, addr)
                    ).start()
                elif msg['type'] == 'REQUEST':
                    self.handle_node_request(msg)
                elif msg['type'] == 'OK':
                    self.handle_ok(msg)

            except Exception as e:
                print(f"⚠️ Erro no listener: {e}")

    # =========================================================================
    # GERENCIAMENTO DO PEDIDO DO CLIENTE
    # =========================================================================

    def handle_client_request(self, msg, client_addr):
        client_id     = msg.get('client_id')
        req_timestamp = msg.get('timestamp')

        sync_client_request(self.id, client_id, req_timestamp)

        # 1. Ricart-Agrawala: aguarda permissão de todos os peers
        self.request_critical_section(req_timestamp)

        # 2. SEÇÃO CRÍTICA REAL: escreve no Cluster Store
        sync_critical_enter(self.id)

        # request_id único para idempotência (sub-caso 2.3)
        request_id = f"{self.id}-{client_id}-{req_timestamp}"
        content    = f"Acesso de {client_id} via Sync Node {self.id}"

        success = self._write_to_store(request_id, content)
        if not success:
            sync_store_exhausted(self.id, MAX_STORE_RETRIES)

        # 3. Libera a seção crítica
        self.release_critical_section()

        # 4. Responde ao cliente
        response = json.dumps({'type': 'COMMITTED', 'node_id': self.id})
        self.server_socket.sendto(response.encode(), client_addr)

    # =========================================================================
    # ESCRITA NO CLUSTER STORE (Protocolo 1 — cliente)
    # =========================================================================

    def _write_to_store(self, request_id, content):
        """
        Tenta escrever no primário do Cluster Store.
        - Se receber REDIRECT, atualiza o primário cached e retenta.
        - Se receber timeout/conexão recusada, tenta o próximo nó na ordem.
        - Retorna True se obteve WRITE_OK, False após MAX_STORE_RETRIES falhas.

        Cobre os sub-casos:
          2.2 — Nó Store cai com pedido pendente → Sync recebe timeout → retenta
          2.3 — Nó Store cai durante escrita   → request_id garante idempotência
        """
        # Ordena nós do Store por ID para ter ordem determinística de fallback
        ordered_store_ids = sorted(self.store_nodes.keys())

        # Garante que tentamos o primário cached primeiro
        if self.store_primary_id in ordered_store_ids:
            ordered_store_ids.remove(self.store_primary_id)
            ordered_store_ids.insert(0, self.store_primary_id)

        msg = json.dumps({
            'type':       'WRITE',
            'node_id':    self.id,
            'content':    content,
            'request_id': request_id
        })

        attempts = 0
        tried    = set()

        for store_id in ordered_store_ids:
            if attempts >= MAX_STORE_RETRIES:
                break
            if store_id in tried:
                continue

            tried.add(store_id)
            attempts += 1

            host, port = self.store_nodes[store_id]
            sync_store_attempt(self.id, store_id, host, port, attempts, MAX_STORE_RETRIES)

            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(STORE_TIMEOUT)
                s.connect((host, port))
                s.sendall(msg.encode())
                raw = s.recv(1024).decode()
                s.close()
                resp = json.loads(raw)

                if resp.get('type') == 'WRITE_OK':
                    # Atualiza cache do primário para requisições futuras
                    sync_store_ok(self.id, store_id, resp.get('replicas', 0))
                    return True

                elif resp.get('type') == 'REDIRECT':
                    # O nó nos indicou o verdadeiro primário
                    new_primary    = resp.get('primary_id')
                    new_prim_host  = resp.get('primary_host')
                    new_prim_port  = resp.get('primary_port')
                    sync_store_redirect(self.id, store_id, new_primary)
                    self.store_primary_id = new_primary

                    # Só segue o redirect se ainda não tentamos esse nó
                    if new_primary not in tried and attempts < MAX_STORE_RETRIES:
                        tried.add(new_primary)
                        attempts += 1
                        try:
                            s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s2.settimeout(STORE_TIMEOUT)
                            s2.connect((new_prim_host, new_prim_port))
                            s2.sendall(msg.encode())
                            raw2 = s2.recv(1024).decode()
                            s2.close()
                            resp2 = json.loads(raw2)
                            if resp2.get('type') == 'WRITE_OK':
                                sync_store_ok(self.id, new_primary, resp2.get('replicas', 0))
                                return True
                        except Exception as e:
                            sync_store_fail(self.id, new_primary, e)
                    # Se já tentamos, ignora e continua o loop para o próximo nó

            except Exception as e:
                # Sub-caso 2.2: Store com pedido pendente caiu → timeout aqui
                sync_store_fail(self.id, store_id, e)

        return False  # Todas as tentativas falharam

    # =========================================================================
    # RICART-AGRAWALA (idêntico ao TP2)
    # =========================================================================

    def request_critical_section(self, timestamp):
        with self.lock:
            self.state        = 'WANTED'
            self.my_timestamp = timestamp
            self.num_oks      = 0
            self.reply_event.clear()

        request_msg = json.dumps({
            'type': 'REQUEST', 'node_id': self.id, 'timestamp': self.my_timestamp
        })
        peers = [nid for nid in self.cluster_nodes if nid != self.id]

        if not peers:
            with self.lock:
                self.state = 'HELD'
            return

        sync_ra_request_sent(self.id, self.my_timestamp, peers)
        for peer_id in peers:
            self.send_message(peer_id, request_msg)

        needed_oks = len(self.cluster_nodes) - 1
        while self.num_oks < needed_oks:
            self.reply_event.wait()
            self.reply_event.clear()

        with self.lock:
            self.state = 'HELD'

    def handle_node_request(self, msg):
        req_id, req_ts = msg['node_id'], msg['timestamp']
        send_ok = False

        with self.lock:
            if self.state == 'RELEASED':
                send_ok = True

            elif self.state == 'HELD':
                self.defer_queue.append(req_id)
                sync_ra_deferred(self.id, req_id, req_ts, self.my_timestamp)

            elif self.state == 'WANTED':
                if (req_ts < self.my_timestamp) or \
                   (req_ts == self.my_timestamp and req_id < self.id):
                    send_ok = True
                    sync_ra_approved(self.id, req_id, req_ts, self.my_timestamp)
                else:
                    self.defer_queue.append(req_id)
                    sync_ra_deferred(self.id, req_id, req_ts, self.my_timestamp)

        if send_ok:
            self.send_ok(req_id)

    def handle_ok(self, msg):
        with self.lock:
            self.num_oks += 1
            sync_ra_ok_received(self.id, msg['node_id'], self.num_oks, len(self.cluster_nodes) - 1)
            if self.num_oks >= (len(self.cluster_nodes) - 1):
                self.reply_event.set()

    def release_critical_section(self):
        with self.lock:
            self.state = 'RELEASED'
            sync_critical_exit(self.id)
            for node_id in self.defer_queue:
                self.send_ok(node_id)
            self.defer_queue = []

    def send_ok(self, target_id):
        self.send_message(target_id, json.dumps({'type': 'OK', 'node_id': self.id}))

    def send_message(self, target_id, msg):
        ip, port = self.cluster_nodes[target_id]
        self.server_socket.sendto(msg.encode(), (ip, port))


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python node_cluster.py <ID>")
        sys.exit(1)

    my_id = int(sys.argv[1])
    nodes_conf, rs_conf, store_conf = load_config()
    node = RicartAgrawalaNode(my_id, nodes_conf, rs_conf, store_conf)
    node.start()
