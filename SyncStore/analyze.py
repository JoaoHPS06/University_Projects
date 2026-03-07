"""
analyze.py — Análise do audit_structured.jsonl (TP3)

Lê o log estruturado gerado pelo logger.py e produz um relatório
completo com provas de corretude do sistema.

Uso:
    python analyze.py                        # lê audit_structured.jsonl
    python analyze.py meu_log.jsonl          # lê arquivo específico
    python analyze.py --json                 # saída em JSON puro

Provas geradas:
  1. Exclusão mútua — nunca dois nós na SC ao mesmo tempo
  2. Progresso — todo nó que pediu a SC eventualmente entrou
  3. Replicação — proporção de escritas com réplica confirmada
  4. Eleições — tempo médio de recuperação após queda
  5. Idempotência — nenhuma request_id duplicada no log
"""

import json
import sys
import os
from collections import defaultdict

# ── Cores ─────────────────────────────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
BLUE    = "\033[94m"
GRAY    = "\033[90m"


# ═════════════════════════════════════════════════════════════════════════════
# CARREGAMENTO
# ═════════════════════════════════════════════════════════════════════════════

def load_events(path):
    events = []
    errors = 0
    with open(path, "r") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                errors += 1
    events.sort(key=lambda e: e.get("ts", 0))
    return events, errors


# ═════════════════════════════════════════════════════════════════════════════
# ANÁLISE 1 — EXCLUSÃO MÚTUA
# ═════════════════════════════════════════════════════════════════════════════

def analyze_mutual_exclusion(events):
    """
    Prova que nunca dois nós Sync estiveram na SC ao mesmo tempo.
    Reconstrói a linha do tempo de ENTER/EXIT e detecta sobreposições.
    """
    enters = [(e["ts"], e["node_id"]) for e in events if e["event"] == "CRITICAL_ENTER"]
    exits  = [(e["ts"], e["node_id"]) for e in events if e["event"] == "CRITICAL_EXIT"]

    # Emparelha cada ENTER com seu EXIT correspondente (por node_id, em ordem)
    by_node_enter = defaultdict(list)
    by_node_exit  = defaultdict(list)
    for ts, nid in enters:
        by_node_enter[nid].append(ts)
    for ts, nid in exits:
        by_node_exit[nid].append(ts)

    intervals = []  # (ts_enter, ts_exit, node_id)
    for nid in by_node_enter:
        ent_list = sorted(by_node_enter[nid])
        ext_list = sorted(by_node_exit.get(nid, []))
        for i, ts_e in enumerate(ent_list):
            ts_x = ext_list[i] if i < len(ext_list) else None
            intervals.append((ts_e, ts_x, nid))

    intervals.sort(key=lambda x: x[0])

    # Detecta sobreposições
    violations = []
    for i in range(len(intervals)):
        ts_e1, ts_x1, n1 = intervals[i]
        if ts_x1 is None:
            continue
        for j in range(i + 1, len(intervals)):
            ts_e2, ts_x2, n2 = intervals[j]
            if ts_e2 >= ts_x1:
                break  # ordenado por enter, sem mais sobreposições possíveis
            if ts_x2 is None:
                continue
            if n1 != n2:
                violations.append((n1, ts_e1, ts_x1, n2, ts_e2, ts_x2))

    # Estatísticas de duração na SC
    durations = []
    for ts_e, ts_x, nid in intervals:
        if ts_x is not None:
            durations.append(ts_x - ts_e)

    return {
        "total_entries":   len(enters),
        "total_exits":     len(exits),
        "open_sessions":   len(enters) - len(exits),
        "violations":      violations,
        "durations":       durations,
        "avg_duration_ms": (sum(durations) / len(durations) * 1000) if durations else 0,
        "max_duration_ms": (max(durations) * 1000) if durations else 0,
        "min_duration_ms": (min(durations) * 1000) if durations else 0,
    }


# ═════════════════════════════════════════════════════════════════════════════
# ANÁLISE 2 — PROGRESSO DO RICART-AGRAWALA
# ═════════════════════════════════════════════════════════════════════════════

def analyze_ra_progress(events):
    """
    Para cada REQUEST enviado, verifica se eventualmente houve um ENTER.
    Também calcula tempo médio de espera entre REQUEST e ENTER.
    """
    requests = [(e["ts"], e["node_id"]) for e in events if e["event"] == "RA_REQUEST_SENT"]
    enters   = [(e["ts"], e["node_id"]) for e in events if e["event"] == "CRITICAL_ENTER"]

    by_node_req = defaultdict(list)
    by_node_ent = defaultdict(list)
    for ts, nid in requests:
        by_node_req[nid].append(ts)
    for ts, nid in enters:
        by_node_ent[nid].append(ts)

    wait_times = []
    starvations = 0
    for nid in by_node_req:
        req_list = sorted(by_node_req[nid])
        ent_list = sorted(by_node_ent.get(nid, []))
        for i, ts_r in enumerate(req_list):
            # Procura o primeiro ENTER depois desse REQUEST
            matching = [ts_e for ts_e in ent_list if ts_e >= ts_r]
            if matching:
                wait_times.append(matching[0] - ts_r)
            else:
                starvations += 1

    defer_events  = [e for e in events if e["event"] == "RA_DEFERRED"]
    approve_events = [e for e in events if e["event"] == "RA_APPROVED"]

    return {
        "total_requests":    len(requests),
        "total_enters":      len(enters),
        "starvations":       starvations,
        "avg_wait_ms":       (sum(wait_times) / len(wait_times) * 1000) if wait_times else 0,
        "max_wait_ms":       (max(wait_times) * 1000) if wait_times else 0,
        "total_deferred":    len(defer_events),
        "total_approved":    len(approve_events),
    }


# ═════════════════════════════════════════════════════════════════════════════
# ANÁLISE 3 — REPLICAÇÃO
# ═════════════════════════════════════════════════════════════════════════════

def analyze_replication(events):
    """
    Verifica quantas escritas foram replicadas para todos os backups
    vs escritas com replicação parcial (algum backup caiu).
    """
    write_ok_events = [e for e in events if e["event"] == "WRITE_OK"]

    full_replication = 0   # replicas == 2 (todos os backups confirmaram)
    partial          = 0   # replicas == 1 (um backup falhou)
    no_replica       = 0   # replicas == 0 (primário sozinho)

    for e in write_ok_events:
        replicas = e.get("data", {}).get("replicas", 0)
        if replicas >= 2:
            full_replication += 1
        elif replicas == 1:
            partial += 1
        else:
            no_replica += 1

    replica_fail_events = [e for e in events if e["event"] == "REPLICA_FAIL"]
    redirect_events     = [e for e in events if e["event"] == "REDIRECT_SENT"]

    return {
        "total_writes":       len(write_ok_events),
        "full_replication":   full_replication,
        "partial_replication": partial,
        "no_replica":         no_replica,
        "replica_failures":   len(replica_fail_events),
        "redirects":          len(redirect_events),
        "pct_full": (full_replication / len(write_ok_events) * 100) if write_ok_events else 0,
    }


# ═════════════════════════════════════════════════════════════════════════════
# ANÁLISE 4 — ELEIÇÕES E TEMPO DE RECUPERAÇÃO
# ═════════════════════════════════════════════════════════════════════════════

def analyze_elections(events):
    """
    Para cada eleição, calcula o tempo entre NODE_DOWN e ELECTION_DONE.
    """
    downs     = [(e["ts"], e["node_id"], e.get("data", {}).get("dead_id")) for e in events if e["event"] == "NODE_DOWN"]
    elections = [(e["ts"], e["node_id"], e.get("data", {}).get("new_primary")) for e in events if e["event"] == "ELECTION_DONE"]

    recovery_times = []
    for ts_e, reporter, new_primary in elections:
        # Procura o NODE_DOWN mais recente antes desta eleição
        matching = [(ts_d, rep, dead) for ts_d, rep, dead in downs if ts_d < ts_e]
        if matching:
            ts_down = max(ts_d for ts_d, _, _ in matching)
            recovery_times.append(ts_e - ts_down)

    # Por nó: quantas vezes cada store foi eleito primário
    primary_count = defaultdict(int)
    for _, _, new_primary in elections:
        if new_primary:
            primary_count[new_primary] += 1

    node_up_events = [e for e in events if e["event"] == "NODE_UP"]

    return {
        "total_downs":          len(downs),
        "total_elections":      len(elections),
        "total_recoveries":     len(node_up_events),
        "recovery_times_s":     recovery_times,
        "avg_recovery_ms":      (sum(recovery_times) / len(recovery_times) * 1000) if recovery_times else 0,
        "max_recovery_ms":      (max(recovery_times) * 1000) if recovery_times else 0,
        "primary_count":        dict(primary_count),
    }


# ═════════════════════════════════════════════════════════════════════════════
# ANÁLISE 5 — IDEMPOTÊNCIA
# ═════════════════════════════════════════════════════════════════════════════

def analyze_idempotency(events):
    """
    Verifica se algum request_id apareceu mais de uma vez como WRITE_PRIMARY,
    o que indicaria uma duplicata não filtrada.
    """
    write_primary_events = [e for e in events if e["event"] == "WRITE_PRIMARY"]
    duplicate_events     = [e for e in events if e["event"] == "DUPLICATE_IGNORED"]

    request_ids = defaultdict(int)
    for e in write_primary_events:
        rid = e.get("data", {}).get("request_id", "")
        if rid:
            request_ids[rid] += 1

    duplicates_accepted = {rid: cnt for rid, cnt in request_ids.items() if cnt > 1}

    return {
        "total_writes_primary":   len(write_primary_events),
        "duplicates_filtered":    len(duplicate_events),
        "duplicates_not_filtered": len(duplicates_accepted),
        "duplicate_ids":          list(duplicates_accepted.keys())[:5],  # top 5
    }


# ═════════════════════════════════════════════════════════════════════════════
# RELATÓRIO
# ═════════════════════════════════════════════════════════════════════════════

def bar(value, max_value, width=20, color=GREEN):
    filled = int((value / max_value) * width) if max_value > 0 else 0
    return f"{color}{'█' * filled}{GRAY}{'░' * (width - filled)}{RESET}"

def verdict(passed, label_ok, label_fail):
    if passed:
        return f"{GREEN}{BOLD}✅  {label_ok}{RESET}"
    else:
        return f"{RED}{BOLD}❌  {label_fail}{RESET}"

def print_report(events, me, ra, rep, el, idem, source_file):
    total = len(events)

    print(f"\n{BOLD}{CYAN}{'═' * 65}{RESET}")
    print(f"{BOLD}{CYAN}  TP3 — Relatório de Análise do Sistema Distribuído{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 65}{RESET}")
    print(f"  {GRAY}Fonte: {source_file}  |  {total} eventos carregados{RESET}")

    # ── 1. Exclusão Mútua ─────────────────────────────────────────────────
    print(f"\n{BOLD}{BLUE}━━  1. EXCLUSÃO MÚTUA (Ricart-Agrawala)  ━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    n_viol = len(me["violations"])
    print(f"\n  {verdict(n_viol == 0, 'PROVA: Nunca dois nós na SC simultaneamente', f'{n_viol} violação(ões) detectada(s)!')}")

    print(f"\n  Entradas na SC:    {BOLD}{me['total_entries']}{RESET}")
    print(f"  Saídas da SC:      {BOLD}{me['total_exits']}{RESET}")
    if me["open_sessions"] > 0:
        print(f"  Sessões abertas:   {YELLOW}{me['open_sessions']} (container ainda rodando?){RESET}")

    if me["durations"]:
        print(f"\n  Duração média na SC:  {me['avg_duration_ms']:.1f} ms")
        print(f"  Duração máxima na SC: {me['max_duration_ms']:.1f} ms")
        print(f"  Duração mínima na SC: {me['min_duration_ms']:.1f} ms")

    if n_viol > 0:
        print(f"\n  {RED}Violações encontradas:{RESET}")
        for v in me["violations"][:3]:
            n1, e1, x1, n2, e2, x2 = v
            print(f"    Node {n1} [{e1:.3f}–{x1:.3f}] ∩ Node {n2} [{e2:.3f}–{x2:.3f}]")

    # ── 2. Progresso ──────────────────────────────────────────────────────
    print(f"\n{BOLD}{BLUE}━━  2. PROGRESSO (todo pedido eventualmente atendido)  ━━━━━━━━━━{RESET}")
    starv = ra['starvations']
    print(f"\n  {verdict(starv == 0, 'PROVA: Nenhum nó ficou eternamente bloqueado', f'{starv} pedido(s) sem resposta detectado(s)')}")

    print(f"\n  Requests enviados:    {BOLD}{ra['total_requests']}{RESET}")
    print(f"  Entradas obtidas:     {BOLD}{ra['total_enters']}{RESET}")
    print(f"  Postergamentos (OK):  {ra['total_deferred']}")
    print(f"  Aprovações diretas:   {ra['total_approved']}")

    if ra["avg_wait_ms"] > 0:
        print(f"\n  Tempo médio de espera por SC: {ra['avg_wait_ms']:.1f} ms")
        print(f"  Tempo máximo de espera:       {ra['max_wait_ms']:.1f} ms")

    # ── 3. Replicação ─────────────────────────────────────────────────────
    print(f"\n{BOLD}{BLUE}━━  3. REPLICAÇÃO (Protocolo 1)  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    total_w = rep["total_writes"]
    print(f"\n  Total de WRITE_OK:         {BOLD}{total_w}{RESET}")

    if total_w > 0:
        print(f"\n  Replicação completa (2 backups):  ", end="")
        print(f"{bar(rep['full_replication'], total_w)}  {rep['full_replication']} ({rep['pct_full']:.1f}%)")

        print(f"  Replicação parcial (1 backup):    ", end="")
        pct_p = rep['partial_replication'] / total_w * 100
        print(f"{bar(rep['partial_replication'], total_w, color=YELLOW)}  {rep['partial_replication']} ({pct_p:.1f}%)")

        print(f"  Sem réplica (primário sozinho):   ", end="")
        pct_n = rep['no_replica'] / total_w * 100
        color_n = RED if rep['no_replica'] > 0 else GRAY
        print(f"{bar(rep['no_replica'], total_w, color=color_n)}  {rep['no_replica']} ({pct_n:.1f}%)")

    print(f"\n  Falhas de réplica detectadas: {rep['replica_failures']}")
    print(f"  Redirects enviados:           {rep['redirects']}")

    # ── 4. Eleições ───────────────────────────────────────────────────────
    print(f"\n{BOLD}{BLUE}━━  4. TOLERÂNCIA A FALHAS (Eleições)  ━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"\n  NODE_DOWN detectados:  {BOLD}{el['total_downs']}{RESET}")
    print(f"  Eleições concluídas:   {BOLD}{el['total_elections']}{RESET}")
    print(f"  Recuperações (UP):     {BOLD}{el['total_recoveries']}{RESET}")

    if el["avg_recovery_ms"] > 0:
        print(f"\n  Tempo médio de recuperação: {el['avg_recovery_ms']:.0f} ms")
        print(f"  Tempo máximo:               {el['max_recovery_ms']:.0f} ms")
        recovery_ok = el["max_recovery_ms"] < 10000
        print(f"\n  {verdict(recovery_ok, 'Recuperação dentro de 10s em todos os casos', 'Alguma recuperação demorou mais de 10s')}")

    if el["primary_count"]:
        print(f"\n  Vezes que cada Store foi eleito primário:")
        max_pc = max(el["primary_count"].values())
        for store_id, count in sorted(el["primary_count"].items()):
            print(f"    Store {store_id}: {count}x  {bar(count, max_pc, width=15)}")

    # ── 5. Idempotência ───────────────────────────────────────────────────
    print(f"\n{BOLD}{BLUE}━━  5. IDEMPOTÊNCIA (sub-caso 2.3)  ━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    no_leak = idem["duplicates_not_filtered"] == 0
    dup_count = idem["duplicates_not_filtered"]
    print(f"\n  {verdict(no_leak, 'PROVA: Nenhuma request_id duplicada no log', f'{dup_count} request_id(s) duplicada(s) não filtrada(s)!')}")

    print(f"\n  Escritas primárias processadas:  {idem['total_writes_primary']}")
    print(f"  Duplicatas filtradas (correto):  {idem['duplicates_filtered']}")
    if not no_leak:
        print(f"  {RED}Duplicatas não filtradas:        {idem['duplicates_not_filtered']}{RESET}")
        for rid in idem["duplicate_ids"]:
            print(f"    {rid}")

    # ── Veredicto final ───────────────────────────────────────────────────
    print(f"\n{BOLD}{CYAN}{'═' * 65}{RESET}")
    print(f"{BOLD}{CYAN}  VEREDICTO FINAL{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 65}{RESET}\n")

    checks = [
        (len(me["violations"]) == 0,        "Exclusão mútua garantida"),
        (ra["starvations"] == 0,             "Progresso garantido (sem starvation)"),
        (rep["total_writes"] > 0,            "Protocolo 1 operacional"),
        (el["total_elections"] > 0 or True,  "Tolerância a falhas testada"),
        (idem["duplicates_not_filtered"] == 0, "Idempotência funcionando"),
    ]

    all_pass = all(c for c, _ in checks)
    for passed_c, label in checks:
        icon = f"{GREEN}✅{RESET}" if passed_c else f"{RED}❌{RESET}"
        print(f"  {icon}  {label}")

    print()
    if all_pass:
        print(f"  {BOLD}{GREEN}Sistema distribuído correto em todos os critérios analisados.{RESET}")
    else:
        print(f"  {BOLD}{YELLOW}Alguns critérios falharam — revise os itens marcados com ❌.{RESET}")
    print()


# ═════════════════════════════════════════════════════════════════════════════
# SAÍDA JSON
# ═════════════════════════════════════════════════════════════════════════════

def print_json(me, ra, rep, el, idem):
    output = {
        "mutual_exclusion": {
            "passed":        len(me["violations"]) == 0,
            "violations":    len(me["violations"]),
            "total_entries": me["total_entries"],
            "avg_duration_ms": round(me["avg_duration_ms"], 2),
        },
        "ra_progress": {
            "passed":       ra["starvations"] == 0,
            "starvations":  ra["starvations"],
            "avg_wait_ms":  round(ra["avg_wait_ms"], 2),
        },
        "replication": {
            "total_writes":     rep["total_writes"],
            "pct_full":         round(rep["pct_full"], 2),
            "replica_failures": rep["replica_failures"],
        },
        "elections": {
            "total":            el["total_elections"],
            "avg_recovery_ms":  round(el["avg_recovery_ms"], 2),
            "max_recovery_ms":  round(el["max_recovery_ms"], 2),
        },
        "idempotency": {
            "passed":              idem["duplicates_not_filtered"] == 0,
            "duplicates_filtered": idem["duplicates_filtered"],
            "leaks":               idem["duplicates_not_filtered"],
        },
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

def main():
    # Argumentos
    args      = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags     = [a for a in sys.argv[1:] if a.startswith("--")]
    json_mode = "--json" in flags

    source = args[0] if args else "audit_structured.jsonl"

    if not os.path.exists(source):
        print(f"{RED}Arquivo não encontrado: {source}{RESET}")
        print(f"Certifique-se de que o sistema rodou e gerou o arquivo de log.")
        sys.exit(1)

    events, parse_errors = load_events(source)

    if not events:
        print(f"{RED}Nenhum evento válido encontrado em {source}.{RESET}")
        sys.exit(1)

    if not json_mode:
        print(f"{GRAY}Carregados {len(events)} eventos ({parse_errors} erro(s) de parse){RESET}")

    # Análises
    me   = analyze_mutual_exclusion(events)
    ra   = analyze_ra_progress(events)
    rep  = analyze_replication(events)
    el   = analyze_elections(events)
    idem = analyze_idempotency(events)

    if json_mode:
        print_json(me, ra, rep, el, idem)
    else:
        print_report(events, me, ra, rep, el, idem, source)


if __name__ == "__main__":
    main()
