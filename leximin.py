from components import FundamentalComponent, ValidComponent
from graph import BipartiteGraph
from classification import classify
from imputation import Imputation, compute_imputation
from fractions import Fraction
from matching import max_weight_matching
from events import BinActivationEvent, FullyRepairedEvent, TightEdgeEvent, Event
import heapq
from itertools import count

class LeximinSolver:
    def __init__(self, graph: BipartiteGraph):
        self.graph = graph
        self.clf = classify(graph)
        self.tight_graph = BipartiteGraph(
            u_vertices=graph.u_vertices,
            v_vertices=graph.v_vertices,
            weights={edge: graph.weight(*edge) for edge in self.clf.essential_edges}
        )

        self.bin_set: set[FundamentalComponent] = set()
        self.active: set[ValidComponent] = set()
        self.frozen: set[int] = set(self.clf.subpar_u | self.clf.subpar_v)
        self.fully_repaired: set[int] = set()

        self.imp: Imputation = compute_imputation(graph, max_weight_matching(graph))
        self.clock: Fraction = min(self.imp.profit(v) for v in self.clf.essential_vertices)
        self.pq: list[tuple[Fraction, int, int, Event]] = []
        self.seq = count()

    def solve(self) -> Imputation:
        self._initialize()
        while self.pq:
            event = self._pop_event()
            if not self._is_stale(event):
                self._advance_clock_to(event.clock)
                self._dispatch(event)
        return self.imp

    def _initialize(self):
        for u, v in self.clf.essential_edges:
            fc = FundamentalComponent(u, v)
            self.bin_set.add(fc)
            ev = BinActivationEvent(fc.min_profit(self.imp), fc)
            self._push_event(ev)

    def _push_event(self, event: Event):
        heapq.heappush(self.pq, (event.clock, event.priority, next(self.seq), event))

    def _pop_event(self) -> Event:
        return heapq.heappop(self.pq)[-1]

    def _is_stale(self, event: Event) -> bool:
        if isinstance(event, BinActivationEvent):
            return event.fc not in self.bin_set
        elif isinstance(event, TightEdgeEvent):
            return event.source_vc not in self.active
        else:
            return event.vc not in self.active

    def _advance_clock_to(self, new_clock: Fraction):
        delta = new_clock - self.clock
        if delta > 0:
            for vc in self.active:
                self.imp.apply_rotation(
                    increasing=vc.increasing_vertices(self.imp),
                    decreasing=vc.decreasing_vertices(self.imp),
                    delta=delta
                )
            self.clock = new_clock

    def _dispatch(self, event: Event) -> None:
        if isinstance(event, BinActivationEvent):
            self._on_bin_activation(event)
        elif isinstance(event, FullyRepairedEvent):
            self._on_fully_repaired(event)
        elif isinstance(event, TightEdgeEvent):
            self._on_tight_edge(event)

    def _on_bin_activation(self, event: BinActivationEvent) -> None:
        pass


"""
def solver(bip: BipartiteGraph):



    while bin_set | active:
        _, _, _, event = heapq.heappop(pq)

        delta = event.clock - clock
        if delta > 0:
            for vc in active:
                imp.apply_rotation(
                    increasing=vc.increasing_vertices(imp),
                    decreasing=vc.decreasing_vertices(imp),
                    delta=delta
                )
            clock = event.clock

        if isinstance(event, BinActivationEvent) and event.fc in bin_set:
            bin_set.remove(event.fc)
            if event.fc.has_min_equal(imp):
                fully_repaired |= event.fc.vertices
            else:
                new_vc = ValidComponent(root=event.fc)
                active.add(new_vc)
                candidates = new_vc.right if event.fc.has_min_on_left(imp) else new_vc.left
                for u in candidates:
                    for v in bip.neighbors_of(u):
                        if v not in frozen | fully_repaired:
                            margin = bip.weight(u, v) - imp.profit(u) - imp.profit(v)
                            ev = TightEdgeEvent(clock + margin, (u, v), new_vc)
                            push_event(ev)
                margin = abs(imp.profit(event.fc.u) - imp.profit(event.fc.v)) / 2
                ev = FullyRepairedEvent(clock + margin, new_vc)
                push_event(ev)

        elif isinstance(event, TightEdgeEvent) and event.source_vc in active:
            u, v = event.edge
            active.remove(event.source_vc)

            if v in frozen:
                sub_vc = min_sub3(event.source_vc)
                fcs = get_fcs_of_deleting(event.source_vc, sub_vc)
                frozen.add(sub_vc.vertices)
                for fc in fcs:
                    bin_set.add(fc)
                    ev = BinActivationEvent(fc.min_profit(imp), fc)
                    push_event(ev)
            elif v in fully_repaired:
                sub_vc = min_sub3(event.source_vc)
                fcs = get_fcs_of_deleting(event.source_vc, sub_vc)
                fully_repaired.add(sub_vc.vertices)
                for fc in fcs:
                    bin_set.add(fc)
                    ev = BinActivationEvent(fc.min_profit(imp), fc)
                    push_event(ev)
            elif any(v in vc.vertices for vc in active):
                sub_vc = min_sub2(event.source_vc)
                fcs = get_fcs_of_deleting(event.source_vc, sub_vc)
                fully_repaired.add(sub_vc.vertices)
                for fc in fcs:
                    bin_set.add(fc)
                    ev = BinActivationEvent(fc.min_profit(imp), fc)
                    push_event(ev)
            else:
                [fc] = [fc for fc in bin_set if v in fc.vertices]
                bin_set.remove(fc)
                new_vc = event.source_vc.add_child_at(u, fc)
                active.add(new_vc)
                u = fc.u if fc.has_min_on_left(imp) else fc.v
                for v in bip.neighbors_of(u):
                    if v not in frozen | fully_repaired:
                        margin = bip.weight(u, v) - imp.profit(u) - imp.profit(v)
                        ev = TightEdgeEvent(clock + margin, (u, v), new_vc)
                        push_event(ev)


        elif isinstance(event, FullyRepairedEvent) and event.vc in active:
                active.remove(event.vc)
                sub_vc = min_sub1(event.vc)
                fcs = get_fcs_of_deleting(event.vc, sub_vc)
                fully_repaired.add(sub_vc.vertices)
                bin_set |= fcs


"""
