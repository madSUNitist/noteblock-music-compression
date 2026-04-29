from . import Point, Vector

from typing import List, Set, Optional

class TranslationalEquivalence(object):
    """Translational Equivalence Class: a pattern + set of non-zero translators."""
    def __init__(self, pattern: List[Point], translators: Set[Vector], sub_tecs: Optional[List['TranslationalEquivalence']] = None):
        self.pattern = sorted(pattern)
        self.translators = translators
        self.sub_tecs = sub_tecs if sub_tecs is not None else []
    
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


def is_better_tec(tec1: TranslationalEquivalence, tec2: TranslationalEquivalence, dataset_points: Set[Point]) -> bool:
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