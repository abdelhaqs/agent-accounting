# Value Check & On-Chain Reconciliation Report

**Execution Run ID:** `20260929_204926`  
**Run Timestamp:** 2026-09-29 20:49:26 UTC  
**Primary Source:** **UNIBLOCK**  
**Cross-Check Layer:** **Base On-Chain JSON-RPC** (`https://mainnet.base.org`)  
**Total Agents Audited:** 8  

---

## 1. Executive Summary

- **Audit Health Score:** **8/8 Agents Healthy (100.0%)**
- **Total Capital Tracked (USD):** **$82,182.50**
- **On-Chain Verified Value:** **$81,164.99**
- **Unverified / Reward Assets:** **$1,020.08**
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
| **Yieldseeker Base Agent 1** | `0x4081...b414` | debank | **$2,021.36** | $2,021.36 | **$2,021.44** | $0.00 | **-0.004%** | **OK** |
| **Yieldseeker Base Agent 2** | `0xe51b...1597` | debank | **$10,131.70** | $10,131.70 | **$10,131.60** | +$0.13 | **-0.000%** | **OK** |
| **ZyFAI Base Agent 2** | `0xbf96...e7eb` | debank | **$47,489.88** | $47,489.88 | **$47,490.52** | +$0.40 | **-0.002%** | **OK** |
| **Mamo Base Agent 1** | `0x7c4f...62dd` | debank | **$2,137.74** | $2,137.74 | **$2,132.92** | +$5.10 | **-0.013%** | **OK** |
| **Zyfai AB Risky Agent** | `0x6a9e...015b` | debank | **$10,656.91** | $10,662.13 | **$10,656.83** | +$0.50 | **-0.004%** | **OK** |
| **Mamo AB Agent** | `0x7d42...b256` | debank | **$5,396.81** | $5,396.81 | **$5,396.06** | +$1.46 | **-0.013%** | **OK** |
| **Zyfai Yield Maxing Agent** | `0x3de5...b6b6` | debank | **$4,347.12** | $4,411.06 | **$3,335.61** | +$1,011.51 | **-0.000%** | **OK** |
| **Conservative Zyfai Agent** | `0xc811...4774` | debank | **$0.98** | $0.98 | **$0.00** | +$0.98 | **+0.001%** | **OK** |
| **TOTAL** | — | — | **$82,182.50** | **$82,251.66** | **$81,164.99** | **+$1,020.08** | **-0.003%** | **8/8 HEALTHY** |

---

## 3. Agent Details & Breakdown

### 3.1. Yieldseeker Base Agent 1 (`0x40813df8a23534783e99031fe4f57a65aceeb414`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,021.36`
- **On-Chain Verified Total:** `$2,021.44` (delta: -0.004%)
- **Verified Assets Breakdown:**
  - `USDC`: $2,021.44 (Morpho vault `0xee8f4ec5...`)

### 3.2. Yieldseeker Base Agent 2 (`0xe51b7dba38e732a19838c3f23816df7092441597`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,131.70`
- **On-Chain Verified Total:** `$10,131.60` (delta: -0.000%)
- **Unverified / Reward Assets:** `$0.13`
- **Verified Assets Breakdown:**
  - `USDC` (unverified/reward): $0.00
  - `USDC`: $8,170.41 (Euler vault `0x4c1aeda9...`)
  - `USDC` (unverified/reward): $0.09
  - `USDC`: $0.00 (Moonwell market `0xedc817a2...`)
  - `USDC`: $1,961.19 (Morpho vault `0xbeefa7b8...`)

### 3.3. ZyFAI Base Agent 2 (`0xbf96c935f7cb35b86efaa0693d81d875f4b4e7eb`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$47,489.88`
- **On-Chain Verified Total:** `$47,490.52` (delta: -0.002%)
- **Unverified / Reward Assets:** `$0.40`
- **Verified Assets Breakdown:**
  - `USDC` (unverified/reward): $0.40
  - `USDC`: $47,490.52 (Morpho vault `0x91c056b6...`)

### 3.4. Mamo Base Agent 1 (`0x7c4f5efce7ebd0e99d9d38cad4573140087162dd`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,137.74`
- **On-Chain Verified Total:** `$2,132.92` (delta: -0.013%)
- **Unverified / Reward Assets:** `$5.10`
- **Verified Assets Breakdown:**
  - `WELL`: $1.86 (wallet token)
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
  - `WELL` (unverified/reward): $1.54
  - `USDC`: $2,131.07 (Moonwell market `0xedc817a2...`)

### 3.5. Zyfai AB Risky Agent (`0x6a9e4e59df3e65fdb6a2f8d1ab6f0cd3943c015b`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,656.91`
- **On-Chain Verified Total:** `$10,656.83` (delta: -0.004%)
- **Unverified / Reward Assets:** `$0.50`
- **Verified Assets Breakdown:**
  - `USDC`: $0.01 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.50
  - `USDC`: $10,656.83 (Morpho vault `0x8b12106a...`)

### 3.6. Mamo AB Agent (`0x7d42ae4ec4367b52dc03abfc077461cf5c48b256`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$5,396.81`
- **On-Chain Verified Total:** `$5,396.06` (delta: -0.013%)
- **Unverified / Reward Assets:** `$1.46`
- **Verified Assets Breakdown:**
  - `USDC`: $5,396.06 (Moonwell market `0xedc817a2...`)

### 3.7. Zyfai Yield Maxing Agent (`0x3de51ddb55ffec013f428288559dd993e9eeb6b6`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$4,347.12`
- **On-Chain Verified Total:** `$3,335.61` (delta: -0.000%)
- **Unverified / Reward Assets:** `$1,011.51`
- **Verified Assets Breakdown:**
  - `UP`: $0.00 (wallet token)
  - `WETH`: $0.00 (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `AI`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `ARGUS`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `Claude`: n/a (wallet token)
  - `USDC` (unverified/reward): $1,009.54
  - `FLUID` (unverified/reward): $0.03
  - `USDC` (unverified/reward): $1.94
  - `USDC`: $3,335.45 (Morpho vault `0x8b12106a...`)
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

