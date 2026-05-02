from .tec import TranslationalEquivalence
from . import Point, warn_python_impl_deco
from .cosiatec import cosiatec_compress

from typing import List, Sequence


@warn_python_impl_deco(
    "RecurSIA-COSIATEC is using the Python implementation (slower). "
    "For better performance, consider using the Rust implementation."
)
def recursive_cosiatec_compress(
    dataset: List[Point],
    restrict_dpitch_zero: bool = False,
    min_pattern_size: int = 2, 
    sweepline_optimization: bool = True
) -> Sequence[TranslationalEquivalence]:
    """
    RecurSIA‑COSIATEC: recursively compress patterns uncovered by COSIATEC.

    Steps:
        1. Obtain a top‑level COSIATEC cover (non‑recursive) of `dataset`.
        2. For each resulting TEC:
            - If its pattern size >= min_pattern_size, recursively compress the pattern
              using the same function and store the result in `tec.sub_tecs`.
            - The pattern of the TEC is then cleared (since the sub‑TECs represent it).

    This hierarchy can reveal nested repetitions and often improves compression ratio.

    Args:
        dataset: Input point set.
        restrict_dpitch_zero: Passed to COSIATEC at each recursion level.
        min_pattern_size: Minimum number of points a pattern must have to be
            recursively compressed. Setting this to 1 would recurse infinitely,
            so the interpreter must avoid that (default 2 is safe).
        sweepline_optimization: Whether to use the sweepline optimized implementation.

    Returns:
        A list of top‑level TECs, each possibly containing sub‑TECs.
    """
    # 1. Obtain the top‑level COSIATEC cover (without recursion)
    tecs = cosiatec_compress(
        dataset, 
        restrict_dpitch_zero=restrict_dpitch_zero, 
        sweepline_optimization=sweepline_optimization
    )

    # 2. Recursively compress the pattern of each TEC
    for tec in tecs:
        if len(tec.pattern) >= min_pattern_size:
            tec.sub_tecs = recursive_cosiatec_compress(
                tec.pattern,
                restrict_dpitch_zero=restrict_dpitch_zero,
                min_pattern_size=min_pattern_size, 
                sweepline_optimization=sweepline_optimization
            )
            tec.pattern.clear()
        else:
            tec.sub_tecs = []

    return tecs