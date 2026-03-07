"""
store_node.py — Cluster Store (Protocolo 1: Primário Fixo com Backups)

Papel de cada nó:
  - O nó com menor ID vivo é sempre o PRIMÁRIO.
  - Os demais são BACKUPS.
  - O primário recebe escritas dos Sync Nodes, replica para backups,
    e só confirma (WRITE_OK) quando todos os backups vivos responderam.

Tolerância a falhas (Opção 2):
  - Sub-caso 2.1: Nó idle falha → PING periódico detecta; backup promove.
  - Sub-caso 2.2: Nó falha com pedido pendente → Sync recebe timeout e retenta.
  - Sub-caso 2.3: Nó falha durante escrita → writes são idempotentes (por request_id);
                  Sync retenta com segurança sem duplicar entradas no log.
"""

import socket
import threading
import time
import json
import os
import datetime
import sys
from utils import load_config
from logger import (init_log, store_write_primary, store_write_replica,
                    store_write_ok, store_replica_fail, store_redirect_sent,
                    store_node_down, store_node_up, store_election_start,
                    store_election_done, store_duplicate_ignored)

# ---- Cores ANSI ----
RESET   = "\033[0m"
BOLD    = "\033[1m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"

PING_INTERVAL   = 2
PING_TIMEOUT    = 1
WRITE_TIMEOUT   = 2
STARTUP_WAIT    = 4


class StoreNode:
    def __init__(self, my_id, store_config):
        self.id            = my_id
        self.store_nodes   = store_config          # {1:(host,port), 2:..., 3:...}
        self.lock          = threading.Lock()

        # --- Estado de Eleição ---
        # Invariante: primário = menor ID entre os nós vivos.
        # Começa assumindo que todos estão vivos.
        self.alive_nodes   = set(store_config.keys())
        self.primary_id    = min(self.alive_nodes)

        # --- Idempotência (Sub-caso 2.3) ---
        # Guarda os request_ids já processados para não duplicar entradas no log.
        self.seen_requests = set()

        # --- Log de dados ---
        # Cada nó mantém seu próprio arquivo de log (a "cópia local do recurso R").
        self.log_file = f"store_{my_id}.log"
        with open(self.log_file, 'w') as f:
            f.write(f"=== STORE NODE {my_id} — LOG INICIADO ===\n")
            f.flush(); os.fsync(f.fileno())

        # --- Socket TCP ----
        host, port = store_config[my_id]
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', port))
        self.server_socket.listen(20)

        role = "PRIMÁRIO" if self.id == self.primary_id else "BACKUP"
        print(f"{BOLD}✅ Store Node {self.id} ({role}) online! Porta {port}{RESET}")
        init_log()

    # =========================================================================
    # CICLO DE VIDA
    # =========================================================================

    def start(self):
        threading.Thread(target=self._accept_loop, daemon=True).start()
        threading.Thread(target=self._ping_loop,   daemon=True).start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def _accept_loop(self):
        """Aceita conexões TCP e despacha cada uma para uma thread."""
        while True:
            try:
                conn, _ = self.server_socket.accept()
                threading.Thread(
                    target=self._handle_connection, args=(conn,), daemon=True
                ).start()
            except Exception as e:
                print(f"⚠️ [Store {self.id}] Erro no accept: {e}")

    # =========================================================================
    # ROTEADOR DE MENSAGENS
    # =========================================================================

    def _handle_connection(self, conn):
        try:
            conn.settimeout(10)
            raw = conn.recv(4096).decode().strip()
            if not raw:
                return
            msg = json.loads(raw)

            t = msg.get('type')
            if   t == 'WRITE':         self._handle_write(conn, msg)
            elif t == 'WRITE_REPLICA': self._handle_write_replica(conn, msg)
            elif t == 'PING':          self._handle_ping(conn)
            elif t == 'PROMOTE':       self._handle_promote(msg)
        except Exception as e:
            print(f"⚠️ [Store {self.id}] Erro na conexão: {e}")
        finally:
            conn.close()

    # =========================================================================
    # PROTOCOLO 1 — ESCRITA
    # =========================================================================

    def _handle_write(self, conn, msg):
        """
        Recebe WRITE de um Sync Node.
        Se eu for o primário: grava local + replica para backups + responde WRITE_OK.
        Se não for: redireciona o Sync Node para o primário atual.
        """
        with self.lock:
            am_primary = (self.id == self.primary_id)
            current_primary = self.primary_id

        if not am_primary:
            # ---- Caso 2.2: Sync bateu na porta errada ou primário mudou ----
            p_host, p_port = self.store_nodes[current_primary]
            resp = json.dumps({
                'type':         'REDIRECT',
                'primary_id':   current_primary,
                'primary_host': p_host,
                'primary_port': p_port
            })
            conn.send(resp.encode())
            store_redirect_sent(self.id, msg.get('node_id', '?'), current_primary)
            return

        # ---- Sou o primário ----
        sync_id    = msg.get('node_id')
        content    = msg.get('content', '')
        request_id = msg.get('request_id', '')   # Para idempotência (sub-caso 2.3)

        store_write_primary(self.id, sync_id, request_id)

        # 1. Escreve localmente (idempotente)
        self._write_local(sync_id, content, request_id)

        # 2. Replica para todos os backups vivos
        with self.lock:
            backups = [nid for nid in self.alive_nodes if nid != self.id]

        replica_msg = json.dumps({
            'type':       'WRITE_REPLICA',
            'node_id':    sync_id,
            'content':    content,
            'request_id': request_id
        })

        ok_count = 0
        failed   = []
        for bid in backups:
            if self._replicate(bid, replica_msg):
                ok_count += 1
            else:
                failed.append(bid)

        # Marca backups que falharam como mortos
        if failed:
            with self.lock:
                for bid in failed:
                    self.alive_nodes.discard(bid)
                    store_replica_fail(self.id, bid, "sem resposta")

        # 3. Confirma para o Sync Node
        resp = json.dumps({
            'type':     'WRITE_OK',
            'node_id':  self.id,
            'replicas': ok_count
        })
        conn.send(resp.encode())
        store_write_ok(self.id, sync_id, ok_count)

    def _handle_write_replica(self, conn, msg):
        """Backup recebe replicação do primário."""
        sync_id    = msg.get('node_id')
        content    = msg.get('content', '')
        request_id = msg.get('request_id', '')

        store_write_replica(self.id, sync_id, request_id)
        self._write_local(sync_id, content, request_id)

        conn.send(json.dumps({'type': 'REPLICA_OK', 'node_id': self.id}).encode())

    def _replicate(self, backup_id, replica_msg_json):
        """Envia WRITE_REPLICA para um backup. Retorna True se obteve REPLICA_OK."""
        try:
            host, port = self.store_nodes[backup_id]
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(WRITE_TIMEOUT)
            s.connect((host, port))
            s.sendall(replica_msg_json.encode())
            data = s.recv(1024).decode()
            s.close()
            resp = json.loads(data)
            return resp.get('type') == 'REPLICA_OK'
        except Exception as e:
            print(f"⚠️ [PRIMÁRIO {self.id}] Falha ao replicar → Store {backup_id}: {e}")
            return False

    # =========================================================================
    # PERSISTÊNCIA (com idempotência para o sub-caso 2.3)
    # =========================================================================

    def _write_local(self, sync_id, content, request_id):
        """
        Grava entrada no log local.
        Se request_id já foi visto, ignora (write idempotente).
        """
        with self.lock:
            if request_id and request_id in self.seen_requests:
                store_duplicate_ignored(self.id, request_id)
                return
            if request_id:
                self.seen_requests.add(request_id)

        fuso = datetime.timezone(datetime.timedelta(hours=-3))
        now  = datetime.datetime.now(fuso).strftime("%H:%M:%S.%f")[:-3]
        entry = f"[{now}] Sync {sync_id} | {content}\n"

        with open(self.log_file, 'a') as f:
            f.write(entry)
            f.flush(); os.fsync(f.fileno())

    # =========================================================================
    # PING / DETECÇÃO DE FALHAS / ELEIÇÃO
    # =========================================================================

    def _handle_ping(self, conn):
        conn.send(json.dumps({'type': 'PONG', 'node_id': self.id}).encode())

    def _ping_loop(self):
        """
        Loop periódico de detecção de falhas (sub-casos 2.1 e 2.2).
        Cada nó verifica se seus pares estão vivos via PING TCP.
        Se detectar que o primário caiu, dispara eleição.
        """
        time.sleep(STARTUP_WAIT)   # Aguarda todos os containers subirem

        while True:
            time.sleep(PING_INTERVAL)
            peers = [nid for nid in self.store_nodes if nid != self.id]

            newly_dead  = []
            newly_alive = []

            for peer_id in peers:
                alive = self._ping(peer_id)
                with self.lock:
                    was_alive = peer_id in self.alive_nodes
                if alive and not was_alive:
                    newly_alive.append(peer_id)
                elif not alive and was_alive:
                    newly_dead.append(peer_id)

            if newly_dead or newly_alive:
                with self.lock:
                    for nid in newly_dead:
                        self.alive_nodes.discard(nid)
                        store_node_down(self.id, nid)
                    for nid in newly_alive:
                        self.alive_nodes.add(nid)
                        store_node_up(self.id, nid)

                    primary_died = any(nid == self.primary_id for nid in newly_dead)

                if primary_died:
                    store_election_start(self.id, self.primary_id)
                    self._elect_new_primary()

    def _ping(self, node_id):
        """Envia um PING TCP para o nó. Retorna True se recebeu PONG."""
        try:
            host, port = self.store_nodes[node_id]
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(PING_TIMEOUT)
            s.connect((host, port))
            s.sendall(json.dumps({'type': 'PING'}).encode())
            data = s.recv(256)
            s.close()
            resp = json.loads(data.decode())
            return resp.get('type') == 'PONG'
        except:
            return False

    def _elect_new_primary(self):
        """
        Eleição simples: menor ID entre os nós vivos torna-se primário.
        Garante consistência porque todos usam a mesma regra determinística.
        """
        with self.lock:
            if not self.alive_nodes:
                store_election_start(self.id, self.primary_id)
                return
            new_primary = min(self.alive_nodes)
            self.primary_id = new_primary
            role = "PRIMÁRIO" if new_primary == self.id else "BACKUP"
            store_election_done(self.id, new_primary, role)

        # Notifica os demais nós vivos sobre o novo primário
        notify_targets = []
        with self.lock:
            notify_targets = [nid for nid in self.alive_nodes if nid != self.id]

        for nid in notify_targets:
            self._notify_promote(nid, new_primary)

    def _notify_promote(self, target_id, new_primary_id):
        """Envia mensagem PROMOTE para que o alvo atualize seu primary_id."""
        try:
            host, port = self.store_nodes[target_id]
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((host, port))
            s.sendall(json.dumps({
                'type':        'PROMOTE',
                'new_primary': new_primary_id
            }).encode())
            s.close()
        except:
            pass  # Se falhou ao notificar, o destino descobrirá via PING também

    def _handle_promote(self, msg):
        """Recebe notificação de que o primário mudou."""
        new_primary = msg.get('new_primary')
        with self.lock:
            self.primary_id = new_primary
            role = "PRIMÁRIO" if new_primary == self.id else "BACKUP"
            store_election_done(self.id, new_primary, role)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python store_node.py <ID>")
        sys.exit(1)

    my_id = int(sys.argv[1])
    _, _, store_conf = load_config()

    node = StoreNode(my_id, store_conf)
    node.start()
