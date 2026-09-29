# Value Check & On-Chain Reconciliation Report

**Execution Run ID:** `20260929_000243`  
**Run Timestamp:** 2026-09-29 00:02:43 UTC  
**Primary Source:** **UNIBLOCK**  
**Cross-Check Layer:** **Base On-Chain JSON-RPC** (`https://mainnet.base.org`)  
**Total Agents Audited:** 8  

---

## 1. Executive Summary

- **Audit Health Score:** **8/8 Agents Healthy (100.0%)**
- **Total Capital Tracked (USD):** **$82,224.42**
- **On-Chain Verified Value:** **$64,033.51**
- **Unverified / Reward Assets:** **$18,192.63**
- **Net On-Chain Delta:** **-0.002%**

### Status Breakdown:
- **OK (Healthy):** 8
- **MISMATCH:** 0
- **RPC_UNVERIFIED:** 0
- **FAILED:** 0

---

## 2. Multi-Provider & On-Chain Audit Table

| Agent Name | Address | Provider | Stored Value (USD) | Same-Provider (Raw) | On-Chain Verified (RPC) | On-Chain Unverified | On-Chain Delta (%) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Yieldseeker Base Agent 1** | `0x4081...b414` | debank | **$2,021.22** | $2,021.22 | **$2,021.23** | $0.00 | **-0.000%** | **OK** |
| **Yieldseeker Base Agent 2** | `0xe51b...1597` | debank | **$10,129.66** | $10,129.66 | **$10,130.13** | +$0.13 | **-0.006%** | **OK** |
| **ZyFAI Base Agent 2** | `0xbf96...e7eb` | debank | **$47,485.35** | $47,490.10 | **$47,484.84** | +$1.62 | **-0.002%** | **OK** |
| **Mamo Base Agent 1** | `0x7c4f...62dd` | debank | **$2,137.39** | $2,137.39 | **$1.85** | +$2,135.55 | **-0.000%** | **OK** |
| **Zyfai AB Risky Agent** | `0x6a9e...015b` | debank | **$10,657.00** | $10,662.18 | **$0.01** | +$10,656.99 | **+0.000%** | **OK** |
| **Mamo AB Agent** | `0x7d42...b256` | debank | **$5,395.24** | $5,395.24 | **$0.00** | +$5,395.24 | **-0.000%** | **OK** |
| **Zyfai Yield Maxing Agent** | `0x3de5...b6b6` | debank | **$4,397.57** | $4,461.01 | **$4,395.45** | +$2.12 | **-0.000%** | **OK** |
| **Conservative Zyfai Agent** | `0xc811...4774` | debank | **$0.98** | $0.98 | **$0.00** | +$0.98 | **-0.004%** | **OK** |
| **TOTAL** | — | — | **$82,224.42** | **$82,297.79** | **$64,033.51** | **+$18,192.63** | **-0.002%** | **8/8 HEALTHY** |

---

## 3. Agent Details & Breakdown

### 3.1. Yieldseeker Base Agent 1 (`0x40813df8a23534783e99031fe4f57a65aceeb414`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,021.22`
- **On-Chain Verified Total:** `$2,021.23` (delta: -0.000%)
- **Verified Assets Breakdown:**

### 3.2. Yieldseeker Base Agent 2 (`0xe51b7dba38e732a19838c3f23816df7092441597`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,129.66`
- **On-Chain Verified Total:** `$10,130.13` (delta: -0.006%)
- **Unverified / Reward Assets:** `$0.13`
- **Verified Assets Breakdown:**
  - `USDC` (unverified/reward): $0.09
  - `USDC` (unverified/reward): $0.04

### 3.3. ZyFAI Base Agent 2 (`0xbf96c935f7cb35b86efaa0693d81d875f4b4e7eb`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$47,485.35`
- **On-Chain Verified Total:** `$47,484.84` (delta: -0.002%)
- **Unverified / Reward Assets:** `$1.62`
- **Verified Assets Breakdown:**
  - `USDC`: $0.02 (wallet token)
  - `USDC` (unverified/reward): $1.62

### 3.4. Mamo Base Agent 1 (`0x7c4f5efce7ebd0e99d9d38cad4573140087162dd`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,137.39`
- **On-Chain Verified Total:** `$1.85` (delta: -0.000%)
- **Unverified / Reward Assets:** `$2,135.55`
- **Verified Assets Breakdown:**
  - `WELL`: $1.85 (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `Basecat`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `PIPEDOG`: n/a (wallet token)
  - `WELL` (unverified/reward): $1.54
  - `USDC` (unverified/reward): $2,134.00

### 3.5. Zyfai AB Risky Agent (`0x6a9e4e59df3e65fdb6a2f8d1ab6f0cd3943c015b`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,657.00`
- **On-Chain Verified Total:** `$0.01` (delta: +0.000%)
- **Unverified / Reward Assets:** `$10,656.99`
- **Verified Assets Breakdown:**
  - `USDC`: $0.01 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $4,793.63
  - `USDC` (unverified/reward): $1.90
  - `USDC` (unverified/reward): $5,861.45

### 3.6. Mamo AB Agent (`0x7d42ae4ec4367b52dc03abfc077461cf5c48b256`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$5,395.24`
- **On-Chain Verified Total:** `$0.00` (delta: -0.000%)
- **Unverified / Reward Assets:** `$5,395.24`
- **Verified Assets Breakdown:**
  - `USDC` (unverified/reward): $5,395.24

### 3.7. Zyfai Yield Maxing Agent (`0x3de51ddb55ffec013f428288559dd993e9eeb6b6`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$4,397.57`
- **On-Chain Verified Total:** `$4,395.45` (delta: -0.000%)
- **Unverified / Reward Assets:** `$2.12`
- **Verified Assets Breakdown:**
  - `USDC`: $4,395.45 (wallet token)
  - `UP`: $0.00 (wallet token)
  - `WETH`: $0.00 (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `AI`: n/a (wallet token)
  - `FLUID` (unverified/reward): $0.03
  - `USDC` (unverified/reward): $1.93
  - `WETH` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.16

### 3.8. Conservative Zyfai Agent (`0xc8118008228edd4769fe42f091e7d099a45c4774`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.98`
- **On-Chain Verified Total:** `$0.00` (delta: -0.004%)
- **Unverified / Reward Assets:** `$0.98`
- **Verified Assets Breakdown:**
  - `WETH`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.98

