"""Master Orchestrator CLI for Multi-Chain Accounting & Rate Calculation Pipeline.

Supports granular execution of individual venues, math calculations, safety validations,
broadcast simulations, and reporting.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Path setup
DAG_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DAG_DIR.parent
if str(DAG_DIR) not in sys.path:
    sys.path.insert(0, str(DAG_DIR))

# Phase 1: Extractors
from phase1_extract import (
    extract_vault,
    extract_bridge,
    extract_cctp_inflight,
    extract_zyfai,
    extract_mamo,
    extract_yieldseeker,
)

# Phase 2: Calculators
from phase2_calculate import (
    aggregate_assets,
    deduct_venue_fees,
    derive_share_rate,
)

# Phase 3: Validators
from phase3_validate import (
    check_update_delay,
    check_rate_bounds,
    evaluate_circuit_breaker,
)

# Phase 4: Broadcasters
from phase4_broadcast import (
    simulate_broadcast,
    broadcast_rate,
)

# Phase 5: Reporters
from phase5_report import (
    store_sqlite,
    generate_markdown_report,
    compile_html_dashboard,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("orchestrator")


def run_extract(component: str = "all") -> None:
    logger.info("=== 📦 PHASE 1: EXTRACTION [%s] ===", component.upper())
    extractors = {
        "vault": extract_vault,
        "bridge": extract_bridge,
        "cctp": extract_cctp_inflight,
        "zyfai": extract_zyfai,
        "mamo": extract_mamo,
        "yieldseeker": extract_yieldseeker,
    }
    if component == "all":
        for name, fn in extractors.items():
            fn()
    elif component in extractors:
        extractors[component]()
    else:
        raise ValueError(f"Unknown extractor: {component}. Valid: {list(extractors.keys())} or 'all'")


def run_calculate(component: str = "all") -> None:
    logger.info("=== 🧮 PHASE 2: CALCULATION [%s] ===", component.upper())
    if component in ("all", "aggregate"):
        aggregate_assets()
    if component in ("all", "fees"):
        deduct_venue_fees()
    if component in ("all", "rate"):
        derive_share_rate()


def run_validate(component: str = "all") -> None:
    logger.info("=== 🛡️ PHASE 3: VALIDATION & CIRCUIT BREAKERS [%s] ===", component.upper())
    if component in ("all", "delay"):
        check_update_delay()
    if component in ("all", "bounds"):
        check_rate_bounds()
    if component in ("all", "circuit_breaker", "verdict"):
        evaluate_circuit_breaker()


def run_broadcast(mode: str = "simulate", force: bool = False) -> None:
    logger.info("=== 🤖 PHASE 4: BROADCAST LAYER [%s] ===", mode.upper())
    if mode == "simulate":
        simulate_broadcast()
    elif mode == "live":
        simulate_broadcast()
        broadcast_rate(force=force)
    else:
        raise ValueError(f"Unknown broadcast mode: {mode}. Valid: 'simulate' or 'live'")


def run_report(component: str = "all") -> None:
    logger.info("=== 📊 PHASE 5: STORAGE & REPORTING [%s] ===", component.upper())
    if component in ("all", "sqlite"):
        store_sqlite()
    if component in ("all", "markdown"):
        generate_markdown_report()
    if component in ("all", "html", "dashboard"):
        compile_html_dashboard()


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-Chain Accounting & Rate Pipeline Orchestrator")
    parser.add_argument("--all", action="store_true", help="Run full pipeline end-to-end (safe simulation)")
    parser.add_argument("--phase", choices=["extract", "calculate", "validate", "broadcast", "report"], help="Run entire phase")
    parser.add_argument("--extract", choices=["all", "vault", "bridge", "cctp", "zyfai", "mamo", "yieldseeker"], help="Run specific extractor")
    parser.add_argument("--calculate", choices=["all", "aggregate", "fees", "rate"], help="Run specific calculation")
    parser.add_argument("--validate", choices=["all", "delay", "bounds", "circuit_breaker"], help="Run specific validator")
    parser.add_argument("--broadcast", choices=["simulate", "live"], help="Run broadcast simulation or live push")
    parser.add_argument("--report", choices=["all", "sqlite", "markdown", "html"], help="Run specific reporting step")
    parser.add_argument("--simulate-deposit", type=float, help="Simulate a new user deposit (e.g. --simulate-deposit 30)")
    parser.add_argument("--apply-deposit", action="store_true", help="Apply simulated deposit to artifacts to test downstream calculation & reporting")
    parser.add_argument("--force", action="store_true", help="Force live broadcast even if circuit breaker warns")
    parser.add_argument("--live", action="store_true", help="Execute live on-chain broadcast when running --all")

    args = parser.parse_args()

    if args.simulate_deposit is not None:
        from simulate_deposit import simulate_user_deposit
        simulate_user_deposit(deposit_usdc=args.simulate_deposit, apply_to_artifacts=args.apply_deposit)
        return

    if args.all:
        logger.info("🚀 Starting Full Pipeline Run...")
        run_extract("all")
        run_calculate("all")
        run_validate("all")
        run_broadcast("live" if args.live else "simulate", force=args.force)
        run_report("all")
        logger.info("🎉 Full Pipeline Execution Finished Successfully!")
        return

    handled = False
    if args.phase:
        handled = True
        if args.phase == "extract":
            run_extract("all")
        elif args.phase == "calculate":
            run_calculate("all")
        elif args.phase == "validate":
            run_validate("all")
        elif args.phase == "broadcast":
            run_broadcast("live" if args.live else "simulate", force=args.force)
        elif args.phase == "report":
            run_report("all")

    if args.extract:
        handled = True
        run_extract(args.extract)
    if args.calculate:
        handled = True
        run_calculate(args.calculate)
    if args.validate:
        handled = True
        run_validate(args.validate)
    if args.broadcast:
        handled = True
        run_broadcast(args.broadcast, force=args.force)
    if args.report:
        handled = True
        run_report(args.report)

    if not handled:
        parser.print_help()


if __name__ == "__main__":
    main()
