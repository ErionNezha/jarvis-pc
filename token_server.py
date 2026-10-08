#!/usr/bin/env python3
"""JARVIS PC — token server + shërben faqen e zërit (client/index.html).

Vetëm stdlib + python-dotenv. Jep tokena LiveKit për dhomën e Jarvis.
Niset me:  python token_server.py
Pastaj hap: http://localhost:8765/
"""
import base64
import hashlib
import hmac
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

_BASE = os.path.dirname(os.path.abspath(__file__))
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback minimal nëse python-dotenv s'është instaluar ende
    _env_path = os.path.join(_BASE, ".env")
    if os.path.exists(_env_path):
        with open(_env_path, encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.strip())

BASE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.getenv("JARVIS_PORT", "8765"))
# Prefiksi i dhomës; emri i plotë është unik për çdo /token (shmang
# përgjithmonë dublikatat dhe pjesëmarrësit-zombi — një dhomë, një agent).
ROOM_PREFIX = os.getenv("JARVIS_ROOM", "jarvis-room")
AGENT_NAME = "jarvis-agent"


def _new_room() -> str:
    import random
    return f"{ROOM_PREFIX}-{int(time.time())}-{random.randint(1000, 9999)}"


def dispatch_agent(room: str) -> bool:
    """Explicit dispatch: thërret agentin në dhomë via LiveKit API.

    livekit-agents 1.2.1 s'bën auto-dispatch, ndaj token serveri e thërret
    vetë agentin sa herë kërkohet /token. Dhoma është unike për çdo token,
    kështu që dublikatat janë të pamundura.
    """
    try:
        from livekit import api as lkapi
        from livekit.protocol.agent_dispatch import CreateAgentDispatchRequest
    except ImportError:
        print("[dispatch] livekit-api mungon — kapërcehet")
        return False

    import asyncio

    async def _go() -> bool:
        lk = lkapi.LiveKitAPI(
            url=os.getenv("LIVEKIT_URL", "").strip(),
            api_key=os.getenv("LIVEKIT_API_KEY", "").strip(),
            api_secret=os.getenv("LIVEKIT_API_SECRET", "").strip(),
        )
        try:
            d = await lk.agent_dispatch.create_dispatch(
                CreateAgentDispatchRequest(room=room, agent_name=AGENT_NAME)
            )
            print(f"[dispatch] OK id={d.id} dhoma={d.room}")
            return True
        except Exception as e:
            print(f"[dispatch] GABIM: {e}")
            return False
        finally:
            await lk.aclose()

    try:
        return asyncio.run(_go())
    except Exception as e:
        print(f"[dispatch] GABIM asyncio: {e}")
        return False


def make_token() -> tuple[str | None, str]:
    key = os.getenv("LIVEKIT_API_KEY", "").strip()
    secret = os.getenv("LIVEKIT_API_SECRET", "").strip()
    room = _new_room()
    if not key or not secret:
        return None, room

    def b64(d: bytes) -> str:
        return base64.urlsafe_b64encode(d).rstrip(b"=").decode()

    now = int(time.time())
    header = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = b64(json.dumps({
        "iss": key,
        "sub": "erion",
        "name": "Erion",
        "iat": now,
        "exp": now + 3600,
        "video": {
            "roomJoin": True,
            "room": room,
            "canPublish": True,
            "canSubscribe": True,
        },
        # Explicit dispatch: thërret agentin "jarvis-agent" në dhomë
        # (livekit-agents 1.2.1 s'bën auto-dispatch).
        "roomConfig": {"agents": [{"agentName": "jarvis-agent"}]},
    }).encode())
    sig = b64(hmac.new(secret.encode(), f"{header}.{payload}".encode(),
                       hashlib.sha256).digest())
    return f"{header}.{payload}.{sig}", room


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: str, ctype: str):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/token":
            token, room = make_token()
            if not token:
                return self._send(500, json.dumps({
                    "error": "LIVEKIT_API_KEY / LIVEKIT_API_SECRET mungojnë në .env"
                }), "application/json")
            # Thërret agentin në dhomë (explicit dispatch — s'e bllokon përgjigjen)
            try:
                dispatch_agent(room)
            except Exception as e:
                print(f"[dispatch] {e}")
            return self._send(200, json.dumps({
                "token": token,
                "url": os.getenv("LIVEKIT_URL", "").strip(),
                "room": room,
            }), "application/json")

        if path in ("/", "/index.html"):
            fpath = os.path.join(BASE, "client", "index.html")
            if os.path.exists(fpath):
                with open(fpath, encoding="utf-8") as f:
                    return self._send(200, f.read(), "text/html; charset=utf-8")
        return self._send(404, "S'u gjet.", "text/plain; charset=utf-8")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"JARVIS client: http://localhost:{PORT}/  (dhoma unike për çdo lidhje)")
    print("Mbylle me Ctrl+C.")
    srv.serve_forever()
