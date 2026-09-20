# Multi-Agent Portfolio Comparison & Health Report

**Date:** 2026-09-20  
**Status:** Complete live snapshot of all tracked agents (including newly configured agents)  
**Configuration File:** [`agents.yaml`](file:///c:/Users/chris/Projects/agent-accounting/agents.yaml)  
**Scope:** 7 Active Agents + Summary of Deprecated Agent (`Surfliquid Base Agent 1`)  

---

## 1. Executive Summary

Following the configuration update to [`agents.yaml`](file:///c:/Users/chris/Projects/agent-accounting/agents.yaml):
- **Removed:** `Surfliquid Base Agent 1` (`0x0373...4a11`), which held minor multi-chain test tokens (~$5.70).
- **Added:** 3 new operational agents:
  1. **Zyfai Risky Agent** (`0x6a9e...015b`) — **$10,639.17**
  2. **Mamo AB Agent Abdelhak** (`0x7d42...b256`) — **$5,372.13**
  3. **Zyfai conservative Agent** (`0x3de5...e6b6`) — **$4,723.01**

### Key System Metrics:
- **Total Ecosystem Capital Under Management (AUM):** **$84,387.52** (up from ~$63,656 across previous agents, an increase of **+$20,734.31**).
- **USDC / Stablecoin Dominance:** Over **97.6%** of the entire ecosystem is deployed in USDC yield-generating positions (Morpho vaults, Moonwell lending, Euler, and Fluid).
- **Native Zerion Compatibility:** **All 7 agents** are natively recognized by Zerion's wallet and positions API on Base.

---

## 2. Master Comparison Matrix (All Agents)

| # | Agent Name | Category | Wallet Address | Total USD Value | Primary Protocol(s) | Main Underlying Asset | Strategy Profile | % of Total AUM |
|---|---|---|---|---|---|---|---|---|
| 1 | **ZyFAI Base Agent 2** | Existing | `0xBf96...7eb` | **$47,408.37** | Morpho (Clearstar) | USDC | Primary Core Treasury | **56.18%** |
| 2 | **Zyfai Risky Agent** | **NEW** | `0x6a9e...015b` | **$10,639.17** | Morpho / Fluid / Gauntlet | USDC | High-Yield Quad-Vault | **12.61%** |
| 3 | **Yieldseeker Base Agent 2** | Existing | `0xe51b...1597` | **$10,115.49** | Morpho / Yearn / Euler | USDC | Diversified Vault Yield | **11.99%** |
| 4 | **Mamo AB Agent Abdelhak** | **NEW** | `0x7d42...b256` | **$5,372.13** | Moonwell Lending | USDC | Overcollateralized Money Market | **6.37%** |
| 5 | **Zyfai conservative Agent** | **NEW** | `0x3de5...e6b6` | **$4,723.01** | Morpho (Clearstar) | USDC + ZFI Vesting | Capital Preservation + Vesting | **5.60%** |
| 6 | **Mamo Base Agent 1** | Existing | `0x7c4f...62dd` | **$4,111.41** | Moonwell + Aerodrome | USDC + AERO/LP | Lending + Protocol Incentive | **4.87%** |
| 7 | **Yieldseeker Base Agent 1** | Existing | `0x4081...b414` | **$2,017.94** | Morpho (Steakhouse) | USDC | Focused Single-Vault Yield | **2.39%** |
| — | **Surfliquid Base Agent 1** | *Removed* | `0x0373...4a11` | *$5.70* | Multi-chain test wallet | ETH, MORPHO, EXTRA | *Deprecated from tracking* | — |
| **TOTAL** | — | — | — | **$84,387.52** | — | **~97.6% USDC** | — | **100.00%** |

---

## 3. Deep-Dive Comparison of New Agents

### 3.1. Zyfai Risky Agent (`0x6a9e4e59df3e65fdb6a2f8d1ab6f0cd3943c015b`)
- **Total Balance:** **$10,639.17**
- **Architecture:** Balanced 4-way allocation across higher-yielding lending & vault pools on Base (25.00% target split).
- **Position Breakdown (Underlying USDC vs. Raw Shares):**
  - **Gauntlet USDC Frontier Vault:** 2,536.03 `gtusdcf` shares = **2,659.24 USDC** = **$2,658.32** (24.99%)
  - **Steakhouse High Yield USDC Vault:** 2,538.72 `bbqUSDC` shares = **2,659.24 USDC** = **$2,658.32** (24.99%)
  - **Fluid Yield (USDC Pool):** 2,344.86 `fUSDC` shares = **2,659.23 USDC** = **$2,658.32** (24.99%)
  - **Clearstar cbAssets Vault:** 2,588.65 `CSCBUSDC` shares = **2,659.24 USDC** = **$2,658.31** (24.99%)
  - **ZyFAI Vesting / Rewards:** 860.05 ZFI / rZFI tokens = **$5.90**
- **Why the USDC balances are identical:** The agent runs an automated rebalancing strategy (last executed in Tx `0xe1f40e...` on Sep 20 at 11:35 UTC), dividing its total available capital (~$10,636.93 USDC) into exactly **four equal 25.00% allocations** of **$2,659.23 USDC** each. Zerion resolves and displays the underlying USDC rather than raw vault share tokens (which differ due to varying NAV exchange rates).


### 3.2. Mamo AB Agent Abdelhak (`0x7d42ae4ec4367b52dc03abfc077461cf5c48b256`)
- **Total Balance:** **$5,372.13**
- **Architecture:** Concentrated money-market supply position on Moonwell.
- **Position Breakdown:**
  - **Moonwell Lending (mUSDC):** 5,373.71 USDC supplied = **$5,371.65** (99.99%)
  - **Moonwell Accrued Rewards (WELL):** 248.30 WELL tokens = **$0.48**
- **Analysis:** Clean, low-complexity supply position. Unlike `Mamo Base Agent 1` (which holds 37 separate airdrop/incentive tokens), this agent is focused exclusively on Moonwell USDC lending.

### 3.3. Zyfai Conservative Agent (`0x3de51ddb55ffec013f428288559dd993e9eeb6b6`)
- **Total Balance:** **$4,723.01** (Zerion) / **$4,725.94** (DeBank)
- **Architecture:** Defensive capital allocation focused on prime Morpho vaults with active ZFI reward vesting.
- **Position Breakdown:**
  - **Clearstar cbAssets Vault (Morpho):** 4,308.08 shares = **$4,306.68** (91.19%)
  - **Steakhouse High Yield USDC (Morpho):** 350.08 shares = **$349.97** (7.41%)
  - **ZyFAI Protocol Vesting / Locked / Rewards:** 9,668.0 ZFI tokens in various vesting tiers = **$66.36** (1.40%)
- **Analysis:** As the name suggests, ~91.2% of its funds are anchored in Clearstar's conservative cbAssets vault, with the remainder participating in ZFI protocol vesting schedules.

---

## 4. ZyFAI Cluster Comparison: Risky vs. Conservative vs. Base Agent 2

The three ZyFAI agents form the largest capital cluster (**$62,770.55**, representing **74.4%** of total system AUM):

| Metric | ZyFAI Base Agent 2 | Zyfai Risky Agent | Zyfai conservative Agent |
|---|---|---|---|
| **Capital Deployed** | **$47,408.37** | **$10,639.17** | **$4,723.01** |
| **Strategy Focus** | Core Treasury Anchor | Dynamic Multi-Vault Yield | Capital Preservation |
| **Primary Vaults** | 100% Clearstar cbAssets | 25% Gauntlet, 25% Steakhouse, 25% Fluid, 25% Clearstar | 91.2% Clearstar, 7.4% Steakhouse |
| **Diversification** | Single-vault concentration | Highly diversified across 4 distinct protocols | Conservative 2-vault split |
| **Vesting / Rewards** | 31,255 rZFI | 860.05 ZFI ($5.90) | 9,668 ZFI ($66.36 across 6 streams) |

---

## 5. Mamo Cluster Comparison: Base Agent 1 vs. AB Agent Abdelhak

| Metric | Mamo Base Agent 1 | Mamo AB Agent Abdelhak |
|---|---|---|
| **Wallet Address** | `0x7c4f5EfCE7ebD0E99D9d38CAd4573140087162dd` | `0x7d42ae4ec4367b52dc03abfc077461cf5c48b256` |
| **Total Balance** | **$4,111.41** | **$5,372.13** |
| **Moonwell USDC Supplied** | $2,121.43 (51.6%) | **$5,371.65 (99.9%)** |
| **Secondary Positions** | $1,987.29 in Aerodrome LP / partner tokens | $0.00 |
| **Token Complexity** | High (37 tokens/positions, airdrop dust) | Clean (USDC supply + WELL rewards only) |

---

## 6. Yieldseeker Cluster Comparison: Agent 1 vs. Agent 2

| Metric | Yieldseeker Base Agent 1 | Yieldseeker Base Agent 2 |
|---|---|---|
| **Wallet Address** | `0x40813DF8a23534783E99031fe4F57A65ACEeb414` | `0xe51b7dba38e732a19838c3f23816df7092441597` |
| **Total Balance** | **$2,017.94** | **$10,115.49** |
| **Underlying Positions** | 100% Steakhouse USDC on Morpho (`#e44b61`) | 78.4% Steakhouse High Yield v1.1 + 21.6% Yearn OG USDC |
| **Status History** | Consistently healthy (OK -0.001%) | Historical mismatch (+12.86%) resolved on Sep 15 |

---

## 7. Cloud Deployment & Pipeline Sync Status

1. **Local Configuration:**
   - [`agents.yaml`](file:///c:/Users/chris/Projects/agent-accounting/agents.yaml) has been updated with the 7 agents.
   - Backup API key `6Gqv6O12AkVHyJY4tlqAhczrcqhYG1AOPur7si4WC3M` is configured in `.env` with automated failover.
   - All 12 unit tests pass (`pytest test_sync.py`).

2. **GCP Cloud Run State:**
   - The GCP Cloud Run job (`zerion-sync`) on Google Cloud currently still runs the previous Docker image containing the legacy 5-agent configuration.
   - To deploy the new 7-agent configuration and update Secret Manager in GCP:
     ```powershell
     .\trigger_sync.ps1 -UpdateSecret -DeployCode
     ```
   - Once completed, the automated GCP cron will ingest and reconcile all 7 agents on every scheduled cycle.
