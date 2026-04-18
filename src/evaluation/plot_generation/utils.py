from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

from evaluation.plot_generation.constants import DPI

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def annotate_bars(ax: Axes, bars: Iterable, fmt: str, fontsize: int) -> None:
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            fmt.format(height),
            ha="center",
            va="bottom",
            fontsize=fontsize,
        )


def grouped_bars(
    ax: Axes,
    groups: dict[str, list[float]],
    x_labels: list[str],
    colors: dict[str, str],
    width: float,
    annotate_fmt: str | None,
    annotate_fontsize: int,
) -> None:
    n = len(groups)
    x = np.arange(len(x_labels))
    offsets = [(i - (n - 1) / 2) * width for i in range(n)]
    for offset, (label, values) in zip(offsets, groups.items(), strict=True):
        bars = ax.bar(x + offset, values, width, label=label, color=colors.get(label))
        if annotate_fmt is not None:
            annotate_bars(ax, bars, annotate_fmt, annotate_fontsize)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)


def heatmap(
    ax: Axes,
    fig: Figure,
    data: np.ndarray,
    row_labels: list[str],
    col_labels: list[str],
    cmap: str,
    vmin: float,
    vmax: float,
    fmt: str,
) -> None:
    im = ax.imshow(data, cmap=cmap, aspect="auto", vmin=vmin, vmax=vmax)
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(
                j,
                i,
                fmt.format(data[i, j]),
                ha="center",
                va="center",
                color="black",
                fontsize=9,
            )
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)


def save(fig: Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def rotate_xticks(ax: Axes, rotation: int, fontsize: int | None) -> None:
    for lbl in ax.get_xticklabels():
        lbl.set_rotation(rotation)
        lbl.set_horizontalalignment("right")
        if fontsize is not None:
            lbl.set_fontsize(fontsize)
