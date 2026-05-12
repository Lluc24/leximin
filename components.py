"""Component abstractions used by the event-driven leximin solver."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from fractions import Fraction
from itertools import count

from imputation import Imputation

_uid_gen = count(1)


@dataclass(eq=False, frozen=True)
class Component(ABC):
    """Abstract base for component trees tracked by the solver."""

    uid: int = field(default_factory=lambda: next(_uid_gen), init=False, compare=False)

    @property
    @abstractmethod
    def left(self) -> frozenset[int]:
        ...

    @property
    @abstractmethod
    def right(self) -> frozenset[int]:
        ...

    @property
    def vertices(self) -> frozenset[int]:
        """Return all vertices present in the component."""
        return self.left.union(self.right)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Component) and self.uid == other.uid

    def __hash__(self) -> int:
        return hash(self.uid)

    def copy(self, *, preserve_uid: bool = False) -> "Component":
        """Return a shallow dataclass copy, optionally preserving identifier."""
        new_obj = replace(self)
        if preserve_uid:
            object.__setattr__(new_obj, "uid", self.uid)
        return new_obj


@dataclass(frozen=True, eq=False)
class FundamentalComponent(Component):
    """A single essential edge `(u, v)` that seeds a valid component."""

    u: int
    v: int

    @property
    def left(self) -> frozenset[int]:
        return frozenset({self.u})

    @property
    def right(self) -> frozenset[int]:
        return frozenset({self.v})

    def has_min_on_left(self, imp: Imputation) -> bool:
        """Return True if the left endpoint has the minimum current profit."""
        return imp.profit(self.u) <= imp.profit(self.v)

    def has_min_on_right(self, imp: Imputation) -> bool:
        """Return True if the right endpoint has the minimum current profit."""
        return imp.profit(self.v) <= imp.profit(self.u)

    def has_min_equal(self, imp: Imputation) -> bool:
        """Return True when both endpoints have the same profit."""
        return imp.profit(self.u) == imp.profit(self.v)

    def min_profit(self, imp: Imputation) -> Fraction:
        """Return the lower endpoint profit."""
        return min(imp.profit(self.u), imp.profit(self.v))

    def rotation_to_fully_repair(self, imp: Imputation) -> Fraction:
        """Return the rotation needed to equalize endpoint profits."""
        return abs(imp.profit(self.u) - imp.profit(self.v)) / 2


@dataclass(frozen=True, eq=False)
class ValidComponent(Component):
    """A rooted tree of fundamental components with a common rotation direction."""

    root: FundamentalComponent
    rotation: str = 'CW'  # 'CW' or 'CCW'
    children: frozenset['ValidComponent'] = field(default_factory=frozenset)

    @property
    def left(self) -> frozenset[int]:
        return self.root.left.union(*(child.left for child in self.children))

    @property
    def right(self) -> frozenset[int]:
        return self.root.right.union(*(child.right for child in self.children))

    @property
    def all_fcs(self) -> frozenset[FundamentalComponent]:
        """Return every fundamental component in the tree."""
        return frozenset({self.root}).union(*(child.all_fcs for child in self.children))

    @property
    def increasing_vertices(self) -> frozenset[int]:
        """Return vertices whose profits increase during a rotation step."""
        return self.left if self.rotation == 'CW' else self.right

    @property
    def decreasing_vertices(self) -> frozenset[int]:
        """Return vertices whose profits decrease during a rotation step."""
        return self.right if self.rotation == 'CW' else self.left

    def min_profit_on_left(self, imp: Imputation) -> Fraction:
        """Return the minimum profit over left-side vertices."""
        return min(imp.profit(v) for v in self.left)

    def min_profit_on_right(self, imp: Imputation) -> Fraction:
        """Return the minimum profit over right-side vertices."""
        return min(imp.profit(v) for v in self.right)

    def rotation_to_fully_repair(self, imp: Imputation) -> Fraction:
        """Return the clock delta required to fully repair this component."""
        if self.rotation == 'CW':
            return abs(imp.profit(self.root.u) - self.min_profit_on_right(imp)) / 2
        else:
            return abs(imp.profit(self.root.v) - self.min_profit_on_left(imp)) / 2

    def add_child_at(self, vertex, fc: FundamentalComponent) -> 'ValidComponent':
        """Attach a new fundamental component below the fundamental component containing `vertex`."""
        if vertex in self.root.vertices:
            return ValidComponent(
                root=self.root,
                children=self.children.union({ValidComponent(root=fc, rotation=self.rotation)}),
                rotation=self.rotation
            )
        for child in self.children:
            if vertex in child.vertices:
                new_child = child.add_child_at(vertex, fc)
                return ValidComponent(
                    root=self.root,
                    children=self.children.difference({child}).union({new_child}),
                    rotation=self.rotation
                )
        raise ValueError(f"Vertex {vertex} is not in the component.")

    def compute_min_sub1(self, imp: Imputation) -> 'ValidComponent':
        """Return the minimal subtree for the full-repair event (Sub1)."""
        profit = imp.profit(self.root.u if self.rotation == 'CW' else self.root.v)
        fcs = {self.root}.union(self._get_descendants_with_profit(imp, profit))
        return self._compute_min_tree(fcs)

    def compute_min_sub2(self, other_vc: 'ValidComponent', i, j) -> 'tuple[ValidComponent, ValidComponent]':
        """Return minimal subtrees around tight-edge endpoints in two components (Sub2)."""
        [fc_self] = [fc for fc in self.all_fcs if (i in fc.vertices or j in fc.vertices)]
        [fc_other] = [fc for fc in other_vc.all_fcs if (i in fc.vertices or j in fc.vertices)]
        min_tree_self = self._compute_min_tree({fc_self})
        min_tree_other = other_vc._compute_min_tree({fc_other})
        return min_tree_self, min_tree_other

    def compute_min_sub3(self, vertex) -> 'ValidComponent':
        """Return the minimal subtree containing `vertex` (Sub3)."""
        [fc] = [fc for fc in self.all_fcs if vertex in fc.vertices]
        return self._compute_min_tree({fc})

    def decompose_remainder(self, min_sub: 'ValidComponent') -> frozenset[FundamentalComponent]:
        """Return remaining fundamental components outside a minimal subtree."""
        return self.all_fcs.difference(min_sub.all_fcs)

    def _get_descendants_with_profit(self, imp, profit) -> set[FundamentalComponent]:
        """Collect descendants whose opposite endpoint matches the target profit."""
        fcs = set()
        if self.rotation == 'CW' and imp.profit(self.root.v) == profit:
            fcs.add(self.root)
        elif self.rotation == 'CCW' and imp.profit(self.root.u) == profit:
            fcs.add(self.root)
        return fcs.union(*(c._get_descendants_with_profit(imp, profit) for c in self.children))

    def _compute_min_tree(self, fcs: set[FundamentalComponent]) -> 'ValidComponent | None':
        """Build the smallest subtree that keeps exactly the requested FCs as anchors."""
        # Keep a child only when it contains at least one selected fundamental component.
        children = frozenset(filter(None, [c._compute_min_tree(fcs) for c in self.children]))
        if self.root in fcs or children:
            return ValidComponent(root=self.root, children=children, rotation=self.rotation)
        return None
