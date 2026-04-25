from . import Point
from .tec import TEC
from .siatec import siatec

from typing import List, Tuple


def cosiatec(dataset: List[Point], restrict_dpitch_zero: bool = False) -> List[TEC]:
    """
    COSIATEC greedy compression algorithm. 
    """
    points = set(dataset)
    remaining = set(dataset)
    tec_list = []
    while remaining:
        # compute all TECs on the remaining points
        pts_list = sorted(remaining)
        all_tecs = siatec(pts_list, restrict_dpitch_zero=restrict_dpitch_zero)
        if not all_tecs:
            # no more patterns -> output remaining as trivial TECs (single points)
            for p in remaining:
                tec_list.append(TEC([p], set()))
            break
        # select best TEC
        best = max(all_tecs, key=lambda tec: (tec.compression_ratio, tec.compactness(remaining), len(tec.coverage)))
        tec_list.append(best)
        # remove covered points
        remaining -= best.coverage
    return tec_list

def compress_to_encoding(tecs: List[TEC]) -> List[Tuple]:
    """
    Convert list of TECs to a human-readable encoding format.
    For each TEC: (pattern_points, list_of_translators)
    """
    encoding = []
    for tec in tecs:
        encoding.append((tec.pattern, list(tec.translators)))
    return encoding
