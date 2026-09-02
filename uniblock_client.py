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
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False,
    )
    return HTTPAdapter(max_retries=retry_strategy)


class UniblockClient:
    """Client for DeBank endpoints proxied through Uniblock's Direct API."""

    def __init__(self, api_key: str, rate_limit_delay: float = 0.25):
        if not api_key:
            raise ValueError("UNIBLOCK_API_KEY is required")
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "accept": "application/json",
        })
        self.session.mount(BASE_URL, _build_retry_adapter())

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = self.session.get(f"{BASE_URL}{path}", params=params or {}, timeout=30)
        response.raise_for_status()
        if self.rate_limit_delay > 0:
            time.sleep(self.rate_limit_delay)
        return response.json()

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
