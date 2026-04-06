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


@dataclass(frozen=True)
class ValidComponent:
    root: FundamentalComponent
    children: frozenset['ValidComponent'] = field(default_factory=frozenset)

    def __contains__(self, vertex: int) -> bool:
        return vertex in self.left or vertex in self.right

    def increasing_vertices(self, imp) -> frozenset[int]:
        return self.left if self.has_min_on_left(imp) else self.right

    def decreasing_vertices(self, imp) -> frozenset[int]:
        return self.right if self.has_min_on_left(imp) else self.left

    @property
    def left(self) -> frozenset[int]:
        return self.root.left.union(*(child.left for child in self.children))

    @property
    def right(self) -> frozenset[int]:
        return self.root.right.union(*(child.right for child in self.children))

    @property
    def vertices(self) -> frozenset[int]:
        return self.left.union(self.right)

    def has_min_on_left(self, imp) -> bool:
        return self.min_profit_left(imp) <= self.min_profit_right(imp)

    def has_min_on_right(self, imp) -> bool:
        return self.min_profit_right(imp) <= self.min_profit_left(imp)

    def has_min_equal(self, imp) -> bool:
        return self.min_profit_left(imp) == self.min_profit_right(imp)

    def add_child_at(self, vertex, fc: FundamentalComponent) -> 'ValidComponent':
        if vertex in self.root.vertices:
            return ValidComponent(
                root=self.root,
                children=self.children.union({ValidComponent(root=fc)})
            )
        else:
            for child in self.children:
                if vertex in child.vertices:
                    new_child = child.add_child_at(vertex, fc)
                    return ValidComponent(
                        root=self.root,
                        children=self.children.difference({child}).union({new_child})
                    )
            raise ValueError(f"Vertex {vertex} is not in the component.")

    def min_profit(self, imp) -> Fraction:
        return min([imp.profit(u) for u in self.root.vertices] + [child.min_profit(imp) for child in self.children])

    def min_profit_left(self, imp) -> Fraction:
        return min([imp.profit(self.root.u)] + [child.min_profit_left(imp) for child in self.children])

    def min_profit_right(self, imp) -> Fraction:
        return min([imp.profit(self.root.v)] + [child.min_profit_right(imp) for child in self.children])

    def compute_min_sub1(self, imp) -> 'ValidComponent':
        fcs = self._get_fcs_with_profit(imp, self.min_profit(imp))
        def i_compute_min_sub1(vc: ValidComponent) -> ValidComponent | None:
            children = [i_compute_min_sub1(child) for child in vc.children]
            if vc.root in fcs or children:
                return ValidComponent(root=vc.root, children=frozenset(children))
            return None
        return i_compute_min_sub1(self)



    def decompose_remainder(self, min_sub: 'ValidComponent | None') -> set[FundamentalComponent]:
        if min_sub.root is self.root:
            return set().union(c1.decompose_remainder(c2) for c1, c2 in zip(self.children, min_sub.children))
        return {self.root}.union(c.decompose_remainder(None) for c in self.children)

    def _get_fcs_with_profit(self, imp, profit) -> set[FundamentalComponent]:
        fcs = set()
        if self.root.min_profit(imp) == profit:
            fcs.add(self.root)
        for child in self.children:
            fcs.update(child._get_fcs_with_profit(imp, profit))
        return fcs