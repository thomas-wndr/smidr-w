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

PUBLIC_DIR = Path(__file__).parent / "public"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "change-me"
SESSION_TTL_SECONDS = 8 * 60 * 60  # 8 hours


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

    def create(self, username: str) -> str:
        token = secrets.token_urlsafe(32)
        self._store[token] = {
            "username": username,
            "created": time.time(),
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


def send_json(handler: BaseHTTPRequestHandler, status: HTTPStatus, payload: Dict) -> None:
    encoded = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(encoded)))
    handler.end_headers()
    handler.wfile.write(encoded)


def serve_static(handler: BaseHTTPRequestHandler, path: str) -> None:
    relative_path = path.lstrip("/") or "index.html"
    file_path = PUBLIC_DIR / relative_path
    if file_path.is_dir():
        file_path = file_path / "index.html"
    if not file_path.exists():
        handler.send_error(HTTPStatus.NOT_FOUND, "File not found")
        return
    content = file_path.read_bytes()
    mime_type = "text/plain"
    if file_path.suffix == ".html":
        mime_type = "text/html; charset=utf-8"
    elif file_path.suffix == ".css":
        mime_type = "text/css; charset=utf-8"
    elif file_path.suffix == ".js":
        mime_type = "application/javascript; charset=utf-8"
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
        self.send_header("Access-Control-Allow-Origin", "*")
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
        target_username = os.environ.get("ADMIN_USERNAME", DEFAULT_USERNAME)
        target_password = os.environ.get("ADMIN_PASSWORD", DEFAULT_PASSWORD)
        if username != target_username or password != target_password:
            send_json(self, HTTPStatus.UNAUTHORIZED, {"error": "Feil brukernavn eller passord."})
            return
        token = SESSION_STORE.create(username)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Set-Cookie", f"session_id={token}; HttpOnly; Path=/")
        body = json.dumps({"message": "Innlogging vellykket"}).encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_logout(self) -> None:
        token = extract_session_token(self)
        SESSION_STORE.delete(token)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Set-Cookie", "session_id=deleted; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/")
        body = json.dumps({"message": "Logget ut"}).encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
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
