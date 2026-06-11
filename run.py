"""CLI driver for running the leximin solver on a single graph.

Usage
-----
::

    python run.py --n-u <N_U> --n-v <N_V> --edges <u1> <v1> <w1> [<u2> <v2> <w2> ...]

Example
-------
::

    python run.py --n-u 2 --n-v 2 --edges 0 2 5 0 3 3 1 2 4 1 3 2

Vertex IDs
----------
U-side vertices are ``0, …, N_U - 1``; V-side vertices are
``N_U, …, N_U + N_V - 1``.  Edge weights may be integers or fractions
(e.g. ``3/2``).
"""

import pathlib
import argparse
from fractions import Fraction
from graph import BipartiteGraph
from leximin import LeximinSolver
from utils import set_u_vertices, set_v_vertices, setup_logger


def parse_edges(flat: list[str]) -> dict[tuple[int, int], Fraction]:
    """Parse a flat list of tokens ['u', 'v', 'w', ...] into a weight dict."""
    if len(flat) % 3 != 0:
        raise argparse.ArgumentTypeError(f"--edges requires triples of 'u v w'; got {len(flat)} token(s).")
    weights = {}
    for i in range(0, len(flat), 3):
        u, v, w = int(flat[i]), int(flat[i + 1]), Fraction(flat[i + 2])
        weights[(u, v)] = w
    return weights


def build_graph(args: argparse.Namespace) -> BipartiteGraph:
    """Construct a BipartiteGraph from parsed CLI arguments."""
    u_vertices = set_u_vertices(args.n_u)
    v_vertices = set_v_vertices(args.n_u, args.n_v)
    weights = parse_edges(args.edges)

    unknown = {u for u, _ in weights} - u_vertices
    unknown |= {v for _, v in weights} - v_vertices
    if unknown:
        raise ValueError(f"Edge endpoints not covered by --n-u/--n-v: {unknown}")

    return BipartiteGraph(
        u_vertices=u_vertices,
        v_vertices=v_vertices,
        weights=weights,
    )


def main() -> None:
    log_file = pathlib.Path("logs", "run.log")
    setup_logger(log_file)
    parser = argparse.ArgumentParser(
        description="Run the leximin core-imputation solver on a bipartite graph.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python run.py --n-u 2 --n-v 2 --edges 0 2 5 0 3 3 1 2 4 1 3 2"
        ),
    )

    parser.add_argument(
        "--n-u",
        type=int,
        required=True,
        metavar="N",
        help="Number of U-side vertices (ids 0 … N-1).",
    )
    parser.add_argument(
        "--n-v",
        type=int,
        required=True,
        metavar="N",
        help="Number of V-side vertices (ids n_u … n_u+N-1).",
    )
    parser.add_argument(
        "--edges",
        nargs="+",
        required=True,
        metavar="TOKEN",
        help=(
            "Edge list as flat 'u v w' triples.  "
            "Weights may be integers or fractions (e.g. 3/2).  "
            "Example: --edges 0 2 5 0 3 3 1 2 4"
        ),
    )

    args = parser.parse_args()
    graph = build_graph(args)
    solver = LeximinSolver(graph)
    imputation = solver.solve()
    print(imputation)


if __name__ == "__main__":
    main()