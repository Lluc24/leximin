from dataclasses import dataclass, field
from fractions import Fraction
from imputation import Imputation

@dataclass(frozen=True)
class FundamentalComponent:
    u: int
    v: int

    @property
    def left(self) -> frozenset[int]:
        return frozenset({self.u})

    @property
    def right(self) -> frozenset[int]:
        return frozenset({self.v})

    @property
    def vertices(self) -> frozenset[int]:
        return self.left.union(self.right)

    def has_min_on_left(self, imp: Imputation) -> bool:
        return imp.profit(self.u) <= imp.profit(self.v)

    def has_min_on_right(self, imp: Imputation) -> bool:
        return imp.profit(self.v) <= imp.profit(self.u)

    def has_min_equal(self, imp: Imputation) -> bool:
        return imp.profit(self.u) == imp.profit(self.v)

    def min_profit(self, imp: Imputation) -> Fraction:
        return min(imp.profit(self.u), imp.profit(self.v))

    def rotation_to_fully_repair(self, imp: Imputation) -> Fraction:
        return abs(imp.profit(self.u) - imp.profit(self.v)) / 2

    def __repr__(self):
        return f"FC({self.u}, {self.v})"


@dataclass(frozen=True)
class ValidComponent:
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
    def vertices(self) -> frozenset[int]:
        return self.left.union(self.right)

    @property
    def all_fcs(self) -> frozenset[FundamentalComponent]:
        return frozenset({self.root}).union(*(child.all_fcs for child in self.children))

    @property
    def increasing_vertices(self) -> frozenset[int]:
        return self.left if self.rotation == 'CW' else self.right
    @property
    def decreasing_vertices(self) -> frozenset[int]:
        return self.right if self.rotation == 'CW' else self.left

    def min_profit_on_left(self, imp: Imputation) -> Fraction:
        return min(imp.profit(v) for v in self.left)

    def min_profit_on_right(self, imp: Imputation) -> Fraction:
        return min(imp.profit(v) for v in self.right)

    def rotation_to_fully_repair(self, imp: Imputation) -> Fraction:
        if self.rotation == 'CW':
            return abs(imp.profit(self.root.u) - self.min_profit_on_right(imp)) / 2
        else:
            return abs(imp.profit(self.root.v) - self.min_profit_on_left(imp)) / 2

    def add_child_at(self, vertex, fc: FundamentalComponent) -> 'ValidComponent':
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
        profit = imp.profit(self.root.u if self.rotation == 'CW' else self.root.v)
        fcs = {self.root}.union(self._get_descendants_with_profit(imp, profit))
        return self._compute_min_tree(fcs)

    def compute_min_sub2(self, other_vc: 'ValidComponent', i, j) -> 'tuple[ValidComponent, ValidComponent]':
        [fc_self] = [fc for fc in self.all_fcs if (i in fc.vertices or j in fc.vertices)]
        [fc_other] = [fc for fc in other_vc.all_fcs if (i in fc.vertices or j in fc.vertices)]
        min_tree_self = self._compute_min_tree({fc_self})
        min_tree_other = other_vc._compute_min_tree({fc_other})
        return min_tree_self, min_tree_other

    def compute_min_sub3(self, vertex) -> 'ValidComponent':
        [fc] = [fc for fc in self.all_fcs if vertex in fc.vertices]
        return self._compute_min_tree({fc})

    def decompose_remainder(self, min_sub: 'ValidComponent') -> frozenset[FundamentalComponent]:
        return self.all_fcs.difference(min_sub.all_fcs)

    def _get_descendants_with_profit(self, imp, profit) -> set[FundamentalComponent]:
        fcs = set()
        if self.rotation == 'CW' and imp.profit(self.root.v) == profit:
            fcs.add(self.root)
        elif self.rotation == 'CCW' and imp.profit(self.root.u) == profit:
            fcs.add(self.root)
        return fcs.union(*(c._get_descendants_with_profit(imp, profit) for c in self.children))

    def _compute_min_tree(self, fcs: set[FundamentalComponent]) -> 'ValidComponent | None':
        children = frozenset(filter(None, [c._compute_min_tree(fcs) for c in self.children]))
        if self.root in fcs or children:
            return ValidComponent(root=self.root, children=children, rotation=self.rotation)
        return None

    def __repr__(self):
        return f"VC(root={self.root}, rotation={self.rotation}, children={self.children})"