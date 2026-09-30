# Value Check & On-Chain Reconciliation Report

**Execution Run ID:** `20260930_200404`  
**Run Timestamp:** 2026-09-30 20:04:04 UTC  
**Primary Source:** **UNIBLOCK**  
**Cross-Check Layer:** **Base On-Chain JSON-RPC** (`https://mainnet.base.org`)  
**Total Agents Audited:** 8  

---

## 1. Executive Summary

- **Audit Health Score:** **8/8 Agents Healthy (100.0%)**
- **Total Capital Tracked (USD):** **$82,200.67**
- **On-Chain Verified Value:** **$82,192.68**
- **Unverified / Reward Assets:** **$12.83**
- **Net On-Chain Delta:** **-0.006%**

### Status Breakdown:
- **OK (Healthy):** 8
- **MISMATCH:** 0
- **RPC_UNVERIFIED:** 0
- **FAILED:** 0

---

## 2. Multi-Provider & On-Chain Audit Table

| Agent Name | Address | Provider | Stored Value (USD) | Same-Provider (Raw) | On-Chain Verified (RPC) | On-Chain Unverified | On-Chain Delta (%) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Yieldseeker Base Agent 1** | `0x4081...b414` | debank | **$2,021.80** | $2,021.80 | **$2,021.88** | $0.00 | **-0.004%** | **OK** |
| **Yieldseeker Base Agent 2** | `0xe51b...1597` | debank | **$10,133.10** | $10,133.10 | **$10,134.16** | +$0.13 | **-0.012%** | **OK** |
| **ZyFAI Base Agent 2** | `0xbf96...e7eb` | debank | **$47,497.88** | $47,497.88 | **$47,499.05** | +$1.19 | **-0.005%** | **OK** |
| **Mamo Base Agent 1** | `0x7c4f...62dd` | debank | **$2,138.86** | $2,138.86 | **$2,133.98** | +$5.18 | **-0.014%** | **OK** |
| **Zyfai AB Risky Agent** | `0x6a9e...015b` | debank | **$10,660.40** | $10,665.48 | **$10,658.91** | +$1.50 | **-0.000%** | **OK** |
| **Mamo AB Agent** | `0x7d42...b256` | debank | **$5,399.50** | $5,399.50 | **$5,398.70** | +$1.56 | **-0.014%** | **OK** |
| **Zyfai Yield Maxing Agent** | `0x3de5...b6b6` | debank | **$4,348.15** | $4,410.45 | **$4,345.99** | +$2.29 | **-0.003%** | **OK** |
| **Conservative Zyfai Agent** | `0xc811...4774` | debank | **$0.98** | $0.98 | **$0.00** | +$0.98 | **-0.005%** | **OK** |
| **TOTAL** | — | — | **$82,200.67** | **$82,268.05** | **$82,192.68** | **+$12.83** | **-0.006%** | **8/8 HEALTHY** |

---

## 3. Agent Details & Breakdown

### 3.1. Yieldseeker Base Agent 1 (`0x40813df8a23534783e99031fe4f57a65aceeb414`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,021.80`
- **On-Chain Verified Total:** `$2,021.88` (delta: -0.004%)
- **Verified Assets Breakdown:**
  - `USDC`: $2,021.88 (Morpho vault `0xee8f4ec5...`)

### 3.2. Yieldseeker Base Agent 2 (`0xe51b7dba38e732a19838c3f23816df7092441597`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,133.10`
- **On-Chain Verified Total:** `$10,134.16` (delta: -0.012%)
- **Unverified / Reward Assets:** `$0.13`
- **Verified Assets Breakdown:**
  - `USDC`: $7,802.40 (Euler vault `0x4c1aeda9...`)
  - `USDC` (unverified/reward): $0.09
  - `USDC`: $0.00 (Moonwell market `0xedc817a2...`)
  - `USDC`: $2,331.76 (Morpho vault `0xbeefa7b8...`)

### 3.3. ZyFAI Base Agent 2 (`0xbf96c935f7cb35b86efaa0693d81d875f4b4e7eb`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$47,497.88`
- **On-Chain Verified Total:** `$47,499.05` (delta: -0.005%)
- **Unverified / Reward Assets:** `$1.19`
- **Verified Assets Breakdown:**
  - `USDC`: $0.02 (wallet token)
  - `USDC`: $47,499.03 (Fluid vault `0xf42f5795...`)
  - `USDC` (unverified/reward): $1.19

### 3.4. Mamo Base Agent 1 (`0x7c4f5efce7ebd0e99d9d38cad4573140087162dd`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,138.86`
- **On-Chain Verified Total:** `$2,133.98` (delta: -0.014%)
- **Unverified / Reward Assets:** `$5.18`
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
  - `WELL` (unverified/reward): $1.55
  - `USDC`: $2,132.11 (Moonwell market `0xedc817a2...`)

### 3.5. Zyfai AB Risky Agent (`0x6a9e4e59df3e65fdb6a2f8d1ab6f0cd3943c015b`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,660.40`
- **On-Chain Verified Total:** `$10,658.91` (delta: -0.000%)
- **Unverified / Reward Assets:** `$1.50`
- **Verified Assets Breakdown:**
  - `USDC`: $0.01 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $1.50
  - `USDC`: $10,658.90 (Morpho vault `0x8b12106a...`)

### 3.6. Mamo AB Agent (`0x7d42ae4ec4367b52dc03abfc077461cf5c48b256`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$5,399.50`
- **On-Chain Verified Total:** `$5,398.70` (delta: -0.014%)
- **Unverified / Reward Assets:** `$1.56`
- **Verified Assets Breakdown:**
  - `USDC`: $5,398.70 (Moonwell market `0xedc817a2...`)

### 3.7. Zyfai Yield Maxing Agent (`0x3de51ddb55ffec013f428288559dd993e9eeb6b6`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$4,348.15`
- **On-Chain Verified Total:** `$4,345.99` (delta: -0.003%)
- **Unverified / Reward Assets:** `$2.29`
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
  - `FLUID` (unverified/reward): $0.03
  - `USDC`: $4,345.82 (Fluid vault `0xf42f5795...`)
  - `USDC` (unverified/reward): $2.26
  - `WETH`: $0.00 (Superform vault `0x0e70c10f...`)
  - `USDC`: $0.16 (Superform vault `0x11820afe...`)

### 3.8. Conservative Zyfai Agent (`0xc8118008228edd4769fe42f091e7d099a45c4774`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.98`
- **On-Chain Verified Total:** `$0.00` (delta: -0.005%)
- **Unverified / Reward Assets:** `$0.98`
- **Verified Assets Breakdown:**
  - `WETH`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.98

