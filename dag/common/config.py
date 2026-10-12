"""Common configuration and contract constants for agent-accounting."""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DAG_DIR = PROJECT_ROOT / "dag"
OUTPUT_DIR = PROJECT_ROOT / "output"
CONFIG_DIR = PROJECT_ROOT / "config"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load environment files
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(CONFIG_DIR / ".env")
load_dotenv(PROJECT_ROOT.parent / ".env")  # workspace root .env

# Chain IDs
ARBITRUM_SEPOLIA_CHAIN_ID = 421614
BASE_SEPOLIA_CHAIN_ID = 84532

# RPC Endpoints
ARBITRUM_SEPOLIA_RPC_URL = os.getenv(
    "ARBITRUM_SEPOLIA_RPC_URL",
    os.getenv("ARBITRUM_RPC_URL", "https://sepolia-rollup.arbitrum.io/rpc")
)
BASE_SEPOLIA_RPC_URL = os.getenv(
    "BASE_SEPOLIA_RPC_URL",
    os.getenv("BASE_RPC_URL", "https://sepolia.base.org")
)

# Arbitrum Sepolia Core Contracts
BORING_VAULT_ADDRESS = "0x40dc77867A136bd19dE6F7bb048D2C4c321f05A0"
ACCOUNTANT_ADDRESS = "0x090eD0ff4B6D9a34c9a6100dd2795644B5915aFd"
ROLES_AUTHORITY_ADDRESS = "0xBEBca977Bb0926ebcBc49cEEC1d6546D2CbFcC38"
BRIDGE_AGENT_STRATEGY_ADDRESS = "0xE8117Bd54BF630DB842BC4c2e6DB835c5D63167C"
TELLER_ADDRESS = "0xA15368BFf702b97EBA1418145509532b497ac565"
ARBITRUM_USDC_ADDRESS = "0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d"

# Circle CCTP v1 Addresses
ARBITRUM_CCTP_TOKEN_MESSENGER = os.getenv(
    "CCTP_TOKEN_MESSENGER", "0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5"
)
BASE_CCTP_MESSAGE_TRANSMITTER = os.getenv(
    "BASE_CCTP_MESSAGE_TRANSMITTER", "0x7865fAfC2db2093669d92c0F33AQ934732661985"
)
BASE_DOMAIN_ID = 6

# Base Sepolia Spoke Strategies
BASE_USDC_ADDRESS = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
ZYFAI_STRATEGY_ADDRESS = "0x8EB5426d68f9DCeFE30e9c006AE7fdF524161627"
YIELDSEEKER_STRATEGY_ADDRESS = "0xA9d3B24e2dB0C5278268943c0E0e0133343CBa99"
MAMO_STRATEGY_ADDRESS = "0xE5C41ACeAba121746a43927D8b68D5154eaaF4C8"

# Keeper & Execution
KEEPER_PRIVATE_KEY = (
    os.getenv("KEEPER_PRIVATE_KEY")
    or os.getenv("DEPLOYER_PRIVATE_KEY")
    or "0x4b0a97d9b3c1d81149694a54aee6850f18c00f79f9d682ff83d9f4c0736635ee"
)

# Safety & Circuit Breakers (defaults matching AccountantWithRateProviders)
ALLOWED_RATE_CHANGE_UPPER = int(os.getenv("ACCOUNTANT_ALLOWED_RATE_CHANGE_UPPER", "10050"))
ALLOWED_RATE_CHANGE_LOWER = int(os.getenv("ACCOUNTANT_ALLOWED_RATE_CHANGE_LOWER", "9950"))
MIN_UPDATE_DELAY_SECONDS = int(os.getenv("ACCOUNTANT_MIN_UPDATE_DELAY", "3600"))
ONE_SHARE = 1_000_000  # 6 decimals
