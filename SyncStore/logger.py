"""
logger.py — Logger estruturado para o TP3

Gera dois tipos de saída:
  1. Terminal colorido (igual ao que já existia, mas mais rico)
  2. Arquivo JSON Lines (audit_structured.jsonl) — cada linha é um evento JSON
     que pode ser consumido por ferramentas de análise externas.

Formato de cada linha do JSONL:
{
  "ts": 1772487110.30,          # timestamp UNIX de alta precisão
  "time": "18:31:50.303",       # horário legível (Brasília UTC-3)
  "node_type": "SYNC"|"STORE",  # tipo do nó emissor
  "node_id": 2,                 # ID do nó emissor
  "event": "CRITICAL_ENTER",    # código do evento (ver tabela abaixo)
  "data": { ... }               # dados extras dependendo do evento
}

Códigos de evento:
  SYNC: CLIENT_REQUEST, RA_REQUEST_SENT, RA_DEFERRED, RA_APPROVED, RA_OK_RECEIVED,
        CRITICAL_ENTER, CRITICAL_EXIT, STORE_WRITE_ATTEMPT, STORE_WRITE_OK,
        STORE_WRITE_FAIL, STORE_REDIRECT, STORE_TIMEOUT
  STORE: WRITE_PRIMARY, WRITE_REPLICA, WRITE_OK, REPLICA_OK, REPLICA_FAIL,
         PING_SENT, PONG_RECEIVED, NODE_DOWN, NODE_UP, ELECTION_START, ELECTION_DONE,
         REDIRECT_SENT
"""

import json
import os
import time
import datetime
import threading

# ---- Cores ANSI ----
RESET   = "\033[0m"
BOLD    = "\033[1m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"
BLUE    = "\033[94m"
WHITE   = "\033[97m"

# Fuso Brasília
_TZ = datetime.timezone(datetime.timedelta(hours=-3))

# Lock global para gravação no arquivo
_file_lock = threading.Lock()
_LOG_FILE  = "audit_structured.jsonl"

# =====================================================================
# Inicialização
# =====================================================================

def init_log():
    """Chame uma vez ao iniciar cada processo."""
    with _file_lock:
        with open(_LOG_FILE, "a") as f:
            pass  # apenas garante que o arquivo existe

# =====================================================================
# Função central
# =====================================================================

def log(node_type: str, node_id: int, event: str, msg: str,
        color: str = RESET, data: dict = None):
    """
    Emite uma entrada de log no terminal E no arquivo JSONL.

    Args:
        node_type: "SYNC" | "STORE"
        node_id:   ID inteiro do nó
        event:     código do evento (string sem espaços)
        msg:       mensagem legível para o terminal
        color:     código ANSI para colorir o terminal
        data:      dicionário com dados extras (opcional)
    """
    now_ts   = time.time()
    now_str  = datetime.datetime.now(_TZ).strftime("%H:%M:%S.%f")[:-3]

    # ---- Terminal ----
    prefix = f"[{now_str}][{node_type}{node_id}][{event}]"
    print(f"{color}{BOLD}{prefix}{RESET} {color}{msg}{RESET}")

    # ---- Arquivo JSONL ----
    entry = {
        "ts":        now_ts,
        "time":      now_str,
        "node_type": node_type,
        "node_id":   node_id,
        "event":     event,
        "msg":       msg,
        "data":      data or {}
    }
    with _file_lock:
        try:
            with open(_LOG_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
                f.flush(); os.fsync(f.fileno())
        except Exception as e:
            print(f"{RED}[LOGGER] Erro ao gravar log: {e}{RESET}")

# =====================================================================
# Helpers semânticos — SYNC NODE
# =====================================================================

def sync_client_request(node_id, client_id, req_ts):
    log("SYNC", node_id, "CLIENT_REQUEST",
        f"Pedido de {client_id} | TS={req_ts:.3f}",
        MAGENTA, {"client_id": client_id, "req_ts": req_ts})

def sync_ra_request_sent(node_id, my_ts, peers):
    log("SYNC", node_id, "RA_REQUEST_SENT",
        f"REQUEST broadcast para {peers} | meu TS={my_ts:.3f}",
        CYAN, {"my_ts": my_ts, "peers": peers})

def sync_ra_deferred(node_id, from_id, their_ts, my_ts):
    log("SYNC", node_id, "RA_DEFERRED",
        f"Pedido de Sync{from_id} (TS={their_ts:.3f}) POSTERGADO — eu tenho prioridade (TS={my_ts:.3f})",
        RED, {"from_id": from_id, "their_ts": their_ts, "my_ts": my_ts})

def sync_ra_approved(node_id, from_id, their_ts, my_ts):
    log("SYNC", node_id, "RA_APPROVED",
        f"Pedido de Sync{from_id} (TS={their_ts:.3f}) APROVADO — ele pediu antes (TS={my_ts:.3f})",
        YELLOW, {"from_id": from_id, "their_ts": their_ts, "my_ts": my_ts})

def sync_ra_ok_received(node_id, from_id, total_oks, needed):
    log("SYNC", node_id, "RA_OK_RECEIVED",
        f"OK de Sync{from_id} | progresso: {total_oks}/{needed}",
        CYAN, {"from_id": from_id, "total_oks": total_oks, "needed": needed})

def sync_critical_enter(node_id):
    log("SYNC", node_id, "CRITICAL_ENTER",
        "━━━ ENTROU NA SEÇÃO CRÍTICA ━━━",
        GREEN)

def sync_critical_exit(node_id, duration_s=None):
    extra = f" | duração={duration_s:.2f}s" if duration_s else ""
    log("SYNC", node_id, "CRITICAL_EXIT",
        f"━━━ SAIU DA SEÇÃO CRÍTICA{extra} ━━━",
        GREEN, {"duration_s": duration_s})

def sync_store_attempt(node_id, store_id, host, port, attempt, max_attempts):
    log("SYNC", node_id, "STORE_WRITE_ATTEMPT",
        f"Tentativa {attempt}/{max_attempts} → Store{store_id} ({host}:{port})",
        CYAN, {"store_id": store_id, "attempt": attempt, "max_attempts": max_attempts})

def sync_store_ok(node_id, store_id, replicas):
    log("SYNC", node_id, "STORE_WRITE_OK",
        f"WRITE_OK do Store{store_id} com {replicas} réplica(s)",
        GREEN, {"store_id": store_id, "replicas": replicas})

def sync_store_fail(node_id, store_id, reason):
    log("SYNC", node_id, "STORE_WRITE_FAIL",
        f"Falha ao escrever no Store{store_id}: {reason}",
        RED, {"store_id": store_id, "reason": str(reason)})

def sync_store_redirect(node_id, from_store, new_primary):
    log("SYNC", node_id, "STORE_REDIRECT",
        f"Store{from_store} redirecionou → primário é Store{new_primary}",
        YELLOW, {"from_store": from_store, "new_primary": new_primary})

def sync_store_exhausted(node_id, attempts):
    log("SYNC", node_id, "STORE_EXHAUSTED",
        f"FALHA TOTAL: esgotou {attempts} tentativas no Cluster Store",
        RED, {"attempts": attempts})

# =====================================================================
# Helpers semânticos — STORE NODE
# =====================================================================

def store_write_primary(node_id, sync_id, req_id):
    log("STORE", node_id, "WRITE_PRIMARY",
        f"Recebeu WRITE do Sync{sync_id} | req_id={req_id}",
        GREEN, {"sync_id": sync_id, "req_id": req_id})

def store_write_replica(node_id, sync_id, req_id):
    log("STORE", node_id, "WRITE_REPLICA",
        f"Replicando write do Sync{sync_id} | req_id={req_id}",
        CYAN, {"sync_id": sync_id, "req_id": req_id})

def store_write_ok(node_id, sync_id, replica_count):
    log("STORE", node_id, "WRITE_OK",
        f"WRITE_OK → Sync{sync_id} | {replica_count} réplica(s) confirmada(s)",
        GREEN, {"sync_id": sync_id, "replica_count": replica_count})

def store_replica_fail(node_id, backup_id, reason):
    log("STORE", node_id, "REPLICA_FAIL",
        f"Backup Store{backup_id} não respondeu: {reason}",
        RED, {"backup_id": backup_id, "reason": str(reason)})

def store_redirect_sent(node_id, to_sync, real_primary):
    log("STORE", node_id, "REDIRECT_SENT",
        f"Redirecionando Sync{to_sync} → primário é Store{real_primary}",
        YELLOW, {"real_primary": real_primary})

def store_node_down(node_id, dead_id):
    log("STORE", node_id, "NODE_DOWN",
        f"Store{dead_id} não responde ao PING — marcado como morto",
        RED, {"dead_id": dead_id})

def store_node_up(node_id, recovered_id):
    log("STORE", node_id, "NODE_UP",
        f"Store{recovered_id} voltou a responder",
        GREEN, {"recovered_id": recovered_id})

def store_election_start(node_id, dead_primary):
    log("STORE", node_id, "ELECTION_START",
        f"Primário Store{dead_primary} caiu — iniciando eleição",
        YELLOW, {"dead_primary": dead_primary})

def store_election_done(node_id, new_primary, my_role):
    log("STORE", node_id, "ELECTION_DONE",
        f"Eleição concluída → Store{new_primary} é o novo primário | meu papel: {my_role}",
        BOLD + YELLOW, {"new_primary": new_primary, "my_role": my_role})

def store_duplicate_ignored(node_id, req_id):
    log("STORE", node_id, "DUPLICATE_IGNORED",
        f"req_id={req_id} já processado — escrita duplicada ignorada (idempotência)",
        YELLOW, {"req_id": req_id})
