from .sia import find_mtps
from .tec import TranslationalEquivalence
from . import Point, warn_python_impl_deco

from typing import List, Set


@warn_python_impl_deco(
    "SIATEC algorithm: using Python implementation (slower). "
    "For better performance, consider using the Rust implementation."
)
def build_tecs_from_mtps(dataset: List[Point], restrict_dpitch_zero: bool = False) -> List[TranslationalEquivalence]:
    """
    SIATEC algorithm: for each MTP find its TEC (all occurrences).
    Returns a list of TECs (one per MTP).
    """
    points = set(dataset)
    mtps = find_mtps(dataset, restrict_dpitch_zero=restrict_dpitch_zero)  # vector -> list of starting points
    tecs = []
    for v, start_pts in mtps.items():
        if v == (0, 0):
            continue
        # The pattern is the set of points from the first occurrence? Actually the MTP
        # is the set of points that can be translated. But the MTP includes all points
        # that have a partner by v. However, we need a single pattern (the smallest?).
        # In original SIA, the MTP for v is the set of points p such that p+v in D.
        # But that set may include points that are not connected via v.
        # The typical way: the pattern is the set of start points (which are the points
        # that have a translation by v). That set itself is a pattern. Then all its
        # occurrences are the translations of that pattern by multiples of v?
        # Actually easier: For each v, the TEC is the set of all translations of the
        # pattern (the pattern is the set of points that can be mapped by v onto other
        # points). But we need to find all distinct patterns (occurrences) in the TEC.
        # In the paper, they compute the TEC of the MTP by intersecting columns in the
        # vector table. Let's implement a simplified but correct version:
        #
        # Given an MTP pattern P (the set of start points for vector v), the TEC contains
        # all occurrences of P in the dataset. That is, all sets Q such that Q = P + w
        # for some w and Q ⊆ D.
        #
        # So we need to find all w such that P + w ⊆ D.
        pattern = sorted(start_pts)   # pattern = set of points that can be translated by v
        # Find all translation vectors w that map pattern into D
        # For a candidate w, we need that for every p in pattern, p+w in D.
        # The possible w are differences between any point in D and the first point in pattern.
        if not pattern:
            continue
        
        p0 = pattern[0]
        candidates = set()
        for q in dataset:
            w = (q[0] - p0[0], q[1] - p0[1])
            candidates.add(w)
        
        translators = set()
        for w in candidates:
            if w == (0,0):
                continue

            if restrict_dpitch_zero and w[1] != 0:
                continue

            ok = True
            for p in pattern:
                pp = (p[0] + w[0], p[1] + w[1])
                if pp not in points:
                    ok = False
                    break
            if ok:
                translators.add(w)

        if translators:
            tecs.append(TranslationalEquivalence(pattern, translators))

    return tecs
