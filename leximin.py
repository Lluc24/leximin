"""Event-driven solver for computing a leximin core imputation.

This module is the heart of the implementation.  ``LeximinSolver`` executes
Algorithm 1 of Vazirani (2025): a clock-based primal–dual event loop that
iteratively repairs the minimum-profit vertex until all profits are
leximin-optimal.

High-level flow
---------------
1. **Initialisation** — classify all edges and vertices; find fundamental
   components (connected components of the essential/viable-edge subgraph
   whose vertices are all essential); place them in BIN and schedule their
   activation events.  All non-essential vertices are immediately frozen
   (they receive zero profit in every core imputation).

2. **Event loop** — pop the lowest-clock event from the min-heap and dispatch:

   * ``BinActivationEvent`` — the global clock has reached the minimum profit
     of a BIN component; activate it as a ``ValidComponent`` with the
     appropriate rotation direction and schedule its repair and tight-edge events.

   * ``FullyRepairedEvent`` — an active component's rotation has equalized the
     minimum profit on both sides; extract the minimal subcomponent (Min-Sub1),
     move it to FULLY-REPAIRED, and decompose the remainder back to BIN.

   * ``TightEdgeEvent`` — a subpar edge incident on an active component has
     become tight; apply the correct merge/freeze rule based on the status
     (BIN / ACTIVE / FROZEN / FULLY-REPAIRED) of the opposite endpoint.

3. **Termination** — when the heap is empty every vertex's profit is final
   and the current ``Imputation`` object is returned.

Design notes
------------
- The priority queue stores tuples ``(clock, priority, seq, event)`` so that
  ties are broken deterministically: TightEdge < BinActivation < FullyRepaired
  (see ``events.py``).
- Stale events (referencing components that have already been deactivated) are
  silently skipped via ``_is_stale``.
- The clock advances by rotating *all* currently active components
  simultaneously, preserving the core invariant on every tight edge.
"""

import heapq
import logging
from component import FundamentalComponent, ValidComponent
from classification import classify
from events import BinActivationEvent, FullyRepairedEvent, TightEdgeEvent, Event
from fractions import Fraction
from graph import BipartiteGraph
from imputation import Imputation, compute_imputation
from itertools import count
from matching import max_weight_matching
from utils import s

LOGGER = logging.getLogger(__name__)


class LeximinSolver:
    """Event-driven implementation of Algorithm 1 (Vazirani 2025).

    Attributes
    ----------
    graph:
        The input bipartite graph.
    clf:
        Pre-computed classification of all vertices and edges.
    bin_set:
        Set of fundamental components waiting to be activated.
    active:
        Set of valid components currently undergoing rotation.
    frozen:
        Set of vertex IDs whose profit is permanently fixed (unique-imputation
        components and subpar vertices).
    fully_repaired:
        Set of vertex IDs that have reached their leximin-optimal profit.
    imp:
        The mutable imputation object; updated in place during the event loop.
    clock:
        The current global clock value ``Ω``.
    pq:
        Min-heap of ``(clock, priority, seq, event)`` tuples.
    seq:
        Tie-breaking counter; incremented on every push.
    """

    def __init__(self, graph: BipartiteGraph, imp: Imputation = None):
        """Initialize solver state from graph classification and an optional starting imputation.

        Parameters
        ----------
        graph:
            The bipartite graph for which to compute the leximin core imputation.
        imp:
            An optional pre-computed core imputation to use as the starting point.
            If ``None``, the U-optimal core imputation is computed via LP.
        """
        self.graph = graph
        self.clf = classify(graph)

        self.bin_set: set[FundamentalComponent] = set()
        self.active: set[ValidComponent] = set()
        self.frozen: set[int] = set()
        self.fully_repaired: set[int] = set()

        self.imp: Imputation = imp or compute_imputation(graph, max_weight_matching(graph.weights))
        self.clock: Fraction = Fraction(0)
        self.pq: list[tuple[Fraction, int, int, Event]] = []
        self.seq = count()
        LOGGER.info(
            "Initialized solver (%s imputation, |U|=%d, |V|=%d, |E|=%d)",
            "provided" if imp is not None else "computed",
            len(graph.u_vertices),
            len(graph.v_vertices),
            len(graph.edges),
        )

    def solve(self) -> Imputation:
        """Execute the event loop and return the final imputation."""
        LOGGER.info("Starting leximin event loop")
        self._initialize()
        while self.pq:
            LOGGER.debug("Current priority queue: %s", self.pq)
            event = self._pop_event()
            if self._is_stale(event):
                LOGGER.info("Skipping stale event: %s", event)
            else:
                LOGGER.info("Handling event: %s", event)
                self._advance_clock_to(event.clock)
                self._dispatch(event)
        LOGGER.info("Leximin solve complete at clock %s", self.clock)
        return self.imp

    def _initialize(self):
        """Seed bins with essential edges and schedule first activations."""
        fcs = self._get_fundamental_components()
        fcs_vertices = frozenset(u for fc in fcs for u in fc.vertices)
        self.frozen |= self.graph.vertices.difference(fcs_vertices)
        LOGGER.info("Initializing with fundamental components: %s", fcs)
        for fc in fcs:
            self.bin_set.add(fc)
            ev = BinActivationEvent(fc.min_profit(self.imp), fc)
            self._push_event(ev)
        LOGGER.debug("Initialization complete (bin_set=%d, queued=%d)", len(self.bin_set), len(self.pq))

    def _push_event(self, event: Event):
        """Push event into priority queue with deterministic tie-breaking."""
        heapq.heappush(self.pq, (event.clock, event.priority, next(self.seq), event))
        LOGGER.debug("Scheduled event: %s (queue size=%d)", event, len(self.pq))

    def _pop_event(self) -> Event:
        """Pop the next event from priority queue."""
        event = heapq.heappop(self.pq)[-1]
        LOGGER.debug("Popped event: %s", event)
        return event

    def _is_stale(self, event: Event) -> bool:
        """Return True when event references state that is no longer active."""
        if isinstance(event, BinActivationEvent):
            return event.fc not in self.bin_set
        elif isinstance(event, TightEdgeEvent):
            if event.source_vc not in self.active:
                return True
            if event not in self._get_tight_edge_events_for(event.source_vc):
                return True
            return False
        else:
            return event.vc not in self.active

    def _advance_clock_to(self, new_clock: Fraction):
        """Advance global clock and apply accumulated rotation to active components."""
        delta = new_clock - self.clock
        if delta > 0:
            for vc in self.active:
                self.imp.apply_rotation(
                    increasing=vc.increasing_vertices,
                    decreasing=vc.decreasing_vertices,
                    delta=delta
                )
            self.clock = new_clock
            LOGGER.info(
                "Clock advanced by %s to %s, new imputation: %s",
                delta,
                self.clock,
                self.imp,
            )

    def _dispatch(self, event: Event) -> None:
        """Route one event to its handler."""
        if isinstance(event, BinActivationEvent):
            self._on_bin_activation(event)
        elif isinstance(event, FullyRepairedEvent):
            self._on_fully_repaired(event)
        elif isinstance(event, TightEdgeEvent):
            self._on_tight_edge(event)

    def _on_bin_activation(self, event: BinActivationEvent) -> None:
        """Turn one fundamental component into an active valid component."""
        fc = event.fc
        self.bin_set.remove(fc)
        vc = ValidComponent(root=fc, rotation='CW' if fc.has_min_on_left(self.imp) else 'CCW')
        self.active.add(vc)
        LOGGER.info("Activated bin %s as %s", fc, vc)
        self._schedule_events_for(vc)

    def _on_fully_repaired(self, event: FullyRepairedEvent) -> None:
        """Finalize one valid component and return its remainders to bins."""
        vc = event.vc
        self.active.remove(vc)
        min_sub: ValidComponent = vc.compute_min_sub1(self.imp)
        LOGGER.info("Component fully repaired: %s; minsub1=%s", vc, min_sub)
        self.fully_repaired.update(min_sub.vertices)
        self._add_remainders_to_bin(vc, min_sub)

    def _on_tight_edge(self, event: TightEdgeEvent) -> None:
        """Handle a tight subpar edge according to current status of its endpoint."""
        source_vc = event.source_vc
        i, j = event.edge if event.edge[0] in source_vc.vertices else event.edge[::-1]
        self.active.remove(source_vc)
        LOGGER.info("Handling tight edge detected from %s (i=%d, j=%d)", source_vc, i, j)

        if j in self.frozen:
            min_sub = source_vc.compute_min_sub3(i)
            LOGGER.info("Tight edge endpoint %d is frozen; minsub3=%s", j, min_sub)
            self.frozen.update(min_sub.vertices)
            self._add_remainders_to_bin(source_vc, min_sub)

        elif j in self.fully_repaired:
            min_sub = source_vc.compute_min_sub3(i)
            LOGGER.info("Tight edge endpoint %d is fully repaired; minsub3=%s", j, min_sub)
            self.fully_repaired.update(min_sub.vertices)
            self._add_remainders_to_bin(source_vc, min_sub)

        elif any(j in vc.vertices for vc in self.active):
            [other_vc] = [vc for vc in self.active if j in vc.vertices]
            self.active.remove(other_vc)
            source_min_sub, other_min_sub = source_vc.compute_min_sub2(other_vc, i, j)
            LOGGER.info("Tight edge joins active components: %s and %s; minsub2=(%s, %s)", source_vc, other_vc, source_min_sub, other_min_sub)
            self.fully_repaired.update(source_min_sub.vertices | other_min_sub.vertices)
            self._add_remainders_to_bin(source_vc, source_min_sub)
            self._add_remainders_to_bin(other_vc, other_min_sub)

        else:
            # Endpoint `j` is still in a bin; absorb that FC as a child and continue.
            [fc] = [fc for fc in self.bin_set if j in fc.vertices]
            self.bin_set.remove(fc)
            new_vc = source_vc.add_child_at(i, fc)
            self.active.add(new_vc)
            LOGGER.info("Attached bin component %s to %s at vertex %d -> %s", fc, source_vc, i, new_vc)
            self._schedule_events_for(new_vc)

    def _schedule_events_for(self, vc: ValidComponent) -> None:
        """Schedule full-repair and tight-edge events for an active component."""
        delta = vc.rotation_to_fully_repair(self.imp)
        ev = FullyRepairedEvent(self.clock + delta, vc)
        LOGGER.info("Scheduled full repair event for %s at clock %s (delta=%s)", vc, ev.clock, delta)
        self._push_event(ev)
        tight_events = self._get_tight_edge_events_for(vc)
        for ev in tight_events:
            LOGGER.info("Scheduled tight edge event for %s at clock %s", ev.edge, ev.clock)
            self._push_event(ev)

    def _get_tight_edge_events_for(self, vc: ValidComponent) -> list[TightEdgeEvent]:
        """Compute the set of TightEdgeEvents that may fire before ``vc`` is fully repaired.

        For each subpar edge ``(u, v)`` with ``u ∈ vc.decreasing_vertices`` and
        ``v ∉ vc``, the slack ``s = p(u) + p(v) - w(u,v)`` changes at a rate
        that depends on whether ``v`` is in another active component and whether
        it is on the increasing or decreasing side of that component.

        Three cases arise (let ``δ₁ = vc.rotation_to_fully_repair``,
        ``δ₂ = other_vc.rotation_to_fully_repair``):

        **Case A — ``v`` is decreasing in another active component.**
        Both endpoints move downward at unit rate, so slack decreases at rate 2.

        - If ``s ≤ 2·min(δ₁, δ₂)``: the edge tightens before either component
          is repaired.  Fire at ``clock + s/2``.
        - If ``2·min(δ₁, δ₂) < s < δ₁ + δ₂``: the first component to be
          repaired stops moving, after which only ``vc``'s endpoint decreases.
          The slack at the repair moment of the first component is
          ``s - 2·min(δ₁, δ₂)``, and tightening happens ``s - min(δ₁, δ₂)``
          after the current clock.  Fire at ``clock + s - min(δ₁, δ₂)``.
        - If ``s ≥ δ₁ + δ₂``: both components repair before the edge tightens;
          no event is scheduled.

        **Case B — ``v`` is increasing in another active component.**
        ``v``'s profit increases, widening the slack, so the edge can only
        tighten after ``other_vc`` is fully repaired (at ``clock + δ₂``), at
        which point ``v`` stops moving and the remaining slack is ``s + δ₂``.
        The edge then tightens at ``clock + δ₂ + (s + δ₂)`` only if
        ``s + δ₂ < δ₁`` (otherwise ``vc`` repairs first).  Fire at
        ``clock + s + δ₂`` when ``s + δ₂ < δ₁``.

        **Case C — ``v`` is not in any active component.**
        Slack decreases at rate 1 (only ``u`` is moving).  Schedule a tight-
        edge event at ``clock + s`` if ``s < δ₁``.

        Only events that would fire strictly before ``vc`` is fully repaired
        are scheduled; all others are omitted because they will be recreated
        (if still relevant) after the repair event fires.
        """
        events = []
        delta = vc.rotation_to_fully_repair(self.imp)
        for u in vc.decreasing_vertices:
            for v in self.graph.neighbors_of(u).difference(vc.vertices):
                edge = s(u, v)
                if edge in self.clf.subpar_edges:
                    slack = self.imp.slack(self.graph, *edge)
                    if any(v in other_vc.decreasing_vertices for other_vc in self.active):
                        # Case A: both endpoints decreasing — slack falls at rate 2.
                        [other_vc] = [other_vc for other_vc in self.active if v in other_vc.decreasing_vertices]
                        delta2 = other_vc.rotation_to_fully_repair(self.imp)
                        if slack <= 2 * min(delta, delta2):
                            LOGGER.info("Detected tight edge event for %s between %s and %s (slack=%s, delta1=%s, delta2=%s). Both profits are decreasing and the slack is smaller than two times the smaller delta", edge, vc, other_vc, slack, delta, delta2)
                            ev = TightEdgeEvent(self.clock + slack / 2, edge, vc)
                            events.append(ev)
                        elif slack < delta + delta2:
                            LOGGER.info("Detected tight edge event for %s between %s and %s (slack=%s, delta1=%s, delta2=%s). Both profits are decreasing and the slack is between two times the smaller delta and the sum of both deltas", edge, vc, other_vc, slack, delta, delta2)
                            ev = TightEdgeEvent(self.clock + slack - min(delta, delta2), edge, vc)
                            events.append(ev)
                    elif any(v in other_vc.increasing_vertices for other_vc in self.active):
                        # Case B: v is increasing — slack grows until other_vc repairs, then falls.
                        [other_vc] = [other_vc for other_vc in self.active if v in other_vc.increasing_vertices]
                        delta2 = other_vc.rotation_to_fully_repair(self.imp)
                        if slack + delta2 < delta:
                            LOGGER.info("Detected tight edge event for %s between %s and %s (slack=%s, delta1=%s, delta2=%s). The other endpoint is increasing, but it will stop being increasing before the first component is fully repaired, and the slack is smaller than the time until that happens", edge, vc, other_vc, slack, delta, delta2)
                            ev = TightEdgeEvent(self.clock + slack + delta2, edge, vc)
                            events.append(ev)
                    elif slack < delta:
                        # Case C: v is static — slack falls at rate 1.
                        LOGGER.info("Detected tight edge event for %s from %s (slack=%s, delta=%s). The other endpoint is not in active, and the slack is smaller than the time until the component is fully repaired", edge, vc, slack, delta)
                        ev = TightEdgeEvent(self.clock + slack, edge, vc)
                        events.append(ev)
        return events

    def _add_remainders_to_bin(self, vc: ValidComponent, min_sub: ValidComponent) -> None:
        """Decompose residual FCs and schedule their bin activation events."""
        remainder_fcs = vc.decompose_remainder(min_sub)
        LOGGER.info("Adding %s to bin set", remainder_fcs)
        for fc in remainder_fcs:
            self.bin_set.add(fc)
            ev = BinActivationEvent(fc.min_profit(self.imp), fc)
            self._push_event(ev)

    def _get_fundamental_components(self) -> list[FundamentalComponent]:
        """Decompose graph into connected components using DFS. Only essential and viable edges are traversed."""
        visited = set()
        components = []

        def dfs(u: int) -> frozenset[int]:
            reachable = frozenset([u])
            neighbors = [
                v for v in self.graph.neighbors_of(u)
                if v not in visited and (s(u, v) in self.clf.essential_edges or s(u, v) in self.clf.viable_edges)
            ]
            for v in neighbors:
                visited.add(v)
                reachable |= dfs(v)
            return reachable

        for vertex in self.graph.vertices:
            if vertex not in visited:
                components.append(dfs(vertex))

        fcs = []
        for component in components:
            if all(vertex in self.clf.essential_u | self.clf.essential_v for vertex in component):
                # If all vertices in the component are essential, then it is a fundamental component
                fcs.append(
                    FundamentalComponent(
                        U=component.intersection(self.clf.essential_u),
                        V=component.intersection(self.clf.essential_v)
                    )
                )
        LOGGER.debug("Computed %d fundamental components", len(fcs))
        return fcs
