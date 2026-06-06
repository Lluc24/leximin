import pathlib
from itertools import product

import matplotlib.pyplot as plt
import pandas as pd

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
DEGENERATE_P_VALUES = (0.3, 0.6, 1.0)
RUNTIME_CONSTANT = 0.000001
MEMORY_CONSTANT = 1
OUTPUT_DIR = ROOT_DIR / "experiments" / "results" / "plots"

plt.style.use("seaborn-v0_8-whitegrid")


def _plot_series(ax: plt.Axes, graphs_df: pd.DataFrame, n_values: list[int], metric: str) -> None:
    for p in DEGENERATE_P_VALUES:
        series = [
            graphs_df[(graphs_df["density"] == p) & (graphs_df["n"] == n)][metric].mean()
            for n in n_values
        ]
        ax.plot(n_values, series, label=f"p={p}", linewidth=2.2, marker="o", markersize=4)


def _plot_bound(ax: plt.Axes, n_values: list[int], constant: float, power: int, label: str) -> None:
    ax.plot(
        n_values,
        [constant * n**power for n in n_values],
        label=label,
        color="black",
        linestyle=":",
        linewidth=2.5,
        alpha=0.9,
    )

def _finish_plot(fig: plt.Figure, ax: plt.Axes, output_name: str, title: str, ylabel: str, *, log_scale: bool) -> None:
    if log_scale:
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.grid(True, which="both", linestyle="--", linewidth=0.6, alpha=0.6)
    else:
        ax.grid(True, which="major", linestyle="--", linewidth=0.6, alpha=0.6)

    ax.set_xlabel("Number of Vertices (n)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(frameon=True, fancybox=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / output_name)
    plt.close(fig)

def plot_runtime(df: pd.DataFrame, is_deg: bool, n_values: list[int], log_scale: bool) -> None:
    title = f"Runtime for {"" if is_deg else "Non-"}Degenerate Graphs"
    output_name = f"{"deg" if is_deg else "non-deg"}_runtime{"_log" if log_scale else ""}.png"
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    _plot_series(ax, df, n_values, "runtime_s")
    _plot_bound(ax, n_values, RUNTIME_CONSTANT, 5, "$O(n^5)$")
    _finish_plot(fig, ax, output_name, title, "Average Runtime (s)", log_scale=log_scale)

def plot_memory(df: pd.DataFrame, is_deg: bool, n_values: list[int], log_scale: bool) -> None:
    title = f"Memory Usage for {"" if is_deg else "Non-"}Degenerate Graphs"
    output_name = f"{"deg" if is_deg else "non-deg"}_memory{"_log" if log_scale else ""}.png"
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    _plot_series(ax, df, n_values, "peak_memory_kb")
    _plot_bound(ax, n_values, MEMORY_CONSTANT, 2, "$O(n^2)$")
    _finish_plot(fig, ax, output_name, title, "Peak Memory (KB)", log_scale=log_scale)

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics_file = ROOT_DIR / "experiments" / "results" / "metrics.csv"
    df = pd.read_csv(metrics_file)
    n_values = sorted(df["n"].unique())
    for is_deg, log_scale in product([False, True], [False, True]):
        graph_type = "degenerate" if is_deg else "non_degenerate"
        plot_runtime(df[df["graph_type"] == graph_type], is_deg, n_values, log_scale)
        plot_memory(df[df["graph_type"] == graph_type], is_deg, n_values, log_scale)


if __name__ == "__main__":
    main()
