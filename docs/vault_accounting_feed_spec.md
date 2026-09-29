# Vault Accounting Feed Specification & Data Requirements

This document specifies the data models, exact calculations, unit definitions, and JSON payload format expected by the **Bond Credit Vault Accountant** (`AccountantWithRateProviders`).

---

## 1. Mathematical Formula & Decimals

The exchange rate to be pushed to `Accountant.sol` on Arbitrum is defined as:

$$\text{newExchangeRate} = \frac{\text{totalAssets} \times 10^{\text{shareDecimals}}}{\text{vault.totalSupply()}}$$

### Decimals & Units
* **Base Asset (`USDC`):** 6 decimals ($10^6$).
* **Vault Shares (`BoringVault`):** 18 decimals ($10^{18}$).
* **`newExchangeRate` (`uint96`):** Stored in **USDC decimals (6 decimals)**.
  $$\text{Human Readable Rate} = \frac{\text{newExchangeRate}}{10^6} \text{ USDC per share}$$
  * *Example:* If each share is backed by 1.003449 USDC:
    $$\text{newExchangeRate} = 1{,}003{,}449$$

---

## 2. Itemized Breakdown of `totalAssets`

`totalAssets` must represent the total liquidatable USDC value backing the vault at an atomic snapshot block:

$$\text{totalAssets} = \text{IdleCash} + \text{DeployedNAV} + \text{InFlightBridge} - \text{AccruedFees}$$

### Term 1: Idle USDC Balances
Cash held in protocol contracts on both chains (quoted in raw USDC units, $10^6$):

| Asset Component | Chain | Contract Address | Method |
| :--- | :--- | :--- | :--- |
| Vault Idle Cash | Arbitrum | `0xFf0d384bE00f3Fc36FA03C0A38b08C235a28EEBc` | `USDC.balanceOf(vault)` |
| Bridge Agent Idle Cash | Arbitrum | `0xEC9479F1125A5CC7a3ab16FfB09834F7B2c92b36` | `USDC.balanceOf(bridgeAgent)` |
| Mamo Agent Idle Cash | Base | `0x54F904ae06B6469d118c4C0010F29626e19D3Ce5` | `USDC.balanceOf(mamoAgent)` |
| Zyfai Agent Idle Cash | Base | `0xF8aB601573612323B96d568248FD518E3821FE17` | `USDC.balanceOf(zyfaiAgent)` |
| Yieldseeker Agent Idle Cash | Base | `0xc663aE634045917481Ab5977534c341Aa1f9DdB8` | `USDC.balanceOf(yieldseekerAgent)` |

---

### Term 2: Deployed Venue NAVs (Base)
Assets actively working in venue lending and yield contracts:

#### 1. Mamo Strategy (`mamoNav`)
Mamo operates an on-chain strategy contract `ERC20MoonwellMorphoStrategy`. Its NAV consists of:
* **MetaMorpho Vault:** `metaMorphoVault.convertToAssets(metaMorphoVault.balanceOf(strategy))`
* **Moonwell Market:** `mToken.balanceOfUnderlying(strategy)`
* **Local USDC Cash:** `USDC.balanceOf(strategy)`
$$\text{mamoNav} = \text{MorphoAssets} + \text{MoonwellAssets} + \text{StrategyUSDC}$$

#### 2. Zyfai Strategy (`zyfaiNav`)
Zyfai deploys funds through an off-chain automated manager into Base protocols:
* **Deployed Assets (Net):** `portfolio.portfolioByAssetType.USDC.balanceWithFee`
  *(Must use `balanceWithFee`, which is net of Zyfai's pending performance fee; gross balance includes funds not owned by the vault).*
* **Undeployed Wallet Cash:** `portfolio.portfolioByAssetType.USDC.staleBalances`
$$\text{zyfaiNav} = \text{balanceWithFee} + \text{staleBalances}$$

#### 3. Yieldseeker Strategy (`yieldSeekerNav`)
Yieldseeker positions are held in smart agent wallets:
* Sum of verified on-chain vault positions (e.g. Euler USDC vault `0x4c1aeda9...` + Morpho Steakhouse USDC `0xbeefa7b8...`) or fetched via Yieldseeker Snapshot API (`totalValueBase`).

---

### Term 3: In-Flight Bridge Funds (Circle CCTP)
When USDC is transferred between Arbitrum and Base, CCTP **burns** the token on the source chain before it is minted on the destination. During transit, neither chain's `balanceOf` includes these funds.

$$\text{inFlight} = \text{inFlightFromArbitrum} + \text{inFlightFromBase}$$

#### Arbitrum $\rightarrow$ Base (Capital Allocation):
1. Query `DepositForBurn` events emitted by Arbitrum `TokenMessenger` (`0x19330d10D9Cc8751218eaf51E8885D058642E08A`) where `depositor == bridgeAgentStrategy`.
2. For each burn, check the Base `MessageTransmitter` (`0xAD09780d193884d503182aD4588450C416D6F9D4`):
   ```solidity
   bytes32 key = keccak256(abi.encodePacked(uint32(3), burn.nonce));
   bool delivered = messageTransmitter.usedNonces(key) == 1;
   ```
3. If `!delivered`, add `burn.amount` to `inFlightFromArbitrum`.

#### Base $\rightarrow$ Arbitrum (Redemption Recall):
1. Query `DepositForBurn` events on Base `TokenMessenger` (`0x1682Ae6375C4E4A97e4B583BC394c861A46D8962`) for each Base agent strategy.
2. For each burn, check the Arbitrum `MessageTransmitter` (`0xC30362313FBBA5cf9163F0bb16a0e01f01A896ca`):
   ```solidity
   bytes32 key = keccak256(abi.encodePacked(uint32(6), burn.nonce));
   bool delivered = messageTransmitter.usedNonces(key) == 1;
   ```
3. If `!delivered`, add `burn.amount` to `inFlightFromBase`.

---

### Term 4: Accrued Liabilities (`feesOwedInBase`)
* Read `accountant.accountantState().feesOwedInBase` on Arbitrum.
* **Must be subtracted:** These funds sit in the vault but belong to the protocol fee recipient.

---

### Denominator: Total Share Supply
* Read `vault.totalSupply()` on Arbitrum.
* **Important:** Do **not** subtract shares sitting in `DelayedWithdraw` or `BoringOnChainQueue`. Those shares are escrowed claims that still belong to `totalSupply` until the solver or user burns them.

---

## 3. Canonical JSON Feed Schema (`accountant_feed.json`)

The accounting service should export an atomic JSON payload with the following structure:

```json
{
  "version": "1.0.0",
  "timestamp": 1727650000,
  "datetime_utc": "2026-09-29T22:45:00Z",
  "blocks": {
    "arbitrum": 258900120,
    "base": 20450190
  },
  "balances_usdc_raw": {
    "idle": {
      "arbitrum_vault": "1500000000",
      "arbitrum_bridge_agent": "0",
      "base_mamo_agent": "5100000",
      "base_zyfai_agent": "500000",
      "base_yieldseeker_agent": "130000"
    },
    "deployed": {
      "mamo": "5396060000",
      "zyfai": "10656830000",
      "yieldseeker": "10131600000"
    },
    "in_flight": {
      "arbitrum_to_base": "0",
      "base_to_arbitrum": "0"
    },
    "liabilities": {
      "fees_owed_in_base": "1250000"
    }
  },
  "totals": {
    "total_gross_assets_usdc": "27689590000",
    "total_liabilities_usdc": "1250000",
    "total_net_assets_usdc": "27688340000",
    "vault_total_supply_shares": "27593250000000000000000"
  },
  "rate": {
    "new_exchange_rate_uint96": 1003446,
    "human_readable_rate": "1.003446 USDC / share",
    "decimals": 6
  },
  "pre_flight_checks": {
    "is_paused": false,
    "seconds_since_last_update": 14450,
    "minimum_update_delay": 14400,
    "rate_change_bps": 3.4,
    "allowed_upper_bps": 50,
    "allowed_lower_bps": 50,
    "is_within_bounds": true,
    "can_execute_on_chain": true
  }
}
```

---

## 4. Keeper Pre-Submission Validation Checklist

Before calling `accountant.updateExchangeRate(newExchangeRate)`, the execution bot/keeper must run this validation checklist:

- [ ] **Contract Active:** `accountantState.isPaused == false`
- [ ] **Delay Satisfied:** `block.timestamp >= lastUpdateTimestamp + minimumUpdateDelayInSeconds`
- [ ] **Within Bounds:**
  $$\text{exchangeRate} \times \frac{\text{allowedLower}}{10000} \le \text{newExchangeRate} \le \text{exchangeRate} \times \frac{\text{allowedUpper}}{10000}$$
- [ ] **Non-Zero Supply:** `vault.totalSupply() > MINIMUM_HONEST_SUPPLY` (prevent donation inflation attacks)
- [ ] **Non-Zero Rate:** `newExchangeRate > 0`
