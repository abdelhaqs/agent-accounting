# Phase 5: Third User Deposit Simulation & Pipeline Integration

> **Depositor Address (Testnet 3)**: [`0x2dBEDD97D181E5825e68Fc590716766E5206970F`](https://sepolia.arbiscan.io/address/0x2dBEDD97D181E5825e68Fc590716766E5206970F)  
> **Execution Network**: Arbitrum Sepolia (`421614`)  
> **Deposit Amount**: `20.000000 USDC` (`20,000,000` raw)  
> **Shares Received**: `20.000000 bcUSD` (`20,000,000` raw)  
> **Pre-Deposit TVL**: `$30.00 USDC` / `30.00 bcUSD`  
> **Post-Deposit TVL**: `$50.00 USDC` / `50.00 bcUSD`  

---

## 📜 On-Chain Transaction Hashes

| Step | Action | Transaction Hash | Gas Used | Block Number | Arbiscan Link |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **0** | **Gas Funding** (0.015 ETH from Deployer) | `0x9c147c65eb9f8f34969c673d021b3669785f2bd46736c0e6c6f059c88aa76966` | 21,000 | 318523075 | [View on Arbiscan](https://sepolia.arbiscan.io/tx/0x9c147c65eb9f8f34969c673d021b3669785f2bd46736c0e6c6f059c88aa76966) |
| **1** | **Approve Teller** (`20.0 USDC`) | `0xe698908355352f69364a3785fcfce20fc0112e09f8b0a6a191cc40bedde928d8` | 55,437 | 318523111 | [View on Arbiscan](https://sepolia.arbiscan.io/tx/0xe698908355352f69364a3785fcfce20fc0112e09f8b0a6a191cc40bedde928d8) |
| **2** | **Approve BoringVault** (`20.0 USDC`) | `0x350607cbcf3e17328b9ba4bbbbd37cea5ef58b66cc4b0bcdbf2f5de073e715a1` | 55,437 | 318523142 | [View on Arbiscan](https://sepolia.arbiscan.io/tx/0x350607cbcf3e17328b9ba4bbbbd37cea5ef58b66cc4b0bcdbf2f5de073e715a1) |
| **3** | **Deposit 20 USDC into Teller** | `0x810efbba37e0604f6d92aa21fe24c0c2abb5701d46c613f79958670287f67dc0` | 118,292 | 318523195 | [View on Arbiscan](https://sepolia.arbiscan.io/tx/0x810efbba37e0604f6d92aa21fe24c0c2abb5701d46c613f79958670287f67dc0) |

---

## 🧮 Smart Contract Share Minting Math

During Step 3, [`TellerWithMultiAssetSupport._erc20Deposit`](https://sepolia.arbiscan.io/address/0xA15368BFf702b97EBA1418145509532b497ac565) evaluated:

$$\text{Rate} = \text{accountant.getRateInQuoteSafe(USDC)} = 1{,}000{,}000 \text{ (1.000000)}$$

$$\text{Shares} = \lfloor \frac{20{,}000{,}000 \times 1{,}000{,}000}{1{,}000{,}000} \rfloor = 20{,}000{,}000 \text{ raw units} = \mathbf{20.000000\ bcUSD}$$

The Teller then executed:
```solidity
vault.enter(0x2dBEDD97..., USDC, 20000000, 0x2dBEDD97..., 20000000);
```
Minting **`20.000000 bcUSD`** directly to `0x2dBEDD97D181E5825e68Fc590716766E5206970F`.

---

## 📊 Post-Deposit Cap Table (All 3 Users)

| User | Address | Shares (`bcUSD`) | Underlying Value | Ownership Share |
| :--- | :--- | :---: | :---: | :---: |
| **User 1 (Deployer)** | [`0xe8a7bA64913127AF7e47bF4ca4975Bb846a747F8`](https://sepolia.arbiscan.io/address/0xe8a7bA64913127AF7e47bF4ca4975Bb846a747F8) | 10.00 bcUSD | $10.00 USDC | **20.000%** |
| **User 2** | [`0x974998D1f7dF5ff1A9fFDF5446f4CdBc29690535`](https://sepolia.arbiscan.io/address/0x974998D1f7dF5ff1A9fFDF5446f4CdBc29690535) | 20.00 bcUSD | $20.00 USDC | **40.000%** |
| **User 3 (Testnet 3)** | [`0x2dBEDD97D181E5825e68Fc590716766E5206970F`](https://sepolia.arbiscan.io/address/0x2dBEDD97D181E5825e68Fc590716766E5206970F) | 20.00 bcUSD | $20.00 USDC | **40.000%** |
| **Total Outstanding** | — | **50.00 bcUSD** | **$50.00 USDC** | **100.000%** |

---

## 🤖 Off-Chain Modular Pipeline Ingestion Results

Following the on-chain deposit, the modular ETL engine was executed:
```bash
python dag/run.py --all
```

* **Phase 1 (Extraction)**: BoringVault balance automatically updated to **`$50.000000 USDC`** and **`50.000000 bcUSD`** shares.
* **Phase 2 (Calculation)**: Gross Assets = **`$50.00`**, Net Assets = **`$50.00`**, Derived Rate = **`1.000000 USDC/share`**.
* **Phase 3 (Validation)**: Delay check `PASSED`, bounds check `PASSED`, Circuit Breaker: `APPROVED (Safe to broadcast)`.
* **Phase 4 (Broadcast Simulation)**: Dry-run `Simulation PASSED` via `eth_call` (zero gas spent, no live push as requested).
* **Phase 5 (Reporting)**: Rebuilt interactive HTML audit dashboard and updated `usdc_balance_data.json`.
