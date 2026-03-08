import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app import store

ROOT = Path(__file__).resolve().parents[1]


def json_response(handler: SimpleHTTPRequestHandler, payload: dict, status: int = 200) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.end_headers()
    handler.wfile.write(body)


class SafeWanderHandler(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
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

    def do_GET(self):
        parsed = urlparse(self.path)
        path = self._resolve_api_path(parsed.path)

        if parsed.path == "/":
            self.path = "/safewander-v2.html"
            return super().do_GET()

        if path == "/api/health":
            return json_response(self, {"status": "ok", "time": store.utc_now_iso()})

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

    def do_POST(self):
        parsed = urlparse(self.path)
        path = self._resolve_api_path(parsed.path)
        payload = self._read_json()
        if payload is None:
            return json_response(self, {"error": "invalid JSON"}, 400)

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


def run() -> None:
    store.ensure_db()
    os.chdir(ROOT)
    port = int(os.environ.get("PORT", "8000"))
    httpd = ThreadingHTTPServer(("0.0.0.0", port), SafeWanderHandler)
    print(f"SafeWander upgraded API running on http://0.0.0.0:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
