from .sia_family.point import Point
from .sia_family.tec import TEC

from collections import defaultdict

import pynbs

from typing import List


def notes_to_points(notes):
    return [Point(tick, key, instrument) for tick, key, instrument in notes]

def tecs_to_nbs(tecs: List[TEC], header: dict) -> pynbs.File:
    """
    Convert TECs to NBS file with layer blocks per TEC.
    Each TEC gets a contiguous block of layers.
    Notes are sorted by tick before saving.
    """
    # 1. Compute max concurrency per TEC
    tec_concurrency = []
    for tec in tecs:
        coverage = tec.coverage
        if not coverage:
            tec_concurrency.append(0)
            continue
        tick_counts = defaultdict(int)
        for p in coverage:
            tick_counts[p.tick] += 1
        max_count = max(tick_counts.values())
        tec_concurrency.append(max_count)

    # 2. Compute layer start offsets
    layer_offsets = []
    current = 0
    for conc in tec_concurrency:
        layer_offsets.append(current)
        current += conc

    # 3. Collect all notes
    all_notes = []
    for tec_idx, tec in enumerate(tecs):
        offset = layer_offsets[tec_idx]
        tick_groups = defaultdict(list)
        for p in tec.coverage:
            tick_groups[p.tick].append(p)
        for tick, points in tick_groups.items():
            points_sorted = sorted(points, key=lambda p: p.instrument)
            for local_layer, p in enumerate(points_sorted):
                layer = offset + local_layer
                note = pynbs.Note(
                    tick=tick,
                    layer=layer,
                    instrument=p.instrument,
                    key=p.key,
                    velocity=100,
                    panning=0,
                    pitch=0
                )
                all_notes.append(note)

    # 4. Sort notes by tick (required by NBS format)
    all_notes.sort(key=lambda note: note.tick)

    # 5. Create NBSFile and assign notes
    new_file = pynbs.new_file(**header)
    new_file.notes = all_notes
    return new_file