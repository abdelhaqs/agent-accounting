# Value Check & On-Chain Reconciliation Report

**Execution Run ID:** `20261008_040112`  
**Run Timestamp:** 2026-10-08 04:01:12 UTC  
**Primary Source:** **UNIBLOCK**  
**Cross-Check Layer:** **Base On-Chain JSON-RPC** (`https://mainnet.base.org`)  
**Total Agents Audited:** 8  

---

## 1. Executive Summary

- **Audit Health Score:** **8/8 Agents Healthy (100.0%)**
- **Total Capital Tracked (USD):** **$81,283.64**
- **On-Chain Verified Value:** **$73,654.42**
- **Unverified / Reward Assets:** **$7,634.69**
- **Net On-Chain Delta:** **-0.007%**

### Status Breakdown:
- **OK (Healthy):** 8
- **MISMATCH:** 0
- **RPC_UNVERIFIED:** 0
- **FAILED:** 0

---

## 2. Multi-Provider & On-Chain Audit Table

| Agent Name | Address | Provider | Stored Value (USD) | Same-Provider (Raw) | On-Chain Verified (RPC) | On-Chain Unverified | On-Chain Delta (%) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Yieldseeker Base Agent 1** | `0x4081...b414` | debank | **$2,023.58** | $2,023.58 | **$2,023.63** | $0.00 | **-0.002%** | **OK** |
| **Yieldseeker Base Agent 2** | `0xe51b...1597` | debank | **$10,143.06** | $10,143.06 | **$2,520.65** | +$7,622.50 | **-0.001%** | **OK** |
| **ZyFAI Base Agent 2** | `0xbf96...e7eb` | debank | **$47,539.32** | $47,539.32 | **$47,540.95** | +$2.89 | **-0.010%** | **OK** |
| **Mamo Base Agent 1** | `0x7c4f...62dd` | debank | **$2,145.81** | $2,145.81 | **$2,140.37** | +$5.63 | **-0.009%** | **OK** |
| **Zyfai AB Risky Agent** | `0x6a9e...015b` | debank | **$0.05** | $10.52 | **$0.00** | +$0.05 | **+0.044%** | **OK** |
| **Mamo AB Agent** | `0x7d42...b256` | debank | **$5,416.72** | $5,416.76 | **$5,414.74** | +$2.39 | **-0.007%** | **OK** |
| **Zyfai Yield Maxing Agent** | `0x3de5...b6b6` | debank | **$14,014.12** | $14,076.78 | **$14,014.08** | +$0.25 | **-0.002%** | **OK** |
| **Conservative Zyfai Agent** | `0xc811...4774` | debank | **$0.98** | $0.98 | **$0.00** | +$0.98 | **+0.004%** | **OK** |
| **TOTAL** | — | — | **$81,283.64** | **$81,356.81** | **$73,654.42** | **+$7,634.69** | **-0.007%** | **8/8 HEALTHY** |

---

## 3. Agent Details & Breakdown

### 3.1. Yieldseeker Base Agent 1 (`0x40813df8a23534783e99031fe4f57a65aceeb414`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,023.58`
- **On-Chain Verified Total:** `$2,023.63` (delta: -0.002%)
- **Verified Assets Breakdown:**
  - `USDC`: $2,023.63 (Morpho vault `0xee8f4ec5...`)

### 3.2. Yieldseeker Base Agent 2 (`0xe51b7dba38e732a19838c3f23816df7092441597`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,143.06`
- **On-Chain Verified Total:** `$2,520.65` (delta: -0.001%)
- **Unverified / Reward Assets:** `$7,622.50`
- **Verified Assets Breakdown:**
  - `USDC`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $7,622.37
  - `USDC` (unverified/reward): $0.09
  - `USDC`: $0.00 (Moonwell market `0xedc817a2...`)
  - `USDC`: $2,520.65 (Morpho vault `0xbeefa7b8...`)

### 3.3. ZyFAI Base Agent 2 (`0xbf96c935f7cb35b86efaa0693d81d875f4b4e7eb`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$47,539.32`
- **On-Chain Verified Total:** `$47,540.95` (delta: -0.010%)
- **Unverified / Reward Assets:** `$2.89`
- **Verified Assets Breakdown:**
  - `USDC`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.02
  - `USDC` (unverified/reward): $2.88
  - `USDC`: $47,540.95 (Morpho vault `0x91c056b6...`)

### 3.4. Mamo Base Agent 1 (`0x7c4f5efce7ebd0e99d9d38cad4573140087162dd`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,145.81`
- **On-Chain Verified Total:** `$2,140.37` (delta: -0.009%)
- **Unverified / Reward Assets:** `$5.63`
- **Verified Assets Breakdown:**
  - `WELL`: $1.92 (wallet token)
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
  - `WELL` (unverified/reward): $1.59
  - `USDC`: $2,138.44 (Moonwell market `0xedc817a2...`)

### 3.5. Zyfai AB Risky Agent (`0x6a9e4e59df3e65fdb6a2f8d1ab6f0cd3943c015b`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.05`
- **On-Chain Verified Total:** `$0.00` (delta: +0.044%)
- **Unverified / Reward Assets:** `$0.05`
- **Verified Assets Breakdown:**
  - `USDC`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.04

### 3.6. Mamo AB Agent (`0x7d42ae4ec4367b52dc03abfc077461cf5c48b256`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$5,416.72`
- **On-Chain Verified Total:** `$5,414.74` (delta: -0.007%)
- **Unverified / Reward Assets:** `$2.39`
- **Verified Assets Breakdown:**
  - `USDC`: $5,414.74 (Moonwell market `0xedc817a2...`)

### 3.7. Zyfai Yield Maxing Agent (`0x3de51ddb55ffec013f428288559dd993e9eeb6b6`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$14,014.12`
- **On-Chain Verified Total:** `$14,014.08` (delta: -0.002%)
- **Unverified / Reward Assets:** `$0.25`
- **Verified Assets Breakdown:**
  - `UP`: $0.00 (wallet token)
  - `WETH`: $0.00 (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `AI`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `ARGUS`: n/a (wallet token)
  - `OpenAI`: n/a (wallet token)
  - `Claude`: n/a (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `FLUID` (unverified/reward): $0.04
  - `USDC` (unverified/reward): $0.21
  - `USDC`: $14,013.92 (Morpho vault `0x91c056b6...`)
  - `WETH`: $0.00 (Superform vault `0x0e70c10f...`)
  - `USDC`: $0.16 (Superform vault `0x11820afe...`)

### 3.8. Conservative Zyfai Agent (`0xc8118008228edd4769fe42f091e7d099a45c4774`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.98`
- **On-Chain Verified Total:** `$0.00` (delta: +0.004%)
- **Unverified / Reward Assets:** `$0.98`
- **Verified Assets Breakdown:**
  - `WETH`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.98

