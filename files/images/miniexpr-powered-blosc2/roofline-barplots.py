#!/usr/bin/env python3
"""Generate before/after bar plots for Blosc2 (compressed vs uncompressed).

This reads BENCH_DATA from roofline-plot.py (old) and roofline-plot-miniexpr.py (new)
so the plots stay in sync with the roofline datasets.
"""

import ast
import re
from pathlib import Path

import matplotlib.pyplot as plt

WORKLOADS = ["very low", "low", "medium"]
BACKENDS = ["blosc2", "blosc2-nocomp"]

FIGSIZE = (4.5, 2.5)
TITLE_SIZE = 9
LABEL_SIZE = 8
TICK_SIZE = 7
LEGEND_SIZE = 7
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


def plot_machine_mode(machine: str, mode: str, old_data: dict, new_data: dict, out_dir: Path) -> None:
    legend = "in-memory" if mode == "mem" else "on-disk"

    old_results = ast.literal_eval(old_data[machine][mode])
    new_results = ast.literal_eval(new_data[machine][mode])

    # Build arrays
    values = {}
    for backend in BACKENDS:
        values[backend] = {
            "old": [old_results[backend][w]["GFLOPS"] for w in WORKLOADS],
            "new": [new_results[backend][w]["GFLOPS"] for w in WORKLOADS],
        }

    # Layout
    x = list(range(len(WORKLOADS)))
    width = 0.18
    offsets = {
        ("blosc2", "old"): -1.5 * width,
        ("blosc2", "new"): -0.5 * width,
        ("blosc2-nocomp", "old"): 0.5 * width,
        ("blosc2-nocomp", "new"): 1.5 * width,
    }

    colors = {
        "blosc2": "#1f77b4",
        "blosc2-nocomp": "#2ca02c",
    }

    fig, ax = plt.subplots(figsize=FIGSIZE, constrained_layout=True)

    for backend in BACKENDS:
        for era in ["old", "new"]:
            xpos = [xi + offsets[(backend, era)] for xi in x]
            bars = ax.bar(
                xpos,
                values[backend][era],
                width=width,
                color=colors[backend],
                alpha=0.45 if era == "old" else 0.9,
                hatch="//" if era == "old" else None,
                label=f"{'compressed' if backend == 'blosc2' else 'uncompressed'} ({era})",
            )

            # Speedup labels on the new bars
            if era == "new":
                for bar, base in zip(bars, values[backend]["old"]):
                    new_val = bar.get_height()
                    if base > 0:
                        speedup = new_val / base
                        ax.text(
                            bar.get_x() + bar.get_width() / 2.0,
                            new_val * 1.03,
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

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"barplot-{machine}-{legend}.png"
    plt.savefig(out_path, dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    old_data = extract_bench_data(root / "roofline-plot.py")
    new_data = extract_bench_data(root / "roofline-plot-miniexpr.py")

    out_dir = root / "output"
    for machine in ["AMD-7800X3D", "Apple-M4-Pro"]:
        for mode in ["mem", "disk"]:
            plot_machine_mode(machine, mode, old_data, new_data, out_dir)
