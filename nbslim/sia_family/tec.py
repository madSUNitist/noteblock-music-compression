"""
Translational Equivalence Class (TEC) data structure.

A TEC represents a set of points (the *pattern*) together with a set of non‑zero
translation vectors (the *translators*). Every translation of the pattern by any
translator yields another occurrence that is also present in the original dataset.
TECs are the core building block for SIATEC, COSIATEC and RecurSIA algorithms.

TECs can be nested: when recursion is applied, the `sub_tecs` field holds a list
of TECs that encode the pattern itself. This allows representing hierarchical
repetitions (e.g., a phrase that repeats, whose internal motifs also repeat).

The coverage of a TEC is the union of:
- its pattern points,
- the coverage of all its sub‑TECs,
- and all translations of the above by every translator in `translators`.

Compression ratio and compactness are computed recursively to reflect the
full hierarchical structure.
"""

from . import Point, Vector

from typing import List, Set, Optional, Tuple, Sequence

class TranslationalEquivalence(object):
    """
    Translational Equivalence Class (TEC).

    A TEC represents a set of points (pattern) that repeats within the dataset
    via a set of non‑zero translation vectors (translators). Formally,
    for pattern P and translators T, the TEC covers all points
    { p + v | p ∈ P, v ∈ T ∪ {0} }.

    This class supports recursion: if the pattern itself was discovered by
    compressing a larger pattern, `sub_tecs` holds the inner TECs and the
    `pattern` field may be cleared to avoid duplication. This enables
    hierarchical compression (e.g., RecurSIA).

    Attributes:
        pattern (List[Point]): Sorted list of points forming the base pattern.
            For non‑leaf TECs (with sub_tecs), this list is usually empty.
        translators (Set[Vector]): Non‑zero translation vectors (dtick, dpitch)
            that map the pattern onto other occurrences.
        sub_tecs (List[TranslationalEquivalence]): Recursively compressed
            representations of the pattern (empty for leaf TECs).

    Example:
        >>> pattern = [(0, 60), (2, 64)]
        >>> translators = {(4, 0), (8, 0)}
        >>> tec = TranslationalEquivalence(pattern, translators)
        >>> sorted(tec.coverage)
        [(0, 60), (2, 64), (4, 60), (6, 64), (8, 60), (10, 64)]
        >>> print(f"{tec.compression_ratio:.2f}")
        2.00
    """
    
    def __init__(self, pattern: List[Point], translators: Set[Vector], sub_tecs: Optional[Sequence['TranslationalEquivalence']] = None):
        """
        Initialise a TranslationalEquivalence.

        The pattern will be sorted automatically. `sub_tecs` defaults to an
        empty list if not provided.

        Args:
            pattern: The base pattern points. May be empty when recursion is used.
            translators: All non‑zero translation vectors that map the pattern
                into the dataset.
            sub_tecs: Optional list of inner TECs representing a compressed
                form of the pattern (used by RecurSIA).

        Note:
            For correctness, the translator set should not contain the zero
            vector, but this constructor does not enforce it.
        """
        self.pattern = sorted(pattern)
        self.translators = translators
        self.sub_tecs = sub_tecs if sub_tecs is not None else []
        
    @property
    def coverage(self) -> Set[Point]:
        """
        Compute the set of all points covered by this TEC, recursively.

        The covered set is defined as:
            Let S = pattern ∪ (union of coverage of all sub_tecs).
            Then coverage = S ∪ { p + v | p ∈ S, v ∈ translators }.

        Returns:
            Set of all points (tick, pitch) that belong to any occurrence of
            the pattern or its sub‑patterns.
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
        Recursive compression ratio of this TEC.

        For a leaf TEC (no sub_tecs):
            ratio = |coverage| / (|pattern| + |translators|)

        For a non‑leaf TEC:
            The pattern itself is not stored; instead it is represented by
            the sub_tecs. Therefore:
            total_encoding_units = |translators| + Σ(units of each sub_tec)
            ratio = |coverage| / total_encoding_units

        Returns:
            A float >= 1.0 if compression is beneficial, but it can be < 1.0
            for trivial patterns (e.g., single‑point TEC). Higher is better.

        Note:
            This ratio is used in the multi‑level sorting to select the best
            TEC during greedy compression (COSIATEC).
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
        Recursive bounding‑box compactness.

        Define the pattern set as:
        - If sub_tecs exists: union of coverage of all sub_tecs.
        - Else: self.pattern.

        Then compactness = (size of pattern set) / (number of points from `points`
        that lie inside the axis‑aligned bounding box of the pattern set).

        Args:
            points: The full dataset (or relevant subset) as a set of (tick, pitch).

        Returns:
            A float in [0, 1]. Returns 0.0 if the pattern set or its bounding
            box is empty. Higher compactness indicates that the pattern
            occupies a dense region relative to the surrounding notes.

        Note:
            For leaf TECs, the pattern set is simply `self.pattern`.
            For non‑leaf TECs, it includes coverage of all sub‑TECs.
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

    def summary(self, indent: int=0) -> str:
        """
        Recursively generate a formatted summary of the TEC.

        Args:
            indent: Number of spaces per indentation level (default 0).
                Each level adds `indent` spaces.

        Returns:
            A multi‑line string containing the pattern (if any), translators,
            coverage count, compression ratio, and any sub‑TECs.
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

    def __repr__(self):
        return f"TEC(pattern={self.pattern}, translators={self.translators}, sub_tecs={self.sub_tecs.__repr__()})"


def tec_sort_key(tec: TranslationalEquivalence, dataset_points: Set[Point]) -> Tuple[float, float, int, int, int, int]:
    """
    Return a sortable key tuple that follows the ISBETTERTEC comparison rules.

    Lower key means a **better** TEC. The ordering priority (from most to least
    important) is:

        1. Higher compression ratio
        2. Higher compactness
        3. Larger coverage size
        4. Larger pattern size
        5. Smaller temporal width (Δtick range)
        6. Smaller bounding‑box area (Δtick * Δpitch)

    Args:
        tec: The TranslationalEquivalence to evaluate.
        dataset_points: The set of points in the dataset (used for compactness).

    Returns:
        A tuple where the first two elements are negated to achieve descending
        order for those fields. The tuple is comparable using default ordering.

    Note:
        The pattern size and coverage are taken from the leaf‑level pattern
        (if sub_tecs exist, the pattern is the union of leaf patterns).
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