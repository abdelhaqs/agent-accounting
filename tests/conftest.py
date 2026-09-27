"""Pytest fixtures and environment setup."""
import sys
from pathlib import Path

# Add project root and dag directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
dag_dir = root_dir / "dag"

for path in [str(dag_dir), str(root_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)
