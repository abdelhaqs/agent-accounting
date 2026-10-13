# 📊 Portfolio Value Check & Rate Derivation Report

> **Run Timestamp (UTC)**: `2026-10-13T23:32:13.264943+00:00`  
> **Circuit Breaker Status**: `REJECTED_BY_CIRCUIT_BREAKER`

---

## 🏛️ Venue Breakdown

| Venue / Contract | Network | Balance / NAV (USDC) | Raw Units | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **BoringVault** | Arbitrum Sepolia | `$70.000000` | `70000000` | Custody & shares |
| **BridgeAgentStrategy** | Arbitrum Sepolia | `$0.000000` | `0` | Idle on Hub |
| **Circle CCTP In-Flight** | Cross-Chain | `$0.000000` | `0` | In-transit burns |
| **ZyFAI Base Strategy** | Base Sepolia | `$0.000000` | `0` | Deployed + Stale |
| **Mamo Base Strategy** | Base Sepolia | `$0.000000` | `0` | Moonwell + Morpho |
| **YieldSeeker Strategy** | Base Sepolia | `$0.000000` | `0` | Snapshot NAV |

---

## 🧮 Portfolio Valuation & Rate Derivation

* **Total Gross Assets**: `$70.000000 USDC`
* **Net Assets (After Venue Fees)**: `$70.000000 USDC`
* **Total Outstanding Shares**: `50.000000 bcUSD`
* **Global Derived Rate**: **`1.400000 USDC / bcUSD`** (`1400000` raw units)

---

## 🛡️ Circuit Breaker & Safety Verdict

* **Allowed to Broadcast**: `❌ NO`
* **Rejection Reasons**: `Proposed rate is outside allowed change bounds`
