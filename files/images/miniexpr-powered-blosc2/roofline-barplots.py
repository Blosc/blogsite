#!/usr/bin/env python3
"""Generate before/after bar plots for Blosc2 (compressed vs uncompressed).

This reads BENCH_DATA from roofline-plot.py (before miniexpr) and roofline-plot-miniexpr.py (after miniexpr)
so the plots stay in sync with the roofline datasets.
"""

import ast
import re
from pathlib import Path

import matplotlib.pyplot as plt

WORKLOADS = ["very low", "low", "medium"]
BACKENDS = ["blosc2", "blosc2-nocomp", "numpy/numexpr"]

FIGSIZE = (4.5, 2.5)
TITLE_SIZE = 9
LABEL_SIZE = 8
TICK_SIZE = 7
LEGEND_SIZE = 6
SPEEDUP_SIZE = 6


def extract_bench_data(path: Path) -> dict:
    text = path.read_text()
    match = re.search(
        r"BENCH_DATA\s*=\s*(\{.*?\})\n\s*# ---------------------------------------------------------------------\n# Select benchmark",
        text,
        re.S,
    )
    if not match:
        raise SystemExit(f"BENCH_DATA not found in {path}")
    return ast.literal_eval(match.group(1))


def human_machine(name: str) -> str:
    return name.replace("-", " ")


def backend_label(backend: str) -> str:
    if backend == "blosc2":
        return "Blosc2 compressed"
    if backend == "blosc2-nocomp":
        return "Blosc2 uncompressed"
    return "Numexpr"


def plot_machine_mode(machine: str, mode: str, before_data: dict, after_data: dict, out_dir: Path) -> None:
    legend = "in-memory" if mode == "mem" else "on-disk"

    before_results = ast.literal_eval(before_data[machine][mode])
    after_results = ast.literal_eval(after_data[machine][mode])

    # Build arrays
    values = {}
    for backend in BACKENDS:
        values[backend] = {
            "before": [before_results[backend][w]["GFLOPS"] for w in WORKLOADS],
            "after": [after_results[backend][w]["GFLOPS"] for w in WORKLOADS],
        }

    # Layout
    x = list(range(len(WORKLOADS)))
    width = 0.16
    offsets = {}
    # 5 bars per workload: blosc2 before/after, blosc2-nocomp before/after, numexpr (after only)
    offset_steps = [-2, -1, 0, 1, 2]
    pairs = [
        ("blosc2", "before"),
        ("blosc2", "after"),
        ("blosc2-nocomp", "before"),
        ("blosc2-nocomp", "after"),
        ("numpy/numexpr", "after"),
    ]
    for step, key in zip(offset_steps, pairs):
        offsets[key] = step * width

    colors = {
        "blosc2": "#1f77b4",
        "blosc2-nocomp": "#2ca02c",
        "numpy/numexpr": "#ff7f0e",
    }

    fig, ax = plt.subplots(figsize=FIGSIZE, constrained_layout=True)

    for backend in BACKENDS:
        eras = ["after"] if backend == "numpy/numexpr" else ["before", "after"]
        for era in eras:
            xpos = [xi + offsets[(backend, era)] for xi in x]
            bars = ax.bar(
                xpos,
                values[backend][era],
                width=width,
                color=colors[backend],
                alpha=0.45 if era == "before" else 0.9,
                hatch="//" if era == "before" else None,
                label=backend_label(backend) if backend == "numpy/numexpr" else f"{backend_label(backend)} ({era})",
            )

            # Speedup labels on the new bars
            if era == "after" and backend != "numpy/numexpr":
                for bar, base in zip(bars, values[backend]["before"]):
                    after_val = bar.get_height()
                    if base > 0:
                        speedup = after_val / base
                        ax.text(
                            bar.get_x() + bar.get_width() / 2.0,
                            after_val * 1.03,
                            f"{speedup:.2g}x",
                            ha="center",
                            va="bottom",
                            fontsize=SPEEDUP_SIZE,
                        )

    ax.set_xticks(x)
    ax.set_xticklabels(WORKLOADS, fontsize=TICK_SIZE)
    ax.set_ylabel("GFLOPS/sec", fontsize=LABEL_SIZE)
    ax.set_title(
        f"Blosc2 before/after miniexpr: {human_machine(machine)} ({legend})",
        fontsize=TITLE_SIZE,
        fontweight="bold",
    )
    ax.tick_params(axis="y", labelsize=TICK_SIZE)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.legend(loc="upper left", fontsize=LEGEND_SIZE, frameon=False)
    ax.set_ylim(0, 30)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"barplot-{machine}-{legend}.png"
    plt.savefig(out_path, dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    before_data = extract_bench_data(root / "roofline-plot.py")
    after_data = extract_bench_data(root / "roofline-plot-miniexpr.py")

    out_dir = root
    for machine in ["AMD-7800X3D", "Apple-M4-Pro"]:
        for mode in ["mem", "disk"]:
            plot_machine_mode(machine, mode, before_data, after_data, out_dir)
