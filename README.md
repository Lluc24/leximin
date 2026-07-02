# Leximin Core Imputation — Assignment Game

A Python implementation of the combinatorial algorithm for computing the **leximin core imputation** of the assignment game, based on Algorithm 1 of [Vazirani (2025)](https://arxiv.org/abs/2402.11437).

This is the software artifact accompanying the bachelor's thesis:

> **Implementation and Experimental Analysis of Leximin Fair Core Imputations for the Assignment Game**
> Lluc Santamaria Riba — FIB, Universitat Politècnica de Catalunya / UC Irvine, June 2026
>
> Supervisor: Vijay V. Vazirani (UC Irvine) · Tutor: Maria José Serna Iglesias (UPC)

The thesis (PDF) is available [here](https://github.com/Lluc24/leximin-docs/blob/main/memory/final-milestone/thesis.pdf). All project documentation (progress milestones, project management, presentation slides) lives in [github.com/Lluc24/leximin-docs](https://github.com/Lluc24/leximin-docs).

---

## Background

The **assignment game** (Shapley & Shubik, 1971) is a cooperative game defined on a weighted bipartite graph $G = (U, V, E, w)$. Buyers $U$ and sellers $V$ generate a joint profit equal to the weight of a maximum-weight matching (MWM), and the **core** — the set of stable profit allocations — coincides with the optimal dual solutions of the MWM linear program.

While the core guarantees coalition stability, it gives no individual-fairness guarantee: some agents can receive arbitrarily small payoffs. The **leximin core imputation** addresses this by lexicographically maximising the sorted profit vector, i.e., first maximising the minimum individual profit, then the second minimum, and so on. Vazirani (2025) proved that this imputation is unique and gave the first strongly polynomial combinatorial algorithm ($O(mn^3)$) to compute it.

This project provides the **first public implementation** of that algorithm, validated against all worked examples in the original paper and against an independent LP-based reference solver.

---

## Features

- Exact rational arithmetic (`fractions.Fraction`) — no floating-point drift.
- Covers both **non-degenerate** (unique MWM) and **degenerate** (multiple MWMs, viable edges) instances.
- Modular architecture: eight focused modules plus a full test suite.
- Random graph generator for benchmarking (non-degenerate and degenerate families).
- LP-based reference solver (`LeximinLPSolver`) for independent correctness checks.
- Structured logging to file and stdout.

---

## Algorithm Overview

The solver runs a **clock-based primal–dual event loop**:

1. **Classification** — every vertex and edge is classified as *essential*, *viable*, or *subpar* using $O(m+n)$ MWM calls.
2. **Initialisation** — essential vertices are grouped into *fundamental components* (FCs); all FCs enter the BIN set. Non-essential vertices are frozen at profit 0.
3. **Event loop** — a global clock $\Omega$ rises continuously. Three event types are dispatched in priority order:
   - **BIN activation**: when $\Omega$ reaches the minimum profit of a BIN component, the component becomes ACTIVE and starts rotating (CW or CCW), increasing the lower side's profit toward parity.
   - **Fully repaired**: when both sides of an active component equalise, the minimal sub-component (Min-Sub1) moves to FULLY-REPAIRED; the remainder decomposes back to BIN.
   - **Tight subpar edge**: when a subpar edge incident on an ACTIVE component reaches zero slack, the appropriate merge/freeze rule fires depending on the opposite endpoint's status (BIN → absorb, ACTIVE → merge, FROZEN/FULLY-REPAIRED → freeze sub-path).

When the event queue empties, the current imputation is leximin-optimal.

Complexity: $O(mn^3)$ time (dominated by classification), $O(n^2)$ space.

---

## Installation

**Requirements:** Python 3.13+, `networkx`, `pulp`, `matplotlib`, `tqdm`.

```bash
git clone https://github.com/Lluc24/leximin.git
cd leximin
python -m venv env
source env/bin/activate
pip install networkx pulp matplotlib tqdm
```

---

## Quick Start

### Command-line interface

```bash
python run.py --n-u <N_U> --n-v <N_V> --edges <u1> <v1> <w1> [...]
```

- U-side vertices have IDs `0, …, N_U - 1`.
- V-side vertices have IDs `N_U, …, N_U + N_V - 1`.
- Edge weights may be integers or fractions (e.g. `3/2`).

**Example** — 2 buyers, 2 sellers, 4 edges:

```bash
python run.py --n-u 2 --n-v 2 --edges 0 2 5 0 3 3 1 2 4 1 3 2
```

### Python API

```python
from fractions import Fraction
from graph import BipartiteGraph
from leximin import LeximinSolver
from utils import set_u_vertices, set_v_vertices

# Build a 2×2 graph
u_vertices = set_u_vertices(2)   # {0, 1}
v_vertices = set_v_vertices(2, 2)  # {2, 3}
weights = {
    (0, 2): Fraction(5),
    (0, 3): Fraction(3),
    (1, 2): Fraction(4),
    (1, 3): Fraction(2),
}
graph = BipartiteGraph(u_vertices=u_vertices, v_vertices=v_vertices, weights=weights)

solver = LeximinSolver(graph)
imputation = solver.solve()
print(imputation.profits)  # {0: Fraction(3, 2), 1: Fraction(3, 2), 2: Fraction(7, 2), 3: Fraction(3, 2)}
```

### Loading / saving graphs

```python
graph.save("my_graph.json")
loaded = BipartiteGraph.load("my_graph.json")
```

---

## Running the Tests

```bash
pytest
```

The test suite in `tests/` covers:
- Classification correctness on all Vazirani (2025) examples.
- Leximin output matched against the LP reference solver on all paper examples.
- Graph and matching utilities.
- The random graph generator.

The randomized cross-validation tests (`test_random_crossval.py`) are excluded by default because they are slow. Run them explicitly with:

```bash
pytest -m crossval
```

Logs are written to `logs/pytest.log`.

---

## Repository Structure

```
.
├── graph.py           # BipartiteGraph: immutable weighted bipartite graph
├── matching.py        # MaxWeightMatching wrapper around NetworkX
├── classification.py  # Essential / viable / subpar classification
├── imputation.py      # Imputation dataclass + LP-based initialisation
├── component.py       # FundamentalComponent and ValidComponent trees
├── events.py          # Event types: BinActivation, FullyRepaired, TightEdge
├── leximin.py         # LeximinSolver: the main event-driven solver
├── lp_solver.py       # LeximinLPSolver: LP reference solver for validation
├── generator.py       # Random graph generators for benchmarks
├── run.py             # CLI entry point
├── utils.py           # Shared helpers (vertex IDs, edge canonicalisation, logger)
├── tests/             # pytest test suite
├── pytest.ini         # pytest configuration
└── LICENSE            # MIT License
```

---

## Technical Decisions

| Decision | Choice | Reason |
|---|---|---|
| Language | Python 3.13 | Rapid development; built-in `fractions.Fraction`; scientific ecosystem |
| Arithmetic | `fractions.Fraction` | Exact tightness decisions; float rounding caused incorrect results in prototypes |
| MWM library | NetworkX `max_weight_matching` | Correct, pure-Python, sufficient for validation sizes |
| LP solver | PuLP + CBC | Free, open-source; used only as reference, not in the combinatorial algorithm |
| Component representation | Immutable frozen dataclasses | Avoids aliasing bugs; correctness reasoning is simpler |
| Priority queue | `heapq` | Standard library; $O(\log n)$ insert and extract-min |

---

## Institutional Context

This project was carried out during a research stay at the **Donald Bren School of Information and Computer Sciences, University of California, Irvine**, under the direct supervision of **Professor Vijay V. Vazirani** — one of the leading figures in algorithmic game theory and the author of the paper implemented here. The stay was funded by the **Balsells Fellowship Program**, which each semester supports up to three engineering students from Catalonia at UC Irvine. The home institution is the **Facultat d'Informàtica de Barcelona (FIB), Universitat Politècnica de Catalunya (UPC)**, where the thesis was co-supervised by **Professor Maria José Serna Iglesias**.

---

## Citation

If you use this software, please cite the original algorithm and this implementation:

```bibtex
@misc{vazirani2025,
  author    = {Vijay V. Vazirani},
  title     = {Leximin and Leximax Fair Core Imputations for the Assignment Game},
  year      = {2025},
  eprint    = {2402.11437},
  archivePrefix = {arXiv},
}

@misc{santamaria2026,
  author    = {Lluc Santamaria Riba},
  title     = {Implementation and Experimental Analysis of Leximin Fair Core
               Imputations for the Assignment Game},
  year      = {2026},
  url       = {https://github.com/Lluc24/leximin},
  note      = {Bachelor's thesis, FIB--UPC / UC Irvine},
}
```

---

## License

MIT — see [LICENSE](LICENSE).
