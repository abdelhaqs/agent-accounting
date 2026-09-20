# ETL Script: `zerion_client.py`

**Source File:** [`zerion_client.py`](file:///c:/Users/chris/Projects/agent-accounting/zerion_client.py)  
**Role:** Primary Data Extraction (Zerion REST API v1)  
**Language:** Python 3.12  

---

## 1. Overview

`zerion_client.py` implements the client interface for Zerion's v1 REST API (`https://api.zerion.io/v1`). It is the primary data source for token positions, vault receipt shares, and multi-asset transaction histories.

---

## 2. API Endpoints Used

| Endpoint | Method | Purpose in Pipeline |
| :--- | :--- | :--- |
| `/v1/wallets/{address}/portfolio` | `GET` | Fetches overall portfolio net worth and per-chain value breakdown. |
| `/v1/wallets/{address}/positions` | `GET` | Retrieves all wallet tokens, staked assets, LP tokens, and yield vault positions (`filter[positions]=no_filter`). |
| `/v1/wallets/{address}/transactions` | `GET` | Paginated transaction history containing individual inbound and outbound ERC-20 transfer legs. |

---

## 3. Key Methods & Class Interface

### `ZerionClient(api_key, base_url, rate_limit_delay)`
Initializes the HTTP session with HTTP Basic Authentication (`api_key` encoded with empty password) and sets custom headers.

#### Methods:

- **`get_wallet_portfolio(wallet: str) -> dict`**  
  Returns total USD valuation and portfolio distribution.

- **`get_positions(wallet: str) -> Generator[dict]`**  
  Paginates through `/positions` using the `page[after]` cursor and yields normalized position dictionaries:
  ```python
  {
      "wallet": "0x...",
      "chain": "base",
      "token_address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
      "token_name": "USD Coin",
      "token_symbol": "USDC",
      "decimals": 6,
      "balance_raw": "2500000000",
      "balance_float": 2500.00,
      "price": 1.00,
      "usd_value": 2500.00,
      "is_receipt_token": False,
      "position_type": "wallet",
      "protocol": None,
      "timestamp": "2026-09-20T12:00:00Z",
      "provider": "zerion"
  }
  ```

- **`get_transactions(wallet: str) -> Generator[dict]`**  
  Streams transactions and unpacks multi-transfer legs into individual inbound/outbound transfer rows for the `transfers` table.

- **`get_raw_positions(wallet: str) -> list[dict]`** & **`get_raw_transactions(wallet: str) -> list[dict]`**  
  Fetches the complete, untouched JSON API responses for forensic audit archiving.

---

## 4. Rate Limiting & Retry Mechanism

- Automatically mounts a `requests.adapters.HTTPAdapter` with `urllib3.util.retry.Retry`.
- Retries transient errors (`429`, `500`, `502`, `503`, `504`) with exponential backoff.
- Built-in `time.sleep(rate_limit_delay)` ensures API request pacing stays within Zerion free-tier limits.
