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
        return self._min_profit_left(imp) <= self._min_profit_right(imp)

    def has_min_on_right(self, imp) -> bool:
        return self._min_profit_right(imp) <= self._min_profit_left(imp)

    def has_min_equal(self, imp) -> bool:
        return self._min_profit_left(imp) == self._min_profit_right(imp)

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


    def _min_profit_left(self, imp) -> Fraction:
        return min([imp.profit(self.root.u)] + [child._min_profit_left(imp) for child in self.children])

    def _min_profit_right(self, imp) -> Fraction:
        return min([imp.profit(self.root.v)] + [child._min_profit_right(imp) for child in self.children])
