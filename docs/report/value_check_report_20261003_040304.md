# Value Check & On-Chain Reconciliation Report

**Execution Run ID:** `20261003_040304`  
**Run Timestamp:** 2026-10-03 04:03:04 UTC  
**Primary Source:** **UNIBLOCK**  
**Cross-Check Layer:** **Base On-Chain JSON-RPC** (`https://mainnet.base.org`)  
**Total Agents Audited:** 8  

---

## 1. Executive Summary

- **Audit Health Score:** **8/8 Agents Healthy (100.0%)**
- **Total Capital Tracked (USD):** **$82,189.81**
- **On-Chain Verified Value:** **$82,184.25**
- **Unverified / Reward Assets:** **$9.48**
- **Net On-Chain Delta:** **-0.005%**

### Status Breakdown:
- **OK (Healthy):** 8
- **MISMATCH:** 0
- **RPC_UNVERIFIED:** 0
- **FAILED:** 0

---

## 2. Multi-Provider & On-Chain Audit Table

| Agent Name | Address | Provider | Stored Value (USD) | Same-Provider (Raw) | On-Chain Verified (RPC) | On-Chain Unverified | On-Chain Delta (%) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Yieldseeker Base Agent 1** | `0x4081...b414` | debank | **$2,021.57** | $2,021.57 | **$2,021.63** | $0.00 | **-0.003%** | **OK** |
| **Yieldseeker Base Agent 2** | `0xe51b...1597` | debank | **$10,133.30** | $10,133.30 | **$10,133.41** | +$0.13 | **-0.002%** | **OK** |
| **ZyFAI Base Agent 2** | `0xbf96...e7eb` | debank | **$47,486.91** | $47,486.91 | **$47,488.37** | $0.00 | **-0.003%** | **OK** |
| **Mamo Base Agent 1** | `0x7c4f...62dd` | debank | **$2,140.21** | $2,140.21 | **$2,135.14** | +$5.29 | **-0.010%** | **OK** |
| **Zyfai AB Risky Agent** | `0x6a9e...015b` | debank | **$0.05** | $10.54 | **$0.00** | +$0.05 | **+0.084%** | **OK** |
| **Mamo AB Agent** | `0x7d42...b256` | debank | **$5,401.65** | $5,401.65 | **$5,401.63** | +$1.75 | **-0.032%** | **OK** |
| **Zyfai Yield Maxing Agent** | `0x3de5...b6b6` | debank | **$15,005.14** | $15,067.96 | **$15,004.07** | +$1.29 | **-0.001%** | **OK** |
| **Conservative Zyfai Agent** | `0xc811...4774` | debank | **$0.98** | $0.98 | **$0.00** | +$0.98 | **-0.001%** | **OK** |
| **TOTAL** | — | — | **$82,189.81** | **$82,263.12** | **$82,184.25** | **+$9.48** | **-0.005%** | **8/8 HEALTHY** |

---

## 3. Agent Details & Breakdown

### 3.1. Yieldseeker Base Agent 1 (`0x40813df8a23534783e99031fe4f57a65aceeb414`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,021.57`
- **On-Chain Verified Total:** `$2,021.63` (delta: -0.003%)
- **Verified Assets Breakdown:**
  - `USDC`: $2,021.63 (Morpho vault `0xee8f4ec5...`)

### 3.2. Yieldseeker Base Agent 2 (`0xe51b7dba38e732a19838c3f23816df7092441597`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,133.30`
- **On-Chain Verified Total:** `$10,133.41` (delta: -0.002%)
- **Unverified / Reward Assets:** `$0.13`
- **Verified Assets Breakdown:**
  - `USDC`: $7,929.23 (Euler vault `0x4c1aeda9...`)
  - `USDC` (unverified/reward): $0.09
  - `USDC`: $0.00 (Moonwell market `0xedc817a2...`)
  - `USDC`: $2,204.18 (Morpho vault `0xbeefa7b8...`)

### 3.3. ZyFAI Base Agent 2 (`0xbf96c935f7cb35b86efaa0693d81d875f4b4e7eb`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$47,486.91`
- **On-Chain Verified Total:** `$47,488.37` (delta: -0.003%)
- **Verified Assets Breakdown:**
  - `USDC`: $47,488.37 (Fluid vault `0xf42f5795...`)
  - `rZFI` (unverified/reward): $0.00

### 3.4. Mamo Base Agent 1 (`0x7c4f5efce7ebd0e99d9d38cad4573140087162dd`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,140.21`
- **On-Chain Verified Total:** `$2,135.14` (delta: -0.010%)
- **Unverified / Reward Assets:** `$5.29`
- **Verified Assets Breakdown:**
  - `WELL`: $1.87 (wallet token)
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
  - `WELL` (unverified/reward): $1.57
  - `USDC`: $2,133.27 (Moonwell market `0xedc817a2...`)

### 3.5. Zyfai AB Risky Agent (`0x6a9e4e59df3e65fdb6a2f8d1ab6f0cd3943c015b`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.05`
- **On-Chain Verified Total:** `$0.00` (delta: +0.084%)
- **Unverified / Reward Assets:** `$0.05`
- **Verified Assets Breakdown:**
  - `USDC`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.04

### 3.6. Mamo AB Agent (`0x7d42ae4ec4367b52dc03abfc077461cf5c48b256`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$5,401.65`
- **On-Chain Verified Total:** `$5,401.63` (delta: -0.032%)
- **Unverified / Reward Assets:** `$1.75`
- **Verified Assets Breakdown:**
  - `USDC`: $5,401.63 (Moonwell market `0xedc817a2...`)

### 3.7. Zyfai Yield Maxing Agent (`0x3de51ddb55ffec013f428288559dd993e9eeb6b6`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$15,005.14`
- **On-Chain Verified Total:** `$15,004.07` (delta: -0.001%)
- **Unverified / Reward Assets:** `$1.29`
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
  - `USDC`: $15,003.90 (Fluid vault `0xf42f5795...`)
  - `USDC` (unverified/reward): $1.26
  - `WETH`: $0.00 (Superform vault `0x0e70c10f...`)
  - `USDC`: $0.16 (Superform vault `0x11820afe...`)

### 3.8. Conservative Zyfai Agent (`0xc8118008228edd4769fe42f091e7d099a45c4774`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.98`
- **On-Chain Verified Total:** `$0.00` (delta: -0.001%)
- **Unverified / Reward Assets:** `$0.98`
- **Verified Assets Breakdown:**
  - `WETH`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.98

