from collections.abc import Collection
from typing import TypeVar, Generator
from itertools import chain, combinations

T = TypeVar('T')

def set_u_vertices(n_u: int) -> frozenset[int]:
    """Return U-side vertex ids in the repository convention."""
    return frozenset(range(n_u))

def set_v_vertices(n_u: int, n_v: int) -> frozenset[int]:
    """Return V-side vertex ids directly after U ids."""
    return frozenset(range(n_u, n_u + n_v))

def s(u: int, v: int) -> tuple[int, int]:
    """Return edge tuple in the repository convention."""
    return (u, v) if u < v else (v, u)

def subsets(collection: Collection[T]) -> Generator[tuple[T, ...], None, None]:
    """Return all subsets of the given set."""
    yield from chain.from_iterable(combinations(collection, size) for size in range(len(collection) + 1))