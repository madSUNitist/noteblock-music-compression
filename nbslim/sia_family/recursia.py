from .tec import TranslationalEquivalence
from . import Point, warn_python_impl_deco
from .cosiatec import cosiatec_compress

from typing import List


@warn_python_impl_deco(
    "RecurSIA-COSIATEC is using the Python implementation (slower). "
    "For better performance, consider using the Rust implementation."
)
def recursive_cosiatec_compress(
    dataset: List[Point],
    restrict_dpitch_zero: bool = False,
    min_pattern_size: int = 2
) -> List[TranslationalEquivalence]:
    """
    RecurSIA applied to COSIATEC: recursively compress patterns.

    First obtains a standard COSIATEC cover (non‑recursive), then recursively
    compresses the pattern of each resulting TEC if it is large enough.

    Args:
        dataset: input point set
        restrict_dpitch_zero: if True, only allow temporal translation (Δpitch=0)
        min_pattern_size: patterns smaller than this are not recursively compressed

    Returns:
        List of TECs, where each TEC's pattern may have been recursively compressed
        and stored in TEC.sub_tecs.
    """
    # 1. Obtain the top‑level COSIATEC cover (without recursion)
    tecs = cosiatec_compress(dataset, restrict_dpitch_zero=restrict_dpitch_zero)

    # 2. Recursively compress the pattern of each TEC
    for tec in tecs:
        if len(tec.pattern) >= min_pattern_size:
            tec.sub_tecs = recursive_cosiatec_compress(
                tec.pattern,
                restrict_dpitch_zero=restrict_dpitch_zero,
                min_pattern_size=min_pattern_size
            )
            tec.pattern.clear()
        else:
            tec.sub_tecs = []

    return tecs