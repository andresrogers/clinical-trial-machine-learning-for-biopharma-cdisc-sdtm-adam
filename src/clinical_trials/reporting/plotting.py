from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns


ARM_ORDER = ["placebo", "ntx101_low", "ntx101_high"]
ARM_COLORS = {
    "placebo": "#6B7280",
    "ntx101_low": "#3A7CA5",
    "ntx101_high": "#0A7F62",
    "screen_failure": "#B7C0CA",
    "unknown": "#9AA5B1",
}
ARM_LABELS = {
    "placebo": "Placebo",
    "ntx101_low": "NTX-101 Low Dose",
    "ntx101_high": "NTX-101 High Dose",
    "screen_failure": "Screen Failure",
    "unknown": "Unknown",
}


def set_pharma_style() -> None:
    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "figure.dpi": 160,
            "savefig.dpi": 200,
            "axes.facecolor": "#FFFFFF",
            "figure.facecolor": "#FFFFFF",
            "axes.edgecolor": "#D0D7DE",
            "axes.labelcolor": "#18324A",
            "axes.titlecolor": "#18324A",
            "xtick.color": "#44556B",
            "ytick.color": "#44556B",
            "grid.color": "#E8EEF5",
            "grid.linestyle": "-",
            "grid.linewidth": 0.8,
            "font.size": 10,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "legend.frameon": False,
        }
    )


def order_arms(values: list[str]) -> list[str]:
    known = [arm for arm in ARM_ORDER if arm in values]
    extras = sorted([arm for arm in values if arm not in known])
    return known + extras


def display_arm_label(value: str) -> str:
    return ARM_LABELS.get(value, value.replace("_", " ").title())


def save_figure(path: str | Path) -> None:
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
