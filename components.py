"""Component abstractions used by the event-driven leximin solver."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import count
from imputation import Imputation

_uid_gen = count(1)


@dataclass(frozen=True)
class Component(ABC):
    """Abstract base for component trees tracked by the solver."""

    uid: int = field(default_factory=lambda: next(_uid_gen))

    @property
    @abstractmethod
    def left(self) -> frozenset[int]:
        """Return the left-side vertices in this component."""
        ...

    @property
    @abstractmethod
    def right(self) -> frozenset[int]:
        """Return the right-side vertices in this component."""
        ...

    @abstractmethod
    def structural_eq(self, other: 'Component') -> bool:
        """Return True when two components have the same structure and rotation."""
        ...

    @property
    def vertices(self) -> frozenset[int]:
        """Return all vertices in this component."""
        return self.left | self.right

    def min_left(self, imp: Imputation) -> Fraction:
        """Return the minimum profit on the left side."""
        return min(imp.profits[u] for u in self.left)

    def min_right(self, imp: Imputation) -> Fraction:
        """Return the minimum profit on the right side."""
        return min(imp.profits[v] for v in self.right)

    def has_min_on_left(self, imp: Imputation) -> bool:
        """Return True if the left side has the minimum current profit."""
        return self.min_left(imp) <= self.min_right(imp)

    def min_profit(self, imp: Imputation) -> Fraction:
        """Return the lower side profit."""
        return min(self.min_left(imp), self.min_right(imp))

    def __hash__(self):
        return hash(self.uid)


@dataclass(frozen=True)
class FundamentalComponent(Component):
    """A single fundamental component that seeds a valid component."""

    U: frozenset[int] = field(default_factory=frozenset)
    V: frozenset[int] = field(default_factory=frozenset)

    @property
    def left(self) -> frozenset[int]:
        """Return the left-side vertices in this component."""
        return self.U

    @property
    def right(self) -> frozenset[int]:
        """Return the right-side vertices in this component."""
        return self.V

    def structural_eq(self, other: 'FundamentalComponent') -> bool:
        """Return True when two fundamental components have the same vertex sets."""
        return isinstance(other, FundamentalComponent) and self.left == other.left and self.right == other.right


@dataclass(frozen=True)
class ValidComponent(Component):
    """A rooted tree of fundamental components with a common rotation direction."""

    root: FundamentalComponent = field(default_factory=FundamentalComponent)
    rotation: str = 'CW'  # 'CW' or 'CCW'
    children: frozenset['ValidComponent'] = field(default_factory=frozenset)

    @property
    def left(self) -> frozenset[int]:
        """Return the left-side vertices in this component."""
        return self.root.left.union(*(child.left for child in self.children))

    @property
    def right(self) -> frozenset[int]:
        """Return the right-side vertices in this component."""
        return self.root.right.union(*(child.right for child in self.children))

    @property
    def increasing_vertices(self) -> frozenset[int]:
        """Return vertices whose profits increase during a rotation step."""
        return self.left if self.rotation == 'CW' else self.right

    @property
    def decreasing_vertices(self) -> frozenset[int]:
        """Return vertices whose profits decrease during a rotation step."""
        return self.right if self.rotation == 'CW' else self.left

    def rotation_to_fully_repair(self, imp: Imputation) -> Fraction:
        """Return the rotation amount until this component is fully repaired."""
        if self.rotation == 'CW':
            return (self.min_right(imp) - self.root.min_left(imp)) / 2
        else:
            return (self.min_left(imp) - self.root.min_right(imp)) / 2

    def rotation_to_fully_repair2(self, imp: Imputation) -> Fraction:
        return self.root.min_profit(imp) - self.min_profit(imp)

    def get_fcs(self) -> frozenset[FundamentalComponent]:
        """Return all fundamental components in this component."""
        return frozenset({self.root}).union(*(child.get_fcs() for child in self.children))

    def structural_eq(self, other: 'ValidComponent') -> bool:
        """Return True when two valid components have the same structure and rotation."""
        if not isinstance(other, ValidComponent):
            return False
        if self.rotation != other.rotation:
            return False
        if not self.root.structural_eq(other.root):
            return False
        if len(self.children) != len(other.children):
            return False
        for child in self.children:
            if not any(child.structural_eq(other_child) for other_child in other.children):
                return False
        return True

    def add_child_at(self, vertex, fc: FundamentalComponent) -> 'ValidComponent':
        """Attach a new fundamental component below the root containing `vertex`."""
        if vertex in self.root.vertices:
            new_vc = ValidComponent(
                root=fc,
                rotation=self.rotation,
            )
            return ValidComponent(
                root=self.root,
                children=self.children.union({new_vc}),
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
        if self.rotation == 'CW':
            profit = self.min_left(imp)
            fcs = {fc for fc in self.get_fcs() if fc.min_right(imp) == profit}
        else:
            profit = self.min_right(imp)
            fcs = {fc for fc in self.get_fcs() if fc.min_left(imp) == profit}
        return self._compute_min_tree(fcs | {self.root})

    def compute_min_sub2(self, other_vc: 'ValidComponent', i, j) -> 'tuple[ValidComponent, ValidComponent]':
        """Return minimal subtrees around tight-edge endpoints in two components (Sub2)."""
        [fc_self] = [fc for fc in self.get_fcs() if (i in fc.vertices or j in fc.vertices)]
        [fc_other] = [fc for fc in other_vc.get_fcs() if (i in fc.vertices or j in fc.vertices)]
        min_tree_self = self._compute_min_tree({fc_self})
        min_tree_other = other_vc._compute_min_tree({fc_other})
        return min_tree_self, min_tree_other

    def compute_min_sub3(self, vertex) -> 'ValidComponent':
        """Return the minimal subtree containing `vertex` (Sub3)."""
        [fc] = [fc for fc in self.get_fcs() if vertex in fc.vertices]
        return self._compute_min_tree({fc})

    def decompose_remainder(self, min_sub: 'ValidComponent') -> frozenset[FundamentalComponent]:
        """Return remaining fundamental components outside a minimal subtree."""
        return self.get_fcs().difference(min_sub.get_fcs())

    def _compute_min_tree(self, fcs: set[FundamentalComponent]) -> 'ValidComponent | None':
        """Build the smallest subtree that keeps exactly the requested FCs as anchors."""
        # Keep a child only when it contains at least one selected fundamental component.
        children = frozenset(filter(None, [c._compute_min_tree(fcs) for c in self.children]))
        if self.root in fcs or children:
            return ValidComponent(root=self.root, children=children, rotation=self.rotation)
        return None
