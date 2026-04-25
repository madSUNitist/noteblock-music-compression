from .point import Point, Vector

from typing import List, Set, Optional

class TEC(object):
    """Translational Equivalence Class: a pattern + set of non-zero translators."""
    def __init__(self, pattern: List[Point], translators: Set[Vector], sub_tecs: Optional[List['TEC']] = None):
        self.pattern = sorted(pattern)
        self.translators = translators
        self.sub_tecs = sub_tecs if sub_tecs is not None else []
    
    @property
    def coverage(self) -> Set[Point]:
        """Covered set = pattern ∪ all translated copies."""
        cov = set(self.pattern)
        for v in self.translators:
            for p in self.pattern:
                cov.add(Point(p.tick + v[0], p.key + v[1], p.instrument))
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
        xs = [p.tick for p in self.pattern]
        ys = [p.key for p in self.pattern]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        # count points in the dataset that fall inside this bounding box
        count = 0
        for p in points:
            if min_x <= p.tick <= max_x and min_y <= p.key <= max_y:
                count += 1
        if count == 0:
            return 0.0
        return len(self.pattern) / count

    def __repr__(self):
        return f"TEC(pattern={self.pattern}, translators={self.translators})"

