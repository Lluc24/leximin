from collections.abc import Callable

from components import FundamentalComponent


def set_u_vertices(n_u: int) -> frozenset[int]:
    """Return U-side vertex ids in the repository convention."""
    return frozenset(range(n_u))

def set_v_vertices(n_u: int, n_v: int) -> frozenset[int]:
    """Return V-side vertex ids directly after U ids."""
    return frozenset(range(n_u, n_u + n_v))

def s(u: int, v: int) -> tuple[int, int]:
    """Return edge tuple in the repository convention."""
    return (u, v) if u < v else (v, u)
