# Value Check & On-Chain Reconciliation Report

**Execution Run ID:** `20260929_060406`  
**Run Timestamp:** 2026-09-29 06:04:06 UTC  
**Primary Source:** **UNIBLOCK**  
**Cross-Check Layer:** **Base On-Chain JSON-RPC** (`https://mainnet.base.org`)  
**Total Agents Audited:** 8  

---

## 1. Executive Summary

- **Audit Health Score:** **8/8 Agents Healthy (100.0%)**
- **Total Capital Tracked (USD):** **$82,232.91**
- **On-Chain Verified Value:** **$72,369.48**
- **Unverified / Reward Assets:** **$9,864.30**
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
| **Yieldseeker Base Agent 1** | `0x4081...b414` | debank | **$2,021.49** | $2,021.49 | **$2,021.50** | $0.00 | **-0.000%** | **OK** |
| **Yieldseeker Base Agent 2** | `0xe51b...1597` | debank | **$10,130.76** | $10,130.76 | **$7,805.55** | +$2,326.08 | **-0.009%** | **OK** |
| **ZyFAI Base Agent 2** | `0xbf96...e7eb` | debank | **$47,491.90** | $47,491.90 | **$47,489.79** | +$2.10 | **+0.000%** | **OK** |
| **Mamo Base Agent 1** | `0x7c4f...62dd` | debank | **$2,137.66** | $2,137.66 | **$1.87** | +$2,135.79 | **-0.000%** | **OK** |
| **Zyfai AB Risky Agent** | `0x6a9e...015b` | debank | **$10,657.29** | $10,662.45 | **$10,655.16** | +$2.13 | **-0.000%** | **OK** |
| **Mamo AB Agent** | `0x7d42...b256` | debank | **$5,395.26** | $5,395.26 | **$0.00** | +$5,395.26 | **+0.000%** | **OK** |
| **Zyfai Yield Maxing Agent** | `0x3de5...b6b6` | debank | **$4,397.58** | $4,460.78 | **$4,395.61** | +$1.97 | **+0.000%** | **OK** |
| **Conservative Zyfai Agent** | `0xc811...4774` | debank | **$0.98** | $0.98 | **$0.00** | +$0.98 | **+0.003%** | **OK** |
| **TOTAL** | — | — | **$82,232.91** | **$82,301.27** | **$72,369.48** | **+$9,864.30** | **-0.001%** | **8/8 HEALTHY** |

---

## 3. Agent Details & Breakdown

### 3.1. Yieldseeker Base Agent 1 (`0x40813df8a23534783e99031fe4f57a65aceeb414`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,021.49`
- **On-Chain Verified Total:** `$2,021.50` (delta: -0.000%)
- **Verified Assets Breakdown:**

### 3.2. Yieldseeker Base Agent 2 (`0xe51b7dba38e732a19838c3f23816df7092441597`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,130.76`
- **On-Chain Verified Total:** `$7,805.55` (delta: -0.009%)
- **Unverified / Reward Assets:** `$2,326.08`
- **Verified Assets Breakdown:**
  - `USDC` (unverified/reward): $2,325.95
  - `USDC` (unverified/reward): $0.09
  - `USDC` (unverified/reward): $0.04

### 3.3. ZyFAI Base Agent 2 (`0xbf96c935f7cb35b86efaa0693d81d875f4b4e7eb`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$47,491.90`
- **On-Chain Verified Total:** `$47,489.79` (delta: +0.000%)
- **Unverified / Reward Assets:** `$2.10`
- **Verified Assets Breakdown:**
  - `USDC`: $47,489.79 (wallet token)
  - `USDC` (unverified/reward): $2.10

### 3.4. Mamo Base Agent 1 (`0x7c4f5efce7ebd0e99d9d38cad4573140087162dd`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,137.66`
- **On-Chain Verified Total:** `$1.87` (delta: -0.000%)
- **Unverified / Reward Assets:** `$2,135.79`
- **Verified Assets Breakdown:**
  - `WELL`: $1.87 (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `Basecat`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `PIPEDOG`: n/a (wallet token)
  - `WELL` (unverified/reward): $1.55
  - `USDC` (unverified/reward): $2,134.23

### 3.5. Zyfai AB Risky Agent (`0x6a9e4e59df3e65fdb6a2f8d1ab6f0cd3943c015b`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,657.29`
- **On-Chain Verified Total:** `$10,655.16` (delta: -0.000%)
- **Unverified / Reward Assets:** `$2.13`
- **Verified Assets Breakdown:**
  - `USDC`: $10,655.16 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $2.13

### 3.6. Mamo AB Agent (`0x7d42ae4ec4367b52dc03abfc077461cf5c48b256`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$5,395.26`
- **On-Chain Verified Total:** `$0.00` (delta: +0.000%)
- **Unverified / Reward Assets:** `$5,395.26`
- **Verified Assets Breakdown:**
  - `USDC` (unverified/reward): $5,395.26

### 3.7. Zyfai Yield Maxing Agent (`0x3de51ddb55ffec013f428288559dd993e9eeb6b6`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$4,397.58`
- **On-Chain Verified Total:** `$4,395.61` (delta: +0.000%)
- **Unverified / Reward Assets:** `$1.97`
- **Verified Assets Breakdown:**
  - `USDC`: $4,395.45 (wallet token)
  - `UP`: $0.00 (wallet token)
  - `WETH`: $0.00 (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `AI`: n/a (wallet token)
  - `FLUID` (unverified/reward): $0.03
  - `USDC` (unverified/reward): $1.94
  - `WETH` (unverified/reward): $0.00

### 3.8. Conservative Zyfai Agent (`0xc8118008228edd4769fe42f091e7d099a45c4774`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.98`
- **On-Chain Verified Total:** `$0.00` (delta: +0.003%)
- **Unverified / Reward Assets:** `$0.98`
- **Verified Assets Breakdown:**
  - `WETH`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.98

