import json
import logging
import os
import signal
import threading
import time
import uuid
from collections import defaultdict, deque
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app import store
from app.settings import API_VERSION, APP_ENV, CORS_ORIGINS, LOG_LEVEL, PORT, RATE_LIMIT_PER_MIN, WRITE_API_KEY

ROOT = Path(__file__).resolve().parents[1]
LOGGER = logging.getLogger("safewander.api")


class RateLimiter:
    def __init__(self, per_minute: int):
        self.per_minute = per_minute
        self.events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            bucket = self.events[key]
            cutoff = now - 60
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= self.per_minute:
                return False
            bucket.append(now)
            return True


RATE_LIMITER = RateLimiter(RATE_LIMIT_PER_MIN)


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s %(message)s",
    )


def _allowed_origin(origin: str | None) -> str:
    if not origin:
        return "*" if "*" in CORS_ORIGINS else CORS_ORIGINS[0]
    if "*" in CORS_ORIGINS:
        return "*"
    return origin if origin in CORS_ORIGINS else CORS_ORIGINS[0]


def json_response(handler: SimpleHTTPRequestHandler, payload: dict, status: int = 200) -> None:
    body = json.dumps(payload).encode("utf-8")
    origin = _allowed_origin(handler.headers.get("Origin"))
    request_id = getattr(handler, "request_id", "")

    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Access-Control-Allow-Origin", origin)
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-Key, X-Request-ID")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("X-Request-ID", request_id)
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("X-Frame-Options", "DENY")
    handler.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
    handler.end_headers()
    handler.wfile.write(body)


class SafeWanderHandler(SimpleHTTPRequestHandler):
    request_id = ""

    def _log(self, level: int, message: str) -> None:
        extra = {"request_id": self.request_id}
        LOGGER.log(level, message, extra=extra)

    def do_OPTIONS(self):
        self.request_id = self.headers.get("X-Request-ID") or str(uuid.uuid4())
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", _allowed_origin(self.headers.get("Origin")))
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-Key, X-Request-ID")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("X-Request-ID", self.request_id)
        self.end_headers()

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return None

    def _resolve_api_path(self, path: str) -> str:
        if path.startswith("/api/v1/"):
            return "/api/" + path[len("/api/v1/") :]
        return path

    def _check_rate_limit(self, path: str) -> bool:
        if not path.startswith("/api/"):
            return True
        identity = self.headers.get("X-Forwarded-For") or self.client_address[0]
        key = f"{identity}:{path}"
        return RATE_LIMITER.allow(key)

    def _check_write_key(self) -> bool:
        if not WRITE_API_KEY:
            return True
        given = self.headers.get("X-API-Key", "")
        return given == WRITE_API_KEY

    def do_GET(self):
        self.request_id = self.headers.get("X-Request-ID") or str(uuid.uuid4())
        parsed = urlparse(self.path)
        path = self._resolve_api_path(parsed.path)

        if not self._check_rate_limit(path):
            return json_response(self, {"error": "rate limit exceeded"}, 429)

        try:
            if parsed.path == "/":
                self.path = "/safewander-v2.html"
                return super().do_GET()

            if path == "/api/health":
                return json_response(self, {"status": "ok", "time": store.utc_now_iso(), "version": API_VERSION, "env": APP_ENV})

            if path == "/api/ready":
                ready = store.readiness_check()
                status = 200 if ready["ready"] else 503
                return json_response(self, ready, status)

            if path == "/api/posts":
                limit = store.parse_limit(parse_qs(parsed.query).get("limit", ["20"])[0])
                return json_response(self, {"posts": store.list_posts(limit)})

            if path == "/api/incidents":
                limit = store.parse_limit(parse_qs(parsed.query).get("limit", ["20"])[0])
                return json_response(self, {"incidents": store.list_incidents(limit)})

            if path == "/api/stats":
                return json_response(self, store.stats())

            if path == "/api/events":
                return json_response(self, {"events": store.list_events()})

            if path == "/api/hostels":
                return json_response(self, {"hostels": store.list_hostels()})

            if path.startswith("/api/"):
                return json_response(self, {"error": "not found"}, 404)

            return super().do_GET()
        finally:
            self._log(logging.INFO, f"GET {path} -> completed")

    def do_POST(self):
        self.request_id = self.headers.get("X-Request-ID") or str(uuid.uuid4())
        parsed = urlparse(self.path)
        path = self._resolve_api_path(parsed.path)

        if not self._check_rate_limit(path):
            return json_response(self, {"error": "rate limit exceeded"}, 429)

        if not self._check_write_key() and path in {"/api/posts", "/api/sos"}:
            return json_response(self, {"error": "unauthorized write"}, 401)

        payload = self._read_json()
        if payload is None:
            return json_response(self, {"error": "invalid JSON"}, 400)

        try:
            if path == "/api/posts":
                name = str(payload.get("name") or "Guest Traveler").strip()[:40]
                location = str(payload.get("location") or "Rishikesh").strip()[:80]
                text = str(payload.get("text") or "").strip()
                if len(text) < 4:
                    return json_response(self, {"error": "post text must be at least 4 characters"}, 400)
                post_id = store.create_post(name=name, location=location, text=text)
                return json_response(self, {"ok": True, "post_id": post_id}, 201)

            if path == "/api/sos":
                name = str(payload.get("name") or "Anonymous").strip()[:60]
                lat = payload.get("lat")
                lng = payload.get("lng")
                if (lat is None) != (lng is None):
                    return json_response(self, {"error": "lat and lng must both be provided"}, 400)
                if lat is not None:
                    try:
                        lat = float(lat)
                        lng = float(lng)
                    except (TypeError, ValueError):
                        return json_response(self, {"error": "lat/lng must be numeric"}, 400)
                    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                        return json_response(self, {"error": "lat/lng out of range"}, 400)
                incident_id = store.create_incident(name=name, lat=lat, lng=lng)
                return json_response(self, {"ok": True, "incident_id": incident_id, "status": "alerting_nearby"}, 201)

            if path.startswith("/api/"):
                return json_response(self, {"error": "not found"}, 404)

            return json_response(self, {"error": "not found"}, 404)
        finally:
            self._log(logging.INFO, f"POST {path} -> completed")


def run() -> None:
    configure_logging()
    store.ensure_db()
    os.chdir(ROOT)
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), SafeWanderHandler)

    def shutdown_handler(signum, _frame):
        LOGGER.warning("Received signal %s, shutting down", signum, extra={"request_id": "system"})
        threading.Thread(target=httpd.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    LOGGER.info(
        "SafeWander API running on http://0.0.0.0:%s env=%s rate_limit_per_min=%s",
        PORT,
        APP_ENV,
        RATE_LIMIT_PER_MIN,
        extra={"request_id": "system"},
    )
    httpd.serve_forever()


if __name__ == "__main__":
    run()
