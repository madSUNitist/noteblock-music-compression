from .sia_family.tec import TranslationalEquivalence

from collections import defaultdict

import pynbs

from typing import List, Tuple, Callable, Set


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

def merge_tecs(
    tecs: List[TranslationalEquivalence],
    filter: Callable[[TranslationalEquivalence], bool] = lambda tec: len(tec.coverage) <= 10
) -> List[TranslationalEquivalence]:
    """
    Merge all TECs that satisfy the filter into a single TEC containing all their coverage points.
    
    The merged TEC has no translators (i.e., it is not a true TEC) and is used only for
    reconstruction. It helps avoid many tiny TECs that would each occupy a small layer block.
    
    Args:
        tecs: List of TECs.
        filter: A callable that returns True for TECs that should be merged (default: coverage size <= 10).
        
    Returns:
        A new list of TECs where all filtered TECs are replaced by a single merged TEC.
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
    tecs: List[TranslationalEquivalence],
    note_dict: defaultdict[Tuple[int, int], List[pynbs.Note]],
    header: dict
) -> pynbs.File:
    """
    Convert TECs to NBS file with layer blocks per TEC.
    
    Each TEC gets a contiguous block of layers. The number of layers allocated
    for a TEC is (max concurrency of its coverage) + 1.
    
    If you want to merge many small TECs into one block, call `merge_tecs` first.
    
    Args:
        tecs: List of TECs (already merged if desired).
        note_dict: Mapping from (tick, encoded_pitch) to list of original Note objects.
        header: Original NBS header (as a dict) to reuse song metadata.
        
    Returns:
        A pynbs.File object with notes placed in appropriate layers.
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


def compression_stats(tecs: List[TranslationalEquivalence], original_points: List[Tuple[int, int]]) -> dict:
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