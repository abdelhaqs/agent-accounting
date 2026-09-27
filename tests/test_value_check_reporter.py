"""Unit tests for automated value check reporter."""
import tempfile
import unittest
from pathlib import Path

from value_check_reporter import generate_value_check_report


class TestValueCheckReporter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.report_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_generate_report_creates_md_files(self):
        reconciliation = [
            {
                "run_timestamp": "20260927_120000",
                "agent_name": "Test Agent",
                "wallet": "0x40813DF8a23534783E99031fe4F57A65ACEeb414",
                "provider": "uniblock",
                "computed_usd": 15000.0,
                "same_provider_total_usd": 15000.5,
                "onchain_total_usd": 15000.0,
                "onchain_unverified_usd": 0.0,
                "onchain_delta_pct": 0.0,
                "status": "OK",
            }
        ]
        onchain_results = {
            "0x40813df8a23534783e99031fe4f57a65aceeb414": {
                "details": [
                    {"kind": "wallet_token", "symbol": "USDC", "usd_value": 15000.0}
                ]
            }
        }

        report_file = generate_value_check_report(
            report_dir=self.report_dir,
            run_timestamp="20260927_120000",
            reconciliation=reconciliation,
            failed_agents=[],
            primary_source="uniblock",
            onchain_results=onchain_results,
        )

        self.assertTrue(report_file.exists())
        self.assertTrue((self.report_dir / "latest_value_check_report.md").exists())

        content = report_file.read_text(encoding="utf-8")
        self.assertIn("# Value Check & On-Chain Reconciliation Report", content)
        self.assertIn("Test Agent", content)
        self.assertIn("$15,000.00", content)
        self.assertIn("1/1 Agents Healthy (100.0%)", content)
        self.assertIn("USDC", content)
