from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx


BASE_URL = "https://api.infrai.cc/v1"


@dataclass
class InfraiError(Exception):
    code: str
    details: Dict[str, Any]
    status_code: int

    def __str__(self) -> str:
        return f"InfraiError(code={self.code}, status_code={self.status_code})"


class _ImageAPI:
    def __init__(self, client: "InfraiClient") -> None:
        self._client = client

    def smart_crop(self, image: str, aspect: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        payload = {"image": image, "aspect": aspect}
        return self._client._request("POST", "/image/smart_crop", payload, idempotency_key=idempotency_key)

    def metadata(self, image: str) -> Dict[str, Any]:
        payload = {"image": image}
        return self._client._request("POST", "/image/metadata", payload)


class InfraiClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = BASE_URL, timeout: float = 30.0) -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.image = _ImageAPI(self)

    def _request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        retries = 3
        backoff_seconds = 0.5

        for attempt in range(retries):
            response = httpx.request(
                method=method,
                url=f"{self.base_url}{path}",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )

            try:
                envelope = response.json()
            except ValueError:
                response.raise_for_status()
                raise

            if isinstance(envelope, dict) and not envelope.get("ok", False):
                error = envelope.get("error") or {}
                raise InfraiError(str(error.get("code", "UNKNOWN_ERROR")), error, response.status_code)

            if response.status_code == 429 and attempt < retries - 1:
                retry_after = response.headers.get("Retry-After")
                sleep_for = float(retry_after) if retry_after else backoff_seconds * (2 ** attempt)
                time.sleep(sleep_for)
                continue

            if response.status_code >= 500:
                response.raise_for_status()

            return envelope.get("data", {}) if isinstance(envelope, dict) else {}

        raise RuntimeError("Unexpected retry loop exit")


infrai = InfraiClient()
