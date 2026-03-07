"""
log_server.py — Servidor HTTP que expõe o audit_structured.jsonl via REST.

Endpoints:
  GET /events          → todos os eventos (JSON array)
  GET /events?since=X  → eventos com ts > X (para polling incremental)
  GET /health          → {"status": "ok"}

O dashboard.html faz polling a cada 1.5s em /events?since=<ultimo_ts>
para receber apenas os novos eventos, sem recarregar tudo.
"""

import json
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

LOG_FILE = "audit_structured.jsonl"
PORT     = 8888


class LogHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self._respond(200, {"status": "ok"})

        elif parsed.path == "/events":
            params = parse_qs(parsed.query)
            since  = float(params.get("since", ["0"])[0])
            events = self._read_events(since)
            self._respond(200, events)

        else:
            self._respond(404, {"error": "not found"})

    def _read_events(self, since=0.0):
        events = []
        if not os.path.exists(LOG_FILE):
            return events
        try:
            with open(LOG_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        e = json.loads(line)
                        if e.get("ts", 0) > since:
                            events.append(e)
                    except json.JSONDecodeError:
                        pass
        except Exception:
            pass
        return events

    def _respond(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        # CORS — permite que o dashboard.html aberto como arquivo acesse a API
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        pass  # silencia os logs de acesso HTTP no terminal


if __name__ == "__main__":
    print(f"📡 Log Server rodando em http://0.0.0.0:{PORT}")
    print(f"   Lendo: {LOG_FILE}")
    server = HTTPServer(("0.0.0.0", PORT), LogHandler)
    server.serve_forever()
