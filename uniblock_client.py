"""Uniblock Direct API client for DeBank endpoints (fallback provider to Zerion).

Docs: https://docs.uniblock.dev/reference/resources/providers
DeBank paths are proxied under /direct/v1/DeBank, e.g.
  GET https://api.uniblock.dev/direct/v1/DeBank/v1/user/total_balance?id=0x...
Auth: x-api-key header with a Uniblock API key.
"""
from __future__ import annotations

import logging
import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)
BASE_URL = "https://api.uniblock.dev/direct/v1/DeBank"


def _build_retry_adapter(retries: int = 4, backoff_factor: float = 1.0) -> HTTPAdapter:
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False,
    )
    return HTTPAdapter(max_retries=retry_strategy)


def _parse_keys(
    api_key: str | list[str] | None, backup_api_key: str | list[str] | None = None
) -> list[str]:
    """Normalize primary and optional backup keys into an ordered deduplicated list."""
    keys: list[str] = []
    for item in (api_key, backup_api_key):
        if not item:
            continue
        if isinstance(item, str):
            parts = [p.strip() for p in item.split(",") if p.strip()]
            for p in parts:
                if p not in keys:
                    keys.append(p)
        elif isinstance(item, (list, tuple)):
            for p in item:
                p_str = str(p).strip()
                if p_str and p_str not in keys:
                    keys.append(p_str)
    return keys


class UniblockClient:
    """Client for DeBank endpoints proxied through Uniblock's Direct API."""

    def __init__(
        self,
        api_key: str | list[str],
        backup_api_key: str | list[str] | None = None,
        rate_limit_delay: float = 0.25,
    ):
        self.api_keys = _parse_keys(api_key, backup_api_key)
        if not self.api_keys:
            raise ValueError("UNIBLOCK_API_KEY is required")
        self.current_key_index = 0
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": self.api_keys[0],
            "accept": "application/json",
        })
        self.session.mount(BASE_URL, _build_retry_adapter())

    def _switch_to_next_key(self, reason: str = "") -> bool:
        """Switch to the next available API key if available."""
        if len(self.api_keys) <= 1:
            return False
        next_index = (self.current_key_index + 1) % len(self.api_keys)
        if next_index == self.current_key_index:
            return False
        prev_key = self.api_keys[self.current_key_index]
        next_key = self.api_keys[next_index]
        logger.warning(
            "Uniblock API key ...%s failed (%s). Switching to backup key ...%s",
            prev_key[-6:] if len(prev_key) >= 6 else prev_key,
            reason,
            next_key[-6:] if len(next_key) >= 6 else next_key,
        )
        self.current_key_index = next_index
        self.session.headers["x-api-key"] = next_key
        return True

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        max_attempts = len(self.api_keys)
        last_exc: Exception | None = None
        for attempt in range(max_attempts):
            try:
                response = self.session.get(f"{BASE_URL}{path}", params=params or {}, timeout=30)
                if response.status_code in (429, 401, 403) and attempt < max_attempts - 1:
                    if self._switch_to_next_key(f"HTTP {response.status_code}"):
                        continue
                response.raise_for_status()
                if self.rate_limit_delay > 0:
                    time.sleep(self.rate_limit_delay)
                return response.json()
            except requests.RequestException as exc:
                last_exc = exc
                status = getattr(getattr(exc, "response", None), "status_code", None)
                if attempt < max_attempts - 1 and self._switch_to_next_key(
                    f"HTTP {status}" if status else str(exc)
                ):
                    continue
                raise
        if last_exc:
            raise last_exc


    def get_total_balance(self, wallet: str) -> dict[str, Any]:
        """Total USD value + per-chain breakdown."""
        return self._get("/v1/user/total_balance", {"id": wallet})

    def get_all_token_list(self, wallet: str, is_all: bool = False) -> list[dict[str, Any]]:
        """Wallet token balances across all chains (DeBank 'core' tokens by default)."""
        return self._get("/v1/user/all_token_list", {"id": wallet, "is_all": str(is_all).lower()})

    def get_complex_protocol_list(
        self, wallet: str, chain_ids: str | None = None
    ) -> list[dict[str, Any]]:
        """DeFi protocol positions (lending, vaults, LP) with underlying token detail."""
        params: dict[str, Any] = {"id": wallet}
        if chain_ids:
            params["chain_ids"] = chain_ids
        return self._get("/v1/user/all_complex_protocol_list", params)

    def get_all_history_list(
        self, wallet: str, chain_ids: str | None = None, page_count: int = 100
    ) -> dict[str, Any]:
        """Transaction history across chains.

        Returns the full response dict (history_list + token_dict + project_dict).
        Note: DeBank paginates via page_count per call; we fetch one page (default 100),
        which is sufficient for low-activity fallback wallets.
        """
        params: dict[str, Any] = {"id": wallet, "page_count": page_count}
        if chain_ids:
            params["chain_ids"] = chain_ids
        return self._get("/v1/user/all_history_list", params)
