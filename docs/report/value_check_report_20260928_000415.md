# Value Check & On-Chain Reconciliation Report

**Execution Run ID:** `20260928_000415`  
**Run Timestamp:** 2026-09-28 00:04:15 UTC  
**Primary Source:** **UNIBLOCK**  
**Cross-Check Layer:** **Base On-Chain JSON-RPC** (`https://mainnet.base.org`)  
**Total Agents Audited:** 8  

---

## 1. Executive Summary

- **Audit Health Score:** **7/8 Agents Healthy (87.5%)**
- **Total Capital Tracked (USD):** **$82,199.10**
- **On-Chain Verified Value:** **$51,819.04**
- **Unverified / Reward Assets:** **$24,297.14**
- **Net On-Chain Delta:** **+7.992%**

### Status Breakdown:
- **OK (Healthy):** 7
- **MISMATCH:** 1
- **RPC_UNVERIFIED:** 0
- **FAILED:** 0

---

## 2. Multi-Provider & On-Chain Audit Table

| Agent Name | Address | Provider | Stored Value (USD) | Same-Provider (Raw) | On-Chain Verified (RPC) | On-Chain Unverified | On-Chain Delta (%) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Yieldseeker Base Agent 1** | `0x4081...b414` | debank | **$2,020.56** | $2,020.56 | **$2,020.59** | $0.00 | **-0.001%** | **OK** |
| **Yieldseeker Base Agent 2** | `0xe51b...1597` | debank | **$10,130.77** | $17,932.31 | **$2,325.08** | +$1,722.20 | **+150.311%** | ❌ **MISMATCH** |
| **ZyFAI Base Agent 2** | `0xbf96...e7eb` | debank | **$47,471.88** | $47,471.88 | **$47,471.50** | +$0.93 | **-0.001%** | **OK** |
| **Mamo Base Agent 1** | `0x7c4f...62dd` | debank | **$2,135.89** | $2,135.89 | **$1.87** | +$2,134.03 | **+0.000%** | **OK** |
| **Zyfai AB Risky Agent** | `0x6a9e...015b` | debank | **$10,651.52** | $10,656.70 | **$0.01** | +$10,651.51 | **-0.000%** | **OK** |
| **Mamo AB Agent** | `0x7d42...b256` | debank | **$5,391.48** | $5,391.48 | **$0.00** | +$5,391.48 | **+0.000%** | **OK** |
| **Zyfai Yield Maxing Agent** | `0x3de5...b6b6` | debank | **$4,396.02** | $4,459.46 | **$0.00** | +$4,396.01 | **-0.000%** | **OK** |
| **Conservative Zyfai Agent** | `0xc811...4774` | debank | **$0.98** | $0.98 | **$0.00** | +$0.98 | **+0.003%** | **OK** |
| **TOTAL** | — | — | **$82,199.10** | **$90,069.26** | **$51,819.04** | **+$24,297.14** | **+7.992%** | **7/8 HEALTHY** |

---

## 3. Agent Details & Breakdown

### 3.1. Yieldseeker Base Agent 1 (`0x40813df8a23534783e99031fe4f57a65aceeb414`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,020.56`
- **On-Chain Verified Total:** `$2,020.59` (delta: -0.001%)
- **Verified Assets Breakdown:**

### 3.2. Yieldseeker Base Agent 2 (`0xe51b7dba38e732a19838c3f23816df7092441597`)
- **Reconciliation Status:** `MISMATCH`
- **Stored Pipeline Total:** `$10,130.77`
- **On-Chain Verified Total:** `$2,325.08` (delta: +150.311%)
- **Unverified / Reward Assets:** `$1,722.20`
- **Verified Assets Breakdown:**
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.09
  - `USDC` (unverified/reward): $0.04
  - `USDC` (unverified/reward): $1,722.07

### 3.3. ZyFAI Base Agent 2 (`0xbf96c935f7cb35b86efaa0693d81d875f4b4e7eb`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$47,471.88`
- **On-Chain Verified Total:** `$47,471.50` (delta: -0.001%)
- **Unverified / Reward Assets:** `$0.93`
- **Verified Assets Breakdown:**
  - `USDC`: $0.01 (wallet token)
  - `USDC` (unverified/reward): $0.93

### 3.4. Mamo Base Agent 1 (`0x7c4f5efce7ebd0e99d9d38cad4573140087162dd`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,135.89`
- **On-Chain Verified Total:** `$1.87` (delta: +0.000%)
- **Unverified / Reward Assets:** `$2,134.03`
- **Verified Assets Breakdown:**
  - `WELL`: $1.87 (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `Basecat`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `PIPEDOG`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `LAPTOP`: n/a (wallet token)
  - `ASTEROID`: n/a (wallet token)
  - `LAPTOP`: n/a (wallet token)
  - `Basecat`: n/a (wallet token)
  - `WELL` (unverified/reward): $1.58
  - `USDC` (unverified/reward): $2,132.45

### 3.5. Zyfai AB Risky Agent (`0x6a9e4e59df3e65fdb6a2f8d1ab6f0cd3943c015b`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,651.52`
- **On-Chain Verified Total:** `$0.01` (delta: -0.000%)
- **Unverified / Reward Assets:** `$10,651.51`
- **Verified Assets Breakdown:**
  - `USDC`: $0.01 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.64
  - `USDC` (unverified/reward): $10,650.87

### 3.6. Mamo AB Agent (`0x7d42ae4ec4367b52dc03abfc077461cf5c48b256`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$5,391.48`
- **On-Chain Verified Total:** `$0.00` (delta: +0.000%)
- **Unverified / Reward Assets:** `$5,391.48`
- **Verified Assets Breakdown:**
  - `USDC` (unverified/reward): $5,391.48

### 3.7. Zyfai Yield Maxing Agent (`0x3de51ddb55ffec013f428288559dd993e9eeb6b6`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$4,396.02`
- **On-Chain Verified Total:** `$0.00` (delta: -0.000%)
- **Unverified / Reward Assets:** `$4,396.01`
- **Verified Assets Breakdown:**
  - `UP`: $0.00 (wallet token)
  - `WETH`: $0.00 (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `AI`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `FLUID` (unverified/reward): $0.03
  - `USDC` (unverified/reward): $4,393.88
  - `USDC` (unverified/reward): $1.95
  - `WETH` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.16

### 3.8. Conservative Zyfai Agent (`0xc8118008228edd4769fe42f091e7d099a45c4774`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.98`
- **On-Chain Verified Total:** `$0.00` (delta: +0.003%)
- **Unverified / Reward Assets:** `$0.98`
- **Verified Assets Breakdown:**
  - `WETH`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.98

