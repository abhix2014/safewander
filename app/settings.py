import os


APP_ENV = os.environ.get("APP_ENV", "development")
PORT = int(os.environ.get("PORT", "8000"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

# Comma separated values, default wildcard for MVP compatibility.
CORS_ORIGINS = [v.strip() for v in os.environ.get("CORS_ORIGINS", "*").split(",") if v.strip()]

# Optional server-to-server write protection for production (POST /api/posts and /api/sos).
WRITE_API_KEY = os.environ.get("WRITE_API_KEY", "")

# Basic in-memory rate limiting for API routes.
RATE_LIMIT_PER_MIN = int(os.environ.get("RATE_LIMIT_PER_MIN", "120"))


API_VERSION = "v1"
