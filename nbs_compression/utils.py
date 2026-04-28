from .sia_family import Point
from .sia_family.tec import TranslationalEquivalence

from collections import defaultdict

import pynbs

from typing import List, Tuple


PITCH_BITS = 14
OFFSET = 1200

def notes_to_points(notes: List[pynbs.Note]) -> Tuple[List[Tuple[int, int]], defaultdict[Tuple[int, int], List[pynbs.Note]]]:
    points = []
    mapping = defaultdict(list)

    for note in notes:
        tick = note.tick
        pitch_cents = note.key * 100 + note.pitch
        pitch_off = pitch_cents + OFFSET
        encoded_y = (note.instrument << PITCH_BITS) | pitch_off
        point = (tick, encoded_y)
        points.append(point)
        mapping[point].append(note)

    return points, mapping


def tecs_to_nbs(tecs: List[TranslationalEquivalence], note_dict: defaultdict[Tuple[int, int], List[pynbs.Note]], header: dict) -> pynbs.File:
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
        tick_counts: defaultdict[int, int] = defaultdict(int)
        for p in coverage:
            tick_counts[p[0]] += len(note_dict[p])
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
        coverage = tec.coverage
        if not coverage:
            continue
        # group by tick
        tick_groups = defaultdict(list)
        for p in coverage:
            tick = p[0]
            original_notes = note_dict[p]
            for note in original_notes:
                tick_groups[tick].append((p[1], note))
        for tick, items in tick_groups.items():
            # Sort points by encoded key to get deterministic layer assignment
            items_sorted = sorted(items, key=lambda x: x[0])
            for local_layer, (_, note) in enumerate(items_sorted):
                note.layer = offset + local_layer
                all_notes.append(note)

    # 4. Sort notes by tick (required by NBS format)
    all_notes.sort(key=lambda note: note.tick)

    # 5. Create NBSFile and assign notes
    new_file = pynbs.new_file(**header)
    new_file.notes = all_notes
    return new_file