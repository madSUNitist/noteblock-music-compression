from .point import Point, Vector

from typing import List, Dict


def sia(dataset: List[Point], restrict_dpitch_zero: bool = False) -> Dict[Vector, List[Point]]:
    """
    SIA algorithm: compute all maximal translatable patterns (MTPs).
    Returns a dict: vector -> list of points that are the MTP (starting points).
    The MTP for vector v is { p in dataset | p+v in dataset }.
    """
    # sort dataset lexicographically (by tick, then pitch)
    points = sorted(dataset)
    n = len(points)
    # build vector table: for each i>j, vector = points[i] - points[j]
    # we'll store (vector, start_point) pairs
    vectors = []  # list of (v, p_start)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if points[i].instrument != points[j].instrument: 
                continue
            v = (points[i].tick - points[j].tick, points[i].key - points[j].key)
            # filter non-zero dpitch
            if restrict_dpitch_zero and v[1] != 0:
                continue
            vectors.append((v, points[j]))
    # sort by vector (lexicographically)
    vectors.sort(key=lambda x: x[0])
    # scan to group by vector
    mtps = {}
    i = 0
    while i < len(vectors):
        v = vectors[i][0]
        start_points = []
        while i < len(vectors) and vectors[i][0] == v:
            start_points.append(vectors[i][1])
            i += 1
        # remove duplicates (same start point may appear multiple times from different pairs)
        start_points = sorted(set(start_points))
        
        if v == (0, 0):
            continue
        if len(start_points) < 2:
            continue
        
        mtps[v] = start_points
    return mtps