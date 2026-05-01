from .tec import TranslationalEquivalence, tec_sort_key
from . import Point, warn_python_impl_deco
from .siatec import build_tecs_from_mtps

from typing import List, Sequence


@warn_python_impl_deco(
    "COSIATEC is using the Python implementation (slower). "
    "For better performance, consider using the Rust implementation."
)
def cosiatec_compress(dataset: List[Point], restrict_dpitch_zero: bool = False) -> Sequence[TranslationalEquivalence]:
    """
    COSIATEC: greedy lossless compression using SIATEC.

    Iteratively:
        1. Build all TECs from the remaining uncovered points.
        2. Select the "best" TEC according to the multi‑level ordering:
           (higher compression ratio, higher compactness, larger coverage,
            larger pattern size, smaller temporal width, smaller bbox area).
        3. Append it to the result and remove its covered points.
    When no TEC with at least one translator can be found, the remaining points
    are encoded as trivial TECs (single points, empty translators).

    Args:
        dataset: Input point set (list of (tick, pitch)).
        restrict_dpitch_zero: Passed to SIATEC; if True, only temporal shifts are allowed.

    Returns:
        A partition of the input points into TECs, ordered by the greedy selection.

    Note:
        The comparison key uses the *remaining* point set (not the full dataset)
        for compactness calculation, as required by the original definition.
    """  
    remaining = set(dataset)
    tec_list = []
    while remaining:
        # compute all TECs on the remaining points
        pts_list = sorted(remaining)
        all_tecs = build_tecs_from_mtps(pts_list, restrict_dpitch_zero=restrict_dpitch_zero)
        if not all_tecs:
            # no more patterns -> output remaining as trivial TECs (single points)
            for p in remaining:
                tec_list.append(TranslationalEquivalence([p], set()))
            break
        # select best TEC
        best = min(all_tecs, key=lambda tec: tec_sort_key(tec, remaining)) # XXX: `remaining`` OR `dataset`? 
        tec_list.append(best)
        # remove covered points
        remaining -= best.coverage
    return tec_list