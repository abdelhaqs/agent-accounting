"""Data Quality and Contract Validation Layer.

Inspired by modern data engineering quality standards (e.g., cuallee / Great Expectations).
Validates schema integrity, completeness, and business rules on balances, transfers,
and reconciliation records before committing to BigQuery or storage.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("data_quality")


@dataclass
class QualityResult:
    rule_name: str
    column: str
    passed: bool
    details: str = ""


@dataclass
class QualityReport:
    suite_name: str
    total_records: int
    results: List[QualityResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def failures(self) -> List[QualityResult]:
        return [r for r in self.results if not r.passed]

    def summary(self) -> str:
        status = "PASSED" if self.passed else "FAILED"
        fail_count = len(self.failures)
        return (
            f"[{status}] {self.suite_name}: {len(self.results)} rules evaluated on "
            f"{self.total_records} rows ({fail_count} failure(s))."
        )


def _validate_with_cuallee(df_pandas: Any, suite_name: str, rules: List[Tuple[str, str, Any]]) -> Optional[QualityReport]:
    """Attempts to run validation using cuallee on a pandas DataFrame."""
    try:
        from cuallee import Check, CheckLevel
        check = Check(CheckLevel.ERROR, suite_name)
        for method, col, arg in rules:
            if hasattr(check, method):
                fn = getattr(check, method)
                if arg is not None:
                    fn(col, arg)
                else:
                    fn(col)
        results_df = check.validate(df_pandas)
        report = QualityReport(suite_name=suite_name, total_records=len(df_pandas))
        for _, row in results_df.iterrows():
            status_val = str(row.get("status", "")).upper()
            rule_name = str(row.get("rule", method))
            col_name = str(row.get("column", ""))
            passed = status_val == "PASS"
            report.results.append(
                QualityResult(
                    rule_name=rule_name,
                    column=col_name,
                    passed=passed,
                    details=f"pass_rate={row.get('pass_rate', 'N/A')}",
                )
            )
        return report
    except Exception as exc:
        logger.debug("Cuallee execution skipped, falling back to native checks: %s", exc)
        return None


def validate_balances(records: List[Dict[str, Any]]) -> QualityReport:
    """Validates an array of balance records before persistence."""
    report = QualityReport(suite_name="BalancesDataContract", total_records=len(records))
    if not records:
        return report

    try:
        import pandas as pd
        df = pd.DataFrame(records)
        rules = [
            ("is_complete", "wallet", None),
            ("is_complete", "token_symbol", None),
            ("is_greater_or_equal_than", "usd_value", 0.0),
            ("is_greater_or_equal_than", "balance_float", 0.0),
        ]
        cuallee_report = _validate_with_cuallee(df, "BalancesDataContract", rules)
        if cuallee_report:
            return cuallee_report
    except ImportError:
        pass

    # Native Python Fallback Checks
    missing_wallets = sum(1 for r in records if not r.get("wallet") or not str(r.get("wallet")).startswith("0x"))
    report.results.append(
        QualityResult(
            rule_name="is_complete",
            column="wallet",
            passed=missing_wallets == 0,
            details=f"{missing_wallets} invalid or missing wallets",
        )
    )

    missing_symbols = sum(1 for r in records if not r.get("token_symbol"))
    report.results.append(
        QualityResult(
            rule_name="is_complete",
            column="token_symbol",
            passed=missing_symbols == 0,
            details=f"{missing_symbols} missing token symbols",
        )
    )

    negative_usd = sum(1 for r in records if (r.get("usd_value") is not None and float(r.get("usd_value", 0)) < 0.0))
    report.results.append(
        QualityResult(
            rule_name="is_greater_or_equal_than_zero",
            column="usd_value",
            passed=negative_usd == 0,
            details=f"{negative_usd} negative usd_value rows",
        )
    )

    negative_balance = sum(1 for r in records if (r.get("balance_float") is not None and float(r.get("balance_float", 0)) < 0.0))
    report.results.append(
        QualityResult(
            rule_name="is_greater_or_equal_than_zero",
            column="balance_float",
            passed=negative_balance == 0,
            details=f"{negative_balance} negative balance_float rows",
        )
    )

    return report


def validate_transfers(records: List[Dict[str, Any]]) -> QualityReport:
    """Validates an array of transfer records."""
    report = QualityReport(suite_name="TransfersDataContract", total_records=len(records))
    if not records:
        return report

    missing_wallets = sum(1 for r in records if not r.get("wallet") or not str(r.get("wallet")).startswith("0x"))
    report.results.append(
        QualityResult(
            rule_name="is_complete",
            column="wallet",
            passed=missing_wallets == 0,
            details=f"{missing_wallets} invalid wallets",
        )
    )

    invalid_amounts = sum(1 for r in records if (r.get("amount_float") is not None and float(r.get("amount_float", 0)) < 0.0))
    report.results.append(
        QualityResult(
            rule_name="is_greater_or_equal_than_zero",
            column="amount_float",
            passed=invalid_amounts == 0,
            details=f"{invalid_amounts} negative amounts",
        )
    )

    valid_directions = {"in", "out", "self", "unknown"}
    invalid_directions = sum(1 for r in records if r.get("direction") and str(r.get("direction")).lower() not in valid_directions)
    report.results.append(
        QualityResult(
            rule_name="is_contained_in",
            column="direction",
            passed=invalid_directions == 0,
            details=f"{invalid_directions} invalid transfer directions",
        )
    )

    return report


def validate_reconciliation(records: List[Dict[str, Any]]) -> QualityReport:
    """Validates reconciliation summary entries."""
    report = QualityReport(suite_name="ReconciliationDataContract", total_records=len(records))
    if not records:
        return report

    valid_statuses = {"OK", "MISMATCH", "RPC_UNVERIFIED", "FAILED"}
    invalid_status_count = sum(1 for r in records if str(r.get("status", "")).upper() not in valid_statuses)
    report.results.append(
        QualityResult(
            rule_name="is_contained_in",
            column="status",
            passed=invalid_status_count == 0,
            details=f"{invalid_status_count} unrecognized statuses",
        )
    )

    invalid_deltas = sum(
        1
        for r in records
        if r.get("onchain_delta_pct") is not None
        and (float(r.get("onchain_delta_pct", 0)) < 0.0 or float(r.get("onchain_delta_pct", 0)) > 100.0)
    )
    report.results.append(
        QualityResult(
            rule_name="is_between",
            column="onchain_delta_pct",
            passed=invalid_deltas == 0,
            details=f"{invalid_deltas} delta values outside [0.0, 100.0]%",
        )
    )

    return report
