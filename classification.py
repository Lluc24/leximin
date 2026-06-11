"""Classification of vertices and edges for the assignment-game algorithm.

Every vertex and edge in the bipartite graph is classified into one of three
categories based on its relationship to the maximum-weight matching (MWM):

* **Essential** — appears in *every* MWM.  Essential vertices always receive
  positive profit in every core imputation; essential edges are always tight.
* **Viable** — appears in *some but not all* MWMs.  Viable edges are still
  tight in every core imputation (Vazirani 2025, Theorem 5).
* **Subpar** — never appears in any MWM.  Subpar vertices always receive zero
  profit; subpar edges may be overpaid.

This three-way partition is the preprocessing step of Algorithm 1 and drives
the construction of fundamental components and the event loop in
``leximin.py``.  The total cost is O((m + n) · T_MWM) where T_MWM = O(n³)
for the Hungarian algorithm used by NetworkX, giving overall O(mn³).
"""

from dataclasses import dataclass, field
import logging

from graph import BipartiteGraph
from matching import max_weight_matching

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Classification:
    """Partition of graph elements into essential, viable, and subpar sets.

    All six vertex sets and three edge sets are disjoint and together cover
    every vertex and edge of the input graph.

    Attributes
    ----------
    essential_u, essential_v:
        Vertices matched in every MWM (positive profit in all core imputations).
    viable_u, viable_v:
        Vertices matched in some but not all MWMs (zero profit in some core
        imputations; positive in others).
    subpar_u, subpar_v:
        Vertices unmatched in every MWM (always receive zero profit).
    essential_edges:
        Edges present in every MWM; always tight under any core imputation.
    viable_edges:
        Edges present in some MWMs; also always tight under any core imputation
        (Vazirani 2025, Theorem 5).
    subpar_edges:
        Edges absent from every MWM; slack may be positive in core imputations.
    """

    essential_u: frozenset[int] = field(default_factory=frozenset)
    essential_v: frozenset[int] = field(default_factory=frozenset)
    viable_u: frozenset[int] = field(default_factory=frozenset)
    viable_v: frozenset[int] = field(default_factory=frozenset)
    subpar_u: frozenset[int] = field(default_factory=frozenset)
    subpar_v: frozenset[int] = field(default_factory=frozenset)

    essential_edges: frozenset[tuple[int, int]] = field(default_factory=frozenset)
    viable_edges: frozenset[tuple[int, int]] = field(default_factory=frozenset)
    subpar_edges: frozenset[tuple[int, int]] = field(default_factory=frozenset)


def classify(graph: BipartiteGraph) -> Classification:
    """Compute the essential/viable/subpar classification of all graph elements.

    The procedure mirrors Section 7.1 of Vazirani (2025):

    1. **Edge classification** — for each edge ``e``, check whether removing
       it strictly decreases the MWM weight.  If so, ``e`` is essential.
       Among the remaining (tentatively subpar) edges, check whether removing
       *both endpoints* of ``e`` decreases the weight by exactly ``w(e)``; if
       so, ``e`` is viable (it participates in an alternative MWM).
    2. **Vertex classification** — a vertex is essential when removing it
       decreases the MWM weight.  Viable vertices are the endpoints of viable
       edges that are not themselves essential.  Everything else is subpar.

    Parameters
    ----------
    graph:
        The input bipartite graph.

    Returns
    -------
    Classification
        Frozen dataclass holding the six vertex sets and three edge sets.
    """
    LOGGER.info(
        "Starting classification (|U|=%d, |V|=%d, |E|=%d)",
        len(graph.u_vertices),
        len(graph.v_vertices),
        len(graph.edges),
    )
    matching = max_weight_matching(graph.weights)
    LOGGER.debug("Reference matching weight: %s", matching.weight)

    essential_edges = frozenset()
    for edge in graph.edges:
        tmp_graph = graph - edge
        tmp_matching = max_weight_matching(tmp_graph.weights)
        if tmp_matching.weight < matching.weight:
            essential_edges |= {edge}
    LOGGER.debug("Essential edges identified: %d", len(essential_edges))

    subpar_edges = graph.edges - essential_edges
    viable_edges = frozenset()
    for u, v in subpar_edges.copy():
        # A non-essential edge (u, v) is viable iff removing both endpoints
        # drops the MWM weight by exactly w(u,v), meaning (u,v) can substitute
        # for the essential edges incident on u and v in some alternative MWM.
        tmp_graph = graph - u - v
        tmp_matching = max_weight_matching(tmp_graph.weights)
        if tmp_matching.weight == matching.weight - graph.weights[u, v]:
            viable_edges |= {(u, v)}
            subpar_edges -= {(u, v)}
    LOGGER.debug(
        "Edge classes computed (essential=%d, viable=%d, subpar=%d)",
        len(essential_edges),
        len(viable_edges),
        len(subpar_edges),
    )

    def classify_vertices(u_vertices: bool) -> tuple[frozenset[int], frozenset[int], frozenset[int]]:
        """Classify either the U side or the V side against the computed edge sets."""
        vertices_set = graph.u_vertices if u_vertices else graph.v_vertices
        essential = frozenset()
        for vtx in vertices_set:
            tmp_g = graph - vtx
            tmp_mwm = max_weight_matching(tmp_g.weights)
            if tmp_mwm.weight < matching.weight:
                essential |= {vtx}
        viable = frozenset(u_ if u_vertices else v_ for u_, v_ in viable_edges) - essential
        subpar = vertices_set - essential - viable
        side = "U" if u_vertices else "V"
        LOGGER.debug(
            "Vertex classes on %s side (essential=%d, viable=%d, subpar=%d)",
            side,
            len(essential),
            len(viable),
            len(subpar),
        )
        return essential, viable, subpar

    essential_u, viable_u, subpar_u = classify_vertices(u_vertices=True)
    essential_v, viable_v, subpar_v = classify_vertices(u_vertices=False)

    result = Classification(
        essential_u=essential_u,
        essential_v=essential_v,
        viable_u=viable_u,
        viable_v=viable_v,
        subpar_u=subpar_u,
        subpar_v=subpar_v,
        essential_edges=essential_edges,
        viable_edges=viable_edges,
        subpar_edges=subpar_edges
    )
    LOGGER.info(
        "Classification complete (E: ess=%s, via=%s, sub=%s | U: ess=%s, via=%s, sub=%s | V: ess=%s, via=%s, sub=%s)",
        set(result.essential_edges),
        set(result.viable_edges),
        set(result.subpar_edges),
        set(result.essential_u),
        set(result.viable_u),
        set(result.subpar_u),
        set(result.essential_v),
        set(result.viable_v),
        set(result.subpar_v),
    )
    return result
