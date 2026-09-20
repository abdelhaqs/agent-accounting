"""Standalone script to read on-chain balances directly from the Base RPC.

Demonstrates:
1. Native ETH balance (eth_getBalance)
2. ERC-20 token balances (eth_call balanceOf)
3. ERC-4626 Vault positions (eth_call convertToAssets)
4. Moonwell Lending money markets (eth_call balanceOfUnderlying)

Usage:
    python demo_rpc_reader.py
    python demo_rpc_reader.py --wallet 0x6a9e4e59df3e65fdb6a2f8d1ab6f0cd3943c015b
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from dotenv import load_dotenv

from rpc_client import UniblockRpcClient

load_dotenv()

BASE_USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

# Known Base DeFi vaults/markets
KNOWN_POOLS = {
    "Steakhouse High Yield USDC (Morpho)": {
        "type": "erc4626",
        "address": "0xbeeF01735c132Ada46AA9aA4c54623cAA92A64CB",
        "decimals": 6,
    },
    "Gauntlet USDC Frontier (Morpho)": {
        "type": "erc4626",
        "address": "0x2371e134e3455e0593363cbf89d3b6cf53740618",
        "decimals": 6,
    },
    "Moonwell USDC Market (mUSDC)": {
        "type": "moonwell",
        "market": "0xEdc817A28E8B93Ca120A327090F2329707dF8032",
        "decimals": 6,
    },
}


def read_wallet_via_rpc(wallet: str, rpc: UniblockRpcClient) -> None:
    print(f"\n" + "=" * 60)
    print(f"Reading On-Chain RPC State for: {wallet}")
    print("=" * 60)

    # 1. Latest Block
    block_num = rpc.get_block_number()
    print(f"Current Base Block: {block_num}")

    # 2. Native ETH
    time.sleep(0.5)
    eth_wei = rpc.get_eth_balance(wallet)
    eth_float = eth_wei / 1e18
    print(f"\n[Native ETH]")
    print(f"  Raw Wei: {eth_wei}")
    print(f"  Balance: {eth_float:.6f} ETH")

    # 3. Wallet USDC
    time.sleep(0.5)
    usdc_raw = rpc.get_erc20_balance(BASE_USDC, wallet)
    usdc_float = usdc_raw / 1e6
    print(f"\n[Wallet ERC-20: USDC]")
    print(f"  Raw Units: {usdc_raw}")
    print(f"  Balance:   {usdc_float:.2f} USDC")

    # 4. Check known vault/market positions
    print(f"\n[DeFi Vault & Lending Checks (ERC-4626 / Moonwell)]")
    found_any = False
    for pool_name, meta in KNOWN_POOLS.items():
        time.sleep(0.5)
        if meta["type"] == "erc4626":
            shares, assets = rpc.get_vault_assets(meta["address"], wallet)
            if shares > 0 or assets > 0:
                found_any = True
                amt = assets / (10 ** meta["decimals"])
                print(f"  - {pool_name}:")
                print(f"      Shares: {shares}")
                print(f"      Underlying Assets: {amt:.2f} USDC (raw: {assets})")
        elif meta["type"] == "moonwell":
            assets = rpc.get_balance_of_underlying(meta["market"], wallet)
            if assets > 0:
                found_any = True
                amt = assets / (10 ** meta["decimals"])
                print(f"  - {pool_name}:")
                print(f"      Underlying Supply: {amt:.2f} USDC (raw: {assets})")

    if not found_any:
        print("  (No positions found in the predefined quick-check pool list)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read on-chain balances via Base JSON-RPC")
    parser.add_argument(
        "--wallet",
        default="0x40813DF8a23534783E99031fe4F57A65ACEeb414",
        help="Wallet address to check",
    )
    args = parser.parse_args()

    primary_key = os.getenv("UNIBLOCK_API_KEY")
    backup_key = os.getenv("UNIBLOCK_API_KEY_BACKUP")

    rpc = UniblockRpcClient(primary_key, backup_api_key=backup_key, rate_limit_delay=0.5)
    read_wallet_via_rpc(args.wallet, rpc)


if __name__ == "__main__":
    main()
