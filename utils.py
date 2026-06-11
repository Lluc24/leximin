"""Shared utility helpers used across the leximin solver and auxiliary scripts.

Vertex-ID convention
--------------------
U-side vertices are assigned IDs ``0, 1, ..., n_u - 1``.
V-side vertices are assigned IDs ``n_u, n_u + 1, ..., n_u + n_v - 1``.
This non-overlapping integer scheme lets both sides live in a single set
without collisions, while keeping edge tuples always in the form ``(u, v)``
with ``u < v``.
"""

import pathlib
from collections.abc import Collection
from typing import TypeVar, Generator
from itertools import chain, combinations
import logging
import sys

T = TypeVar('T')


def set_u_vertices(n_u: int) -> frozenset[int]:
    """Return the frozenset of U-side vertex IDs ``{0, …, n_u - 1}``."""
    return frozenset(range(n_u))


def set_v_vertices(n_u: int, n_v: int) -> frozenset[int]:
    """Return the frozenset of V-side vertex IDs ``{n_u, …, n_u + n_v - 1}``.

    Starting at ``n_u`` ensures U and V ID spaces are disjoint.
    """
    return frozenset(range(n_u, n_u + n_v))


def s(u: int, v: int) -> tuple[int, int]:
    """Return a canonical edge tuple with the smaller ID first.

    All edge dicts and frozensets in this codebase store edges as
    ``(min_id, max_id)`` so that ``(u, v)`` and ``(v, u)`` map to the same
    key.  Use this helper whenever constructing or looking up an edge.
    """
    return (u, v) if u < v else (v, u)


def subsets(collection: Collection[T]) -> Generator[tuple[T, ...], None, None]:
    """Yield every subset of ``collection``, including the empty set.

    Used by ``BipartiteGraph.is_imputation_in_core`` for exhaustive coalition
    enumeration (exponential — only practical for small graphs).
    """
    yield from chain.from_iterable(combinations(collection, size) for size in range(len(collection) + 1))


def setup_logger(log_file: pathlib.Path) -> None:
    """Configure the root logger to write INFO-level output to a file and stdout.

    Replaces any existing handlers so that repeated calls (e.g., from the
    test suite) do not accumulate duplicate handlers.
    """
    log_file.parent.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear stale handlers before attaching fresh ones.
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    logger.info(f"The messages will go both to {log_file} and stdout.")
    logger.info("Logger is set up.")