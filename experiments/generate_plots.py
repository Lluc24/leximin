import logging
import pathlib
from itertools import product

import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils import setup_logger

DEGENERATE_P_VALUES = (0.3, 0.6, 1.0)
RUNTIME_CONSTANT = 0.0000005
MEMORY_CONSTANT = 1.1
OUTPUT_DIR = ROOT_DIR / "experiments" / "results" / "plots"

# Smallest n included in plots and slope fits. Below this the asymptotic
# regime has not kicked in (constant overheads dominate), adding noise.
MIN_N = 16

METRICS_COLUMNS = (
    "filename",
    "graph_type",
    "n",
    "density",
    "seed",
    "runtime_s",
    "peak_memory_kb",
)

plt.style.use("seaborn-v0_8-whitegrid")
logger = logging.getLogger(__name__)


def _plot_series(
    ax: plt.Axes, graphs_df: pd.DataFrame, n_values: list[int], metric: str
) -> dict[float, str]:
    """Plot the mean curve for each p family; return the colour used per p."""
    colors: dict[float, str] = {}
    for p in DEGENERATE_P_VALUES:
        means = []
        for n in n_values:
            subset = graphs_df[(graphs_df["density"] == p) & (graphs_df["n"] == n)][metric]
            means.append(subset.mean())
        means = np.array(means)
        (line,) = ax.plot(n_values, means, label=f"{p=}", linewidth=2.2, marker="o", markersize=4)
        colors[p] = str(line.get_color())
    return colors


def _fit_loglog(
    ax: plt.Axes,
    graphs_df: pd.DataFrame,
    n_values: list[int],
    metric: str,
    label_prefix: str,
    colors: dict[float, str],
) -> None:
    """Fit a least-squares line in log-log space for each p family.

    Reports slope, 95% CI and R^2 per family and overlays the fitted line.
    """
    n_arr = np.array(n_values, dtype=float)
    for p in DEGENERATE_P_VALUES:
        pdf = graphs_df[graphs_df["density"] == p]
        means = np.array([pdf[pdf["n"] == n][metric].mean() for n in n_values])

        valid = ~(np.isnan(means) | (means <= 0))
        log_n = np.log(n_arr[valid])
        log_y = np.log(means[valid])

        result = stats.linregress(log_n, log_y)
        slope, intercept, stderr = result.slope, result.intercept, result.stderr
        r_squared = result.rvalue**2
        n_pts = len(log_n)
        t_crit = stats.t.ppf(0.975, df=n_pts - 2)
        ci = t_crit * stderr

        logger.info(
            "[%s] log-log fit (p=%.1f, n>=%d): slope = %.4f ± %.4f (95%% CI), "
            "R^2 = %.4f (%d points)",
            label_prefix,
            p,
            MIN_N,
            slope,
            ci,
            r_squared,
            n_pts,
        )

        fitted_y = np.exp(intercept + slope * log_n)
        ax.plot(
            n_arr[valid],
            fitted_y,
            label=f"LS fit ({p=}): slope={slope:.2f}",
            color=colors[p],
            linestyle="--",
            linewidth=2.0,
        )


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


def _finish_plot(
    fig: plt.Figure, ax: plt.Axes, output_name: str, title: str, ylabel: str, *, log_scale: bool
) -> None:
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
    colors = _plot_series(ax, df, n_values, "runtime_s")
    if log_scale:
        label = f'{"deg" if is_deg else "non-deg"} runtime'
        _fit_loglog(ax, df, n_values, "runtime_s", label, colors)
    else:
        _plot_bound(ax, n_values, RUNTIME_CONSTANT, 5, "$O(n^5)$")
    _finish_plot(fig, ax, output_name, title, "Average Runtime (s)", log_scale=log_scale)


def plot_memory(df: pd.DataFrame, is_deg: bool, n_values: list[int], log_scale: bool) -> None:
    title = f"Memory Usage for {"" if is_deg else "Non-"}Degenerate Graphs"
    output_name = f"{"deg" if is_deg else "non-deg"}_memory{"_log" if log_scale else ""}.png"
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    colors = _plot_series(ax, df, n_values, "peak_memory_kb")
    if log_scale:
        label = f'{"deg" if is_deg else "non-deg"} memory'
        _fit_loglog(ax, df, n_values, "peak_memory_kb", label, colors)
    else:
        _plot_bound(ax, n_values, MEMORY_CONSTANT, 2, "$O(n^2)$")
    _finish_plot(fig, ax, output_name, title, "Peak Memory (KB)", log_scale=log_scale)


def main() -> None:
    setup_logger(ROOT_DIR / "logs" / "generate_plots.log")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics_file = ROOT_DIR / "experiments" / "results" / "all_metrics.csv"
    df = pd.read_csv(metrics_file, header=None, names=METRICS_COLUMNS)
    df = df[df["n"] >= MIN_N]
    n_values = sorted(df["n"].unique())
    for is_deg, log_scale in product([False, True], [False, True]):
        graph_type = "degenerate" if is_deg else "non_degenerate"
        plot_runtime(df[df["graph_type"] == graph_type], is_deg, n_values, log_scale)
        plot_memory(df[df["graph_type"] == graph_type], is_deg, n_values, log_scale)


if __name__ == "__main__":
    main()