"""Pytest configuration and shared fixtures."""

import logging
from pathlib import Path
import sys
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOGGER = logging.getLogger("tests.cases")


def pytest_configure() -> None:
    """Ensure directories expected by pytest logging exist."""
    (PROJECT_ROOT / "logs").mkdir(exist_ok=True)


@pytest.fixture(autouse=True)
def log_starting_case(request: pytest.FixtureRequest) -> None:
    """Log a standard start message for every executed test case."""
    LOGGER.info("Starting case: %s", request.node.nodeid)
