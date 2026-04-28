from .tec import TEC
from . import Point, warn_python_impl_deco
from .siatec import siatec

from typing import List


@warn_python_impl_deco(
    "RecurSIA-COSIATEC is using the Python implementation (slower). "
    "For better performance, consider using the Rust implementation."
)
def recur_sia_cosiatec(dataset: List[Point], 
                       restrict_dpitch_zero: bool = False,
                       min_pattern_size: int = 2) -> List[TEC]:
    """
    RecurSIA applied to COSIATEC: recursively compress patterns.
    
    Args:
        dataset: input point set
        restrict_dpitch_zero: if True, only allow temporal translation (Δpitch=0)
        min_pattern_size: patterns smaller than this are not recursively compressed
    
    Returns:
        List of TECs, where each TEC's pattern may have been recursively compressed,
        stored in TEC.sub_tecs.
    """    
    remaining = set(dataset)
    tec_list = []
    
    while remaining:
        # 1. Find best TEC
        pts_list = sorted(remaining)
        all_tecs = siatec(pts_list, restrict_dpitch_zero=restrict_dpitch_zero)
        if not all_tecs:
            # No pattern found
            for p in remaining:
                tec_list.append(TEC([p], set()))
            break
        
        # 2. Select best TEC
        best = max(all_tecs, key=lambda tec: (
            tec.compression_ratio, 
            tec.compactness(remaining), 
            len(tec.coverage)
        ))
        
        # 3. Recursion
        if len(best.pattern) >= min_pattern_size:
            sub_tecs = recur_sia_cosiatec(best.pattern, 
                                          restrict_dpitch_zero=restrict_dpitch_zero,
                                          min_pattern_size=min_pattern_size)
            best.sub_tecs = sub_tecs
        else:
            best.sub_tecs = []
        
        tec_list.append(best)
        # 4. Remove best coverage
        remaining -= best.coverage
    
    return tec_list