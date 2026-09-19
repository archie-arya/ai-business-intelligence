"""Minimal client for a locally-running Ollama server."""

from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")


def generate(model: str, prompt: str, *, temperature: float = 0, json_mode: bool = False) -> str:
    request_body = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if json_mode:
        request_body["format"] = "json"
    payload = json.dumps(request_body).encode()
    request = Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=120) as response:  # nosec B310 - local configurable endpoint
        body = json.loads(response.read().decode())
    return body["response"].strip()
