# Value Check & On-Chain Reconciliation Report

**Execution Run ID:** `20260927_191330`  
**Run Timestamp:** 2026-09-27 19:13:30 UTC  
**Primary Source:** **UNIBLOCK**  
**Cross-Check Layer:** **Base On-Chain JSON-RPC** (`https://mainnet.base.org`)  
**Total Agents Audited:** 8  

---

## 1. Executive Summary

- **Audit Health Score:** **8/8 Agents Healthy (100.0%)**
- **Total Capital Tracked (USD):** **$82,197.18**
- **On-Chain Verified Value:** **$62,295.28**
- **Unverified / Reward Assets:** **$19,902.40**
- **Net On-Chain Delta:** **-0.001%**

### Status Breakdown:
- **OK (Healthy):** 8
- **MISMATCH:** 0
- **RPC_UNVERIFIED:** 0
- **FAILED:** 0

---

## 2. Multi-Provider & On-Chain Audit Table

| Agent Name | Address | Provider | Stored Value (USD) | Same-Provider (Raw) | On-Chain Verified (RPC) | On-Chain Unverified | On-Chain Delta (%) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Yieldseeker Base Agent 1** | `0x4081...b414` | debank | **$2,020.52** | $2,020.52 | **$2,020.54** | $0.00 | **-0.001%** | **OK** |
| **Yieldseeker Base Agent 2** | `0xe51b...1597` | debank | **$10,130.62** | $10,130.62 | **$8,408.51** | +$1,722.16 | **-0.000%** | **OK** |
| **ZyFAI Base Agent 2** | `0xbf96...e7eb` | debank | **$47,470.52** | $47,470.52 | **$47,470.44** | +$0.51 | **-0.001%** | **OK** |
| **Mamo Base Agent 1** | `0x7c4f...62dd` | debank | **$2,135.97** | $2,135.97 | **$1.91** | +$2,134.06 | **+0.000%** | **OK** |
| **Zyfai AB Risky Agent** | `0x6a9e...015b` | debank | **$10,651.05** | $10,656.27 | **$0.01** | +$10,651.04 | **+0.000%** | **OK** |
| **Mamo AB Agent** | `0x7d42...b256` | debank | **$5,391.51** | $5,391.51 | **$0.00** | +$5,391.51 | **-0.000%** | **OK** |
| **Zyfai Yield Maxing Agent** | `0x3de5...b6b6` | debank | **$4,396.02** | $4,460.01 | **$4,393.88** | +$2.14 | **-0.000%** | **OK** |
| **Conservative Zyfai Agent** | `0xc811...4774` | debank | **$0.98** | $0.98 | **$0.00** | +$0.98 | **-0.003%** | **OK** |
| **TOTAL** | — | — | **$82,197.18** | **$82,266.39** | **$62,295.28** | **+$19,902.40** | **-0.001%** | **8/8 HEALTHY** |

---

## 3. Agent Details & Breakdown

### 3.1. Yieldseeker Base Agent 1 (`0x40813df8a23534783e99031fe4f57a65aceeb414`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,020.52`
- **On-Chain Verified Total:** `$2,020.54` (delta: -0.001%)
- **Verified Assets Breakdown:**

### 3.2. Yieldseeker Base Agent 2 (`0xe51b7dba38e732a19838c3f23816df7092441597`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,130.62`
- **On-Chain Verified Total:** `$8,408.51` (delta: -0.000%)
- **Unverified / Reward Assets:** `$1,722.16`
- **Verified Assets Breakdown:**
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.09
  - `USDC` (unverified/reward): $0.04
  - `USDC` (unverified/reward): $1,722.03

### 3.3. ZyFAI Base Agent 2 (`0xbf96c935f7cb35b86efaa0693d81d875f4b4e7eb`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$47,470.52`
- **On-Chain Verified Total:** `$47,470.44` (delta: -0.001%)
- **Unverified / Reward Assets:** `$0.51`
- **Verified Assets Breakdown:**
  - `USDC`: $0.01 (wallet token)
  - `USDC` (unverified/reward): $0.51

### 3.4. Mamo Base Agent 1 (`0x7c4f5efce7ebd0e99d9d38cad4573140087162dd`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,135.97`
- **On-Chain Verified Total:** `$1.91` (delta: +0.000%)
- **Unverified / Reward Assets:** `$2,134.06`
- **Verified Assets Breakdown:**
  - `WELL`: $1.91 (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `Basecat`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `PIPEDOG`: n/a (wallet token)
  - `WELL` (unverified/reward): $1.61
  - `USDC` (unverified/reward): $2,132.45

### 3.5. Zyfai AB Risky Agent (`0x6a9e4e59df3e65fdb6a2f8d1ab6f0cd3943c015b`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,651.05`
- **On-Chain Verified Total:** `$0.01` (delta: +0.000%)
- **Unverified / Reward Assets:** `$10,651.04`
- **Verified Assets Breakdown:**
  - `USDC`: $0.01 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $4,699.83
  - `USDC` (unverified/reward): $0.41
  - `USDC` (unverified/reward): $5,950.80

### 3.6. Mamo AB Agent (`0x7d42ae4ec4367b52dc03abfc077461cf5c48b256`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$5,391.51`
- **On-Chain Verified Total:** `$0.00` (delta: -0.000%)
- **Unverified / Reward Assets:** `$5,391.51`
- **Verified Assets Breakdown:**
  - `USDC` (unverified/reward): $5,391.51

### 3.7. Zyfai Yield Maxing Agent (`0x3de51ddb55ffec013f428288559dd993e9eeb6b6`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$4,396.02`
- **On-Chain Verified Total:** `$4,393.88` (delta: -0.000%)
- **Unverified / Reward Assets:** `$2.14`
- **Verified Assets Breakdown:**
  - `USDC`: $4,393.88 (wallet token)
  - `UP`: $0.00 (wallet token)
  - `WETH`: $0.00 (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `AI`: n/a (wallet token)
  - `FLUID` (unverified/reward): $0.03
  - `USDC` (unverified/reward): $1.95
  - `WETH` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.16

### 3.8. Conservative Zyfai Agent (`0xc8118008228edd4769fe42f091e7d099a45c4774`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.98`
- **On-Chain Verified Total:** `$0.00` (delta: -0.003%)
- **Unverified / Reward Assets:** `$0.98`
- **Verified Assets Breakdown:**
  - `WETH`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.98

