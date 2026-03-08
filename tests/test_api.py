import json
import os
import socket
import subprocess
import tempfile
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class ApiClient:
    def __init__(self, base: str):
        self.base = base

    def get(self, path: str):
        with urlopen(self.base + path, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8")), response.headers

    def post(self, path: str, payload: dict, headers: dict | None = None):
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        req = Request(
            self.base + path,
            data=json.dumps(payload).encode("utf-8"),
            headers=req_headers,
            method="POST",
        )
        with urlopen(req, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8")), response.headers


class TestApi:
    @classmethod
    def setup_class(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        port = free_port()
        env = os.environ.copy()
        env["PORT"] = str(port)
        env["DB_PATH"] = os.path.join(cls.temp_dir.name, "test.db")
        env["RATE_LIMIT_PER_MIN"] = "1000"
        cls.process = subprocess.Popen(["python3", "server.py"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        cls.client = ApiClient(f"http://127.0.0.1:{port}")

        for _ in range(40):
            try:
                status, _, _ = cls.client.get("/api/health")
                if status == 200:
                    break
            except Exception:
                time.sleep(0.1)
        else:
            raise RuntimeError("server did not start")

    @classmethod
    def teardown_class(cls):
        cls.process.terminate()
        cls.process.wait(timeout=3)
        cls.temp_dir.cleanup()

    def test_health_legacy_and_v1(self):
        status, legacy, headers = self.client.get("/api/health")
        assert status == 200
        assert legacy["status"] == "ok"
        assert "version" in legacy
        assert headers.get("X-Request-ID")

        status, v1, _ = self.client.get("/api/v1/health")
        assert status == 200
        assert v1["status"] == "ok"

    def test_readiness(self):
        status, ready, _ = self.client.get("/api/ready")
        assert status == 200
        assert ready["ready"] is True
        assert ready["db"] == "ok"

    def test_posts_list_and_create(self):
        status, posts, _ = self.client.get("/api/posts?limit=2")
        assert status == 200
        assert len(posts["posts"]) == 2

        status, create, _ = self.client.post(
            "/api/v1/posts",
            {"name": "Upgrade User", "location": "Tapovan", "text": "Versioned API works great"},
        )
        assert status == 201
        assert create["ok"] is True

        status, latest, _ = self.client.get("/api/posts?limit=1")
        assert status == 200
        assert latest["posts"][0]["location"] == "Tapovan"

    def test_post_validation(self):
        req = Request(
            self.client.base + "/api/posts",
            data=json.dumps({"name": "A", "location": "B", "text": "x"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urlopen(req, timeout=5)
            assert False, "Expected 400"
        except HTTPError as err:
            assert err.code == 400

    def test_sos_and_incidents(self):
        status, created, _ = self.client.post("/api/sos", {"name": "SOS User", "lat": 30.0869, "lng": 78.2676})
        assert status == 201
        assert created["status"] == "alerting_nearby"

        status, incidents, _ = self.client.get("/api/v1/incidents?limit=1")
        assert status == 200
        assert incidents["incidents"][0]["user_name"] == "SOS User"

    def test_stats_events_hostels(self):
        assert self.client.get("/api/stats")[0] == 200
        assert self.client.get("/api/events")[0] == 200
        assert self.client.get("/api/hostels")[0] == 200


class TestRateLimitAndAuth:
    def test_rate_limit(self):
        temp_dir = tempfile.TemporaryDirectory()
        port = free_port()
        env = os.environ.copy()
        env["PORT"] = str(port)
        env["DB_PATH"] = os.path.join(temp_dir.name, "test.db")
        env["RATE_LIMIT_PER_MIN"] = "2"
        proc = subprocess.Popen(["python3", "server.py"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        client = ApiClient(f"http://127.0.0.1:{port}")

        try:
            for _ in range(40):
                try:
                    status, _, _ = client.get("/api/health")
                    if status == 200:
                        break
                except Exception:
                    time.sleep(0.1)

            client.get("/api/stats")
            client.get("/api/stats")
            try:
                client.get("/api/stats")
                assert False, "Expected rate limit to trigger"
            except HTTPError as err:
                assert err.code == 429
        finally:
            proc.terminate()
            proc.wait(timeout=3)
            temp_dir.cleanup()

    def test_optional_write_api_key(self):
        temp_dir = tempfile.TemporaryDirectory()
        port = free_port()
        env = os.environ.copy()
        env["PORT"] = str(port)
        env["DB_PATH"] = os.path.join(temp_dir.name, "test.db")
        env["WRITE_API_KEY"] = "secret-token"
        env["RATE_LIMIT_PER_MIN"] = "1000"
        proc = subprocess.Popen(["python3", "server.py"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        client = ApiClient(f"http://127.0.0.1:{port}")

        try:
            for _ in range(40):
                try:
                    status, _, _ = client.get("/api/health")
                    if status == 200:
                        break
                except Exception:
                    time.sleep(0.1)

            req = Request(
                client.base + "/api/posts",
                data=json.dumps({"name": "A", "location": "B", "text": "Hello secure world"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                urlopen(req, timeout=5)
                assert False, "Expected 401 when missing X-API-Key"
            except HTTPError as err:
                assert err.code == 401

            status, payload, _ = client.post(
                "/api/posts",
                {"name": "A", "location": "B", "text": "Hello secure world"},
                headers={"X-API-Key": "secret-token"},
            )
            assert status == 201
            assert payload["ok"] is True
        finally:
            proc.terminate()
            proc.wait(timeout=3)
            temp_dir.cleanup()
