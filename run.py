"""Dev entry point: brings up the Ollama server alongside the game's web server.

Ollama is best-effort (see eldoria/game/llm.py) -- if the binary isn't on PATH
or it fails to come up, the game still runs, just without local-LLM assist.
"""
import atexit
import socket
import subprocess
import time

import uvicorn

_OLLAMA_HOST = "127.0.0.1"
_OLLAMA_PORT = 11434
_STARTUP_TIMEOUT_SECONDS = 15.0


def _ollama_reachable() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.3)
        return sock.connect_ex((_OLLAMA_HOST, _OLLAMA_PORT)) == 0


def _start_ollama() -> subprocess.Popen | None:
    if _ollama_reachable():
        print("Ollama server already running -- reusing it.")
        return None
    try:
        proc = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print("Ollama not found on PATH -- continuing without local-LLM assist.")
        return None

    deadline = time.monotonic() + _STARTUP_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if _ollama_reachable():
            print(f"Ollama server started (pid {proc.pid}).")
            return proc
        time.sleep(0.3)
    print("Ollama server did not come up in time -- continuing without it.")
    return proc


def _stop_ollama(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


if __name__ == "__main__":
    ollama_proc = _start_ollama()
    atexit.register(_stop_ollama, ollama_proc)

    uvicorn.run("eldoria.web.main:app", host="127.0.0.1", port=8000, reload=True)
