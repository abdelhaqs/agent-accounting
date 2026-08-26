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


def export_json(storage: Storage, wallet: str, agent_dir: Path):
    """Write transfers.json and balances.json to *agent_dir*."""
    agent_dir.mkdir(parents=True, exist_ok=True)

    transfers = storage.get_transfers(wallet)
    balances = storage.get_balances(wallet)

    transfers_path = agent_dir / "transfers.json"
    balances_path = agent_dir / "balances.json"

    transfers_path.write_text(json.dumps(transfers, indent=2), encoding="utf-8")
    balances_path.write_text(json.dumps(balances, indent=2), encoding="utf-8")

    logger.info(
        "Exported %d transfers to %s and %d balances to %s",
        len(transfers),
        transfers_path,
        len(balances),
        balances_path,
    )


def export_raw(
    raw_transactions: list[dict[str, Any]],
    raw_positions: list[dict[str, Any]],
    agent_dir: Path,
):
    """Write raw API page responses to *agent_dir*."""
    agent_dir.mkdir(parents=True, exist_ok=True)

    tx_path = agent_dir / "raw_transactions.json"
    pos_path = agent_dir / "raw_positions.json"

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
        default="./output",
        help="Directory for per-agent exports (default: ./output)",
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

    failed_agents: list[str] = []

    for agent in agents:
        agent_name = agent.get("name")
        wallet = agent["address"]
        wallet_lower = wallet.lower()

        logger.info("Processing agent '%s' (%s)", agent_name, wallet)

        try:
            raw_tx_pages: list[dict[str, Any]] = []
            raw_pos_pages: list[dict[str, Any]] = []

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

            if not args.no_export:
                agent_dir = output_dir / _safe_name(agent_name or wallet_lower)
                export_json(storage, wallet_lower, agent_dir)
                export_raw(raw_tx_pages, raw_pos_pages, agent_dir)

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

    if failed_agents:
        logger.warning("Completed with %d failed agent(s): %s", len(failed_agents), failed_agents)
    else:
        logger.info("Done. Database: %s", args.db_path)


if __name__ == "__main__":
    main()
