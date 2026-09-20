"""DEMO: fetch raw wallet data and store it as JSON files. No database, no transforms.

Flow per agent:
  1. Try Zerion (primary): raw transaction pages + raw position pages
  2. On any failure, fall back to Uniblock/DeBank: token list, protocol
     positions, history, total balance
  3. Write the raw API responses as JSON to <output>/<agent>/<timestamp>/

Usage:
  set ZERION_API_KEY=zk_...        (or in .env)
  set UNIBLOCK_API_KEY=mcr_...     (optional, enables fallback)
  python demo_fetch.py [--output ./demo_output] [--chain-ids base]
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv

from uniblock_client import UniblockClient
from zerion_client import ZerionClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("demo_fetch")


def _safe_name(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name).lower()


def fetch_zerion(client: ZerionClient, wallet: str, chain_ids: str | None) -> dict:
    """Collect raw Zerion pages (no parsing)."""
    tx_pages: list[dict] = []
    pos_pages: list[dict] = []
    for _ in client.get_transactions(wallet, chain_ids=chain_ids, raw_pages=tx_pages):
        pass
    for _ in client.get_positions(
        wallet, positions_filter="no_filter", chain_ids=chain_ids, raw_pages=pos_pages
    ):
        pass
    return {
        "zerion_transactions": tx_pages,
        "zerion_positions": pos_pages,
    }


def fetch_debank(client: UniblockClient, wallet: str, chain_ids: str | None) -> dict:
    """Collect raw DeBank responses (no parsing)."""
    return {
        "debank_total_balance": client.get_total_balance(wallet),
        "debank_token_list": client.get_all_token_list(wallet),
        "debank_protocols": client.get_complex_protocol_list(wallet, chain_ids=chain_ids),
        "debank_history": client.get_all_history_list(wallet, chain_ids=chain_ids),
    }


def zerion_positions_total(pages: list[dict], chains: set[str] | None) -> float:
    """Sum position USD values from raw Zerion position pages."""
    total = 0.0
    for page in pages:
        for pos in page.get("data", []):
            if chains:
                cid = (
                    pos.get("relationships", {})
                    .get("chain", {})
                    .get("data", {})
                    .get("id")
                )
                if cid not in chains:
                    continue
            total += pos.get("attributes", {}).get("value") or 0
    return total


def debank_total(total_balance: dict, chains: set[str] | None) -> float:
    """Sum per-chain USD values from a DeBank total_balance response."""
    chain_list = total_balance.get("chain_list", [])
    if chains:
        return sum(c.get("usd_value", 0) or 0 for c in chain_list if c.get("id") in chains)
    return total_balance.get("total_usd_value") or 0.0


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Demo raw fetch: Zerion -> DeBank fallback -> JSON files")
    parser.add_argument("--output", default="./demo_output", help="Output directory (default: ./demo_output)")
    parser.add_argument("--agents-config", default=os.getenv("AGENTS_CONFIG", "agents.yaml"))
    parser.add_argument(
        "--chain-ids",
        default=os.getenv("CHAIN_IDS", "base"),
        help="Comma-separated chain ids (default: base; empty = all chains)",
    )
    parser.add_argument("--rate-limit-delay", type=float, default=0.25)
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Fetch BOTH providers for every agent and print a side-by-side comparison",
    )
    args = parser.parse_args()

    zerion_key = os.getenv("ZERION_API_KEY")
    if not zerion_key:
        logger.error("Missing ZERION_API_KEY (env or .env)")
        sys.exit(1)

    with open(args.agents_config, encoding="utf-8") as f:
        agents = yaml.safe_load(f).get("agents", [])
    if not agents:
        logger.error("No agents in %s", args.agents_config)
        sys.exit(1)

    chain_ids = args.chain_ids.strip() or None
    zerion = ZerionClient(zerion_key, rate_limit_delay=args.rate_limit_delay)
    uniblock = None
    uniblock_key = os.getenv("UNIBLOCK_API_KEY")
    uniblock_backup = os.getenv("UNIBLOCK_API_KEY_BACKUP")
    if uniblock_key or uniblock_backup:
        uniblock = UniblockClient(
            uniblock_key or "",
            backup_api_key=uniblock_backup,
            rate_limit_delay=args.rate_limit_delay,
        )
        logger.info("DeBank fallback enabled (%d key(s) configured)", len(uniblock.api_keys))
    else:
        logger.warning("UNIBLOCK_API_KEY not set — no fallback, Zerion failures will be skipped")


    run_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_root = Path(args.output)
    summary = []

    chains = set(chain_ids.split(",")) if chain_ids else None

    for agent in agents:
        name = agent.get("name") or agent["address"]
        wallet = agent["address"]
        logger.info("=== %s (%s) ===", name, wallet)

        data: dict = {}
        provider = "zerion"
        zerion_total = debank_total_usd = None

        if args.compare:
            # Fetch both providers independently; tolerate either one failing.
            try:
                zdata = fetch_zerion(zerion, wallet, chain_ids)
                data.update(zdata)
                zerion_total = zerion_positions_total(zdata["zerion_positions"], chains)
            except Exception as exc:
                logger.warning("Zerion failed for %s: %s", name, exc)
            if uniblock is not None:
                try:
                    ddata = fetch_debank(uniblock, wallet, chain_ids)
                    data.update(ddata)
                    debank_total_usd = debank_total(ddata["debank_total_balance"], chains)
                except Exception as exc:
                    logger.warning("DeBank failed for %s: %s", name, exc)
            if not data:
                summary.append({"agent": name, "provider": None, "files": 0, "error": "both providers failed"})
                continue
            provider = "compare"
        else:
            try:
                data = fetch_zerion(zerion, wallet, chain_ids)
            except Exception as exc:
                if uniblock is None:
                    logger.error("Zerion failed for %s and no fallback configured: %s", name, exc)
                    summary.append({"agent": name, "provider": None, "files": 0, "error": str(exc)})
                    continue
                logger.warning("Zerion failed for %s (%s) — falling back to DeBank", name, exc)
                try:
                    data = fetch_debank(uniblock, wallet, chain_ids)
                    provider = "debank"
                except Exception as exc2:
                    logger.error("DeBank fallback also failed for %s: %s", name, exc2)
                    summary.append({"agent": name, "provider": None, "files": 0, "error": str(exc2)})
                    continue

        agent_dir = out_root / _safe_name(name) / run_ts
        agent_dir.mkdir(parents=True, exist_ok=True)
        files = []
        for label, payload in data.items():
            path = agent_dir / f"{label}_{run_ts}.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            files.append(path.name)
            logger.info("  wrote %s (%d bytes)", path, path.stat().st_size)
        summary.append({
            "agent": name,
            "provider": provider,
            "files": len(files),
            "zerion_total": zerion_total,
            "debank_total": debank_total_usd,
        })

    print("\n===== SUMMARY =====")
    for s in summary:
        if s.get("error"):
            print(f"  {s['agent']}: FAILED ({s['error'][:80]})")
        else:
            print(f"  {s['agent']}: {s['provider']} -> {s['files']} files")

    if args.compare:
        print("\n===== PROVIDER COMPARISON (USD, chain filter: %s) =====" % (chain_ids or "all"))
        print(f"  {'Agent':<28} {'Zerion':>14} {'DeBank':>14} {'Delta %':>9}")
        print("  " + "-" * 69)
        for s in summary:
            if s.get("error"):
                continue
            z, d = s["zerion_total"], s["debank_total"]
            zs = f"{z:,.2f}" if z is not None else "n/a"
            ds = f"{d:,.2f}" if d is not None else "n/a"
            if z is not None and d is not None and abs(d) > 1e-9:
                delta = f"{(z - d) / d * 100:+.2f}%"
            else:
                delta = "n/a"
            print(f"  {s['agent']:<28} {zs:>14} {ds:>14} {delta:>9}")

    print(f"Output: {out_root.resolve()}")


if __name__ == "__main__":
    main()
