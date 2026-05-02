from typing import Sequence, Tuple, Set, Optional, Dict

Point = Tuple[int, int]
Vector = Tuple[int, int]


class TranslationalEquivalence(object):
    """
    A translational equivalence class (TEC): a pattern together with a set of translation
    vectors that map the pattern onto other occurrences in the same dataset.

    Attributes:
        pattern: Sorted list of points `(tick, pitch)` forming the pattern.
        translators: Set of non‑zero translation vectors `(dtick, dpitch)` that map the pattern
            onto other points in the dataset.
        sub_tecs: List of child TECs obtained by recursively compressing the pattern
            (used only by `recursive_cosiatec_compress`).
    """
    
    pattern: Sequence[Point]
    translators: Set[Vector]
    sub_tecs: Sequence[TranslationalEquivalence]

    def __init__(self, pattern: Sequence[Point], translators: Set[Vector], sub_tecs: Optional[Sequence[TranslationalEquivalence]] = ...) -> None: 
        """
        Creates a new TEC.

        Args:
            pattern: The points forming the pattern (will be sorted automatically).
            translators: Non‑zero translation vectors.
            sub_tecs: Optional recursively compressed sub‑TECs for the pattern.
        """
        
    @property
    def coverage(self) -> Set[Point]: 
        """
        Returns the set of all points that belong to any occurrence of this TEC.

        This includes the pattern plus every translated copy `pattern + v` for each
        translator `v`. If the TEC has `sub_tecs`, their coverage is also merged.
        """
    
    @property
    def compression_ratio(self) -> float: 
        """
        Recursive compression ratio of this TEC.

        For a leaf TEC: `ratio = |coverage| / (|pattern| + |translators|)`.
        For a non‑leaf TEC: the denominator is `|translators|` plus the sum of
        encoding units of all sub‑TECs. Higher is better.
        """
        
    def compactness(self, points: Set[Point]) -> float: 
        """
        Compactness of the TEC with respect to a given point set.

        Compactness is defined as `|pattern| / (number of points in `points` that lie
        inside the axis‑aligned bounding box of the pattern)`. Higher compactness means
        the pattern occupies a relatively dense region of the dataset.

        Args:
            points: The reference point set (usually the remaining uncovered points in
                a compression step). If `sub_tecs` exist, the pattern of the whole subtree
                is used.

        Returns:
            A float between 0 and 1 (higher is better). Returns `0.0` if the pattern is empty.
        """

    def summary(self, indent: int = 0) -> str: 
        """
        Returns a human‑readable multi‑line summary of the TEC and its sub‑TECs.

        Args:
            indent: Number of spaces to prepend to each line (for nested display).
        """
    
    def __repr__(self) -> str: ...

def find_mtps(
    dataset: Sequence[Point], 
    restrict_dpitch_zero: bool = ...
) -> Dict[Vector, Sequence[Point]]: 
    """
    Finds all maximal translatable patterns (MTPs) in a 2‑D point set using the SIA algorithm.

    For every non‑zero translation vector `v`, the algorithm collects all starting points `p`
    such that both `p` and `p + v` belong to the dataset. The resulting groups (vector → list
    of start points) are the maximal translatable patterns.

    Args:
        dataset: A list of points `(tick, pitch)` with non‑negative coordinates.
        restrict_dpitch_zero: If `True`, only vectors with zero pitch difference are kept,
            i.e. purely temporal translations (horizontal repetition).

    Returns:
        A dictionary mapping each translation vector `(dtick, dpitch)` to a sorted list of
        start points that form the MTP for that vector. The zero vector `(0, 0)` is excluded,
        as are vectors that map fewer than two points.
    """

def build_tecs_from_mtps(
    dataset: Sequence[Point], 
    restrict_dpitch_zero: bool = ...
) -> Sequence[TranslationalEquivalence]: 
    """
    Builds translational equivalence classes (TECs) for every maximal translatable pattern (MTP)
    found by `find_mtps`.

    For each MTP (pattern + translation vector `v`), the function determines all translation
    vectors `w` such that `pattern + w` is entirely contained in the dataset. These `w` become
    the TEC's translator set.

    Args:
        dataset: A list of points `(tick, pitch)`.
        restrict_dpitch_zero: If `True`, only translation vectors with zero pitch difference
            are accepted (purely temporal shifts).

    Returns:
        A list of `TranslationalEquivalence` objects, one per distinct MTP. Patterns that have
        no translators (other than the zero vector) are omitted.
    """

def cosiatec_compress(
    dataset: Sequence[Point], 
    restrict_dpitch_zero: bool = ..., 
    sweepline_optimization: bool = ...
) -> Sequence[TranslationalEquivalence]: 
    """
    COSIATEC: greedy, iterative compression algorithm based on translational equivalence classes.

    The algorithm repeatedly runs SIATEC on the remaining uncovered points, selects the best
    TEC according to multi‑level comparison rules (compression ratio, compactness, coverage size,
    pattern size, temporal width, bounding box area), adds it to the result list, and removes
    its covered points. This continues until all points are covered. Any remaining points that
    cannot form a pattern are output as trivial single‑point TECs (empty translator set).

    Args:
        dataset: The full set of points `(tick, pitch)` to compress.
        restrict_dpitch_zero: If `True`, only translation vectors with zero pitch difference
            are considered (horizontal repetition only).
        sweepline_optimization: If `True`, use the sweepline‑based implementation of SIATEC
            (faster for large datasets). If `False`, use the original `O(n²)` implementation.

    Returns:
        A list of `TranslationalEquivalence` objects that partition the input points (each point
        appears in exactly one TEC). The `sub_tecs` field is not used in this base algorithm.
    """

def recursive_cosiatec_compress(
    dataset: Sequence[Point], 
    restrict_dpitch_zero: bool = ..., 
    min_pattern_size: int = ..., 
    sweepline_optimization: bool = ...
) -> Sequence[TranslationalEquivalence]: 
    """
    RECURSIA applied to COSIATEC: recursively compresses the pattern of each resulting TEC.

    This function first obtains a standard COSIATEC cover of the dataset. For each resulting TEC
    whose pattern contains at least `min_pattern_size` points, it recursively compresses that
    pattern using the same algorithm and stores the result in the TEC's `sub_tecs` field.
    After recursion, the original pattern field of the parent TEC is cleared (set to empty).

    Args:
        dataset: The full set of points `(tick, pitch)` to compress.
        restrict_dpitch_zero: If `True`, only purely temporal translations are allowed.
        min_pattern_size: Minimum number of points a pattern must contain to be considered
            for recursion. Patterns smaller than this are left unchanged.
        sweepline_optimization: If `True`, use the sweepline‑based implementation for each
            compression step.

    Returns:
        A list of top‑level `TranslationalEquivalence` objects. Each TEC may have a non‑empty
        `sub_tecs` field containing the recursively compressed version of its pattern, and its
        `pattern` field will be empty.
    """


def build_tecs_from_mtps_sweepline(
    dataset: Sequence[Point], 
    restrict_dpitch_zero: bool = ...
) -> Sequence[TranslationalEquivalence]: 
    """
    Sweepline‑based version of `build_tecs_from_mtps`.

    Uses a sweepline algorithm for exact translation matching, which is generally faster than
    the naive `O(n²)` approach. The MTP discovery still uses the standard SIA algorithm.

    **IMPORTANT:** The `dataset` MUST be lexicographically sorted by `(tick, pitch)` in
    ascending order. Unsorted input leads to incorrect results or infinite loops.
    Use `sorted(dataset)` before calling this function.

    Args:
        dataset: A **sorted** list of points `(tick, pitch)`.
        restrict_dpitch_zero: If `True`, only translation vectors with zero pitch difference
            are accepted.

    Returns:
        A list of `TranslationalEquivalence` objects, one per distinct MTP that has at least
        one translator. Patterns with fewer than 2 points are skipped.
    """
