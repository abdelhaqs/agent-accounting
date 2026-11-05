# Value Check & On-Chain Reconciliation Report

**Execution Run ID:** `20261105_120430`  
**Run Timestamp:** 2026-11-05 12:04:30 UTC  
**Primary Source:** **UNIBLOCK**  
**Cross-Check Layer:** **Base On-Chain JSON-RPC** (`https://mainnet.base.org`)  
**Total Agents Audited:** 8  

---

## 1. Executive Summary

- **Audit Health Score:** **8/8 Agents Healthy (100.0%)**
- **Total Capital Tracked (USD):** **$67,640.68**
- **On-Chain Verified Value:** **$67,632.67**
- **Unverified / Reward Assets:** **$12.86**
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
| **Yieldseeker Base Agent 1** | `0x4081...b414` | debank | **$2,032.57** | $2,032.37 | **$2,032.63** | $0.00 | **-0.003%** | **OK** |
| **Yieldseeker Base Agent 2** | `0xe51b...1597` | debank | **$10,203.92** | $10,203.92 | **$10,204.13** | +$0.22 | **-0.004%** | **OK** |
| **ZyFAI Base Agent 2** | `0xbf96...e7eb` | debank | **$47,747.52** | $48,280.10 | **$47,749.07** | +$1.47 | **-0.006%** | **OK** |
| **Mamo Base Agent 1** | `0x7c4f...62dd` | debank | **$2,171.35** | $2,171.35 | **$2,166.03** | +$5.56 | **-0.011%** | **OK** |
| **Zyfai AB Risky Agent** | `0x6a9e...015b` | debank | **$0.05** | $26.92 | **$0.00** | +$0.05 | **-0.006%** | **OK** |
| **Mamo AB Agent** | `0x7d42...b256` | debank | **$5,483.88** | $5,483.88 | **$5,480.64** | +$4.35 | **-0.020%** | **OK** |
| **Zyfai Yield Maxing Agent** | `0x3de5...b6b6` | debank | **$0.41** | $145.11 | **$0.17** | +$0.24 | **-0.000%** | **OK** |
| **Conservative Zyfai Agent** | `0xc811...4774` | debank | **$0.98** | $0.98 | **$0.00** | +$0.98 | **-0.003%** | **OK** |
| **TOTAL** | — | — | **$67,640.68** | **$68,344.63** | **$67,632.67** | **+$12.86** | **-0.007%** | **8/8 HEALTHY** |

---

## 3. Agent Details & Breakdown

### 3.1. Yieldseeker Base Agent 1 (`0x40813df8a23534783e99031fe4f57a65aceeb414`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,032.57`
- **On-Chain Verified Total:** `$2,032.63` (delta: -0.003%)
- **Verified Assets Breakdown:**
  - `USDC`: $2,032.63 (Morpho vault `0xee8f4ec5...`)

### 3.2. Yieldseeker Base Agent 2 (`0xe51b7dba38e732a19838c3f23816df7092441597`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$10,203.92`
- **On-Chain Verified Total:** `$10,204.13` (delta: -0.004%)
- **Unverified / Reward Assets:** `$0.22`
- **Verified Assets Breakdown:**
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.19
  - `USDC`: $0.00 (Moonwell market `0xedc817a2...`)
  - `USDC`: $2,320.60 (Morpho vault `0x8b12106a...`)
  - `USDC`: $7,883.53 (Revert vault `0x36aeae0e...`)

### 3.3. ZyFAI Base Agent 2 (`0xbf96c935f7cb35b86efaa0693d81d875f4b4e7eb`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$47,747.52`
- **On-Chain Verified Total:** `$47,749.07` (delta: -0.006%)
- **Unverified / Reward Assets:** `$1.47`
- **Verified Assets Breakdown:**
  - `USDC`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.02
  - `USDC` (unverified/reward): $1.45
  - `USDC`: $47,749.06 (Morpho vault `0xee8f4ec5...`)

### 3.4. Mamo Base Agent 1 (`0x7c4f5efce7ebd0e99d9d38cad4573140087162dd`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$2,171.35`
- **On-Chain Verified Total:** `$2,166.03` (delta: -0.011%)
- **Unverified / Reward Assets:** `$5.56`
- **Verified Assets Breakdown:**
  - `WELL`: $1.56 (wallet token)
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
  - `WELL` (unverified/reward): $1.32
  - `USDC`: $2,164.47 (Moonwell market `0xedc817a2...`)

### 3.5. Zyfai AB Risky Agent (`0x6a9e4e59df3e65fdb6a2f8d1ab6f0cd3943c015b`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.05`
- **On-Chain Verified Total:** `$0.00` (delta: -0.006%)
- **Unverified / Reward Assets:** `$0.05`
- **Verified Assets Breakdown:**
  - `USDC`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.04

### 3.6. Mamo AB Agent (`0x7d42ae4ec4367b52dc03abfc077461cf5c48b256`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$5,483.88`
- **On-Chain Verified Total:** `$5,480.64` (delta: -0.020%)
- **Unverified / Reward Assets:** `$4.35`
- **Verified Assets Breakdown:**
  - `USDC`: $5,480.64 (Moonwell market `0xedc817a2...`)

### 3.7. Zyfai Yield Maxing Agent (`0x3de51ddb55ffec013f428288559dd993e9eeb6b6`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.41`
- **On-Chain Verified Total:** `$0.17` (delta: -0.000%)
- **Unverified / Reward Assets:** `$0.24`
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
  - `FLUID` (unverified/reward): $0.06
  - `USDC` (unverified/reward): $0.18
  - `WETH`: $0.00 (Superform vault `0x0e70c10f...`)
  - `USDC`: $0.16 (Superform vault `0x11820afe...`)

### 3.8. Conservative Zyfai Agent (`0xc8118008228edd4769fe42f091e7d099a45c4774`)
- **Reconciliation Status:** `OK`
- **Stored Pipeline Total:** `$0.98`
- **On-Chain Verified Total:** `$0.00` (delta: -0.003%)
- **Unverified / Reward Assets:** `$0.98`
- **Verified Assets Breakdown:**
  - `WETH`: $0.00 (wallet token)
  - `USDC` (unverified/reward): $0.00
  - `USDC` (unverified/reward): $0.98

