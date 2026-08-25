"""Serve the teacher chat interface and proxy conversations to Claude."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from anthropic import Anthropic
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).parent
STATIC_DIR = ROOT_DIR / "static"
load_dotenv(ROOT_DIR / ".env", override=True)


def load_teacher_prompt() -> str:
    """Load the teacher guidance used by the chat assistant."""
    return (ROOT_DIR / "skills.md").read_text(encoding="utf-8")


def create_response(messages: list[dict[str, str]]) -> str:
    """Send the conversation to Claude and return its text response."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Set ANTHROPIC_API_KEY in the environment before chatting.")

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
        max_tokens=1200,
        system=load_teacher_prompt(),
        messages=messages,
    )
    return "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )


class AppHandler(BaseHTTPRequestHandler):
    """Handle static assets and the chat endpoint."""

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self.serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return

        assets = {
            "/styles.css": (STATIC_DIR / "styles.css", "text/css; charset=utf-8"),
            "/app.js": (STATIC_DIR / "app.js", "text/javascript; charset=utf-8"),
        }
        if path in assets:
            file_path, content_type = assets[path]
            self.serve_file(file_path, content_type)
            return

        self.send_error(404, "Not found")

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/chat":
            self.send_error(404, "Not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload: dict[str, Any] = json.loads(self.rfile.read(content_length))
            messages = payload.get("messages", [])
            if not isinstance(messages, list) or not messages:
                raise ValueError("At least one message is required.")
            response_text = create_response(messages)
            self.send_json(200, {"response": response_text})
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self.send_json(400, {"error": str(error)})
        except Exception as error:
            print(f"Claude request failed: {type(error).__name__}: {error}", flush=True)
            self.send_json(502, {"error": "Claude could not respond right now."})

    def serve_file(self, file_path: Path, content_type: str) -> None:
        try:
            content = file_path.read_bytes()
        except FileNotFoundError:
            self.send_error(404, "Not found")
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, status: int, payload: dict[str, str]) -> None:
        content = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args: Any) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), AppHandler)
    print("Teacher chat is running at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping teacher chat.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
