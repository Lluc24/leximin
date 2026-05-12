"""Pytest configuration and shared fixtures."""

from pathlib import Path
import sys
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from graph import BipartiteGraph
from tests.graphs import SAMPLE_GRAPH

def pytest_configure() -> None:
    """Ensure directories expected by pytest logging exist."""
    (PROJECT_ROOT / "logs").mkdir(exist_ok=True)


@pytest.fixture
def sample_graph() -> BipartiteGraph:
    """Provide the canonical 2x2 sample graph fixture."""
    return SAMPLE_GRAPH
