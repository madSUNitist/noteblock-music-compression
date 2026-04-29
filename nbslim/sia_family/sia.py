from . import Point, Vector, warn_python_impl_deco
from typing import List, Dict
from collections import defaultdict

@warn_python_impl_deco(
    "SIA algorithm: using Python implementation (slower). "
    "For better performance, consider using the Rust implementation."
)
def find_mtps(dataset: List[Point], restrict_dpitch_zero: bool = False) -> Dict[Vector, List[Point]]:
    """
    SIA algorithm: compute all maximal translatable patterns (MTPs).
    Returns a dict: vector -> list of points that are the MTP (starting points).
    The MTP for vector v is { p in dataset | p+v in dataset }.
    """
    points = list(dataset)          # no sorting, just a copy
    n = len(points)

    # Use a dictionary to group start points by vector online
    groups = defaultdict(set)       # vector -> set of start points

    for i in range(n):
        ti, pi = points[i]
        for j in range(n):
            if i == j:
                continue
            tj, pj = points[j]
            dx = ti - tj
            dy = pi - pj
            if restrict_dpitch_zero and dy != 0:
                continue
            groups[(dx, dy)].add((tj, pj))

    # Build result: filter out zero vector and groups with fewer than 2 points
    mtps = {}
    for v, start_set in groups.items():
        if v == (0, 0):
            continue
        if len(start_set) < 2:
            continue
        mtps[v] = sorted(start_set)   # sorted to match original output order

    return mtps