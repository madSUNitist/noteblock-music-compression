import math
from collections import defaultdict
from typing import List, Tuple, Set, Dict, Optional

Point = Tuple[int, int]   # (tick, pitch)
Vector = Tuple[int, int]  # (dt, dp)

class TEC(object):
    """Translational Equivalence Class: a pattern + set of non-zero translators."""
    def __init__(self, pattern: List[Point], translators: Set[Vector]):
        # pattern is a list of points (sorted lexicographically)
        self.pattern = sorted(pattern)
        self.translators = translators   # set of non-zero vectors

    @property
    def coverage(self) -> Set[Point]:
        """Covered set = pattern ∪ all translated copies."""
        cov = set(self.pattern)
        for v in self.translators:
            for p in self.pattern:
                cov.add((p[0] + v[0], p[1] + v[1]))
        return cov

    @property
    def compression_ratio(self) -> float:
        """Compression ratio = |covered set| / (|pattern| + |translators|)."""
        covered_size = len(self.coverage)
        pattern_size = len(self.pattern)
        trans_count = len(self.translators)
        if pattern_size + trans_count == 0:
            return 0.0
        return covered_size / (pattern_size + trans_count)

    def compactness(self, points: Set[Point]) -> float:
        """Bounding-box compactness: |pattern| / (number of dataset points inside pattern's bbox)."""
        if not self.pattern:
            return 0.0
        xs = [p[0] for p in self.pattern]
        ys = [p[1] for p in self.pattern]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        # count points in the dataset that fall inside this bounding box
        count = 0
        for p in points:
            if min_x <= p[0] <= max_x and min_y <= p[1] <= max_y:
                count += 1
        if count == 0:
            return 0.0
        return len(self.pattern) / count

    def __repr__(self):
        return f"TEC(pattern={self.pattern}, translators={self.translators})"


def sia(dataset: List[Point]) -> Dict[Vector, List[Point]]:
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
            v = (points[i][0] - points[j][0], points[i][1] - points[j][1])
            # we consider all vectors for now, later we'll filter duplicates
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
        mtps[v] = start_points
    return mtps

def siatec(dataset: List[Point]) -> List[TEC]:
    """
    SIATEC algorithm: for each MTP find its TEC (all occurrences).
    Returns a list of TECs (one per MTP).
    """
    points = set(dataset)
    mtps = sia(dataset)  # vector -> list of starting points
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
            w = (q[0] - p0[0], q[1] - p0[1])
            candidates.add(w)
        translators = set()
        for w in candidates:
            if w == (0,0):
                continue
            ok = True
            for p in pattern:
                pp = (p[0] + w[0], p[1] + w[1])
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
    width1 = max(p[0] for p in tec1.pattern) - min(p[0] for p in tec1.pattern)
    width2 = max(p[0] for p in tec2.pattern) - min(p[0] for p in tec2.pattern)
    if width1 != width2:
        return width1 < width2
    # bounding box area (tick_range * pitch_range)
    x1 = max(p[0] for p in tec1.pattern) - min(p[0] for p in tec1.pattern)
    y1 = max(p[1] for p in tec1.pattern) - min(p[1] for p in tec1.pattern)
    area1 = x1 * y1
    x2 = max(p[0] for p in tec2.pattern) - min(p[0] for p in tec2.pattern)
    y2 = max(p[1] for p in tec2.pattern) - min(p[1] for p in tec2.pattern)
    area2 = x2 * y2
    return area1 < area2

def cosiatec(dataset: List[Point], restrict_dpitch_zero: bool = False) -> List[TEC]:
    """
    COSIATEC greedy compression algorithm.
    If restrict_dpitch_zero is True, only consider vectors with dp==0 (temporal translation only).
    """
    points = set(dataset)
    remaining = set(dataset)
    tec_list = []
    while remaining:
        # compute all TECs on the remaining points
        pts_list = sorted(remaining)
        all_tecs = siatec(pts_list)
        if not all_tecs:
            # no more patterns -> output remaining as trivial TECs (single points)
            for p in remaining:
                tec_list.append(TEC([p], set()))
            break
        # filter by restrict_dpitch_zero if needed
        if restrict_dpitch_zero:
            filtered = []
            for tec in all_tecs:
                # check if all translators have dp==0
                ok = all(v[1] == 0 for v in tec.translators)
                if ok:
                    filtered.append(tec)
            all_tecs = filtered
        if not all_tecs:
            # no allowed patterns -> output remaining as trivial TECs
            for p in remaining:
                tec_list.append(TEC([p], set()))
            break
        # select best TEC
        best = max(all_tecs, key=lambda tec: (tec.compression_ratio, tec.compactness(remaining), len(tec.coverage)))
        tec_list.append(best)
        # remove covered points
        remaining -= best.coverage
    return tec_list

def compress_to_encoding(tecs: List[TEC]) -> List[Tuple]:
    """
    Convert list of TECs to a human-readable encoding format.
    For each TEC: (pattern_points, list_of_translators)
    """
    encoding = []
    for tec in tecs:
        encoding.append((tec.pattern, list(tec.translators)))
    return encoding
