"""Deposit Simulator: Calculate exact shares minted for a new user deposit.

Simulates the on-chain math of TellerWithMultiAssetSupport._erc20Deposit:
    shares = depositAmount.mulDivDown(ONE_SHARE, accountant.getRateInQuoteSafe(asset))
    shares = sharePremium > 0 ? shares.mulDivDown(10000 - sharePremium, 10000) : shares

Can also patch simulated balances into output/ artifacts to test downstream ETL calculation
and dashboard reporting end-to-end without broadcasting on-chain.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Path setup
DAG_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DAG_DIR.parent
if str(DAG_DIR) not in sys.path:
    sys.path.insert(0, str(DAG_DIR))

from common.config import (
    ARBITRUM_SEPOLIA_RPC_URL,
    ARBITRUM_USDC_ADDRESS,
    ACCOUNTANT_ADDRESS,
    BORING_VAULT_ADDRESS,
    OUTPUT_DIR,
    ONE_SHARE,
)
from common.rpc import get_token_balance, get_total_supply, get_accountant_rate, eth_call

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("simulate_deposit")

SEL_ASSET_DATA = "0x56a64f40"  # assetData(address)


def query_share_premium(asset_address: str) -> int:
    """Queries assetData(asset) on Teller to get configured sharePremium."""
    from common.config import TELLER_ADDRESS
    clean_addr = asset_address.lower().replace("0x", "").rjust(64, "0")
    try:
        res = eth_call(ARBITRUM_SEPOLIA_RPC_URL, to=TELLER_ADDRESS, data=SEL_ASSET_DATA + clean_addr)
        if res and len(res) >= 130:
            premium = int(res[66:130], 16)
            return premium
    except Exception:
        pass
    return 0


def simulate_user_deposit(deposit_usdc: float, apply_to_artifacts: bool = False) -> dict:
    deposit_raw = int(round(deposit_usdc * 1e6))
    logger.info("==================================================================")
    logger.info("🧪 SIMULATING NEW USER DEPOSIT: $%.2f USDC (%d raw)", deposit_usdc, deposit_raw)
    logger.info("==================================================================")

    # 1. Query Current On-Chain State
    onchain_rate_raw = get_accountant_rate(ARBITRUM_SEPOLIA_RPC_URL, ACCOUNTANT_ADDRESS)
    if onchain_rate_raw == 0:
        onchain_rate_raw = ONE_SHARE
    onchain_rate = onchain_rate_raw / 1e6

    vault_usdc_raw = get_token_balance(ARBITRUM_SEPOLIA_RPC_URL, ARBITRUM_USDC_ADDRESS, BORING_VAULT_ADDRESS)
    total_shares_raw = get_total_supply(ARBITRUM_SEPOLIA_RPC_URL, BORING_VAULT_ADDRESS)
    share_premium = query_share_premium(ARBITRUM_USDC_ADDRESS)

    # 2. Replicate Teller Contract Math
    # shares = depositAmount.mulDivDown(ONE_SHARE, rate)
    base_shares_raw = (deposit_raw * ONE_SHARE) // onchain_rate_raw
    if share_premium > 0:
        net_shares_raw = (base_shares_raw * (10000 - share_premium)) // 10000
    else:
        net_shares_raw = base_shares_raw

    net_shares = net_shares_raw / 1e6

    # 3. Compute Simulated Post-Deposit State
    new_vault_usdc_raw = vault_usdc_raw + deposit_raw
    new_total_shares_raw = total_shares_raw + net_shares_raw
    new_vault_usdc = new_vault_usdc_raw / 1e6
    new_total_shares = new_total_shares_raw / 1e6

    # Post-deposit candidate rate
    post_rate_raw = (new_vault_usdc_raw * ONE_SHARE) // new_total_shares_raw
    post_rate = post_rate_raw / 1e6

    summary = {
        "deposit_amount_usdc": deposit_usdc,
        "deposit_amount_raw": deposit_raw,
        "rate_used_raw": onchain_rate_raw,
        "rate_used": onchain_rate,
        "share_premium_bps": share_premium,
        "shares_minted_raw": net_shares_raw,
        "shares_minted": net_shares,
        "pre_deposit": {
            "vault_usdc": vault_usdc_raw / 1e6,
            "total_shares": total_shares_raw / 1e6,
        },
        "post_deposit": {
            "vault_usdc": new_vault_usdc,
            "total_shares": new_total_shares,
            "resulting_rate": post_rate,
        },
    }

    logger.info("📌 Rate Used by Teller:        %.6f USDC / bcUSD", onchain_rate)
    logger.info("🪙 Shares Minted to New User:  %.6f bcUSD", net_shares)
    logger.info("💰 Vault Assets:               $%.2f -> $%.2f USDC", vault_usdc_raw / 1e6, new_vault_usdc)
    logger.info("📈 Total Shares Supply:        %.2f -> %.2f bcUSD", total_shares_raw / 1e6, new_total_shares)
    logger.info("⚖️  Resulting Exchange Rate:   %.6f USDC / bcUSD", post_rate)

    # 4. If requested, write simulated state to output/ artifacts to test downstream ETL
    if apply_to_artifacts:
        logger.info("💾 Updating local output/ artifacts with simulated deposit...")
        vault_artifact = OUTPUT_DIR / "01_vault_balance.json"
        sim_vault_data = {
            "timestamp": "SIMULATED",
            "venue": "BoringVault (SIMULATED DEPOSIT)",
            "chain": "arbitrum_sepolia",
            "block_number": "SIMULATED",
            "vault_address": BORING_VAULT_ADDRESS,
            "usdc_address": ARBITRUM_USDC_ADDRESS,
            "raw_balance_usdc": new_vault_usdc_raw,
            "balance_usdc": new_vault_usdc,
            "raw_total_shares": new_total_shares_raw,
            "total_shares": new_total_shares,
            "current_onchain_rate": onchain_rate,
        }
        with open(vault_artifact, "w", encoding="utf-8") as f:
            json.dump(sim_vault_data, f, indent=2)

        sim_output_file = OUTPUT_DIR / "simulated_deposit_result.json"
        with open(sim_output_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info("✅ Patched %s with simulated deposit data.", vault_artifact.name)

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate a new user deposit")
    parser.add_argument(
        "--amount",
        type=float,
        default=30.0,
        help="Amount of USDC the new user deposits (default: 30.0)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Patch output/01_vault_balance.json to run downstream ETL calculate & report phases",
    )
    args = parser.parse_args()
    simulate_user_deposit(deposit_usdc=args.amount, apply_to_artifacts=args.apply)
