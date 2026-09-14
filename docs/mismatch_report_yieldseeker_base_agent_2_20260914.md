# Balance Mismatch Investigation — Yieldseeker Base Agent 2

**Date:** 2026-09-14
**Agent:** Yieldseeker Base Agent 2 (`0xe51b7dba38e732a19838c3f23816df7092441597`), chain: Base
**Trigger log:** `logs_downloads/sync_log_20260914_180246.txt:40`

```
Yieldseeker Base Agent 2 [debank]: stored=$11,412.95 | same-provider=$11,412.95 |
cross-provider=$0.00 | on-chain=$10,112.01 (+$0.12 unverified) (+12.864%) -> MISMATCH
```

## TL;DR

The on-chain verification is correct; the **stored (DeBank-derived) balance is overstated by ~10%**.
The wallet's entire portfolio sits in a single Morpho MetaMorpho vault (UltraYield USDC, `edgeUSDC`),
and DeBank's price feed for that vault values its shares ~10% above the redeemable on-chain value.
The mismatch detector is doing its job.

## Reconciliation anatomy

The line compares two independent measurements of the same wallet:

| Source | Value | Notes |
|---|---|---|
| `stored` | $11,412.95 | DeBank portfolio total, written to the balances table |
| `same-provider` | $11,412.95 | Zerion cross-check unavailable for this agent (DeBank-only) |
| `on-chain` | $10,112.01 | Independent JSON-RPC recomputation: ERC-20 `balanceOf` + ERC-4626 `convertToAssets` |
| unverified | $0.12 | Merkl reward position, not verifiable on-chain (correctly excluded) |

Delta = +12.864% → above threshold → MISMATCH. Since the on-chain side reconciles to within
$0.12, the gap lives entirely in the stored balance.

## What the wallet actually holds (verified live via JSON-RPC, 2026-09-14 ~22:50 UTC)

The wallet exited its Euler position between Sep 8 and Sep 14 (Euler shares now **0**) and
consolidated everything into one vault:

- **UltraYield USDC** (`edgeUSDC`) — MetaMorpho vault `0x5435bc53f2c61298167cdb11cdf0db2bfa259ca0`
  - Wallet shares: 4,845.85 (`balanceOf`)
  - Redeemable underlying: **10,111.70 USDC** (`convertToAssets`)
  - Vault-wide `totalAssets` = 799,358.82 USDC / `totalSupply` = 383,078.21 shares
    → true price/share = **2.0867 USDC**
- Wallet USDC balance: 0
- Merkl claimable rewards: ~11 USDC total accrued, ~0 pending (not the source of the gap)

## Root cause: DeBank overstates this specific vault by ~10%

| Source | Position value | Implied price/share |
|---|---|---|
| On-chain `convertToAssets` (ground truth) | 10,111.70 USDC | **2.0867** |
| DeBank API | 11,144.95 USDC | **~2.30** |

DeBank values `edgeUSDC` at ~2.30/share while the vault contract redeems at 2.0867/share.
This is persistent, not a one-off — it appears in every archived snapshot:

| Snapshot | DeBank stored | On-chain | Gap |
|---|---|---|---|
| 2026-09-02 23:30 | 8,417.10 | 7,704.06 | ~9.3% |
| 2026-09-06 18:03 | 2,048.32 | 1,851.78 | ~10.6% |
| 2026-09-07 18:03 | 2,036.15 | 1,842.46 | ~10.6% |
| 2026-09-08 18:04 | 2,505.34 | 2,249.84 | ~11.4% |
| 2026-09-14 22:50 | 11,144.95 | 10,111.70 | ~10.2% |

**Control cases that matched on-chain to the cent**, ruling out a pipeline bug:

- Euler vault position: stored vs on-chain within cents on every snapshot
- Second Morpho vault #de5d03 (exited Sep 3–6): 2,387.39 stored vs 2,387.40 on-chain
- Merkl rewards ($0.09) correctly tracked as unverified, not folded into the total

Ruled out as explanations:

- **Accrued Merkl/Morpho rewards**: wallet's claimable rewards are ~11 USDC total, ~0 pending —
  orders of magnitude too small to explain a ~$1,030 gap.
- **Transfers not yet indexed**: unverified delta is only $0.12; transfers reconcile.

## Why it surfaced now

The ~10% feed error on this vault existed since at least Sep 2, but the wallet was diversified
across Euler + two Morpho vaults, so the blended error stayed small. Around Sep 8–14 the agent
moved 100% of funds into the UltraYield USDC vault, concentrating the whole portfolio in the one
asset DeBank misprices — turning a ~10% position error into a +12.9% whole-wallet mismatch.

## Why DeBank is wrong (hypothesis)

DeBank's `edgeUSDC` valuation (~2.30/share) sits ~10% above the contract's redeemable price
(2.0867/share). Either DeBank's price feed for this vault is stale/erroneous, or the vault has
unrealized bad debt (e.g. from the March 2026 Resolv USR exploit that triggered $180M in
liquidations across 15 Morpho vaults) which DeBank's accounting does not reflect. Either way,
the wallet can only redeem at the on-chain price, so the on-chain figure is the economically
correct one for accounting purposes.

## Recommended actions

1. **Accounting:** treat the on-chain figure ($10,112.01) as the source of truth for this agent;
   the stored DeBank balance overstates holdings by ~$1,300 (12.9%).
2. **Pipeline:** consider flagging per-position deltas in the reconciliation output, not just
   wallet-level — the per-vault gap was visible since Sep 2 but only tripped the threshold after
   the portfolio became concentrated.
3. **Follow-up:** open a DeBank support ticket about the `edgeUSDC` feed, or audit the vault's
   Morpho Blue market allocations for bad debt to confirm which side of the hypothesis is right.

## Appendix: reproduction

The live checks used the project's own clients (`rpc_client.UniblockRpcClient`,
`uniblock_client.UniblockClient`) against Base (chainId 8453), loading credentials the same way
`main.py` does. Archived per-run snapshots in `archive_downloads/full_archive/` provide the
historical comparison.
