"""Pytest configuration and shared fixtures."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def pytest_configure() -> None:
    """Ensure directories expected by pytest logging exist."""
    (PROJECT_ROOT / "logs").mkdir(exist_ok=True)
