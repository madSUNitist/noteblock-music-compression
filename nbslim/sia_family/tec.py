from . import Point, Vector

from typing import List, Set, Optional, Tuple

class TranslationalEquivalence(object):    
    """Translational Equivalence Class: a pattern + set of non-zero translators."""
    def __init__(self, pattern: List[Point], translators: Set[Vector], sub_tecs: Optional[List['TranslationalEquivalence']] = None):
        self.pattern = sorted(pattern)
        self.translators = translators
        self.sub_tecs = sub_tecs if sub_tecs is not None else []
        
    @property
    def coverage(self) -> Set[Point]:
        """
        Recursive covered set.

        Returns the union of:
        - pattern points,
        - all sub-tecs' coverage,
        - and their translations by every translator vector.
        """
        sub_cov = set(self.pattern)
        for sub in self.sub_tecs:
            sub_cov.update(sub.coverage)

        cov = set(sub_cov)
        for dx, dy in self.translators:
            for x, y in sub_cov:
                cov.add((x + dx, y + dy))

        return cov

    @property
    def compression_ratio(self) -> float:
        """
        Recursive compression ratio = coverage size / total encoding units.
        - For a leaf TEC (no sub_tecs), total = |pattern| + |translators|.
        - For a non-leaf TEC, total = |translators| + sum(compression units of sub_tecs).
        """        
        def _total_encoding_units(tec) -> int:
            if tec.sub_tecs:
                # Non-leaf: pattern is encoded by sub_tecs, so only translators count directly
                units = len(tec.translators)
                for sub in tec.sub_tecs:
                    units += _total_encoding_units(sub)
                return units
            else:
                # Leaf: pattern points + translators
                return len(tec.pattern) + len(tec.translators)

        
        cov_size = len(self.coverage)
        total_units = _total_encoding_units(self)
        return cov_size / total_units if total_units != 0 else 0.0

    def compactness(self, points: Set[Point]) -> float:
        """
        Recursive bounding-box compactness.
        - If sub_tecs exist, merge all leaf pattern points from the subtree,
        then compute compactness of that merged point set.
        - Otherwise, compute compactness from self.pattern directly.
        """
        # Helper to recursively collect all leaf pattern points
        pattern_set = self.coverage
        if not pattern_set:
            return 0.0
        
        xs = [p[0] for p in pattern_set]
        ys = [p[1] for p in pattern_set]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        count = 0
        for p in points:
            if min_x <= p[0] <= max_x and min_y <= p[1] <= max_y:
                count += 1
        if count == 0:
            return 0.0
        return len(pattern_set) / count

    def __repr__(self):
        return f"TEC(pattern={self.pattern}, translators={self.translators}, sub_tecs={self.sub_tecs.__repr__()})"

    def summary(self, indent: int=0) -> str:
        """
        Recursively generate a formatted string summarizing the TEC.

        Args:
            indent: Number of spaces per indentation level (default 2).

        Returns:
            A multi-line string with the TEC's pattern, translators, coverage count,
            compression ratio, and any sub-TECs.
        """
        lines = []
        spaces = " " * indent
        if self.pattern:
            lines.append(f"{spaces}pattern={self.pattern}, translators={self.translators}")
        else:
            lines.append(f"{spaces}translators={self.translators}")
        lines.append(f"{spaces}  coverage count: {len(self.coverage)}")
        lines.append(f"{spaces}  compression ratio: {self.compression_ratio:.3f}")
        if self.sub_tecs:
            lines.append(f"{spaces}  sub-tecs:")
            for sub in self.sub_tecs:
                # Recursively call summary with one extra indent level
                sub_summary = sub.summary(indent + 2)
                # Remove the first line's indent? We'll just append as is.
                lines.append(sub_summary)
                
        return "\n".join(lines)


def tec_sort_key(tec: TranslationalEquivalence, dataset_points: Set[Point]) -> Tuple[float, float, int, int, int, int]:
    """
    Return a sortable key tuple that follows the ISBETTERTEC rules.
    
    Lower key means better TEC.
    """
    cr = tec.compression_ratio
    comp = tec.compactness(dataset_points)
    cov_len = len(tec.coverage)
    pat_len = len(tec.pattern)
    width = max(p[0] for p in tec.pattern) - min(p[0] for p in tec.pattern)
    x_range = max(p[0] for p in tec.pattern) - min(p[0] for p in tec.pattern)
    y_range = max(p[1] for p in tec.pattern) - min(p[1] for p in tec.pattern)
    area = x_range * y_range
    # For descending fields, store negative; for ascending fields, store positive.
    return (-cr, -comp, -cov_len, -pat_len, width, area)