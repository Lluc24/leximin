"""Benchmark the leximin solver on all generated graphs.

Records runtime (cProfile) and peak memory (tracemalloc) for each graph.

Usage:
    python run_experiments.py

Reads  : experiments/data/*.json
Writes : experiments/results/metrics.csv
"""

import cProfile
import csv
import io
import logging
import pathlib
import pstats
import re
import sys
import tracemalloc
from tqdm import tqdm

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from graph import BipartiteGraph
from leximin import LeximinSolver
from utils import setup_logger

LOGGER = logging.getLogger(__name__)

COLUMNS = ["filename", "graph_type", "n", "density", "seed", "runtime_s", "peak_memory_kb"]

_FILENAME_RE = re.compile(r'^(non_degenerate|degenerate)_n(\d+)_p(\d+)_seed(\d+)$')


def benchmark(graph_path: pathlib.Path) -> dict:
    m = _FILENAME_RE.fullmatch(graph_path.stem)
    if not m:
        raise ValueError(f"Unexpected filename: {graph_path.name!r}")

    graph = BipartiteGraph.load(graph_path)
    tracemalloc.start()
    pr = cProfile.Profile()
    pr.enable()

    solver = LeximinSolver(graph)
    solver.solve()

    pr.disable()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    runtime = pstats.Stats(pr, stream=io.StringIO()).total_tt

    return {
        "filename": graph_path.name,
        "graph_type": m.group(1),
        "n": int(m.group(2)),
        "density": int(m.group(3)) / 100,
        "seed": int(m.group(4)),
        "runtime_s": runtime,
        "peak_memory_kb": peak / 1024,
    }


def main():
    setup_logger(PROJECT_ROOT / "logs" / "run_experiments.log")

    data_dir = PROJECT_ROOT / "experiments" / "data"
    results_dir = PROJECT_ROOT / "experiments" / "results"
    results_dir.mkdir(exist_ok=True, parents=True)
    csv_path = results_dir / "metrics.csv"

    graph_files = sorted(data_dir.glob("*.json"))
    LOGGER.info("Found %d graph files", len(graph_files))

    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for i, path in tqdm(enumerate(graph_files, 1), total=len(graph_files)):
            try:
                writer.writerow(benchmark(path))
                f.flush()
            except Exception as exc:
                LOGGER.error("Failed on %s: %s", path.name, exc, exc_info=True)

    LOGGER.info("Results saved to %s", csv_path)


if __name__ == "__main__":
    main()