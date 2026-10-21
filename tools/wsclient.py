"""Minimal OpenEnv WebSocket client used by the replay and calibration scripts."""

import json
from urllib.parse import urlsplit, urlunsplit

from websockets.sync.client import connect


def ws_url(base_url: str) -> str:
    parts = urlsplit(base_url.rstrip("/"))
    scheme = "wss" if parts.scheme == "https" else "ws"
    return urlunsplit((scheme, parts.netloc, parts.path + "/ws", "", ""))


class Session:
    def __init__(self, base_url: str, timeout: float = 30):
        self.timeout = timeout
        self.sock = connect(ws_url(base_url), open_timeout=timeout, close_timeout=5, max_size=2**22)

    def _send(self, message: dict) -> dict:
        self.sock.send(json.dumps(message))
        response = json.loads(self.sock.recv(timeout=self.timeout))
        if response.get("type") != "observation":
            raise RuntimeError(f"unexpected response: {response}")
        data = response["data"]
        reward = data.get("reward")
        assert isinstance(data.get("done"), bool), data
        assert reward is None or (isinstance(reward, (int, float)) and 0 <= reward <= 1), data
        return data

    def reset(self, **kwargs) -> dict:
        return self._send({"type": "reset", "data": kwargs})

    def step(self, action: dict) -> dict:
        return self._send({"type": "step", "data": action})

    def close(self):
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
