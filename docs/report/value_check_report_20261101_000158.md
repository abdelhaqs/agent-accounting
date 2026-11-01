# Value Check & On-Chain Reconciliation Report

**Execution Run ID:** `20261101_000158`  
**Run Timestamp:** 2026-11-01 00:01:58 UTC  
**Primary Source:** **UNIBLOCK**  
**Cross-Check Layer:** **Base On-Chain JSON-RPC** (`https://mainnet.base.org`)  
**Total Agents Audited:** 8  

---

## 1. Executive Summary

- **Audit Health Score:** **8/8 Agents Healthy (100.0%)**
- **Total Capital Tracked (USD):** **$67,584.06**
- **On-Chain Verified Value:** **$67,585.70**
- **Unverified / Reward Assets:** **$12.16**
- **Net On-Chain Delta:** **-0.020%**

### Status Breakdown:
- **OK (Healthy):** 8
- **MISMATCH:** 0
- **RPC_UNVERIFIED:** 0
- **FAILED:** 0

---

## 2. Multi-Provider & On-Chain Audit Table

| Agent Name | Address | Provider | Stored Value (USD) | Same-Provider (Raw) | On-Chain Verified (RPC) | On-Chain Unverified | On-Chain Delta (%) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Yieldseeker Base Agent 1** | `0x4081...b414` | debank | **$2,031.34** | $2,031.34 | **$2,031.37** | $0.00 | **-0.002%** | **OK** |
| **Yieldseeker Base Agent 2** | `0xe51b...1597` | debank | **$10,194.03** | $10,194.03 | **$10,196.78** | +$0.09 | **-0.028%** | **OK** |
| **ZyFAI Base Agent 2** | `0xbf96...e7eb` | debank | **$47,717.40** | $48,155.56 | **$47,724.11** | +$1.47 | **-0.017%** | **OK** |
| **Mamo Base Agent 1** | `0x7c4f...62dd` | debank | **$2,167.57** | $2,167.57 | **$2,162.24** | +$5.46 | **-0.006%** | **OK** |
| **Zyfai AB Risky Agent** | `0x6a9e...015b` | debank | **$0.05** | $22.16 | **$0.00** | +$0.05 | **-0.016%** | **OK** |
| **Mamo AB Agent** | `0x7d42...b256` | debank | **$5,472.33** | $5,472.33 | **$5,471.03** | +$3.92 | **-0.048%** | **OK** |
| **Zyfai Yield Maxing Agent** | `0x3de5...b6b6` | debank | **$0.38** | $119.56 | **$0.17** | +$0.20 | **-0.013%** | **OK** |
| **Conservative Zyfai Agent** | `0xc811...4774` | debank | **$0.98** | $0.98 | **$0.00** | +$0.98 | **-0.000%** | **OK** |
| **TOTAL** | — | — | **$67,584.06** | **$68,163.51** | **$67,585.70** | **+$12.16** | **-0.020%** | **8/8 HEALTHY** |

---

## 3. Agent Details & Breakdown

### 3.1. Yieldseeker Base Agent 1 (`0x40813df8a23534783e99031fe4f57a65aceeb414`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,031.34`
- **On-Chain Verified Total:** `$2,031.37` (delta: -0.002%)
- **Verified Assets Breakdown:**
  - `USDC`: $2,031.37 (Morpho vault `0xee8f4ec5...`)

### 3.2. Yieldseeker Base Agent 2 (`0xe51b7dba38e732a19838c3f23816df7092441597`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,194.03`
- **On-Chain Verified Total:** `$10,196.78` (delta: -0.028%)
- **Unverified / Reward Assets:** `$0.09`
- **Verified Assets Breakdown:**
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.06
  - `USDC`: $0.00 (Moonwell market `0xedc817a2...`)
  - `USDC`: $10,196.78 (Morpho vault `0x5435bc53...`)

### 3.3. ZyFAI Base Agent 2 (`0xbf96c935f7cb35b86efaa0693d81d875f4b4e7eb`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$47,717.40`
- **On-Chain Verified Total:** `$47,724.11` (delta: -0.017%)
- **Unverified / Reward Assets:** `$1.47`
- **Verified Assets Breakdown:**
  - `USDC`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.02
  - `USDC` (unverified/reward): $1.45
  - `USDC`: $8,647.30 (Morpho vault `0x236919f1...`)
  - `USDC`: $39,076.80 (Morpho vault `0xee8f4ec5...`)

### 3.4. Mamo Base Agent 1 (`0x7c4f5efce7ebd0e99d9d38cad4573140087162dd`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,167.57`
- **On-Chain Verified Total:** `$2,162.24` (delta: -0.006%)
- **Unverified / Reward Assets:** `$5.46`
- **Verified Assets Breakdown:**
  - `WELL`: $1.57 (wallet token)
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
  - `WELL` (unverified/reward): $1.34
  - `USDC`: $2,160.67 (Moonwell market `0xedc817a2...`)

### 3.5. Zyfai AB Risky Agent (`0x6a9e4e59df3e65fdb6a2f8d1ab6f0cd3943c015b`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.05`
- **On-Chain Verified Total:** `$0.00` (delta: -0.016%)
- **Unverified / Reward Assets:** `$0.05`
- **Verified Assets Breakdown:**
  - `USDC`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.04

### 3.6. Mamo AB Agent (`0x7d42ae4ec4367b52dc03abfc077461cf5c48b256`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$5,472.33`
- **On-Chain Verified Total:** `$5,471.03` (delta: -0.048%)
- **Unverified / Reward Assets:** `$3.92`
- **Verified Assets Breakdown:**
  - `USDC`: $5,471.03 (Moonwell market `0xedc817a2...`)

### 3.7. Zyfai Yield Maxing Agent (`0x3de51ddb55ffec013f428288559dd993e9eeb6b6`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.38`
- **On-Chain Verified Total:** `$0.17` (delta: -0.013%)
- **Unverified / Reward Assets:** `$0.20`
- **Verified Assets Breakdown:**
  - `UP`: $0.00 (wallet token)
  - `USDC`: $0.00 (wallet token)
  - `WETH`: $0.00 (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `AI`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `ARGUS`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `Claude`: n/a (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC`: $0.01 (Euler vault `0x91a9ed5d...`)
  - `FLUID` (unverified/reward): $0.04
  - `USDC` (unverified/reward): $0.16
  - `WETH`: $0.00 (Superform vault `0x0e70c10f...`)
  - `USDC`: $0.16 (Superform vault `0x11820afe...`)

### 3.8. Conservative Zyfai Agent (`0xc8118008228edd4769fe42f091e7d099a45c4774`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.98`
- **On-Chain Verified Total:** `$0.00` (delta: -0.000%)
- **Unverified / Reward Assets:** `$0.98`
- **Verified Assets Breakdown:**
  - `WETH`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.98

