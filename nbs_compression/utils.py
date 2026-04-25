from .sia_family.point import Point
from .sia_family.tec import TEC

from collections import defaultdict

from matplotlib import pyplot as plt

import numpy as np

from typing import List


def notes_to_points(notes):
    return [Point(tick, key, instrument) for tick, key, instrument in notes]

def visualize(tecs: List[TEC]) -> None:
    """
    Visualize the compressed point sets (TECs) with distinct colors.
    
    Each TEC's entire covered set is plotted using a unique color.
    The base pattern points of each TEC are highlighted with a star marker.
    This helps to see how patterns repeat via translations.

    Args:
        tecs: List of TEC objects (e.g., output of COSIATEC or RecurSIA).
    """
    if not tecs:
        print("No TECs to visualize.")
        return

    plt.figure(figsize=(12, 8))
    # Use a colormap to assign colors to each TEC
    colors = plt.cm.tab20(np.linspace(0, 1, len(tecs))) # type: ignore

    for idx, tec in enumerate(tecs):
        color = colors[idx]
        # Get all covered points (all occurrences of the pattern)
        covered = tec.coverage
        if not covered:
            continue

        # Separate x (tick) and y (pitch) coordinates
        xs = [p.tick for p in covered]
        ys = [p.key for p in covered]

        # Plot all covered points as circles
        plt.scatter(xs, ys, c=[color], marker='o', s=30, alpha=0.7, label=f"TEC {idx+1}")

        # Highlight the base pattern points with a star marker
        pattern_xs = [p.tick for p in tec.pattern]
        pattern_ys = [p.key for p in tec.pattern]
        plt.scatter(pattern_xs, pattern_ys, c=[color], marker='*', s=120, edgecolors='black', linewidth=0.8,
                    label=f"_nolegend")  # no separate legend entry for stars

    plt.xlabel("Tick (time)", fontsize=12)
    plt.ylabel("Pitch", fontsize=12)
    plt.title("Compressed Music Visualization – Each TEC in a Different Color")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.show()

def rebuild(tecs: List[TEC]) -> List[Point]:
    points = set()
    for tec in tecs:
        # recursively rebuild pattern if sub_tecs exist
        if tec.sub_tecs:
            pattern_points = rebuild(tec.sub_tecs)  # returns list of points, convert to set? careful with duplicates within sub_tecs
        else:
            pattern_points = tec.pattern
        # add all points from pattern
        points.update(pattern_points)
        # add translated copies
        for v in tec.translators:
            for p in pattern_points:
                translated = Point(p.tick + v[0], p.key + v[1], p.instrument)
                points.add(translated)
    # optionally sort for consistent output
    return sorted(points)  # sorted by tick then pitch