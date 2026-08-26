"""Thin Zerion API v1 client with retries and polite pagination."""
from __future__ import annotations

import base64
import logging
import time
from typing import Any, Iterator
from urllib.parse import parse_qsl, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)
BASE_URL = "https://api.zerion.io/v1"


def _build_retry_adapter(
    retries: int = 5,
    backoff_factor: float = 1.0,
) -> HTTPAdapter:
    """Adapter that retries 429/5xx with exponential backoff."""
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False,
    )
    return HTTPAdapter(max_retries=retry_strategy)


class ZerionClient:
    """Client for Zerion Wallet API endpoints."""

    def __init__(
        self,
        api_key: str,
        rate_limit_delay: float = 0.25,
        retry_backoff: float = 1.0,
    ):
        if not api_key:
            raise ValueError("ZERION_API_KEY is required")
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        # Zerion uses Basic Auth with the API key as username and no password.
        creds = base64.b64encode(f"{api_key}:".encode()).decode()
        self.session.headers.update({
            "Authorization": f"Basic {creds}",
            "Accept": "application/json",
        })
        self.session.mount(BASE_URL, _build_retry_adapter(backoff_factor=retry_backoff))

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{BASE_URL}{path}"
        response = self.session.get(url, params=params or {}, timeout=30)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _chain_ids_param(chain_ids: list[str] | str | None) -> str | None:
        if chain_ids is None:
            return None
        if isinstance(chain_ids, str):
            return chain_ids
        return ",".join(chain_ids)

    def get_transactions(
        self,
        wallet: str,
        currency: str = "usd",
        page_size: int = 100,
        chain_ids: list[str] | str | None = None,
        raw_pages: list[dict[str, Any]] | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Yield every transaction for *wallet*, paginating through the API.

        If *raw_pages* is provided, each raw page response is appended to it.
        """
        params: dict[str, Any] = {"currency": currency, "page[size]": page_size}
        chain_filter = self._chain_ids_param(chain_ids)
        if chain_filter:
            params["filter[chain_ids]"] = chain_filter
        is_first = True
        while True:
            data = self._get(f"/wallets/{wallet}/transactions/", params=params)
            if raw_pages is not None:
                raw_pages.append(data)
            for tx in data.get("data", []):
                yield tx

            next_url = data.get("links", {}).get("next")
            if not next_url:
                break

            # Be polite to the free tier: pause between paginated requests.
            if not is_first and self.rate_limit_delay > 0:
                time.sleep(self.rate_limit_delay)
            is_first = False

            # Extract query params from the next URL to keep pagination stateless.
            parsed = urlparse(next_url)
            params = dict(parse_qsl(parsed.query))
            logger.debug("Fetching next page: %s", next_url)

    def get_positions(
        self,
        wallet: str,
        currency: str = "usd",
        positions_filter: str = "no_filter",
        page_size: int = 100,
        chain_ids: list[str] | str | None = None,
        raw_pages: list[dict[str, Any]] | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Yield every position for *wallet*, including vault/LP receipt tokens.

        If *raw_pages* is provided, each raw page response is appended to it.
        """
        params: dict[str, Any] = {
            "currency": currency,
            "filter[positions]": positions_filter,
            "page[size]": page_size,
        }
        chain_filter = self._chain_ids_param(chain_ids)
        if chain_filter:
            params["filter[chain_ids]"] = chain_filter
        is_first = True
        while True:
            data = self._get(f"/wallets/{wallet}/positions/", params=params)
            if raw_pages is not None:
                raw_pages.append(data)
            for pos in data.get("data", []):
                yield pos

            next_url = data.get("links", {}).get("next")
            if not next_url:
                break

            if not is_first and self.rate_limit_delay > 0:
                time.sleep(self.rate_limit_delay)
            is_first = False

            parsed = urlparse(next_url)
            params = dict(parse_qsl(parsed.query))
            logger.debug("Fetching next positions page: %s", next_url)
