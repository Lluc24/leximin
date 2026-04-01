from fractions import Fraction
from pathlib import Path
import sys
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from graph import BipartiteGraph

def pytest_configure() -> None:
    # Keep file logging stable even on fresh clones.
    (PROJECT_ROOT / "logs").mkdir(exist_ok=True)


@pytest.fixture
def sample_graph() -> BipartiteGraph:
    return BipartiteGraph(
        u_vertices=frozenset({0, 1}),
        v_vertices=frozenset({2, 3}),
        weights={
            (0, 2): Fraction(3, 2),
            (1, 2): Fraction(1),
            (1, 3): Fraction(5),
        },
    )
