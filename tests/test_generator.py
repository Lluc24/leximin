import logging
import random
from generator import generate_non_degenerate, generate_degenerate
from classification import classify

_TRIALS = 10

LOGGER = logging.getLogger("test.generator")


def test_generate_non_degenerate_returns_non_degenerate_graph():
    seed = random.randint(0, 1_000_000)
    n = random.randint(2, 20)
    p = random.uniform(0, 1.0)
    g = generate_non_degenerate(n=n, p=p, seed=seed)
    LOGGER.info(f"Generated graph with {len(g.vertices)} vertices and {len(g.edges)} edges for {n=}, {p=}, {seed=}")
    clf = classify(g)
    assert len(clf.viable_edges) == 0, f"generate_non_degenerate produced degenerate graph for {n=}, {p=}, {seed=}"


def test_generate_degenerate_returns_degenerate_graph():
    seed = random.randint(0, 1_000_000)
    n = random.randint(10, 20)
    p = random.uniform(0.4, 1.0)
    g = generate_degenerate(n=n, p=p, seed=seed)
    LOGGER.info(f"Generated graph with {len(g.vertices)} vertices and {len(g.edges)} edges for {n=}, {p=}, {seed=}")
    clf = classify(g)
    assert len(clf.viable_edges) != 0, f"generate_degenerate produced non-degenerate graph for {n=}, {p=}, {seed=}"