"""Component abstractions used by the event-driven leximin solver.

The solver maintains a forest of *valid components*, each of which is a
rooted tree of *fundamental components* (FCs) connected by legitimate tight
subpar edges.  Two classes implement this hierarchy:

``FundamentalComponent``
    A single connected component of the essential/viable-edge subgraph ``H₀``
    whose vertices are all essential.  In the non-degenerate case each FC is a
    single essential edge; in the degenerate case it may span multiple vertices
    linked by viable edges.

``ValidComponent``
    A rooted tree of FCs.  The root FC drives the rotation direction: CW
    (left profits increase, right decrease) when the root's minimum profit is
    on the left side, CCW otherwise.  Children are attached when a tight
    subpar edge legitimately connects an ACTIVE component to a BIN component
    (Definition 20 of Vazirani 2025).

Both classes are *frozen dataclasses* — every structural change (child
attachment, sub-component extraction) produces a new instance rather than
mutating the existing one.  Component identity is tracked via a per-instance
``uid`` integer rather than by value equality, because two structurally
identical components at different points in the algorithm are distinct objects.
"""

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

    def __repr__(self):
        return f"FC({set(self.U)}, {set(self.V)})"


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
        """Return the rotation amount ``δ`` needed to fully repair this component.

        Full repair means the minimum profit on both sides of the *root* FC
        are equal.  For a CW rotation the left side increases and the right
        side decreases at unit rate, so both sides converge in ``δ`` steps where
        ``min_right - min_left = 2δ``.  Symmetrically for CCW.

        Only the root's minimum profits determine the repair time because the
        tree invariant guarantees that the root always has the current overall
        minimum (Vazirani 2025, Definition 19, item 2).
        """
        if self.rotation == 'CW':
            return (self.min_right(imp) - self.root.min_left(imp)) / 2
        else:
            return (self.min_left(imp) - self.root.min_right(imp)) / 2

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

    def add_child_at(self, vertex: int, fc: FundamentalComponent) -> 'ValidComponent':
        """Return a new component with ``fc`` attached as a child of the FC that contains ``vertex``.

        The new child inherits the same rotation direction as this component,
        which preserves the single-rotation-per-tree invariant of valid components
        (Vazirani 2025, Definition 19, item 1).  The method recurses down the
        tree until the FC that owns ``vertex`` is found.
        """
        if vertex in self.root.vertices:
            new_vc = ValidComponent(root=fc, rotation=self.rotation)
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
        """Return the minimal sub-component (Min-Sub1) for the full-repair event.

        At the moment of full repair the root's lower side has reached parity
        with the opposite side.  Min-Sub1 is the smallest subtree containing
        the root and every child FC whose opposite-side minimum also equals the
        root's lower-side profit.  These are exactly the FCs that cannot be
        improved further without violating tightness of already-tight edges.
        The remaining FCs are decomposed and returned to BIN for further repair.
        """
        if self.rotation == 'CW':
            profit = self.min_left(imp)
            fcs = {fc for fc in self.get_fcs() if fc.min_right(imp) == profit}
        else:
            profit = self.min_right(imp)
            fcs = {fc for fc in self.get_fcs() if fc.min_left(imp) == profit}
        return self._compute_min_tree(fcs | {self.root})

    def compute_min_sub2(self, other_vc: 'ValidComponent', i: int, j: int) -> 'tuple[ValidComponent, ValidComponent]':
        """Return the pair of minimal sub-components (Min-Sub2) for a tight-edge merge.

        When a tight subpar edge ``(i, j)`` links two ACTIVE components, only
        the sub-path from each component's root to the FC containing the edge
        endpoint is moved to FULLY-REPAIRED.  This is the minimal structure
        needed to enforce the legitimacy of ``(i, j)``.
        """
        [fc_self] = [fc for fc in self.get_fcs() if (i in fc.vertices or j in fc.vertices)]
        [fc_other] = [fc for fc in other_vc.get_fcs() if (i in fc.vertices or j in fc.vertices)]
        min_tree_self = self._compute_min_tree({fc_self})
        min_tree_other = other_vc._compute_min_tree({fc_other})
        return min_tree_self, min_tree_other

    def compute_min_sub3(self, vertex: int) -> 'ValidComponent':
        """Return the minimal sub-component (Min-Sub3) containing ``vertex``.

        Used when a tight subpar edge connects an ACTIVE component to a FROZEN
        or FULLY-REPAIRED vertex.  Only the sub-path from the root to the FC
        owning ``vertex`` is moved (to FROZEN or FULLY-REPAIRED, matching the
        destination of the opposite endpoint).
        """
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

    def __repr__(self):
        return f"VC({self.root} | {self.rotation} | children={set(self.children)})"
