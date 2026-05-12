"""Event-driven solver for computing a leximin core imputation."""

import heapq
from collections.abc import Callable
from components import FundamentalComponent, ValidComponent
from classification import classify
from events import BinActivationEvent, FullyRepairedEvent, TightEdgeEvent, Event
from fractions import Fraction
from graph import BipartiteGraph
from imputation import Imputation, compute_imputation
from itertools import count
from matching import max_weight_matching

class LeximinSolver:
    """Run Algorithm 1 style event processing until no event remains."""

    def __init__(self, graph: BipartiteGraph, imp: Imputation = None):
        """Initialize solver state from graph classification and initial imputation."""
        self.graph = graph
        self.clf = classify(graph)

        self.bin_set: set[FundamentalComponent] = set()
        self.active: set[ValidComponent] = set()
        self.frozen: set[int] = set()
        self.fully_repaired: set[int] = set()

        self.imp: Imputation = imp or compute_imputation(graph, max_weight_matching(graph))
        self.clock: Fraction = Fraction(0)
        self.pq: list[tuple[Fraction, int, int, Event]] = []
        self.seq = count()

    def solve(self) -> Imputation:
        """Execute the event loop and return the final imputation."""
        self._initialize()
        while self.pq:
            event = self._pop_event()
            if not self._is_stale(event):
                self._advance_clock_to(event.clock)
                self._dispatch(event)
        return self.imp

    def _initialize(self):
        """Seed bins with essential edges and schedule first activations."""
        for u, v in self.clf.essential_edges:
            fc = FundamentalComponent(u, v)
            self.bin_set.add(fc)
            ev = BinActivationEvent(fc.min_profit(self.imp), fc)
            self._push_event(ev)

    def _push_event(self, event: Event):
        """Push event into priority queue with deterministic tie-breaking."""
        heapq.heappush(self.pq, (event.clock, event.priority, next(self.seq), event))

    def _pop_event(self) -> Event:
        """Pop the next event from priority queue."""
        return heapq.heappop(self.pq)[-1]

    def _is_stale(self, event: Event) -> bool:
        """Return True when event references state that is no longer active."""
        if isinstance(event, BinActivationEvent):
            return event.fc not in self.bin_set
        elif isinstance(event, TightEdgeEvent):
            return event.source_vc not in self.active
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
        self._schedule_events_for(vc)

    def _on_fully_repaired(self, event: FullyRepairedEvent) -> None:
        """Finalize one valid component and return its remainders to bins."""
        vc = event.vc
        self.active.remove(vc)
        min_sub = vc.compute_min_sub1(self.imp)
        remainder_fcs = vc.decompose_remainder(min_sub)
        self.fully_repaired.update(min_sub.vertices)
        for fc in remainder_fcs:
            self.bin_set.add(fc)
            ev = BinActivationEvent(clock=fc.min_profit(self.imp), fc=fc)
            self._push_event(ev)

    def _on_tight_edge(self, event: TightEdgeEvent) -> None:
        """Handle a tight subpar edge according to current status of its endpoint."""
        source_vc = event.source_vc
        i, j = event.edge if event.edge[0] in source_vc.vertices else event.edge[::-1]
        self.active.remove(source_vc)

        if j in self.frozen:
            min_sub = source_vc.compute_min_sub3(i)
            self.frozen.update(min_sub.vertices)
            self._add_remainders_to_bin(source_vc, min_sub)

        elif j in self.fully_repaired:
            min_sub = source_vc.compute_min_sub3(i)
            self.fully_repaired.update(min_sub.vertices)
            self._add_remainders_to_bin(source_vc, min_sub)

        elif any(j in vc.vertices for vc in self.active):
            [other_vc] = [vc for vc in self.active if j in vc.vertices]
            self.active.remove(other_vc)
            source_min_sub, other_min_sub = source_vc.compute_min_sub2(other_vc, i, j)
            self.fully_repaired.update(source_min_sub.vertices | other_min_sub.vertices)
            self._add_remainders_to_bin(source_vc, source_min_sub)
            self._add_remainders_to_bin(other_vc, other_min_sub)

        else:
            # Endpoint `j` is still in a bin; absorb that FC as a child and continue.
            [fc] = [fc for fc in self.bin_set if j in fc.vertices]
            self.bin_set.remove(fc)
            new_vc = source_vc.add_child_at(i, fc)
            self.active.add(new_vc)
            self._schedule_events_for(new_vc)

    def _schedule_events_for(self, vc: ValidComponent) -> None:
        """Schedule full-repair and tight-edge events for an active component."""
        if vc.rotation == 'CW':
            delta = abs(self.imp.profit(vc.root.u) - vc.min_profit_on_right(self.imp)) / 2
        else:
            delta = abs(self.imp.profit(vc.root.v) - vc.min_profit_on_left(self.imp)) / 2
        ev = FullyRepairedEvent(self.clock + delta, vc)
        self._push_event(ev)
        for u in vc.decreasing_vertices:
            for v in self.graph.neighbors_of(u).difference(vc.vertices):
                edge = (u, v) if u < v else (v, u)
                if edge in self.clf.subpar_edges:
                    slack = self.imp.slack(self.graph, *edge)
                    if any(v in other_vc.decreasing_vertices for other_vc in self.active):
                        # The other endpoint is also decreasing
                        [other_vc] = [other_vc for other_vc in self.active if v in other_vc.decreasing_vertices]
                        delta2 = other_vc.rotation_to_fully_repair(self.imp)
                        if slack <= 2*min(delta, delta2):
                            # Both components are being repaired, so slack decreases at rate 2
                            # If it is less than two times the smaller delta, then the edge will become tight before
                            # either component is fully repaired
                            ev = TightEdgeEvent(self.clock + slack / 2, edge, vc)
                            self._push_event(ev)
                        elif slack < min(delta, delta2) + max(delta, delta2):
                            # Max is the min plus the positive difference, so it is checking if slack is less than two
                            # times the smaller delta but more than two times the smaller delta plus the positive
                            # difference
                            ev = TightEdgeEvent(self.clock + slack - min(delta, delta2), edge, vc)
                            self._push_event(ev)
                    elif slack < delta:
                        ev = TightEdgeEvent(self.clock + slack, edge, vc)
                        self._push_event(ev)

    def _add_remainders_to_bin(self, vc: ValidComponent, min_sub: ValidComponent) -> None:
        """Decompose residual FCs and schedule their bin activation events."""
        remainder_fcs = vc.decompose_remainder(min_sub)
        for fc in remainder_fcs:
            self.bin_set.add(fc)
            ev = BinActivationEvent(fc.min_profit(self.imp), fc)
            self._push_event(ev)

    def _dfs_decomposition(self) -> list[set[int]]:
        """Decompose graph into connected components using DFS. Only essential and viable edges are traversed."""
        visited = set()
        components = []

        def dfs(u: int) -> set[int]:
            reachable = {u}
            s: Callable[[int, int], tuple[int, int]] = lambda x, y: (x, y) if x < y else (y, x)
            neighbors = [
                v for v in self.graph.neighbors_of(u)
                if v not in visited and (s(u, v) in self.clf.essential_edges or s(u, v) in self.clf.subpar_edges)
            ]
            for v in neighbors:
                visited.add(v)
                reachable.update(dfs(v))
            return reachable


        for vertex in self.graph.vertices:
            if vertex not in visited:
                components.append(dfs(vertex))
        return components