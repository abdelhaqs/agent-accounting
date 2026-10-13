# Stale Rate vs. Updated Rate: New User Deposit Dilution Analysis

> **Navigation**: [← Phase 5: Third User Deposit Simulation](05_THIRD_USER_DEPOSIT_SIMULATION.md) • **Deposit Dilution Analysis**

---

## 🏛️ Context & Problem Statement

Following the direct deposit of simulated strategy yield (+20 USDC) into the BoringVault:
* **Real Treasury Assets**: **`$70.000000 USDC`**
* **Total Outstanding Shares**: **`50.000000 bcUSD`**
* **Real Economic NAV**: **`$1.400000 USDC / share`**
* **Stored On-Chain Rate on Accountant**: **`1.000000 USDC / share`** *(Before Keeper updates)*

What happens if a new user (User 4) deposits into the vault right now?

---

## ⚠️ Scenario 1: Deposit with Stale Rate (`1.000000`)

The smart contract calculates shares strictly using `accountant.getRateInQuoteSafe(USDC)`:

$$\text{Shares} = \lfloor \frac{\text{Deposit Amount} \times 10^6}{\text{accountant.getRateInQuoteSafe(USDC)}} \rfloor = \frac{\text{Deposit Amount} \times 10^6}{\mathbf{1{,}000{,}000}}$$

### Concrete Example: User Deposits $14.00 USDC
1. **Shares Minted**:
   The contract uses `1.000000`, minting **`14.000000 bcUSD`** to the new user.
2. **Post-Deposit Pool State**:
   * Total Assets: $\$70.00 + \$14.00 = \mathbf{\$84.00\text{ USDC}}$
   * Total Shares: $50.00 + 14.00 = \mathbf{64.00\text{ bcUSD}}$
3. **The Dilution Effect**:
   * Post-deposit share value: $\frac{\$84.00}{64.00} = \mathbf{\$1.3125\text{ per share}}$
   * The new user paid **`$14.00`**, but received shares worth $14 \times \$1.3125 = \mathbf{\$18.375}$ (an instant **`+$4.375 profit`**).
   * **Dilution of Existing Users**: Existing share value dropped from `$1.40` down to `$1.3125`.

---

## ✅ Scenario 2: Deposit with Updated Rate (`1.400000`)

Once the off-chain keeper pushes the updated rate of **`1.400000`** to the Accountant:

### Concrete Example: User Deposits $14.00 USDC
1. **Shares Minted**:
   $$\text{Shares} = \lfloor \frac{14{,}000{,}000 \times 1{,}000{,}000}{\mathbf{1{,}400{,}000}} \rfloor = \mathbf{10.000000\ bcUSD}$$
2. **Post-Deposit Pool State**:
   * Total Assets: $\$70.00 + \$14.00 = \mathbf{\$84.00\text{ USDC}}$
   * Total Shares: $50.00 + 10.00 = \mathbf{60.00\text{ bcUSD}}$
3. **Fair Value & Zero Dilution**:
   * Post-deposit share value: $\frac{\$84.00}{60.00} = \mathbf{\$1.400000\text{ per share}}$
   * The new user paid **`$14.00`** and received shares worth exactly **`$14.00`**.
   * Existing users retain their full **`$1.40 per share`** without any dilution.

---

## 📊 Comparison Summary Table

| Metric | Scenario 1: Deposit with Stale Rate (`1.00`) | Scenario 2: Deposit with Updated Rate (`1.40`) |
| :--- | :---: | :---: |
| **New User Deposits** | `$14.00 USDC` | `$14.00 USDC` |
| **Rate Used by Teller** | `1.000000 USDC / share` | `1.400000 USDC / share` |
| **Shares Minted to User** | **`14.00 bcUSD`** *(Too many!)* | **`10.00 bcUSD`** *(Exact fair value)* |
| **Post-Deposit Total Assets** | `$84.00 USDC` | `$84.00 USDC` |
| **Post-Deposit Total Shares** | `64.00 bcUSD` | `60.00 bcUSD` |
| **Final Share NAV** | **`$1.3125`** *(Diluted)* | **`$1.4000`** *(Protected)* |
| **Existing Users' Value** | Drops from `$70.00` $\rightarrow$ `$65.62` | Retains full `$70.00` |

---

## 🛡️ Protocol Protections & Role of Off-Chain Keeper

1. **Keep Rates Synchronized**: The off-chain keeper ensures that on-chain storage reflects actual venue balances before new deposits occur.
2. **Deposit Lock Period (`shareLockPeriod`)**: User shares are locked upon deposit, preventing sandwich attacks where users deposit at a stale rate and immediately withdraw to steal yield.
