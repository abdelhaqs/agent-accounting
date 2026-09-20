"""Sync ERC-20 transfers and balances from Zerion to SQLite for one or many wallets/agents."""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from requests import HTTPError

from storage import Balance, Storage, Transfer
from zerion_client import ZerionClient

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


def setup_logging(log_file: str | None = None) -> logging.Logger:
    """Configure logging to console and optional file."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.handlers = []

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)

    return logger


logger = setup_logging()


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    # Zerion returns ISO 8601 with timezone offset, e.g. 2022-08-15T11:26:31+00:00
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def extract_chain(resource: dict[str, Any]) -> str:
    rel = resource.get("relationships", {})
    chain_data = rel.get("chain", {}).get("data", {})
    return chain_data.get("id", "unknown")


def extract_fungible_details(
    fungible: dict[str, Any], qty: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Pull token id/name/symbol/address/decimals from a fungible_info block."""
    impls = fungible.get("implementations", [])
    impl = impls[0] if impls else {}
    decimals = impl.get("decimals")
    if decimals is None and qty:
        decimals = qty.get("decimals")
    return {
        "token_id": fungible.get("id") or impl.get("fungible_id"),
        "token_name": fungible.get("name"),
        "token_symbol": fungible.get("symbol"),
        "token_address": impl.get("address"),
        "chain_id": impl.get("chain_id"),
        "decimals": decimals,
    }


def extract_quantity(qty: dict[str, Any]) -> dict[str, Any]:
    """Normalise Zerion's quantity object to raw/float/decimals."""
    raw = qty.get("int") if "int" in qty else qty.get("string")
    return {
        "amount_raw": raw,
        "amount_float": qty.get("float"),
        "decimals": qty.get("decimals"),
    }


def load_agents(config_path: str | None) -> list[dict[str, str]]:
    """Load agents from a YAML config file.

    Falls back to a single wallet from WALLET_ADDRESS env var if no config is found.
    Agent name is optional and defaults to the wallet address.
    """
    if config_path and Path(config_path).exists():
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        agents = data.get("agents", [])
        if not agents:
            raise ValueError(f"No agents found in {config_path}")
        for agent in agents:
            if not agent.get("name"):
                agent["name"] = agent["address"]
        return agents

    wallet = os.getenv("WALLET_ADDRESS")
    if not wallet:
        return []
    return [{"name": wallet, "address": wallet}]


def build_transfer(
    wallet: str,
    agent_name: str | None,
    tx: dict[str, Any],
    transfer: dict[str, Any],
    direction: str,
) -> Transfer | None:
    """Build a Transfer record from a Zerion transaction transfer object."""
    fungible = transfer.get("fungible_info")
    if not fungible:
        # Skip non-fungible transfers (NFTs).
        return None

    qty = extract_quantity(transfer.get("quantity", {}))
    details = extract_fungible_details(fungible, transfer.get("quantity", {}))
    if details["decimals"] is None:
        details["decimals"] = qty["decimals"]

    mined_at = parse_iso(tx.get("attributes", {}).get("mined_at"))
    if mined_at is None:
        mined_at = datetime.now(timezone.utc)

    # Zerion docs use sender/recipient; the community SDK uses from/to.
    sender = transfer.get("sender") or transfer.get("from") or ""
    recipient = transfer.get("recipient") or transfer.get("to") or ""

    return Transfer(
        wallet=wallet.lower(),
        agent_name=agent_name,
        tx_id=tx.get("id", ""),
        tx_hash=tx.get("attributes", {}).get("hash", ""),
        chain=extract_chain(tx),
        mined_at=mined_at,
        direction=direction,
        sender=sender.lower(),
        recipient=recipient.lower(),
        amount_raw=qty["amount_raw"],
        amount_float=qty["amount_float"],
        price=transfer.get("price"),
        usd_value=transfer.get("value"),
        **details,
    )


def sync_transfers(
    client: ZerionClient,
    wallet: str,
    storage: Storage,
    agent_name: str | None = None,
    chain_ids: list[str] | str | None = None,
    raw_pages: list[dict[str, Any]] | None = None,
):
    """Fetch all transactions and persist every ERC-20 transfer."""
    wallet = wallet.lower()
    transfers: list[Transfer] = []
    count = 0

    for tx in client.get_transactions(wallet, chain_ids=chain_ids, raw_pages=raw_pages):
        count += 1
        attrs = tx.get("attributes", {})
        for tr in attrs.get("transfers", []):
            direction = tr.get("direction")
            if direction not in ("in", "out"):
                continue
            record = build_transfer(wallet, agent_name, tx, tr, direction)
            if record:
                transfers.append(record)

        # Batch insert every 500 transactions to keep memory bounded.
        if count % 500 == 0:
            logger.info("Processed %d transactions, saving %d transfers...", count, len(transfers))
            storage.save_transfers(transfers)
            transfers = []

    if transfers:
        storage.save_transfers(transfers)

    logger.info("Transfer sync complete for %s. Transactions scanned: %d", wallet, count)


def build_balance(
    wallet: str,
    position: dict[str, Any],
    position_type: str,
    agent_name: str | None = None,
) -> Balance | None:
    attrs = position.get("attributes", {})
    fungible = attrs.get("fungible_info")
    if not fungible:
        return None

    qty = extract_quantity(attrs.get("quantity", {}))
    details = extract_fungible_details(fungible, attrs.get("quantity", {}))
    if details["decimals"] is None:
        details["decimals"] = qty["decimals"]

    if not details["token_symbol"] and not details["token_name"]:
        return None

    return Balance(
        wallet=wallet.lower(),
        agent_name=agent_name,
        chain=extract_chain(position),
        position_type=position_type,
        balance_raw=qty["amount_raw"],
        balance_float=qty["amount_float"],
        price=attrs.get("price"),
        usd_value=attrs.get("value"),
        is_receipt_token=position_type != "wallet",
        **details,
    )


def sync_balances(
    client: ZerionClient,
    wallet: str,
    storage: Storage,
    agent_name: str | None = None,
    chain_ids: list[str] | str | None = None,
    raw_pages: list[dict[str, Any]] | None = None,
):
    """Fetch positions and persist current balances including vault/LP receipts."""
    wallet = wallet.lower()
    balances: list[Balance] = []

    for pos in client.get_positions(
        wallet, positions_filter="no_filter", chain_ids=chain_ids, raw_pages=raw_pages
    ):
        position_type = pos.get("attributes", {}).get("position_type", "unknown")
        b = build_balance(wallet, pos, position_type, agent_name=agent_name)
        if b:
            balances.append(b)

    storage.replace_balances(wallet, balances)
    logger.info("Balance sync complete for %s. Positions stored: %d", wallet, len(balances))


def _debank_balance(
    wallet: str,
    agent_name: str | None,
    token: dict[str, Any],
    position_type: str,
    is_receipt: bool,
) -> Balance | None:
    """Map a DeBank token object (wallet or protocol supply) to a Balance."""
    if not token.get("symbol") and not token.get("name"):
        return None
    amount = token.get("amount")
    price = token.get("price")
    raw = token.get("raw_amount")
    return Balance(
        wallet=wallet,
        agent_name=agent_name,
        chain=token.get("chain", "unknown"),
        position_type=position_type,
        token_id=token.get("id"),
        token_name=token.get("name"),
        token_symbol=token.get("symbol") or token.get("optimized_symbol"),
        token_address=token.get("id"),
        chain_id=token.get("chain"),
        decimals=token.get("decimals"),
        balance_raw=str(raw) if raw is not None else None,
        balance_float=amount,
        price=price,
        usd_value=(amount or 0) * (price or 0) if amount is not None else None,
        is_receipt_token=is_receipt,
        provider="debank",
    )


def _debank_transfer(
    wallet: str,
    agent_name: str | None,
    tx_id: str,
    tx_hash: str,
    chain: str,
    mined_at: datetime,
    direction: str,
    sender: str,
    recipient: str,
    entry: dict[str, Any],
    token_dict: dict[str, Any],
) -> Transfer | None:
    """Map a DeBank history send/receive entry to a Transfer."""
    token_id = entry.get("token_id")
    token = token_dict.get(token_id, {})
    amount = entry.get("amount")
    price = token.get("price")
    return Transfer(
        wallet=wallet,
        agent_name=agent_name,
        tx_id=tx_id,
        tx_hash=tx_hash,
        chain=chain,
        mined_at=mined_at,
        direction=direction,
        sender=(sender or "").lower(),
        recipient=(recipient or "").lower(),
        token_id=token_id,
        token_name=token.get("name"),
        token_symbol=token.get("symbol") or token.get("optimized_symbol"),
        token_address=token_id,
        chain_id=chain,
        decimals=token.get("decimals"),
        amount_raw=None,
        amount_float=amount,
        price=price,
        usd_value=(amount or 0) * (price or 0) if amount is not None else None,
        provider="debank",
    )


def sync_via_debank(
    uniblock: "UniblockClient",
    wallet: str,
    storage: Storage,
    agent_name: str | None = None,
    chain_ids: list[str] | str | None = None,
) -> dict[str, Any]:
    """Fallback sync via Uniblock/DeBank for wallets Zerion doesn't index.

    Fetches wallet tokens, DeFi protocol positions, and transaction history,
    then persists them with provider='debank'. Returns raw responses for archiving.
    """
    wallet_lower = wallet.lower()
    chain_filter = (
        chain_ids if isinstance(chain_ids, str)
        else ",".join(chain_ids) if chain_ids else None
    )
    chains = set(chain_filter.split(",")) if chain_filter else None

    logger.info("DeBank fallback: fetching token list for %s", wallet)
    token_list = uniblock.get_all_token_list(wallet)
    logger.info("DeBank fallback: fetching protocol positions for %s", wallet)
    protocols = uniblock.get_complex_protocol_list(wallet, chain_ids=chain_filter)
    logger.info("DeBank fallback: fetching history for %s", wallet)
    history = uniblock.get_all_history_list(wallet, chain_ids=chain_filter)

    balances: list[Balance] = []
    for t in token_list:
        if chains and t.get("chain") not in chains:
            continue
        b = _debank_balance(wallet_lower, agent_name, t, "wallet", is_receipt=False)
        if b:
            balances.append(b)

    for p in protocols:
        pname = p.get("name") or p.get("id") or "protocol"
        for item in p.get("portfolio_item_list", []):
            itype = item.get("name") or "deposited"
            # Distinguish multiple vaults/pools of the same type within one protocol
            # (e.g. two Morpho USDC vaults) via the pool id.
            pool_id = (item.get("pool") or {}).get("id") or ""
            pool_suffix = f" #{pool_id[-6:]}" if pool_id else ""
            detail = item.get("detail", {})
            for key in ("supply_token_list", "reward_token_list"):
                for t in detail.get(key) or []:
                    if chains and t.get("chain") not in chains:
                        continue
                    b = _debank_balance(
                        wallet_lower, agent_name, t,
                        f"{pname}: {itype}{pool_suffix}", is_receipt=True,
                    )
                    if b:
                        balances.append(b)

    # The balances UNIQUE key includes position_type, so the same token can live in
    # several protocol positions (e.g. two Morpho vaults). Dedupe only exact dupes.
    seen: set[tuple] = set()
    unique_balances: list[Balance] = []
    for b in balances:
        k = (b.chain, b.token_id, b.token_address, b.is_receipt_token, b.position_type)
        if k in seen:
            continue
        seen.add(k)
        unique_balances.append(b)
    balances = unique_balances

    storage.replace_balances(wallet_lower, balances)
    logger.info("DeBank fallback: stored %d balances for %s", len(balances), wallet)

    transfers: list[Transfer] = []
    token_dict = history.get("token_dict", {})
    for h in history.get("history_list", []):
        tx_hash = h.get("tx", {}).get("id") or h.get("id", "")
        tx_id = f"{tx_hash}:{h.get('idx', 0)}"
        if h.get("time_at"):
            mined_at = datetime.fromtimestamp(h["time_at"], tz=timezone.utc)
        else:
            mined_at = datetime.now(timezone.utc)
        chain = h.get("chain", "unknown")
        for send in h.get("sends", []):
            tr = _debank_transfer(
                wallet_lower, agent_name, tx_id, tx_hash, chain, mined_at,
                "out", wallet_lower, send.get("to_addr", ""), send, token_dict,
            )
            if tr:
                transfers.append(tr)
        for recv in h.get("receives", []):
            tr = _debank_transfer(
                wallet_lower, agent_name, tx_id, tx_hash, chain, mined_at,
                "in", recv.get("from_addr", ""), wallet_lower, recv, token_dict,
            )
            if tr:
                transfers.append(tr)

    storage.save_transfers(transfers)
    logger.info("DeBank fallback: stored %d transfers for %s", len(transfers), wallet)

    return {"tokens": token_list, "protocols": protocols, "history": history}


RECONCILE_TOLERANCE_PCT = 1.0
RECONCILE_TOLERANCE_USD = 1.0


def reconcile_balances(
    wallet: str,
    agent_name: str | None,
    provider: str,
    storage: Storage,
    zerion: ZerionClient,
    uniblock: "UniblockClient | None",
    chain_ids: list[str] | str | None,
    run_timestamp: str,
) -> dict[str, Any]:
    """Cross-check stored balances against provider aggregate endpoints.

    Three numbers per agent:
    - computed: SUM(usd_value) of the rows we stored
    - same-provider aggregate: Zerion /portfolio or DeBank /total_balance
      (note: Zerion /portfolio is known to miss deposited positions for some
      wallets, so it is recorded for information but never decides the status)
    - cross-provider aggregate: the other provider's total (the real check)

    Status is MISMATCH when the deciding delta exceeds 1% and $1.
    """
    computed = sum(b["usd_value"] or 0 for b in storage.get_balances(wallet))
    chain_filter = (
        chain_ids if isinstance(chain_ids, str)
        else ",".join(chain_ids) if chain_ids else None
    )
    chains = set(chain_filter.split(",")) if chain_filter else None

    def zerion_total() -> float | None:
        p = zerion.get_portfolio(wallet, chain_ids=chain_ids)
        return p.get("data", {}).get("attributes", {}).get("total", {}).get("positions")

    def debank_total() -> float | None:
        if uniblock is None:
            return None
        tb = uniblock.get_total_balance(wallet)
        chain_list = tb.get("chain_list", [])
        if chains:
            return sum(c.get("usd_value", 0) or 0 for c in chain_list if c.get("id") in chains)
        return tb.get("total_usd_value")

    same_provider_total: float | None = None
    cross_total: float | None = None
    try:
        same_provider_total = zerion_total() if provider == "zerion" else debank_total()
    except Exception as exc:
        logger.warning("Reconcile: same-provider total failed for %s: %s", wallet, exc)
    try:
        cross_total = debank_total() if provider == "zerion" else zerion_total()
    except Exception as exc:
        logger.warning("Reconcile: cross-provider total failed for %s: %s", wallet, exc)

    def delta_pct(ref: float | None) -> float | None:
        if ref is None:
            return None
        if abs(ref) < 1e-9:
            return 0.0 if abs(computed) < 1e-9 else 100.0
        return round((computed - ref) / ref * 100, 3)

    # For zerion agents the /portfolio endpoint is unreliable (misses deposits),
    # so the cross-provider delta decides; for debank agents the same-provider
    # delta decides (it catches mapping bugs like dropped positions).
    deciding_delta = delta_pct(cross_total) if provider == "zerion" else delta_pct(same_provider_total)
    if deciding_delta is None:
        deciding_delta = delta_pct(same_provider_total) or delta_pct(cross_total)

    if deciding_delta is None:
        status = "SKIP"
    else:
        ref = cross_total if provider == "zerion" else same_provider_total
        within = abs(deciding_delta) <= RECONCILE_TOLERANCE_PCT or (
            ref is not None and abs(computed - ref) <= RECONCILE_TOLERANCE_USD
        )
        status = "OK" if within else "MISMATCH"

    record = {
        "run_timestamp": run_timestamp,
        "agent_name": agent_name,
        "wallet": wallet.lower(),
        "provider": provider,
        "computed_usd": round(computed, 4),
        "same_provider_total_usd": round(same_provider_total, 4) if same_provider_total is not None else None,
        "cross_provider_total_usd": round(cross_total, 4) if cross_total is not None else None,
        "same_provider_delta_pct": delta_pct(same_provider_total),
        "cross_provider_delta_pct": delta_pct(cross_total),
        "status": status,
    }
    log_fn = logger.info if status == "OK" else logger.warning
    log_fn(
        "Reconcile %s (%s): stored=$%.2f | same-provider=$%s | cross-provider=$%s -> %s",
        agent_name,
        provider,
        computed,
        f"{same_provider_total:,.2f}" if same_provider_total is not None else "n/a",
        f"{cross_total:,.2f}" if cross_total is not None else "n/a",
        status,
    )
    return record


def verify_onchain(
    wallet: str,
    agent_name: str | None,
    computed_usd: float,
    balances: list[dict[str, Any]],
    rpc: "UniblockRpcClient",
    uniblock: "UniblockClient | None",
    debank_raw: dict[str, Any] | None,
) -> dict[str, Any]:
    """Verify stored balances against raw on-chain state via JSON-RPC (Base).

    Two layers:
    - wallet tokens: eth_call balanceOf for each stored wallet-row token
      (plus eth_getBalance for native ETH rows)
    - vault positions: for every ERC-4626 vault discovered in the DeBank
      protocol list, balanceOf (shares) + convertToAssets -> underlying amount

    Returns onchain_total_usd, onchain_delta_pct vs the stored computed total,
    and a per-item breakdown (archived as raw_onchain_<timestamp>.json).
    """
    details: list[dict[str, Any]] = []
    total = 0.0

    # --- Layer 1: wallet token balances ---
    wallet_rows = [
        b for b in balances
        if not b.get("is_receipt_token") and (b.get("chain") or "").lower() == "base"
    ]
    wallet_rows.sort(key=lambda b: b.get("usd_value") or 0, reverse=True)
    for row in wallet_rows[:20]:  # cap calls; dust beyond this is immaterial
        addr = row.get("token_address")
        decimals = row.get("decimals")
        price = row.get("price")
        symbol = row.get("token_symbol") or row.get("token_name") or "?"
        try:
            if addr and addr.startswith("0x"):
                raw = rpc.get_erc20_balance(addr, wallet)
            elif (symbol or "").upper() == "ETH":
                raw = rpc.get_eth_balance(wallet)
                decimals = decimals if decimals is not None else 18
            else:
                continue
        except Exception as exc:
            logger.warning("On-chain check: balanceOf failed for %s (%s): %s", symbol, addr, exc)
            continue
        amount = raw / 10**decimals if decimals else None
        usd = amount * price if amount is not None and price else None
        if usd:
            total += usd
        details.append({
            "kind": "wallet_token", "symbol": symbol, "token_address": addr,
            "onchain_raw": str(raw), "onchain_amount": amount,
            "price": price, "usd_value": usd,
        })

    # --- Layer 2: ERC-4626 vault positions (Morpho etc.) ---
    protocols: list[dict[str, Any]] = []
    if debank_raw is not None:
        protocols = debank_raw.get("protocols") or []
    elif uniblock is not None:
        try:
            protocols = uniblock.get_complex_protocol_list(wallet, chain_ids="base")
        except Exception as exc:
            logger.warning("On-chain check: vault discovery failed for %s: %s", wallet, exc)

    seen_vaults: set[str] = set()
    unverified_usd = 0.0
    for p in protocols:
        pname = p.get("name") or p.get("id") or "protocol"
        for item in p.get("portfolio_item_list", []):
            pool_id = (item.get("pool") or {}).get("id") or ""
            if not pool_id.startswith("0x") or pool_id.lower() in seen_vaults:
                continue
            detail = item.get("detail") or {}
            supply = detail.get("supply_token_list") or []
            if not supply:
                continue
            seen_vaults.add(pool_id.lower())
            underlying = supply[0]
            decimals = underlying.get("decimals")
            price = underlying.get("price")
            symbol = underlying.get("symbol") or underlying.get("optimized_symbol") or "?"
            # USD value of anything attached to this position that we cannot
            # verify on-chain (reward tokens, or the whole position if both
            # verification strategies fail).
            reward_usd = sum(
                (t.get("amount") or 0) * (t.get("price") or 0)
                for t in detail.get("reward_token_list") or []
            )
            item_usd = sum(
                (t.get("amount") or 0) * (t.get("price") or 0)
                for t in supply
            ) + reward_usd

            # Strategy 1: ERC-4626 vault (Morpho etc.)
            try:
                shares, assets = rpc.get_vault_assets(pool_id, wallet)
                amount = assets / 10**decimals if decimals else None
                usd = amount * price if amount is not None and price else None
                if usd:
                    total += usd
                unverified_usd += reward_usd
                details.append({
                    "kind": "vault", "protocol": pname, "vault_address": pool_id,
                    "underlying_symbol": symbol, "shares_raw": str(shares),
                    "assets_raw": str(assets), "onchain_amount": amount,
                    "price": price, "usd_value": usd,
                })
                continue
            except Exception:
                pass

            # Strategy 2: Compound-fork money market (Moonwell etc.) — the
            # DeBank pool id is the comptroller; resolve the mToken market
            # whose underlying matches, then balanceOfUnderlying(wallet).
            try:
                token_addr = underlying.get("id") or ""
                market = (
                    rpc.find_market_for_underlying(pool_id, token_addr)
                    if token_addr.startswith("0x") else None
                )
                if market is None:
                    raise ValueError(f"no market for underlying {token_addr[:10]}")
                assets = rpc.get_balance_of_underlying(market, wallet)
                amount = assets / 10**decimals if decimals else None
                usd = amount * price if amount is not None and price else None
                if usd:
                    total += usd
                unverified_usd += reward_usd
                details.append({
                    "kind": "money_market", "protocol": pname,
                    "comptroller": pool_id, "market": market,
                    "underlying_symbol": symbol, "assets_raw": str(assets),
                    "onchain_amount": amount, "price": price, "usd_value": usd,
                })
                continue
            except Exception as exc:
                logger.info(
                    "On-chain check: %s pool %s not verifiable on-chain (%s)",
                    pname, pool_id[:10], exc,
                )

            # Fallback: position type we cannot verify — keep it out of the
            # delta so it never false-flags, but record it explicitly.
            unverified_usd += item_usd
            details.append({
                "kind": "unverified", "protocol": pname, "pool": pool_id,
                "underlying_symbol": symbol, "usd_value": item_usd,
            })

    covered = total + unverified_usd
    if abs(covered) < 1e-9:
        delta_pct = 0.0 if abs(computed_usd) < 1e-9 else 100.0
    else:
        delta_pct = round((computed_usd - covered) / covered * 100, 3)

    logger.info(
        "On-chain check %s: stored=$%.2f | on-chain=$%.2f + unverified=$%.2f (delta %s%%, %d items)",
        agent_name, computed_usd, total, unverified_usd, f"{delta_pct:+.3f}", len(details),
    )
    return {
        "onchain_total_usd": round(total, 4),
        "onchain_unverified_usd": round(unverified_usd, 4),
        "onchain_delta_pct": delta_pct,
        "details": details,
    }


def export_json(
    storage: Storage, wallet: str, run_dir: Path, run_timestamp: str
) -> tuple[int, int]:
    """Write timestamped transfers/balances JSON files to *run_dir*.

    Returns (transfers_count, balances_count).
    """
    run_dir.mkdir(parents=True, exist_ok=True)

    transfers = storage.get_transfers(wallet)
    balances = storage.get_balances(wallet)

    transfers_path = run_dir / f"transfers_{run_timestamp}.json"
    balances_path = run_dir / f"balances_{run_timestamp}.json"

    transfers_path.write_text(json.dumps(transfers, indent=2), encoding="utf-8")
    balances_path.write_text(json.dumps(balances, indent=2), encoding="utf-8")

    logger.info(
        "Exported %d transfers to %s and %d balances to %s",
        len(transfers),
        transfers_path,
        len(balances),
        balances_path,
    )
    return len(transfers), len(balances)


def export_raw(
    raw_transactions: list[dict[str, Any]],
    raw_positions: list[dict[str, Any]],
    run_dir: Path,
    run_timestamp: str,
):
    """Write raw API page responses to *run_dir* with timestamped filenames."""
    run_dir.mkdir(parents=True, exist_ok=True)

    tx_path = run_dir / f"raw_transactions_{run_timestamp}.json"
    pos_path = run_dir / f"raw_positions_{run_timestamp}.json"

    tx_path.write_text(json.dumps(raw_transactions, indent=2), encoding="utf-8")
    pos_path.write_text(json.dumps(raw_positions, indent=2), encoding="utf-8")

    logger.info(
        "Exported %d raw transaction pages to %s and %d raw position pages to %s",
        len(raw_transactions),
        tx_path,
        len(raw_positions),
        pos_path,
    )


def _safe_name(name: str) -> str:
    """Make a filesystem-safe name from an agent name or address."""
    return "".join(c if c.isalnum() else "_" for c in name).lower()


def write_run_log(
    logs_dir: Path,
    run_timestamp: str,
    entries: list[dict[str, Any]],
    failed_agents: list[str],
    reconciliation: list[dict[str, Any]] | None = None,
) -> Path:
    """Write a run summary log to <logs_dir>/sync_log_<timestamp>.txt."""
    logs_dir.mkdir(parents=True, exist_ok=True)

    lines = [f"Zerion sync run: {run_timestamp}", ""]
    for e in entries:
        lines.append(f"Agent: {e['agent']} ({e['wallet']})")
        lines.append(f"  Transfers exported: {e['transfers']}")
        lines.append(f"  Balances exported: {e['balances']}")
        lines.append(f"  Raw transaction pages: {e['raw_tx']}")
        lines.append(f"  Raw position pages: {e['raw_pos']}")
        lines.append(f"  Files archived: {', '.join(e['files'])}")
        lines.append("")

    if reconciliation:
        lines.append("Balance reconciliation:")
        for r in reconciliation:
            same = f"${r['same_provider_total_usd']:,.2f}" if r["same_provider_total_usd"] is not None else "n/a"
            cross = f"${r['cross_provider_total_usd']:,.2f}" if r["cross_provider_total_usd"] is not None else "n/a"
            if r.get("onchain_total_usd") is not None:
                unver = r.get("onchain_unverified_usd") or 0
                onchain = f"${r['onchain_total_usd']:,.2f}"
                if unver:
                    onchain += f" (+${unver:,.2f} unverified)"
                onchain += f" ({r['onchain_delta_pct']:+.3f}%)"
            else:
                onchain = "n/a"
            lines.append(
                f"  {r['agent_name']} [{r['provider']}]: stored=${r['computed_usd']:,.2f} "
                f"| same-provider={same} | cross-provider={cross} | on-chain={onchain} -> {r['status']}"
            )
        lines.append("")

    if failed_agents:
        lines.append(f"Failed agents: {', '.join(failed_agents)}")
    else:
        lines.append("All agents completed successfully.")

    log_path = logs_dir / f"sync_log_{run_timestamp}.txt"
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Wrote run log to %s", log_path)
    return log_path


def move_to_archive(run_dir: Path, archive_dir: Path, prefix: str) -> None:
    """Move JSON files from the staging run dir into the flat archive folder.

    Each file is renamed to <prefix>_<filename> so multiple agents can share
    one flat Archive folder without collisions. Staging dir is removed after.
    """
    archive_dir.mkdir(parents=True, exist_ok=True)

    moved = 0
    for f in sorted(run_dir.glob("*.json")):
        f.replace(archive_dir / f"{prefix}_{f.name}")
        moved += 1

    # Remove now-empty staging dir.
    try:
        run_dir.rmdir()
    except OSError:
        pass

    logger.info("Moved %d file(s) from %s to %s (prefix=%s)", moved, run_dir, archive_dir, prefix)


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Sync Zerion wallet data to SQLite")
    parser.add_argument("--db-path", default="zerion.db", help="SQLite database path")
    parser.add_argument("--full-resync", action="store_true", help="Clear transfers and re-fetch from scratch")
    parser.add_argument(
        "--rate-limit-delay",
        type=float,
        default=0.25,
        help="Seconds to sleep between paginated API requests (default 0.25; increase on free plans)",
    )
    parser.add_argument(
        "--chain-ids",
        type=str,
        default=os.getenv("CHAIN_IDS", "base"),
        help="Comma-separated chain ids to sync (default: base; env: CHAIN_IDS; set empty for all chains)",
    )
    parser.add_argument(
        "--agents-config",
        type=str,
        default=os.getenv("AGENTS_CONFIG", "agents.yaml"),
        help="Path to agents YAML config (default: agents.yaml; env: AGENTS_CONFIG)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./RECV",
        help="Staging directory for received JSON exports before archiving (default: ./RECV)",
    )
    parser.add_argument(
        "--archive-dir",
        type=str,
        default="./Archive",
        help="Final destination for timestamped JSON files (default: ./Archive)",
    )
    parser.add_argument(
        "--logs-dir",
        type=str,
        default="./logs",
        help="Directory for per-run summary logs (default: ./logs)",
    )
    parser.add_argument(
        "--bq-dataset",
        type=str,
        default=os.getenv("BQ_DATASET", "agent_accounting"),
        help="BigQuery dataset for balances/transfers tables (default: agent_accounting; env: BQ_DATASET)",
    )
    parser.add_argument(
        "--bq-project",
        type=str,
        default=os.getenv("BQ_PROJECT"),
        help="BigQuery project id (default: inferred from credentials; env: BQ_PROJECT)",
    )
    parser.add_argument(
        "--skip-bq",
        action="store_true",
        help="Skip loading data into BigQuery",
    )
    parser.add_argument(
        "--skip-uniblock",
        action="store_true",
        help="Disable the Uniblock/DeBank fallback for Zerion-unsupported wallets",
    )
    parser.add_argument(
        "--skip-rpc",
        action="store_true",
        help="Disable the on-chain (JSON-RPC) balance verification layer",
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Skip exporting JSON/raw files (only update SQLite)",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default="zerion_sync.log",
        help="Log file path (default: zerion_sync.log; set to empty to disable file logging)",
    )
    args = parser.parse_args()

    global logger
    logger = setup_logging(args.log_file or None)

    if args.log_file:
        logger.info("Logging to %s", Path(args.log_file).resolve())

    api_key = os.getenv("ZERION_API_KEY")
    if not api_key:
        logger.error("Missing ZERION_API_KEY. Check your .env file.")
        sys.exit(1)

    agents = load_agents(args.agents_config)
    if not agents:
        logger.error(
            "No wallets/agents to track. Provide agents.yaml or set WALLET_ADDRESS in .env."
        )
        sys.exit(1)

    chain_ids = args.chain_ids.strip() or None
    client = ZerionClient(api_key, rate_limit_delay=args.rate_limit_delay)
    storage = Storage(args.db_path)
    output_dir = Path(args.output_dir)
    archive_dir = Path(args.archive_dir)
    logs_dir = Path(args.logs_dir)
    run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    bq_client = None
    if not args.skip_bq:
        try:
            from bigquery_loader import get_client

            bq_client = get_client(args.bq_project)
            logger.info("BigQuery loading enabled (dataset=%s)", args.bq_dataset)
        except Exception as exc:
            logger.error("BigQuery client init failed, continuing without BQ: %s", exc)

    uniblock_client = None
    uniblock_key = os.getenv("UNIBLOCK_API_KEY")
    uniblock_backup_key = os.getenv("UNIBLOCK_API_KEY_BACKUP")
    if (uniblock_key or uniblock_backup_key) and not args.skip_uniblock:
        from uniblock_client import UniblockClient

        uniblock_client = UniblockClient(
            uniblock_key or "",
            backup_api_key=uniblock_backup_key,
            rate_limit_delay=args.rate_limit_delay,
        )
        logger.info(
            "Uniblock/DeBank fallback enabled for Zerion-unsupported wallets (%d key(s) configured)",
            len(uniblock_client.api_keys),
        )

    rpc_client = None
    if (uniblock_key or uniblock_backup_key) and not args.skip_rpc:
        from rpc_client import UniblockRpcClient

        rpc_client = UniblockRpcClient(
            uniblock_key or "",
            backup_api_key=uniblock_backup_key,
        )
        logger.info(
            "On-chain (JSON-RPC) balance verification enabled (%d key(s) configured)",
            len(rpc_client.api_keys),
        )


    failed_agents: list[str] = []
    run_entries: list[dict[str, Any]] = []
    reconciliation_records: list[dict[str, Any]] = []
    onchain_results: dict[str, dict[str, Any]] = {}  # wallet -> verify_onchain result
    staged: list[tuple[Path, Path]] = []  # (run_dir, archive_agent_dir)

    for agent in agents:
        agent_name = agent.get("name")
        wallet = agent["address"]
        wallet_lower = wallet.lower()

        logger.info("Processing agent '%s' (%s)", agent_name, wallet)

        try:
            raw_tx_pages: list[dict[str, Any]] = []
            raw_pos_pages: list[dict[str, Any]] = []
            debank_raw: dict[str, Any] | None = None
            provider = "zerion"

            try:
                if args.full_resync:
                    logger.info("Full resync requested: clearing existing transfer data for %s", wallet)
                    storage.clear_transfers(wallet_lower)

                logger.info("Starting transfer sync for %s (chains=%s)", wallet, chain_ids or "all")
                sync_transfers(
                    client,
                    wallet,
                    storage,
                    agent_name=agent_name,
                    chain_ids=chain_ids,
                    raw_pages=raw_tx_pages if not args.no_export else None,
                )

                logger.info("Starting balance sync for %s (chains=%s)", wallet, chain_ids or "all")
                sync_balances(
                    client,
                    wallet,
                    storage,
                    agent_name=agent_name,
                    chain_ids=chain_ids,
                    raw_pages=raw_pos_pages if not args.no_export else None,
                )
            except Exception as exc:
                if uniblock_client is None:
                    raise
                logger.warning(
                    "Zerion sync failed for '%s' (%s): %s — falling back to Uniblock/DeBank",
                    agent_name,
                    wallet,
                    exc,
                )
                debank_raw = sync_via_debank(
                    uniblock_client,
                    wallet,
                    storage,
                    agent_name=agent_name,
                    chain_ids=chain_ids,
                )
                provider = "debank"

            if bq_client is not None:
                try:
                    from bigquery_loader import load_balances, load_transfers

                    load_transfers(bq_client, args.bq_dataset, storage.get_transfers(wallet_lower))
                    load_balances(
                        bq_client, args.bq_dataset, wallet_lower, storage.get_balances(wallet_lower)
                    )
                except Exception as exc:
                    logger.error("BigQuery load failed for %s: %s", wallet, exc, exc_info=True)

            rec: dict[str, Any] | None = None
            try:
                rec = reconcile_balances(
                    wallet,
                    agent_name,
                    provider,
                    storage,
                    client,
                    uniblock_client,
                    chain_ids,
                    run_timestamp,
                )
                reconciliation_records.append(rec)
            except Exception as exc:
                logger.error("Reconciliation failed for %s: %s", wallet, exc, exc_info=True)

            if rpc_client is not None and rec is not None:
                try:
                    onchain = verify_onchain(
                        wallet,
                        agent_name,
                        rec["computed_usd"],
                        storage.get_balances(wallet_lower),
                        rpc_client,
                        uniblock_client,
                        debank_raw,
                    )
                    rec["onchain_total_usd"] = onchain["onchain_total_usd"]
                    rec["onchain_unverified_usd"] = onchain["onchain_unverified_usd"]
                    rec["onchain_delta_pct"] = onchain["onchain_delta_pct"]
                    onchain_results[wallet_lower] = onchain
                    # On-chain ground truth participates in the verdict.
                    d = onchain["onchain_delta_pct"]
                    covered = onchain["onchain_total_usd"] + onchain["onchain_unverified_usd"]
                    if (
                        d is not None
                        and abs(d) > RECONCILE_TOLERANCE_PCT
                        and abs(rec["computed_usd"] - covered)
                        > RECONCILE_TOLERANCE_USD
                        and rec["status"] == "OK"
                    ):
                        rec["status"] = "MISMATCH"
                        logger.warning(
                            "Reconcile %s: on-chain delta %+.3f%% escalates status to MISMATCH",
                            agent_name, d,
                        )
                except Exception as exc:
                    logger.error("On-chain verification failed for %s: %s", wallet, exc, exc_info=True)

            if not args.no_export:
                agent_dir = output_dir / _safe_name(agent_name or wallet_lower)
                run_dir = agent_dir / run_timestamp
                transfers_count, balances_count = export_json(
                    storage, wallet_lower, run_dir, run_timestamp
                )
                export_raw(raw_tx_pages, raw_pos_pages, run_dir, run_timestamp)
                if debank_raw is not None:
                    run_dir.mkdir(parents=True, exist_ok=True)
                    for name, payload in debank_raw.items():
                        (run_dir / f"raw_debank_{name}_{run_timestamp}.json").write_text(
                            json.dumps(payload, indent=2), encoding="utf-8"
                        )
                if wallet_lower in onchain_results:
                    run_dir.mkdir(parents=True, exist_ok=True)
                    (run_dir / f"raw_onchain_{run_timestamp}.json").write_text(
                        json.dumps(onchain_results[wallet_lower], indent=2), encoding="utf-8"
                    )
                prefix = _safe_name(agent_name or wallet_lower)
                staged.append((run_dir, prefix))
                run_entries.append(
                    {
                        "agent": agent_name,
                        "wallet": wallet,
                        "transfers": transfers_count,
                        "balances": balances_count,
                        "raw_tx": len(raw_tx_pages),
                        "raw_pos": len(raw_pos_pages),
                        "files": [f"{prefix}_{f.name}" for f in sorted(run_dir.glob("*.json"))],
                    }
                )

        except HTTPError as exc:
            logger.error(
                "Skipping agent '%s' (%s) due to Zerion API error: %s",
                agent_name,
                wallet,
                exc,
                exc_info=True,
            )
            failed_agents.append(wallet)
        except Exception as exc:
            logger.error(
                "Skipping agent '%s' (%s) due to unexpected error: %s",
                agent_name,
                wallet,
                exc,
                exc_info=True,
            )
            failed_agents.append(wallet)

    if bq_client is not None and reconciliation_records:
        try:
            from bigquery_loader import save_reconciliation

            save_reconciliation(bq_client, args.bq_dataset, reconciliation_records)
        except Exception as exc:
            logger.error("BigQuery reconciliation load failed: %s", exc, exc_info=True)

    if not args.no_export:
        write_run_log(logs_dir, run_timestamp, run_entries, failed_agents, reconciliation_records)
        for run_dir, prefix in staged:
            move_to_archive(run_dir, archive_dir, prefix)

    if failed_agents:
        logger.warning("Completed with %d failed agent(s): %s", len(failed_agents), failed_agents)
    else:
        logger.info("Done. Database: %s", args.db_path)


if __name__ == "__main__":
    main()
