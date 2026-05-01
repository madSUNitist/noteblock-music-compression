from . import Point, Vector, warn_python_impl_deco
from typing import List, Dict
from collections import defaultdict

@warn_python_impl_deco(
    "SIA algorithm: using Python implementation (slower). "
    "For better performance, consider using the Rust implementation."
)
def find_mtps(dataset: List[Point], restrict_dpitch_zero: bool = False) -> Dict[Vector, List[Point]]:
    """
    SIA (Structure Induction Algorithm): find all maximal translatable patterns (MTPs).

    For each non‑zero translation vector v = (Δtick, Δpitch), the MTP is defined as
    { p ∈ dataset | p+v ∈ dataset }. The algorithm groups all ordered point pairs
    (p, q) by the vector q - p and collects the starting points.

    Args:
        dataset: List of unique points (tick, pitch). Duplicates are not expected.
        restrict_dpitch_zero: If True, only vectors with Δpitch = 0 (purely temporal
            translations) are considered.

    Returns:
        Dictionary mapping a translation vector (i32, i32) to a sorted list of starting
        points (the MTP for that vector). The zero vector is excluded, and only vectors
        with at least two starting points are included.

    Complexity:
        Time O(n²) where n = len(dataset). Memory O(n²) in worst case, but the online
        aggregation reduces typical usage.

    Note:
        The result is deterministic because points are sorted before grouping.
    """
    points = list(dataset)
    n = len(points)

    # Use a dictionary to group start points by vector online
    groups = defaultdict(set)       # vector -> set of start points

    for i in range(n):
        ti, pi = points[i]
        for j in range(i):
            if i == j:
                continue
            tj, pj = points[j]
            dx = ti - tj
            dy = pi - pj
            if restrict_dpitch_zero and dy != 0:
                continue
            groups[(dx, dy)].add((tj, pj))
            groups[(-dx, -dy)].add((ti, pi))

    # Build result: filter out zero vector and groups with fewer than 2 points
    mtps = {}
    for v, start_set in groups.items():
        if v == (0, 0):
            continue
        if len(start_set) < 2:
            continue
        mtps[v] = sorted(start_set)   # sorted to match original output order

    return mtps