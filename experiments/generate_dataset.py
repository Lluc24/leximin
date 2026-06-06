from itertools import product
import pathlib
import sys
from tqdm import tqdm

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from generator import generate_non_degenerate, generate_degenerate

N = tuple(range(4, 41, 3))
P = (0.3, 0.6, 1.0)
SEED = tuple(range(1, 11))

def main():
    data_dir =  PROJECT_ROOT / "experiments" / "data"
    data_dir.mkdir(exist_ok=True, parents=True)
    for n, p, seed in tqdm(product(N, P, SEED), total=len(N)*len(P)*len(SEED)):
        graph = generate_non_degenerate(n=n, p=p, seed=seed)
        graph.save(data_dir / f"non_degenerate_n{n}_p{int(p*100)}_seed{seed}.json")
        graph = generate_degenerate(n=n, p=p, seed=seed)
        graph.save(data_dir / f"degenerate_n{n}_p{int(p*100)}_seed{seed}.json")

if __name__=="__main__":
    main()