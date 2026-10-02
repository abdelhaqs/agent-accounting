# Value Check & On-Chain Reconciliation Report

**Execution Run ID:** `20261002_120500`  
**Run Timestamp:** 2026-10-02 12:05:00 UTC  
**Primary Source:** **UNIBLOCK**  
**Cross-Check Layer:** **Base On-Chain JSON-RPC** (`https://mainnet.base.org`)  
**Total Agents Audited:** 8  

---

## 1. Executive Summary

- **Audit Health Score:** **8/8 Agents Healthy (100.0%)**
- **Total Capital Tracked (USD):** **$82,195.91**
- **On-Chain Verified Value:** **$82,187.10**
- **Unverified / Reward Assets:** **$11.85**
- **Net On-Chain Delta:** **-0.004%**

### Status Breakdown:
- **OK (Healthy):** 8
- **MISMATCH:** 0
- **RPC_UNVERIFIED:** 0
- **FAILED:** 0

---

## 2. Multi-Provider & On-Chain Audit Table

| Agent Name | Address | Provider | Stored Value (USD) | Same-Provider (Raw) | On-Chain Verified (RPC) | On-Chain Unverified | On-Chain Delta (%) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Yieldseeker Base Agent 1** | `0x4081...b414` | debank | **$2,021.60** | $2,021.60 | **$2,021.67** | $0.00 | **-0.003%** | **OK** |
| **Yieldseeker Base Agent 2** | `0xe51b...1597` | debank | **$10,133.09** | $10,133.09 | **$10,133.42** | +$0.13 | **-0.005%** | **OK** |
| **ZyFAI Base Agent 2** | `0xbf96...e7eb` | debank | **$47,492.51** | $47,492.51 | **$47,491.74** | +$2.27 | **-0.003%** | **OK** |
| **Mamo Base Agent 1** | `0x7c4f...62dd` | debank | **$2,139.94** | $2,139.94 | **$2,134.81** | +$5.36 | **-0.011%** | **OK** |
| **Zyfai AB Risky Agent** | `0x6a9e...015b` | debank | **$0.05** | $10.53 | **$0.00** | +$0.05 | **+0.074%** | **OK** |
| **Mamo AB Agent** | `0x7d42...b256` | debank | **$5,402.22** | $5,402.22 | **$5,400.72** | +$1.78 | **-0.005%** | **OK** |
| **Zyfai Yield Maxing Agent** | `0x3de5...b6b6` | debank | **$15,005.52** | $15,068.30 | **$15,004.74** | +$1.28 | **-0.003%** | **OK** |
| **Conservative Zyfai Agent** | `0xc811...4774` | debank | **$0.98** | $0.98 | **$0.00** | +$0.98 | **+0.002%** | **OK** |
| **TOTAL** | — | — | **$82,195.91** | **$82,269.16** | **$82,187.10** | **+$11.85** | **-0.004%** | **8/8 HEALTHY** |

---

## 3. Agent Details & Breakdown

### 3.1. Yieldseeker Base Agent 1 (`0x40813df8a23534783e99031fe4f57a65aceeb414`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,021.60`
- **On-Chain Verified Total:** `$2,021.67` (delta: -0.003%)
- **Verified Assets Breakdown:**
  - `USDC`: $2,021.67 (Morpho vault `0xee8f4ec5...`)

### 3.2. Yieldseeker Base Agent 2 (`0xe51b7dba38e732a19838c3f23816df7092441597`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,133.09`
- **On-Chain Verified Total:** `$10,133.42` (delta: -0.005%)
- **Unverified / Reward Assets:** `$0.13`
- **Verified Assets Breakdown:**
  - `USDC`: $7,929.22 (Euler vault `0x4c1aeda9...`)
  - `USDC` (unverified/reward): $0.09
  - `USDC`: $0.00 (Moonwell market `0xedc817a2...`)
  - `USDC`: $2,204.20 (Morpho vault `0xbeefa7b8...`)

### 3.3. ZyFAI Base Agent 2 (`0xbf96c935f7cb35b86efaa0693d81d875f4b4e7eb`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$47,492.51`
- **On-Chain Verified Total:** `$47,491.74` (delta: -0.003%)
- **Unverified / Reward Assets:** `$2.27`
- **Verified Assets Breakdown:**
  - `USDC`: $0.03 (wallet token)
  - `USDC`: $47,491.71 (Fluid vault `0xf42f5795...`)
  - `USDC` (unverified/reward): $2.27

### 3.4. Mamo Base Agent 1 (`0x7c4f5efce7ebd0e99d9d38cad4573140087162dd`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,139.94`
- **On-Chain Verified Total:** `$2,134.81` (delta: -0.011%)
- **Unverified / Reward Assets:** `$5.36`
- **Verified Assets Breakdown:**
  - `WELL`: $1.91 (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `Basecat`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `PIPEDOG`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `Anthropic`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `LAPTOP`: n/a (wallet token)
  - `ASTEROID`: n/a (wallet token)
  - `LAPTOP`: n/a (wallet token)
  - `Basecat`: n/a (wallet token)
  - `我的女友景甜`: n/a (wallet token)
  - `LAPTOP`: n/a (wallet token)
  - `LAPTOP`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `FLAP`: n/a (wallet token)
  - `WELL` (unverified/reward): $1.60
  - `USDC`: $2,132.90 (Moonwell market `0xedc817a2...`)

### 3.5. Zyfai AB Risky Agent (`0x6a9e4e59df3e65fdb6a2f8d1ab6f0cd3943c015b`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.05`
- **On-Chain Verified Total:** `$0.00` (delta: +0.074%)
- **Unverified / Reward Assets:** `$0.05`
- **Verified Assets Breakdown:**
  - `USDC`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.04

### 3.6. Mamo AB Agent (`0x7d42ae4ec4367b52dc03abfc077461cf5c48b256`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$5,402.22`
- **On-Chain Verified Total:** `$5,400.72` (delta: -0.005%)
- **Unverified / Reward Assets:** `$1.78`
- **Verified Assets Breakdown:**
  - `USDC`: $5,400.72 (Moonwell market `0xedc817a2...`)

### 3.7. Zyfai Yield Maxing Agent (`0x3de51ddb55ffec013f428288559dd993e9eeb6b6`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$15,005.52`
- **On-Chain Verified Total:** `$15,004.74` (delta: -0.003%)
- **Unverified / Reward Assets:** `$1.28`
- **Verified Assets Breakdown:**
  - `USDC`: $0.01 (wallet token)
  - `UP`: $0.00 (wallet token)
  - `WETH`: $0.00 (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `AI`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `ARGUS`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `Claude`: n/a (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `FLUID` (unverified/reward): $0.03
  - `USDC`: $15,004.57 (Fluid vault `0xf42f5795...`)
  - `USDC` (unverified/reward): $1.25
  - `WETH`: $0.00 (Superform vault `0x0e70c10f...`)
  - `USDC`: $0.16 (Superform vault `0x11820afe...`)

### 3.8. Conservative Zyfai Agent (`0xc8118008228edd4769fe42f091e7d099a45c4774`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.98`
- **On-Chain Verified Total:** `$0.00` (delta: +0.002%)
- **Unverified / Reward Assets:** `$0.98`
- **Verified Assets Breakdown:**
  - `WETH`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.98

