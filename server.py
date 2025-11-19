import json
import os
import secrets
import time
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict, Optional
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

PUBLIC_DIR = Path(__file__).parent
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "change-me"
DEFAULT_ALLOWED_PAGES = ["default"]
SESSION_TTL_SECONDS = 8 * 60 * 60  # 8 hours
ALLOWED_STATIC_SUFFIXES = {
    ".html",
    ".css",
    ".js",
    ".json",
    ".ico",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".txt",
    ".webmanifest",
    ".woff",
    ".woff2",
}


def parse_allowed_origins() -> list[str]:
    raw = os.environ.get("ALLOWED_ORIGINS", "")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


ALLOWED_ORIGINS = parse_allowed_origins()


def bool_from_env(value: Optional[str], fallback: bool) -> bool:
    if value is None:
        return fallback
    return value.strip().lower() in {"1", "true", "yes", "on"}


def cookie_settings() -> list[str]:
    same_site_override = os.environ.get("SESSION_COOKIE_SAMESITE")
    same_site = (
        f"SameSite={same_site_override}"
        if same_site_override
        else ("SameSite=None" if ALLOWED_ORIGINS else "SameSite=Lax")
    )
    secure_flag = bool_from_env(os.environ.get("SESSION_COOKIE_SECURE"), bool(ALLOWED_ORIGINS))
    attributes = ["HttpOnly", "Path=/", same_site]
    if secure_flag:
        attributes.append("Secure")
    return attributes


COOKIE_SETTINGS = cookie_settings()


def parse_allowed_pages(raw: Optional[str]) -> list[str]:
    if not raw:
        return DEFAULT_ALLOWED_PAGES.copy()
    pages = [item.strip() for item in raw.split(",") if item.strip()]
    return pages or DEFAULT_ALLOWED_PAGES.copy()


def normalize_pages(source) -> list[str]:
    if isinstance(source, list):
        cleaned = [str(item).strip() for item in source if str(item).strip()]
        return cleaned or DEFAULT_ALLOWED_PAGES.copy()
    if isinstance(source, str):
        return parse_allowed_pages(source)
    return DEFAULT_ALLOWED_PAGES.copy()


def load_users() -> Dict[str, Dict]:
    users_env = os.environ.get("APP_USERS")
    if users_env:
        try:
            parsed = json.loads(users_env)
        except json.JSONDecodeError as err:
            raise RuntimeError("APP_USERS must be valid JSON.") from err
        users: Dict[str, Dict] = {}
        if isinstance(parsed, list):
            for entry in parsed:
                username = entry.get("username")
                password = entry.get("password")
                pages = normalize_pages(entry.get("pages"))
                if username and password:
                    users[username] = {"password": password, "pages": pages}
        elif isinstance(parsed, dict):
            for username, config in parsed.items():
                if isinstance(config, dict) and "password" in config:
                    users[username] = {
                        "password": config["password"],
                        "pages": normalize_pages(config.get("pages")),
                    }
        if users:
            return users
    username = os.environ.get("ADMIN_USERNAME", DEFAULT_USERNAME)
    password = os.environ.get("ADMIN_PASSWORD", DEFAULT_PASSWORD)
    pages = parse_allowed_pages(os.environ.get("DEFAULT_ALLOWED_PAGES"))
    return {
        username: {
            "password": password,
            "pages": pages,
        }
    }


USER_STORE = load_users()


def build_cookie_header(value: str, expires: Optional[str] = None) -> str:
    parts = [f"session_id={value}"]
    if expires:
        parts.append(f"Expires={expires}")
    parts.extend(COOKIE_SETTINGS)
    return "; ".join(parts)


def read_request_body(handler: BaseHTTPRequestHandler) -> Dict:
    content_length = int(handler.headers.get("Content-Length", "0"))
    raw_body = handler.rfile.read(content_length) if content_length else b""
    if not raw_body:
        return {}
    try:
        return json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


class SessionStore:
    def __init__(self) -> None:
        self._store: Dict[str, Dict] = {}

    def create(self, username: str, allowed_pages: list[str]) -> str:
        token = secrets.token_urlsafe(32)
        self._store[token] = {
            "username": username,
            "created": time.time(),
            "allowed_pages": allowed_pages,
        }
        return token

    def get(self, token: Optional[str]) -> Optional[Dict]:
        if not token:
            return None
        data = self._store.get(token)
        if not data:
            return None
        if time.time() - data["created"] > SESSION_TTL_SECONDS:
            self.delete(token)
            return None
        return data

    def delete(self, token: Optional[str]) -> None:
        if token and token in self._store:
            del self._store[token]


SESSION_STORE = SessionStore()


def extract_session_token(handler: BaseHTTPRequestHandler) -> Optional[str]:
    cookie_header = handler.headers.get("Cookie")
    if not cookie_header:
        return None
    cookie = SimpleCookie()
    cookie.load(cookie_header)
    morsel = cookie.get("session_id")
    return morsel.value if morsel else None


def resolve_request_origin(handler: BaseHTTPRequestHandler) -> Optional[str]:
    origin = handler.headers.get("Origin")
    if not origin:
        return None
    if "*" in ALLOWED_ORIGINS:
        return origin
    if origin in ALLOWED_ORIGINS:
        return origin
    return None


def add_cors_headers(handler: BaseHTTPRequestHandler) -> None:
    origin = resolve_request_origin(handler)
    if not origin:
        return
    handler.send_header("Access-Control-Allow-Origin", origin)
    handler.send_header("Vary", "Origin")
    handler.send_header("Access-Control-Allow-Credentials", "true")


def send_json(handler: BaseHTTPRequestHandler, status: HTTPStatus, payload: Dict) -> None:
    encoded = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(encoded)))
    add_cors_headers(handler)
    handler.end_headers()
    handler.wfile.write(encoded)


def serve_static(handler: BaseHTTPRequestHandler, path: str) -> None:
    relative_path = path.lstrip("/") or "index.html"
    file_path = (PUBLIC_DIR / relative_path).resolve()
    try:
        file_path.relative_to(PUBLIC_DIR)
    except ValueError:
        handler.send_error(HTTPStatus.FORBIDDEN, "Access denied")
        return
    if file_path.is_dir():
        file_path = file_path / "index.html"
    if not file_path.exists():
        handler.send_error(HTTPStatus.NOT_FOUND, "File not found")
        return
    suffix = file_path.suffix.lower()
    if suffix and suffix not in ALLOWED_STATIC_SUFFIXES:
        handler.send_error(HTTPStatus.FORBIDDEN, "Access denied")
        return
    content = file_path.read_bytes()
    mime_type = "text/plain"
    if suffix == ".html":
        mime_type = "text/html; charset=utf-8"
    elif suffix == ".css":
        mime_type = "text/css; charset=utf-8"
    elif suffix == ".js":
        mime_type = "application/javascript; charset=utf-8"
    elif suffix == ".json":
        mime_type = "application/json; charset=utf-8"
    elif suffix in {".png", ".jpg", ".jpeg", ".gif"}:
        mime_type = f"image/{file_path.suffix.lstrip('.')}"
    elif suffix == ".svg":
        mime_type = "image/svg+xml"
    elif suffix == ".ico":
        mime_type = "image/x-icon"
    elif suffix == ".woff":
        mime_type = "font/woff"
    elif suffix == ".woff2":
        mime_type = "font/woff2"
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", mime_type)
    handler.send_header("Content-Length", str(len(content)))
    handler.end_headers()
    handler.wfile.write(content)


def call_openai_agent(agent_id: str, message: str) -> Dict:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    payload = {
        "agent_id": agent_id,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": message},
                ],
            }
        ],
    }

    req = urllib_request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib_request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except HTTPError as err:
        error_body = err.read().decode("utf-8")
        raise RuntimeError(f"OpenAI error: {err.code} {error_body}") from err
    except URLError as err:
        raise RuntimeError(f"Network error: {err.reason}") from err

    messages = []
    for item in result.get("output", []):
        for piece in item.get("content", []):
            if piece.get("type") == "output_text":
                messages.append(piece.get("text", ""))
            elif piece.get("type") == "text":
                messages.append(piece.get("text", ""))
    combined = "\n".join(part for part in messages if part)
    return {
        "response": combined or "Agenten svarte uten tekst. Se rårespons for detaljer.",
        "raw": result,
    }


class SurveyAgentHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        add_cors_headers(self)
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path.startswith("/api/session"):
            self.handle_session_check()
        elif self.path.startswith("/api"):
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown API path")
        else:
            serve_static(self, self.path)

    def do_POST(self) -> None:
        if self.path == "/api/login":
            self.handle_login()
        elif self.path == "/api/logout":
            self.handle_logout()
        elif self.path == "/api/query":
            self.handle_query()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown API path")

    def handle_login(self) -> None:
        data = read_request_body(self)
        username = data.get("username", "")
        password = data.get("password", "")
        user = USER_STORE.get(username)
        if not user or user.get("password") != password:
            send_json(self, HTTPStatus.UNAUTHORIZED, {"error": "Feil brukernavn eller passord."})
            return
        allowed_pages = normalize_pages(user.get("pages"))
        token = SESSION_STORE.create(username, allowed_pages)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Set-Cookie", build_cookie_header(token))
        body = json.dumps(
            {"message": "Innlogging vellykket", "allowedPages": allowed_pages}
        ).encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
        add_cors_headers(self)
        self.end_headers()
        self.wfile.write(body)

    def handle_logout(self) -> None:
        token = extract_session_token(self)
        SESSION_STORE.delete(token)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header(
            "Set-Cookie",
            build_cookie_header("deleted", "Thu, 01 Jan 1970 00:00:00 GMT"),
        )
        body = json.dumps({"message": "Logget ut"}).encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
        add_cors_headers(self)
        self.end_headers()
        self.wfile.write(body)

    def handle_session_check(self) -> None:
        token = extract_session_token(self)
        session_data = SESSION_STORE.get(token)
        send_json(
            self,
            HTTPStatus.OK,
            {
                "authenticated": session_data is not None,
                "username": session_data.get("username") if session_data else None,
                "allowedPages": session_data.get("allowed_pages") if session_data else [],
            },
        )

    def handle_query(self) -> None:
        token = extract_session_token(self)
        session_data = SESSION_STORE.get(token)
        if not session_data:
            send_json(self, HTTPStatus.UNAUTHORIZED, {"error": "Du må være innlogget."})
            return
        payload = read_request_body(self)
        agent_id = payload.get("agentId")
        message = payload.get("message")
        if not agent_id or not message:
            send_json(self, HTTPStatus.BAD_REQUEST, {"error": "agentId og message er påkrevd."})
            return
        try:
            result = call_openai_agent(agent_id, message)
        except RuntimeError as err:
            send_json(self, HTTPStatus.BAD_GATEWAY, {"error": str(err)})
            return
        send_json(self, HTTPStatus.OK, {"reply": result["response"], "raw": result["raw"]})


def run_server() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    httpd = HTTPServer((host, port), SurveyAgentHandler)
    print(f"Server kjører på http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopper server...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run_server()
