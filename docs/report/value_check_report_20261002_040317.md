# Value Check & On-Chain Reconciliation Report

**Execution Run ID:** `20261002_040317`  
**Run Timestamp:** 2026-10-02 04:03:17 UTC  
**Primary Source:** **UNIBLOCK**  
**Cross-Check Layer:** **Base On-Chain JSON-RPC** (`https://mainnet.base.org`)  
**Total Agents Audited:** 8  

---

## 1. Executive Summary

- **Audit Health Score:** **8/8 Agents Healthy (100.0%)**
- **Total Capital Tracked (USD):** **$82,200.29**
- **On-Chain Verified Value:** **$79,971.73**
- **Unverified / Reward Assets:** **$2,230.78**
- **Net On-Chain Delta:** **-0.003%**

### Status Breakdown:
- **OK (Healthy):** 8
- **MISMATCH:** 0
- **RPC_UNVERIFIED:** 0
- **FAILED:** 0

---

## 2. Multi-Provider & On-Chain Audit Table

| Agent Name | Address | Provider | Stored Value (USD) | Same-Provider (Raw) | On-Chain Verified (RPC) | On-Chain Unverified | On-Chain Delta (%) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Yieldseeker Base Agent 1** | `0x4081...b414` | debank | **$2,021.74** | $2,021.74 | **$2,021.79** | $0.00 | **-0.003%** | **OK** |
| **Yieldseeker Base Agent 2** | `0xe51b...1597` | debank | **$10,133.91** | $10,133.91 | **$7,913.71** | +$2,220.31 | **-0.001%** | **OK** |
| **ZyFAI Base Agent 2** | `0xbf96...e7eb` | debank | **$47,496.95** | $47,496.95 | **$47,495.16** | +$1.97 | **-0.000%** | **OK** |
| **Mamo Base Agent 1** | `0x7c4f...62dd` | debank | **$2,139.80** | $2,139.80 | **$2,134.72** | +$5.29 | **-0.010%** | **OK** |
| **Zyfai AB Risky Agent** | `0x6a9e...015b` | debank | **$0.05** | $10.51 | **$0.00** | +$0.05 | **+0.064%** | **OK** |
| **Mamo AB Agent** | `0x7d42...b256` | debank | **$5,400.60** | $5,400.60 | **$5,400.53** | +$1.67 | **-0.030%** | **OK** |
| **Zyfai Yield Maxing Agent** | `0x3de5...b6b6` | debank | **$15,006.26** | $15,068.91 | **$15,005.83** | +$0.52 | **-0.001%** | **OK** |
| **Conservative Zyfai Agent** | `0xc811...4774` | debank | **$0.98** | $0.98 | **$0.00** | +$0.98 | **+0.001%** | **OK** |
| **TOTAL** | — | — | **$82,200.29** | **$82,273.40** | **$79,971.73** | **+$2,230.78** | **-0.003%** | **8/8 HEALTHY** |

---

## 3. Agent Details & Breakdown

### 3.1. Yieldseeker Base Agent 1 (`0x40813df8a23534783e99031fe4f57a65aceeb414`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,021.74`
- **On-Chain Verified Total:** `$2,021.79` (delta: -0.003%)
- **Verified Assets Breakdown:**
  - `USDC`: $2,021.79 (Morpho vault `0xee8f4ec5...`)

### 3.2. Yieldseeker Base Agent 2 (`0xe51b7dba38e732a19838c3f23816df7092441597`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,133.91`
- **On-Chain Verified Total:** `$7,913.71` (delta: -0.001%)
- **Unverified / Reward Assets:** `$2,220.31`
- **Verified Assets Breakdown:**
  - `USDC`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $2,220.18
  - `USDC`: $7,913.71 (Euler vault `0x4c1aeda9...`)
  - `USDC` (unverified/reward): $0.09
  - `USDC`: $0.00 (Moonwell market `0xedc817a2...`)

### 3.3. ZyFAI Base Agent 2 (`0xbf96c935f7cb35b86efaa0693d81d875f4b4e7eb`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$47,496.95`
- **On-Chain Verified Total:** `$47,495.16` (delta: -0.000%)
- **Unverified / Reward Assets:** `$1.97`
- **Verified Assets Breakdown:**
  - `USDC`: $0.03 (wallet token)
  - `USDC`: $47,495.13 (Fluid vault `0xf42f5795...`)
  - `USDC` (unverified/reward): $1.97

### 3.4. Mamo Base Agent 1 (`0x7c4f5efce7ebd0e99d9d38cad4573140087162dd`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,139.80`
- **On-Chain Verified Total:** `$2,134.72` (delta: -0.010%)
- **Unverified / Reward Assets:** `$5.29`
- **Verified Assets Breakdown:**
  - `WELL`: $1.89 (wallet token)
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
  - `WELL` (unverified/reward): $1.58
  - `USDC`: $2,132.83 (Moonwell market `0xedc817a2...`)

### 3.5. Zyfai AB Risky Agent (`0x6a9e4e59df3e65fdb6a2f8d1ab6f0cd3943c015b`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.05`
- **On-Chain Verified Total:** `$0.00` (delta: +0.064%)
- **Unverified / Reward Assets:** `$0.05`
- **Verified Assets Breakdown:**
  - `USDC`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.04

### 3.6. Mamo AB Agent (`0x7d42ae4ec4367b52dc03abfc077461cf5c48b256`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$5,400.60`
- **On-Chain Verified Total:** `$5,400.53` (delta: -0.030%)
- **Unverified / Reward Assets:** `$1.67`
- **Verified Assets Breakdown:**
  - `USDC`: $5,400.53 (Moonwell market `0xedc817a2...`)

### 3.7. Zyfai Yield Maxing Agent (`0x3de51ddb55ffec013f428288559dd993e9eeb6b6`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$15,006.26`
- **On-Chain Verified Total:** `$15,005.83` (delta: -0.001%)
- **Unverified / Reward Assets:** `$0.52`
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
  - `USDC`: $15,005.66 (Fluid vault `0xf42f5795...`)
  - `USDC` (unverified/reward): $0.49
  - `WETH`: $0.00 (Superform vault `0x0e70c10f...`)
  - `USDC`: $0.16 (Superform vault `0x11820afe...`)

### 3.8. Conservative Zyfai Agent (`0xc8118008228edd4769fe42f091e7d099a45c4774`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.98`
- **On-Chain Verified Total:** `$0.00` (delta: +0.001%)
- **Unverified / Reward Assets:** `$0.98`
- **Verified Assets Breakdown:**
  - `WETH`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.98

