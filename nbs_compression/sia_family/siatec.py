from .sia import sia
from .tec import TEC
from .point import Point

from typing import List, Set



def siatec(dataset: List[Point], restrict_dpitch_zero: bool = False) -> List[TEC]:
    """
    SIATEC algorithm: for each MTP find its TEC (all occurrences).
    Returns a list of TECs (one per MTP).
    """
    points = set(dataset)
    mtps = sia(dataset, restrict_dpitch_zero=restrict_dpitch_zero)  # vector -> list of starting points
    tecs = []
    for v, start_pts in mtps.items():
        if v == (0, 0):
            continue
        # The pattern is the set of points from the first occurrence? Actually the MTP
        # is the set of points that can be translated. But the MTP includes all points
        # that have a partner by v. However, we need a single pattern (the smallest?).
        # In original SIA, the MTP for v is the set of points p such that p+v in D.
        # But that set may include points that are not connected via v.
        # The typical way: the pattern is the set of start points (which are the points
        # that have a translation by v). That set itself is a pattern. Then all its
        # occurrences are the translations of that pattern by multiples of v?
        # Actually easier: For each v, the TEC is the set of all translations of the
        # pattern (the pattern is the set of points that can be mapped by v onto other
        # points). But we need to find all distinct patterns (occurrences) in the TEC.
        # In the paper, they compute the TEC of the MTP by intersecting columns in the
        # vector table. Let's implement a simplified but correct version:
        #
        # Given an MTP pattern P (the set of start points for vector v), the TEC contains
        # all occurrences of P in the dataset. That is, all sets Q such that Q = P + w
        # for some w and Q ⊆ D.
        #
        # So we need to find all w such that P + w ⊆ D.
        pattern = sorted(start_pts)   # pattern = set of points that can be translated by v
        # Find all translation vectors w that map pattern into D
        # For a candidate w, we need that for every p in pattern, p+w in D.
        # The possible w are differences between any point in D and the first point in pattern.
        if not pattern:
            continue
        
        p0 = pattern[0]
        candidates = set()
        for q in dataset:
            if q.instrument != p0.instrument: 
                continue
            w = (q.tick - p0.tick, q.key - p0.key)
            candidates.add(w)
        
        translators = set()
        for w in candidates:
            if w == (0,0):
                continue

            if restrict_dpitch_zero and w[1] != 0:
                continue

            ok = True
            for p in pattern:
                pp = Point(p.tick + w[0], p.key + w[1], p.instrument)
                if pp not in points:
                    ok = False
                    break
            if ok:
                translators.add(w)

        if translators:
            tecs.append(TEC(pattern, translators))

    return tecs

def is_better_tec(tec1: TEC, tec2: TEC, dataset_points: Set[Point]) -> bool:
    """Compare two TECs according to the rules in ISBETTERTEC."""
    # compression ratio
    if tec1.compression_ratio != tec2.compression_ratio:
        return tec1.compression_ratio > tec2.compression_ratio
    # compactness
    comp1 = tec1.compactness(dataset_points)
    comp2 = tec2.compactness(dataset_points)
    if comp1 != comp2:
        return comp1 > comp2
    # coverage size
    cov1 = len(tec1.coverage)
    cov2 = len(tec2.coverage)
    if cov1 != cov2:
        return cov1 > cov2
    # pattern size
    if len(tec1.pattern) != len(tec2.pattern):
        return len(tec1.pattern) > len(tec2.pattern)
    # temporal width (duration of pattern)
    width1 = max(p.tick for p in tec1.pattern) - min(p.tick for p in tec1.pattern)
    width2 = max(p.tick for p in tec2.pattern) - min(p.tick for p in tec2.pattern)
    if width1 != width2:
        return width1 < width2
    # bounding box area (tick_range * pitch_range)
    x1 = max(p.tick for p in tec1.pattern) - min(p.tick for p in tec1.pattern)
    y1 = max(p.key for p in tec1.pattern) - min(p.key for p in tec1.pattern)
    area1 = x1 * y1
    x2 = max(p.tick for p in tec2.pattern) - min(p.tick for p in tec2.pattern)
    y2 = max(p.key for p in tec2.pattern) - min(p.key for p in tec2.pattern)
    area2 = x2 * y2
    return area1 < area2