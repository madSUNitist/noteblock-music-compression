from .sia_family import TranslationalEquivalence

from collections import defaultdict

import pynbs

from typing import List, Tuple, Callable, Set, Sequence


PITCH_BITS = 14
OFFSET = 1200

def notes_to_points(notes: List[pynbs.Note]) -> Tuple[List[Tuple[int, int]], defaultdict[Tuple[int, int], List[pynbs.Note]]]:
    """
    Utility functions for converting between NBS notes and points,
    rebuilding NBS files from TECs, merging small TECs, and computing
    compression statistics.

    The encoding scheme used in `notes_to_points`:
    - tick: the timestamp (integer, can be large).
    - pitch_cents = note.key * 100 + note.pitch
    - pitch_off = pitch_cents + OFFSET (OFFSET = 1200)
    - encoded_y = (instrument << PITCH_BITS) | pitch_off
    where PITCH_BITS = 14 ensures enough bits to store pitch offset.
    """
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

def merge_tecs(
    tecs: Sequence[TranslationalEquivalence],
    filter: Callable[[TranslationalEquivalence], bool] = lambda tec: len(tec.coverage) <= 10
) -> Sequence[TranslationalEquivalence]:
    """
    Merge all TECs satisfying `filter` into a single "miscellaneous" TEC.

    The merged TEC has:
    - pattern = union of all coverage points of the filtered TECs (sorted).
    - translators = empty set (it is not a true TEC, but a holder for notes).
    This reduces the number of layer blocks when there are many very small patterns.

    Args:
        tecs: Original list of TECs.
        filter: Predicate that determines which TECs to merge. Default merges
            TECs that cover at most 10 points.

    Returns:
        A new list where all filtered TECs are replaced by a single merged TEC
        at the end of the list. If no TEC satisfies the filter, the original list
        is returned unchanged.
    """
    to_merge = []
    to_keep = []
    for tec in tecs:
        if filter(tec):
            to_merge.append(tec)
        else:
            to_keep.append(tec)
    
    if not to_merge:
        return tecs  # no change
    
    # Collect all points from the TECs to be merged
    merged_points: Set[Tuple[int, int]] = set()
    for tec in to_merge:
        merged_points.update(tec.coverage)
    
    if not merged_points:
        # No points (shouldn't happen) – just keep originals
        return tecs
    
    # Sort points to get a deterministic pattern
    sorted_points = sorted(merged_points)
    merged_tec = TranslationalEquivalence(
        pattern=sorted_points,
        translators=set(),      # no translators
        sub_tecs=None
    )
    
    return to_keep + [merged_tec]

def tecs_to_nbs(
    tecs: Sequence[TranslationalEquivalence],
    note_dict: defaultdict[Tuple[int, int], List[pynbs.Note]],
    header: dict
) -> pynbs.File:
    """
    Reconstruct an NBS file from a list of TECs.

    Layers are allocated as follows:
    - Each TEC gets a block of consecutive layers.
    - The block size = (max concurrency within the TEC's coverage) + 1.
    - The "+1" adds an empty separator layer (optional, reduces seam artifacts).
    Notes from the same tick within a TEC are assigned to different layers
    to avoid collisions (polyphony support).

    Args:
        tecs: List of TECs (already merged if desired). The order determines layer order.
        note_dict: Mapping from (tick, encoded_pitch) to the original Note objects.
            This is required because the TEC only stores coordinates, not instrument/volume etc.
        header: Original NBS header dictionary (e.g., `song.header.__dict__`).

    Returns:
        A pynbs.File object with all notes placed in the computed layers.
    """
    # All TECs are treated as multi_tecs (no special single‑point handling)
    multi_tecs = tecs

    # Compute max concurrency per TEC
    tec_concurrency = []
    for tec in multi_tecs:
        coverage = tec.coverage
        if not coverage:
            tec_concurrency.append(0)
            continue
        tick_counts: defaultdict[int, int] = defaultdict(int)
        for p in coverage:
            tick_counts[p[0]] += len(note_dict[p])
        max_count = max(tick_counts.values()) if tick_counts else 0
        tec_concurrency.append(max_count)

    # Compute layer start offsets for each TEC
    layer_offsets = []
    current = 0
    for conc in tec_concurrency:
        layer_offsets.append(current)
        current += conc + 1   # +1 leaves an empty layer as separator (optional)

    # Collect all notes
    all_notes = []

    # Process each TEC
    for tec_idx, tec in enumerate(multi_tecs):
        offset = layer_offsets[tec_idx]
        coverage = tec.coverage
        if not coverage:
            continue
        # Group coverage points by tick
        tick_groups = defaultdict(list)
        for p in coverage:
            tick = p[0]
            original_notes = note_dict[p]
            for note in original_notes:
                tick_groups[tick].append((p[1], note))
        for tick, items in tick_groups.items():
            # Sort by encoded pitch (y) to get deterministic layer order
            items_sorted = sorted(items, key=lambda x: x[0])
            for local_layer, (_, note) in enumerate(items_sorted):
                note.layer = offset + local_layer
                all_notes.append(note)

    # Sort notes by tick (required by NBS format)
    all_notes.sort(key=lambda note: note.tick)

    # Create the new NBS file
    new_file = pynbs.new_file(**header)
    new_file.layers = [pynbs.Layer(i, "", False, 100, 0) for i in range(current)]
    new_file.notes = all_notes
    return new_file


def compression_stats(tecs: Sequence[TranslationalEquivalence], original_points: List[Tuple[int, int]]) -> dict:
    """
    Calculate compression statistics for a list of TECs.

    Args:
        tecs: List of TranslationalEquivalence objects (possibly with nested sub_tecs)
        original_points: The original point set before compression

    Returns:
        A dictionary with keys:
        - 'original_count': number of original points
        - 'encoded_units': total number of units after compression
        - 'compression_ratio': original_count / encoded_units
    """
    def _count_units(tec_list):
        units = 0
        for t in tec_list:
            units += len(t.translators)
            if t.sub_tecs:
                units += _count_units(t.sub_tecs)
            else:
                units += len(t.pattern)
        return units

    original = len(original_points)
    encoded = _count_units(tecs)
    ratio = original / encoded if encoded > 0 else 0.0
    return {
        "original_count": original,
        "encoded_units": encoded,
        "compression_ratio": ratio,
    }