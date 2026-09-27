# Agent Tracking Recap

> **Project:** `agent-accounting` · **GCP Project:** `agent-accounting-506719` · **Region:** `us-central1`
> **Last updated:** 2026-09-02 (execution `zerion-sync-jlkr5`)
> **Schedule:** every 6 hours via Cloud Scheduler (`zerion-sync-6hr`)

---

## Provider strategy

| Priority | Provider | Role | Auth |
|---|---|---|---|
| 1 | **Zerion API** | Primary source for all agents | `ZERION_API_KEY` (Secret Manager: `zerion-api-key`) |
| 2 | **Uniblock → DeBank** | Automatic fallback when Zerion doesn't index a wallet | `UNIBLOCK_API_KEY` (Secret Manager: `uniblock-api-key`) |

Every row in the warehouse is tagged with `provider = 'zerion' | 'debank'`.

---

## Tracked agents (all on Base network)

| # | Agent | Address | Provider | Balances | USD value |
|---|---|---|---|---|---|
| 1 | ZyFAI Base Agent 2 | `0xBf96c935F7cB35b86Efaa0693D81d875f4B4e7eb` | zerion | 8 | $47,304.44 |
| 2 | Mamo Base Agent 1 | `0x7c4f5EfCE7ebD0E99D9d38CAd4573140087162dd` | debank | 28 | $2,097.41 |
| 3 | Yieldseeker Base Agent 1 | `0x40813DF8a23534783E99031fe4F57A65ACEeb414` | debank | 1 | $2,015.06 |
| 4 | Yieldseeker Base Agent 2 | `0xe51b7dba38e732a19838c3f23816df7092441597` | debank | 6 | $10,322.20 |
| 5 | Surfliquid Base Agent 1 | `0x0373beEef981B60dD35D05db9D32DDc100474a11` | zerion | 5 | $5.33 |

### No longer tracked

| Agent | Address | Note |
|---|---|---|
| Mamo Base Agent 2 | `0x53d78cc346e05f153401ac4c0c7626062e0b9a40` | Replaced by Mamo Base Agent 1 on 2026-09-02; historical rows still in warehouse |

---

## Endpoints used

### Zerion (primary) — `https://api.zerion.io/v1`

| Endpoint | Purpose | Filters applied |
|---|---|---|
| `GET /wallets/{address}/transactions/` | ERC-20 transfer history (paginated) | `filter[chain_ids]=base`, `currency=usd`, `page[size]=100` |
| `GET /wallets/{address}/positions/` | Token + DeFi positions (incl. vault/LP receipts) | `filter[positions]=no_filter`, `filter[chain_ids]=base` |

Auth: HTTP Basic (API key as username). Source: [zerion_client.py](zerion_client.py)

### Uniblock Direct API → DeBank (fallback) — `https://api.uniblock.dev/direct/v1/DeBank`

| Endpoint | Purpose | Filters applied |
|---|---|---|
| `GET /v1/user/all_token_list` | Wallet token balances | `is_all=false` (core tokens), client-side chain filter `base` |
| `GET /v1/user/all_complex_protocol_list` | DeFi positions (Morpho, Moonwell, Merkl…) | `chain_ids=base` |
| `GET /v1/user/all_history_list` | Transaction history (sends/receives) | `chain_ids=base`, `page_count=100` |
| `GET /v1/user/total_balance` | Total USD sanity check | — |

Auth: `x-api-key` header. Source: [uniblock_client.py](uniblock_client.py)

---

## Pipeline flow (per agent, per run)

```
Zerion API ──fails──▶ Uniblock/DeBank fallback
     │                       │
     └───────────┬───────────┘
                 ▼
   SQLite (ephemeral scratch)
                 ▼
   RECV/  (staging, timestamped JSONs)
                 ▼
   logs/  (sync_log_<timestamp>.txt)
                 ▼
   Archive/  (flat, <agent>_<type>_<timestamp>.json)
                 ▼
   BigQuery dataset: agent_accounting
     ├─ transfers  (append + MERGE dedupe, partitioned by mined_at)
     └─ balances   (per-wallet snapshot replace, partitioned by updated_at)
```

**GCS bucket:** `gs://agent-accounting-506719-zerion-raw-data/`
**BigQuery:** `agent_accounting.transfers` · `agent_accounting.balances`

---

## Position detail (latest run)

| Agent | Position | Token | USD |
|---|---|---|---|
| ZyFAI Base Agent 2 | wallet + DeFi (via Zerion) | USDC & others | $47,304.44 |
| Yieldseeker Base Agent 2 | Morpho: Yield #2d3a3c | USDC | $7,648.23 |
| Yieldseeker Base Agent 2 | Morpho: Yield #259ca0 | USDC | $2,673.25 |
| Yieldseeker Base Agent 2 | wallet / Merkl / Moonwell | USDC, WELL | $0.72 |
| Mamo Base Agent 1 | wallet + protocols (via DeBank) | various | $2,097.41 |
| Yieldseeker Base Agent 1 | Morpho: Yield #e44b61 | USDC | $2,015.06 |
| Surfliquid Base Agent 1 | wallet + DeFi (via Zerion) | ETH, MORPHO, EXTRA | $5.33 |

**Total tracked value: ~$61,746**
