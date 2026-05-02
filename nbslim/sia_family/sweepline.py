"""
Sweepline-based pattern matching and translation equivalence construction.

This module implements a sweepline algorithm for exact translation matching between
a **sorted** dataset of points (tick, pitch) and a sorted pattern. It is used to discover
translational equivalences (TECs) by first finding maximal translatable patterns (MTPs)
and then verifying all translations that embed the pattern into the dataset.
"""

from typing import List, Tuple, Set
from .sia import find_mtps
from .tec import TranslationalEquivalence


def exact_match_pattern(
    dataset: List[Tuple[int, int]],
    pattern: List[Tuple[int, int]],
    restrict_dpitch_zero: bool = False,
) -> Set[Tuple[int, int]]:
    """
    Finds all translation vectors `w` such that `pattern + w` is entirely contained in `dataset`.

    **IMPORTANT**: `dataset` MUST be lexicographically sorted by `(tick, pitch)` in ascending order.
    The same applies to `pattern`. Passing an unsorted list leads to incorrect results.

    Implements Ukkonen et al. Algorithm 1 (sweepline exact matching).

    Args:
        dataset: A **lexicographically sorted** list of points `(tick, pitch)`.
        pattern: A **lexicographically sorted** list of points forming the pattern.
        restrict_dpitch_zero: If `True`, only translations with zero pitch difference are returned.

    Returns:
        A set of non‑zero translation vectors `(dtick, dpitch)` that map the pattern into the dataset.
    """
    # Optional debug checks (can be removed in production)
    assert all(dataset[i] <= dataset[i + 1] for i in range(len(dataset) - 1)), \
        "dataset must be lexicographically sorted"
    assert all(pattern[i] <= pattern[i + 1] for i in range(len(pattern) - 1)), \
        "pattern must be lexicographically sorted"

    m = len(pattern)
    n = len(dataset)
    if m < 2 or n < m:
        return set()

    # q[i] holds the next candidate index in dataset for pattern[i]
    q = [0] * m
    p0_tick, p0_pitch = pattern[0]
    translators = set()

    # Main loop: only consider dataset points that can possibly be the image of pattern[0]
    for j in range(n - m + 1):
        tj, pj = dataset[j]
        if restrict_dpitch_zero and pj != p0_pitch:
            continue

        f = (tj - p0_tick, pj - p0_pitch)
        if f == (0, 0) or (restrict_dpitch_zero and f[1] != 0):
            continue

        # q[0] should be at least j
        q[0] = max(q[0], j)
        matched = True

        for idx in range(1, m):
            # target point = pattern[idx] + f
            target = (
                pattern[idx][0] + f[0],
                pattern[idx][1] + f[1],
            )
            # Advance pointer to the first dataset point >= target
            ptr = max(q[idx], q[idx - 1])
            while ptr < n and dataset[ptr] < target:
                ptr += 1
            q[idx] = ptr
            if ptr >= n or dataset[ptr] != target:
                matched = False
                break

        if matched:
            translators.add(f)

    return translators


def build_tecs_from_mtps(
    dataset: List[Tuple[int, int]],
    restrict_dpitch_zero: bool = False,
) -> List[TranslationalEquivalence]:
    """
    Builds translational equivalences (TECs) using sweepline both for MTP discovery and exact matching.

    This function first calls `find_mtps` to obtain a set of maximal translatable patterns (MTPs)
    from the dataset. For each such pattern (except the trivial zero translation), it then computes
    all translation vectors that map the pattern into the dataset using `exact_match_pattern`.
    The resulting `(pattern, translation_set)` pairs are wrapped into `TranslationalEquivalence`
    structures and returned as a list.

    Args:
        dataset: A **lexicographically sorted** list of points `(tick, pitch)`.
        restrict_dpitch_zero: If `True`, only translations with zero pitch difference are considered.

    Returns:
        A list of `TranslationalEquivalence` objects, each containing a pattern and the set of
        translations that embed it into the dataset.
    """
    mtps = find_mtps(dataset, restrict_dpitch_zero)
    tecs = []

    for v, pattern in mtps.items():
        if v == (0, 0) or len(pattern) < 2:
            continue
        translators = exact_match_pattern(dataset, pattern, restrict_dpitch_zero)
        if translators:
            tecs.append(TranslationalEquivalence(pattern, translators, None))

    return tecs