import logging
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from generator import generate_non_degenerate, generate_degenerate
from utils import setup_logger

N = tuple(range(4, 41, 3))
P = (0.3, 0.6, 1.0)
SEED = tuple(range(1, 11))

LOGGER = logging.getLogger(__name__)

def main():
    log_file = PROJECT_ROOT / "logs" / "generate_dataset.log"
    setup_logger(log_file)
    data_dir =  PROJECT_ROOT / "experiments" / "data"
    data_dir.mkdir(exist_ok=True, parents=True)
    for n in N:
        for p in P:
            for seed in SEED:
                LOGGER.info(f"Generating graphs for n={n}, p={p}, seed={seed}")
                graph = generate_non_degenerate(n=n, p=p, seed=seed)
                graph.save(data_dir / f"non_degenerate_n{n}_p{int(p*100)}_seed{seed}.json")
                graph = generate_degenerate(n=n, p=p, seed=seed)
                graph.save(data_dir / f"degenerate_n{n}_p{int(p*100)}_seed{seed}.json")

if __name__=="__main__":
    main()