"""Unit tests for the data quality and contract verification module."""
import unittest
from data_quality import validate_balances, validate_transfers, validate_reconciliation


class TestDataQuality(unittest.TestCase):
    def test_valid_balances_pass(self):
        records = [
            {
                "wallet": "0x40811b7a2d677db638e4a9e52e5a60032e29b414",
                "token_symbol": "USDC",
                "usd_value": 2020.47,
                "balance_float": 2020.47,
            },
            {
                "wallet": "0x40811b7a2d677db638e4a9e52e5a60032e29b414",
                "token_symbol": "ETH",
                "usd_value": 0.05,
                "balance_float": 0.00002,
            },
        ]
        report = validate_balances(records)
        self.assertTrue(report.passed, f"Expected validation to pass but got: {report.failures}")

    def test_invalid_balances_detected(self):
        records = [
            {
                "wallet": "invalid_wallet_address",  # Doesn't start with 0x
                "token_symbol": "",                  # Missing symbol
                "usd_value": -10.5,                  # Negative USD
                "balance_float": -1.0,
            }
        ]
        report = validate_balances(records)
        self.assertFalse(report.passed)
        self.assertGreater(len(report.failures), 0)

    def test_transfers_validation(self):
        valid_transfers = [
            {
                "wallet": "0x1111111111111111111111111111111111111111",
                "amount_float": 100.0,
                "direction": "in",
            }
        ]
        report = validate_transfers(valid_transfers)
        self.assertTrue(report.passed)

        invalid_transfers = [
            {
                "wallet": "0x1111111111111111111111111111111111111111",
                "amount_float": -5.0,
                "direction": "bogus_direction",
            }
        ]
        report = validate_transfers(invalid_transfers)
        self.assertFalse(report.passed)

    def test_reconciliation_validation(self):
        valid_reconciliation = [
            {
                "wallet": "0x1111111111111111111111111111111111111111",
                "status": "OK",
                "onchain_delta_pct": 0.012,
            }
        ]
        report = validate_reconciliation(valid_reconciliation)
        self.assertTrue(report.passed)

        invalid_reconciliation = [
            {
                "wallet": "0x1111111111111111111111111111111111111111",
                "status": "UNKNOWN_ERROR_CODE",
                "onchain_delta_pct": 150.0,  # > 100%
            }
        ]
        report = validate_reconciliation(invalid_reconciliation)
        self.assertFalse(report.passed)


if __name__ == "__main__":
    unittest.main()
