from __future__ import annotations

import threading
import time
import webbrowser

import httpx
import uvicorn
import webview

from docflow.api.app import create_app
from docflow.settings import get_settings


def start_server() -> None:
    settings = get_settings()
    uvicorn.run(
        create_app(start_worker=True), host="127.0.0.1", port=settings.api_port, log_level="info"
    )


def wait_for_server(base_url: str, timeout_seconds: float = 20.0) -> bool:
    deadline = time.time() + timeout_seconds
    with httpx.Client(timeout=1.5) as client:
        while time.time() < deadline:
            try:
                response = client.get(f"{base_url}/api/health")
                if response.status_code == 200:
                    return True
            except Exception:  # noqa: BLE001
                pass
            time.sleep(0.3)
    return False


def main() -> None:
    settings = get_settings()
    base_url = f"http://127.0.0.1:{settings.api_port}"
    server_thread = threading.Thread(target=start_server, daemon=True, name="docflow-api")
    server_thread.start()
    if not wait_for_server(base_url):
        webbrowser.open(base_url)
        raise RuntimeError("DocFlow API failed to start within the expected time window.")
    webview.create_window(settings.desktop_title, base_url, min_size=(1280, 800))
    webview.start()
