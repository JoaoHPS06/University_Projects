# SyncStore — Distributed Systems: Replication & Fault Tolerance

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)
![Status](https://img.shields.io/badge/Status-Completed-green?style=for-the-badge)

<img width="1361" height="626" alt="image" src="https://github.com/user-attachments/assets/0a8780f5-9175-49cc-82bf-9cc4325fdf78" />


## 📌 Project Description

**SyncStore** is a fully distributed system built in Python and orchestrated with Docker Compose, implementing two core distributed computing protocols from scratch:

- **Ricart-Agrawala Mutual Exclusion** — a decentralized algorithm ensuring only one node accesses the shared resource at a time, with no central coordinator.
- **Primary-Backup Replication** — a fault-tolerant storage cluster where writes are synchronously replicated to backup nodes before confirmation.

The system simulates a real-world scenario: **5 external clients** send concurrent write requests to a **Sync Cluster** (5 nodes), which coordinates access via Ricart-Agrawala and writes to a **Store Cluster** (3 nodes) that replicates data and handles node failures automatically.

This project was developed as part of the **BCC362 — Distributed Systems** course.

---

## 👥 Team Members

- [Camile Reis de Sousa](https://github.com/camile16)
- [João Henrique Pedrosa de Souza](https://github.com/JoaoHPS06)
- [Theo dos Anjos Silva](https://github.com/ooehT)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  5 External Clients                     │
│          Client_A  B  C  D  E  (UDP requests)           │
└──────────────────────┬──────────────────────────────────┘
                       │ UDP
┌──────────────────────▼──────────────────────────────────┐
│              Cluster Sync — Ricart-Agrawala             │
│         Node1  Node2  Node3  Node4  Node5               │
│    (ports 5001–5005 · mutual exclusion via R.A.)        │
└──────────────────────┬──────────────────────────────────┘
                       │ TCP (only while in Critical Section)
┌──────────────────────▼──────────────────────────────────┐
│        Cluster Store — Protocol 1: Primary-Backup       │
│  Store1 (PRIMARY)  ←→  Store2 (backup)  Store3 (backup) │
│        (ports 7001–7003 · automatic election)           │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ Protocols Implemented

### Ricart-Agrawala (Mutual Exclusion)

Each Sync node operates in one of three states:

| State | Behavior |
|---|---|
| `RELEASED` | Not requesting the resource. Sends OK immediately to any request. |
| `WANTED` | Broadcast `REQUEST` with timestamp to all peers. Waits for N-1 OKs. |
| `HELD` | Inside the Critical Section. Defers all incoming requests to a queue. |

When a node receives a `REQUEST`, it decides based on timestamp priority: lower timestamp wins. Ties are broken by node ID.

### Primary-Backup Replication

The node with the **lowest ID among alive nodes** is always the primary. Write flow:

1. Sync Node (inside the CS) sends `WRITE` to the primary Store.
2. Primary replicates to all alive backups via `WRITE_REPLICA`.
3. Only sends `WRITE_OK` after receiving `REPLICA_OK` from all backups.
4. If a Sync Node reaches a backup, it receives `REDIRECT` and retries the primary.

### Fault Tolerance — Store Cluster Failures

| Sub-case | Trigger | Resolution |
|---|---|---|
| **2.1** — Idle failure | Node stops responding to PING (every 2s) | Automatic election: `min(alive_nodes)` becomes primary. Notified via `PROMOTE`. |
| **2.2** — Failure with pending request | Sync Node gets TCP timeout (2s) during write | Retry on next live node in ordered list. |
| **2.3** — Failure during write (idempotency) | Sync Node retries with same `request_id` | Store checks `seen_requests` set — duplicate writes are silently ignored. |

---

## 📁 Project Structure

```
tp3/
├── config.json          # All network addresses and ports
├── utils.py             # load_config() — shared config loader
├── client.py            # External clients (UDP)
├── node_cluster.py      # Sync Cluster — Ricart-Agrawala + Store client
├── store_node.py        # Store Cluster — Protocol 1 + fault tolerance
├── resource_server.py   # Legacy TP2 auditor (collision detection)
├── logger.py            # Structured logger → terminal + JSONL
├── log_server.py        # HTTP server exposing JSONL via REST (port 8888)
├── dashboard.html       # Real-time monitoring dashboard (open in browser)
├── analyze.py           # Correctness proof tool — reads JSONL, finds violations
├── test_fault.py        # Automated fault injection test (sub-cases 2.1/2.2/2.3)
├── docker-compose.yml   # Orchestrates all 15 containers
└── Dockerfile           # Base image: python:3.11-slim
```

---

## 🚀 Running the System

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/)
- Python 3.8+ (for running `analyze.py` and `test_fault.py` on the host)

### Start

```bash
# Clone the repository
git clone https://github.com/JoaoHPS06/University_Projects/SyncStore.git
cd SyncStore

# Build and start all 15 containers
docker-compose up --build
```

### Monitor

Open `dashboard.html` directly in your browser — no server needed.
It polls `http://localhost:8888` every 1.5s and updates in real time.

### Stop

```bash
docker-compose down
```

---

## 🧪 Testing Fault Tolerance

Run the automated test suite from your host machine while the system is running:

```bash
python test_fault.py
```

Select which sub-case to run:
- `1` — Sub-case 2.1: idle Store failure and automatic election
- `2` — Sub-case 2.2: Store failure with a pending write
- `3` — Sub-case 2.3: idempotency (no duplicate log entries)
- `A` — All sub-cases in sequence

To manually simulate a failure:

```bash
# Pause store1 (simulates omission failure — process frozen, no RST sent)
docker pause store1

# Watch store2 become primary in the dashboard, then recover:
docker unpause store1
```

---

## 📊 Correctness Analysis

After running the system, analyze the structured audit log:

```bash
# Full report with mathematical proofs
python analyze.py

# JSON output for automation
python analyze.py --json
```

The report includes:

| Analysis | What it proves |
|---|---|
| **Mutual Exclusion** | Reconstructs all [ENTER, EXIT] intervals. Zero overlapping intervals = Ricart-Agrawala is correct. |
| **Progress** | Every `RA_REQUEST_SENT` eventually led to a `CRITICAL_ENTER`. No starvation detected. |
| **Replication** | Distribution of writes by replica count (full / partial / none). |
| **Elections** | Average and max recovery time after a primary failure. |
| **Idempotency** | No `request_id` was processed more than once in the Store log. |

---

## 📡 Observability Stack

The system includes a full observability pipeline:

```
node_cluster.py / store_node.py
        ↓
    logger.py  →  audit_structured.jsonl  (one JSON per line)
                         ↓
                  log_server.py :8888  (REST API)
                         ↓
                  dashboard.html  (browser, polls every 1.5s)
```

Each event in the JSONL has: `ts` (Unix timestamp), `time` (human-readable), `node_type`, `node_id`, `event` (code), `msg`, and `data` (event-specific fields).

---

## 📸 Dashboard

> The dashboard auto-detects node state changes, primary elections, and write distribution in real time.

| Panel | Description |
|---|---|
| Stats bar | Total writes OK, SC entries, R.A. deferrals, failures, elections |
| Cluster Sync | Each node shown as idle / WAITING / in Critical Section |
| Cluster Store | PRIMARY (crown) / backup / DEAD (skull) per node |
| Recent Elections | Last 5 primary changes with timestamps |
| Writes by Node | Proportional bar chart per Sync node |
| Timeline | Scrollable event feed with filters: ALL, SYNC, STORE, FAULT, ELECTION, SC |

---

## 🔧 Configuration

All addresses and ports are defined in `config.json` — no hardcoded values anywhere else:

```json
{
  "nodes":           { "1": ["node1", 5001], "...", "5": ["node5", 5005] },
  "store_nodes":     { "1": ["store1", 7001], "2": ["store2", 7002], "3": ["store3", 7003] },
  "resource_server": ["resource_server", 6000]
}
```
