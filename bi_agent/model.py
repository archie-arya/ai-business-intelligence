"""Local chat model configuration."""

from __future__ import annotations

import os

from langchain_ollama import ChatOllama


def get_model() -> ChatOllama:
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3:latest"),
        base_url=os.getenv(
            "OLLAMA_BASE_URL",
            "http://127.0.0.1:11434",
        ),
        temperature=0,
    )