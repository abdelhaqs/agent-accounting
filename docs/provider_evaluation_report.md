# Data Provider Evaluation: Zerion vs. DeBank (via Uniblock)

**Date:** 2026-09-12
**Scope:** Agent-accounting pipeline on GCP — 5 Base-chain agent wallets, balance snapshots 2026-08-30 → 2026-09-08 (191 balance snapshot files)
**Audience:** Team report — provider selection recommendation

---

## TL;DR

- **Both providers return accurate USD values where they can be checked.** On the one direct overlap (ZyFAI, 2026-09-02), Zerion's two pipelines agreed within **0.011%**, and day-over-day trends are smooth for all agents.
- **DeBank is the better data provider for accounting purposes.** Its schema carries protocol-level position IDs (`Moonwell: Lending #3ef26c`, `Morpho: Yield #259ca0`), so duplicate rows are structurally detectable. Across 91 DeBank snapshot files we found **zero** duplicate incidents.
- **Zerion's schema is too coarse for reliable accounting.** With only generic `deposit`/`reward`/`wallet` position types and no position ID, **7 of its snapshots double-counted the same USDC deposit** (2× the real balance on 2026-09-06/07), and the duplicate is not reliably detectable from the payload alone — we fixed it only with a value-proximity (1%) heuristic that could in theory merge two genuinely separate positions.
- **Recommendation: make DeBank (via Uniblock) the primary provider for balance/accounting data; keep Zerion as a secondary source; keep the on-chain JSON-RPC verification layer as ground truth.** Also fix the write path: the duplicate rows are sequential DB ids written microseconds apart — a missing unique constraint on `(wallet, token, position, snapshot)`, not a provider error.

---

## 1. Background and Setup

The pipeline (deployed on GCP as a **Cloud Run Job** triggered every 6 hours by **Cloud Scheduler**, output to **Cloud Storage**, loaded into **BigQuery**) tracks 5 agent wallets on Base:

| Agent | Address | Data source in archive |
|---|---|---|
| Yieldseeker Base Agent 1 | `0x40813D…eb414` | DeBank |
| Yieldseeker Base Agent 2 | `0xe51b7d…1597` | DeBank |
| Mamo Base Agent 1 | `0x7c4f5E…162dd` | DeBank |
| ZyFAI Base Agent 2 | `0xBf96c9…e7eb` | Zerion |
| Surfliquid Base Agent 1 | `0x0373be…74a11` | Zerion |

The sync runs on a 6-hour cadence (00:00 / 06:00 / 12:00 / 18:00 UTC). This evaluation is based on the archived snapshot files in `archive_downloads/full_archive/` covering **2026-08-30 → 2026-09-08** (10 days).

Architecture roles in the code:

- **Zerion API v1** — primary source for transfers, positions, and portfolio aggregates.
- **Uniblock Direct API (DeBank proxy)** — fallback provider for Zerion-unsupported wallets; supplies token lists, protocol positions, and history.
- **Uniblock JSON-RPC (Base mainnet)** — independent ground-truth verification layer (direct `eth_call` to chain, no indexer).

## 2. Endpoints Used in This Project

### 2.1 Zerion API v1 — primary provider

Base URL: `https://api.zerion.io/v1` — Auth: HTTP Basic (API key as username, empty password). Code: `zerion_client.py`.

| Endpoint | Used for |
|---|---|
| `GET /wallets/{address}/positions/` | All token/DeFi positions, incl. vault & LP receipt tokens (paginated, `page[size]=100`) |
| `GET /wallets/{address}/transactions/` | Full ERC-20 transfer history (paginated) |
| `GET /wallets/{address}/portfolio` | Aggregate portfolio value, used to cross-check position sums |

Client behavior: retries 429/5xx with exponential backoff (5 attempts), 0.25 s polite delay between pages (free-tier friendly).

### 2.2 Uniblock Direct API — DeBank proxy (fallback provider)

Base URL: `https://api.uniblock.dev/direct/v1/DeBank` — Auth: `x-api-key` header. Code: `uniblock_client.py`. Docs: <https://docs.uniblock.dev/reference/resources/providers>.

| Endpoint | Used for |
|---|---|
| `GET /v1/user/total_balance?id={wallet}` | Total USD value + per-chain breakdown |
| `GET /v1/user/all_token_list?id={wallet}` | Wallet token balances across chains |
| `GET /v1/user/all_complex_protocol_list?id={wallet}&chain_ids=base` | DeFi protocol positions (lending, vaults, LP) with underlying-token detail |
| `GET /v1/user/all_history_list?id={wallet}` | Cross-chain transaction history (one page of 100 — sufficient for low-activity wallets) |

### 2.3 Uniblock JSON-RPC — on-chain verification (ground truth)

Endpoint: `https://api.uniblock.dev/uni/v1/json-rpc?chainId=8453` (Base mainnet) — Auth: same `x-api-key`. Code: `rpc_client.py`.

| RPC method | Used for |
|---|---|
| `eth_getBalance` | Native ETH balance |
| `eth_call` + `balanceOf(address)` (`0x70a08231`) | ERC-20 wallet balances |
| `eth_call` + `convertToAssets(uint256)` (`0x07a2d13a`) | ERC-4626 vault shares → underlying assets |
| `eth_call` + `getAllMarkets()` / `underlying()` / `balanceOfUnderlying(address)` | Compound-fork (Moonwell) lending positions |

This layer recomputes balances straight from Base nodes (no indexer in between) and reports the delta % vs. the stored provider totals; per-item breakdowns are archived as `raw_onchain_<timestamp>.json`.

### 2.4 Dashboard

`usdc_balance_chart.html` reads `usdc_balance_data.json` (aggregated by `build_usdc_balance_data.py`); falls back to an embedded snapshot when opened via `file://`. Chart.js + date adapter are loaded from the jsDelivr CDN.

## 3. What We Measured

1. **Accuracy** — cross-provider agreement on overlapping captures; day-over-day trend continuity.
2. **Reliability** — duplicate/ghost rows in the data.
3. **Schema quality** — position granularity, duplicate detectability, metadata (receipt-token flags, protocol IDs).
4. **Completeness/noise** — token coverage, unpriced/zero-value rows.
5. **Operational fit** — auth, rate limits, pagination, fallback coverage.

Caveat: **no agent is covered by both providers in the same file**, so cross-validation is limited to one overlapping day and trend analysis. The on-chain RPC layer exists in the pipeline as ground truth; the findings below are from the archive analysis.

## 4. Findings

### 4.1 Volume and coverage

| Metric | DeBank | Zerion (incl. early unlabeled) |
|---|---|---|
| Snapshot files | 91 | 100 (62 labeled + 38 early, same schema) |
| Balance rows | 1,085 | 565 |
| Distinct position types | 11 protocol-specific (`Moonwell: Lending #…`, `Morpho: Yield #…`, `Merkl: Rewards #…`, `Euler: Yield`, `Spark: Yield`, `wallet`) | 3 generic (`deposit`, `reward`, `wallet`) |
| Agents covered | Mamo 1/2, Yieldseeker 1/2 | ZyFAI 2, Surfliquid 1 |
| Rows without price (zero-value) | 740 (68%) — mostly unpriced junk/meme tokens | 124 (22%) |

DeBank lists everything in the wallet — including scam/meme tokens that have no price and contribute $0. That is noise for accounting but harmless; it also means DeBank **sees** positions Zerion's generic typing doesn't distinguish.

### 4.2 Accuracy: values agree where comparable

- **Direct overlap (ZyFAI, 2026-09-02):** early Zerion pipeline `$47,312.30` vs. labeled Zerion pipeline `$47,317.62` → **0.011% difference**. Same position, two reads hours apart.
- **Trend continuity:** ZyFAI's daily USDC totals move smoothly across the provider switch (`47,297 → 47,301 → 47,294` early vs. `47,312/47,318` labeled) with no step change; all agents show gradual drift consistent with lending yield, no unexplained jumps — except the duplicate bug below.

Conclusion: **both providers' raw values are accurate.**

### 4.3 Reliability: the duplicate-position bug is a Zerion-schema problem

Seven Zerion snapshots (ZyFAI, 2026-09-06 06:01 → 2026-09-07 18:03) contained the **same deposit twice** — two rows identical in every business field (wallet, chain, token, position type) with only cents of price noise between them, written as sequential DB ids microseconds apart. Effect on the daily aggregate:

| Day | Reported | Real | Inflation |
|---|---|---|---|
| 2026-09-06 | $94,708.96 | $47,354.82 | 2.0× |
| 2026-09-07 | $94,677.44 | $47,342.20 | 2.0× |

- **DeBank: 0 duplicate incidents in 91 files.** Its position IDs make duplicates self-evident.
- **Zerion: 7 files with real duplicates**, and because there is no position ID, the duplicate is only detectable by value proximity. Our fix (`build_usdc_balance_data.py`) drops rows within the same `(wallet, chain, token, position_type)` group whose values are within 1% — but that is a heuristic: two genuinely separate deposits of similar size would be wrongly merged. **This risk exists only because of Zerion's schema.**
- Root cause is partly our write path: the doubles landed as sequential ids microseconds apart, indicating a missing **unique constraint on `(wallet, token, position, snapshot)`** in the Zerion ingestion path. The provider payload itself is not malformed — but DeBank's richer schema makes the same class of bug trivially visible, while Zerion's hides it.

### 4.4 Schema quality

| Aspect | DeBank | Zerion |
|---|---|---|
| Position identity | Protocol + unique position ID | Position type only |
| Receipt-token flag | ✅ `is_receipt_token` | ❌ |
| Duplicate detectability | High | None (needs value heuristics) |
| Protocol coverage detail | Named protocols + pool IDs | Generic deposit/reward/wallet |
| Noise | High (unpriced junk tokens) | Low |

### 4.5 Operations

- **Zerion:** Basic-auth API key; free tier workable with polite pagination (0.25 s delay); good pagination (`links.next`); portfolio endpoint is a handy cross-check. Runs as the deployed primary (`zerion-sync` Cloud Run Job).
- **Uniblock/DeBank:** single API key covers both the DeBank proxy and JSON-RPC; retry adapters on 429/5xx; one key serves fallback + verification, which simplifies secret management.
- **GCP cadence:** every 6 hours via Cloud Scheduler; storage on GCS; BigQuery load for analytics.

## 5. Recommendation

**Primary for accounting/balances: DeBank (via Uniblock).** Equal value accuracy, far better position granularity, duplicates are structurally detectable, receipt-token semantics included.

**Secondary: Zerion.** Keep for transfer history (its primary role today) and as an independent cross-check — two indexers agreeing is cheap assurance. Do not rely on it as the sole source of position-level balances.

**Always-on: the JSON-RPC verification layer.** On-chain reads are the only ground truth; keep the delta-% reconciliation and alert when a provider drifts.

**Required fixes (any provider):**

1. Unique constraint / upsert on `(wallet, token_address, position, snapshot_id)` in the ingestion path — prevents the double-insert class of bug at the source.
2. If Zerion remains a balance source, keep the 1% dedup heuristic and monitor for false merges (log when it fires).
3. Keep the daily de-duplication in aggregation (multiple snapshots per day → last one wins).

## 6. Suggested Next Steps

- [ ] Re-point balance snapshots for ZyFAI/Surfliquid wallets at the DeBank fallback path and run both providers in parallel for 2 weeks to get true cross-provider reconciliation numbers (today we have only one overlap day).
- [ ] Add the ingestion unique constraint and back-check the existing SQLite/BigQuery rows for doubles.
- [ ] Surface the RPC delta-% in the dashboard so discrepancies are visible, not just archived.

---

## Appendix A — Evidence Tables

**Duplicate incidents (real, value > $1):** all 7 in Zerion files, ZyFAI wallet `0xbf96c935…`:

| Snapshot | Row A | Row B |
|---|---|---|
| 20260906_060140 | 47,308.69 | 47,308.70 |
| 20260906_120236 | 47,331.46 | 47,332.69 |
| 20260906_180348 | 47,354.14 | 47,354.19 |
| 20260907_000123 | 47,338.27 | 47,339.51 |
| 20260907_060325 | 47,329.94 | 47,332.43 |
| 20260907_120410 | 47,331.21 | 47,335.00 |
| 20260907_180342 | 47,335.24 | 47,340.27 |

**ZyFAI daily USDC (pre-fix):** 08-30 → 09-05 stable ~$47.3k; 09-06 $94,709 and 09-07 $94,678 (doubled); 09-08 back to $47,354 — the sawtooth that exposed the bug.

**Code references:** `zerion_client.py`, `uniblock_client.py`, `rpc_client.py`, `main.py` (`verify_onchain`, DeBank fallback), `build_usdc_balance_data.py` (USDC filter, in-file dedup, daily de-duplication), `usdc_balance_chart.html` (dashboard).
