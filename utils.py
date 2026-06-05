import pathlib
from collections.abc import Collection
from typing import TypeVar, Generator
from itertools import chain, combinations
import logging
import sys

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

def setup_logger(log_file: pathlib.Path) -> None:
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

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    else:
        logger.handlers.clear()
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    logger.info(f"The messages will go both to {log_file} and stdout.")
    logger.info("Logger is set up.")