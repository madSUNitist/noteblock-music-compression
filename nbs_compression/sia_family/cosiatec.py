from .tec import TranslationalEquivalence
from . import Point, warn_python_impl_deco
from .siatec import build_tecs_from_mtps

from typing import List, Tuple


@warn_python_impl_deco(
    "COSIATEC is using the Python implementation (slower). "
    "For better performance, consider using the Rust implementation."
)
def cosiatec_compress(dataset: List[Point], restrict_dpitch_zero: bool = False) -> List[TranslationalEquivalence]:
    """
    COSIATEC greedy compression algorithm. 
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
        best = max(all_tecs, key=lambda tec: (tec.compression_ratio, tec.compactness(remaining), len(tec.coverage)))
        tec_list.append(best)
        # remove covered points
        remaining -= best.coverage
    return tec_list