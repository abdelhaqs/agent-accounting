# ETL Script: `rpc_client.py`

**Source File:** [`rpc_client.py`](file:///c:/Users/chris/Projects/agent-accounting/rpc_client.py)  
**Role:** On-Chain Ground Truth Verification (Base JSON-RPC)  
**Language:** Python 3.12  

---

## 1. Overview

`rpc_client.py` queries the Base mainnet (`chainId=8453`) directly via Uniblock's JSON-RPC endpoint (`https://api.uniblock.dev/uni/v1/json-rpc?chainId=8453`). It provides an independent ground truth verification layer, querying smart contract storage to detect pricing discrepancies or indexing delays in third-party APIs.

For full architectural diagrams and flow, see [**`docs/rpc_client_architecture.md`**](../rpc_client_architecture.md).

---

## 2. On-Chain Methods & ABI Selectors

| Method | ABI Selector | Contract Type | Description |
| :--- | :--- | :--- | :--- |
| `eth_blockNumber` | *Standard RPC* | Node Level | Reads the latest mined Base block height. |
| `eth_getBalance` | *Standard RPC* | Node Level | Reads native ETH balance in wei. |
| `balanceOf(address)` | `0x70a08231` | ERC-20 / Vault | Reads raw token or vault share balance. |
| `convertToAssets(shares)` | `0x07a2d13a` | ERC-4626 Vault | Converts vault shares to underlying token value (Morpho, Steakhouse, Clearstar). |
| `balanceOfUnderlying(address)`| `0x3af9e669` | Compound / Moonwell | Reads accumulated underlying tokens supplied to money markets. |
| `getAllMarkets()` | `0xb0772d0b` | Comptroller | Resolves all active money markets registered on Moonwell. |
| `underlying()` | `0x6f307dc3` | Market cToken | Resolves underlying ERC-20 token address for a cToken market. |

---

## 3. Key Class Interface: `UniblockRpcClient`

### Methods:

- **`get_block_number() -> int`**  
  Returns latest block number as an integer.

- **`get_eth_balance(wallet: str, block: str = "latest") -> int`**  
  Returns native ETH balance in wei.

- **`get_erc20_balance(token: str, wallet: str, block: str = "latest") -> int`**  
  Executes `eth_call` for `balanceOf(wallet)`.

- **`get_vault_assets(vault: str, wallet: str, block: str = "latest") -> tuple[int, int]`**  
  Reads raw shares via `balanceOf(wallet)` and passes shares into `convertToAssets(shares)` to obtain true underlying assets.

- **`get_balance_of_underlying(market: str, wallet: str, block: str = "latest") -> int`**  
  Queries Moonwell money market cTokens directly for user balance.

---

## 4. Multi-Key Failover & Pacing

- Automatically switches headers from `UNIBLOCK_API_KEY` to `UNIBLOCK_API_KEY_BACKUP` upon encountering HTTP `429` (rate limit) or `401/403` (unauthorized/exhausted).
- Applies `rate_limit_delay` (default `0.15s`) between queries to prevent rapid request bursts.
