"""Random bipartite graph generators for benchmarking."""

import random
import logging
from fractions import Fraction
from graph import BipartiteGraph
from classification import classify
from matching import max_weight_matching, MaxWeightMatching
from utils import set_u_vertices, set_v_vertices

_WEIGHT_RANGE = (1, 100)
_ATTEMPT_LIMIT = 100
LOGGER = logging.getLogger(__name__)

def _random_split(n: int, rng: random.Random) -> tuple[int, int]:
    """Split n into (n_u, n_v) with both sides at least 1."""
    n_u = rng.randint(1, n - 1)
    return n_u, n - n_u


def _random_graph(n_u: int, n_v: int, p: float, rng: random.Random) -> BipartiteGraph:
    """Generate a random bipartite graph with approximately p*n_u*n_v edges."""
    u_vertices = set_u_vertices(n_u)
    v_vertices = set_v_vertices(n_u, n_v)
    weights = {
        (u, v): Fraction(rng.randint(*_WEIGHT_RANGE))
        for u in u_vertices
        for v in v_vertices
        if rng.random() < p
    }
    return BipartiteGraph(u_vertices=u_vertices, v_vertices=v_vertices, weights=weights)


def _is_degenerate(graph: BipartiteGraph) -> bool:
    clf = classify(graph)
    return len(clf.viable_edges) != 0


def _find_second_matching(graph: BipartiteGraph, mwm: MaxWeightMatching,) -> MaxWeightMatching | None:
    """Return a maximum-cardinality matching that differs from mwm, or None.

    Iterates over edges of mwm, temporarily removes each one, and checks
    whether the resulting maximum matching has the same cardinality.
    Returns the first such matching found.
    """
    for forbidden_edge in mwm.matching:
        candidate_graph = graph - forbidden_edge
        candidate_mwm = max_weight_matching(candidate_graph.weights)
        if len(candidate_mwm.matching) == len(mwm.matching):
            return candidate_mwm
    return None


def generate_non_degenerate(n: int, p: float, seed: int) -> BipartiteGraph:
    """Generate a random non-degenerate bipartite graph with n vertices.

    n_u and n_v are chosen randomly such that n_u + n_v = n. Edges are
    sampled with probability p. Resamples until the graph is non-degenerate
    (unique MWM). With random integer weights this loop rarely iterates more
    than once.
    """
    rng = random.Random(seed)
    for _ in range(_ATTEMPT_LIMIT):
        n_u, n_v = _random_split(n, rng)
        graph = _random_graph(n_u, n_v, p, rng)
        if graph.edges:
            if not _is_degenerate(graph):
                return graph
            else:
                LOGGER.info(f"Non-degenerate with {len(graph.edges)} edges is DEGENERATE, retrying.")
        else:
            LOGGER.info("Non-degenerate empty graph, retrying.")

    raise RuntimeError(f"Failed to generate non-degenerate graph after {_ATTEMPT_LIMIT} attempts.")


def generate_degenerate(n: int, p: float, seed: int | None) -> BipartiteGraph:
    """Generate a degenerate bipartite graph with two optimal matchings.

    Starts from a non-degenerate graph and performs MWM surgery: a second
    maximum-cardinality matching M' is found, then the weights of its edges
    are adjusted so that w(M') == w(MWM). The graph structure is unchanged;
    only a subset of weights is nudged by a rational Fraction amount.
    """
    rng = random.Random(seed)

    for i in range(_ATTEMPT_LIMIT):
        n_u, n_v = _random_split(n, rng)
        graph = _random_graph(n_u, n_v, p, rng)
        LOGGER.info(f"Degenerate attempt {i+1}: Generated graph with {len(graph.edges)} edges.")
        if graph.edges:
            mwm = max_weight_matching(graph.weights)
            LOGGER.info(f"Degenerate attempt {i+1}: Found MWM with weight {mwm.weight}.")
            second = _find_second_matching(graph, mwm)
            if second is not None:
                second_weight = sum(graph.weights[e] for e in second.matching)
                delta = mwm.weight - second_weight
                bump = Fraction(delta, len(second.matching))
                LOGGER.info(f"Degenerate attempt {i+1}: Found second matching with weight {second_weight}, bump) = {bump} to each of its {len(second.matching)} edges.")
                new_weights = graph.weights.copy()
                for e in second.matching:
                    new_weights[e] += bump

                graph = BipartiteGraph(
                    u_vertices=graph.u_vertices,
                    v_vertices=graph.v_vertices,
                    weights=new_weights,
                )
                if _is_degenerate(graph):
                    return graph
                else:
                    LOGGER.info(f"Degenerate attempt {i+1}: Surgery failed to create degeneracy, skipping.")
            else:
                LOGGER.info(f"Degenerate attempt {i+1}: No second matching found, skipping.")
        else:
            LOGGER.info(f"Degenerate attempt {i+1}: Generated empty graph, skipping.")

    raise RuntimeError(f"Failed to generate degenerate graph after {_ATTEMPT_LIMIT} attempts.")