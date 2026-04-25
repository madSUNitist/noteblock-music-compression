def parse_to_columns(data):
    """
    data: list of (tick, pitch)
    returns: list of tuples, each tuple is sorted pitches in that tick
    """
    from collections import defaultdict
    tick_map = defaultdict(list)
    for tick, pitch in data:
        tick_map[tick].append(pitch)
    # sort by tick
    ticks = sorted(tick_map.keys())
    columns = []
    for t in ticks:
        pitches = sorted(tick_map[t])
        columns.append(tuple(pitches))
    return columns, ticks

def lz77_compress(seq, window_size=256, min_match=1):
    """
    LZ77 compression on a sequence of hashable objects.
    Returns list of tokens.
    Each token: either ('lit', index, value) or ('match', start_pos, distance, length)
    Also returns sequence of original indices for reference.
    """
    n = len(seq)
    i = 0
    tokens = []
    while i < n:
        # search for longest match in window
        best_len = 0
        best_dist = 0
        start = max(0, i - window_size)
        for j in range(start, i):
            length = 0
            while i + length < n and j + length < i and seq[i+length] == seq[j+length]:
                length += 1
            if length > best_len:
                best_len = length
                best_dist = i - j
        if best_len >= min_match:
            tokens.append(('match', i, best_dist, best_len))
            i += best_len
        else:
            tokens.append(('lit', i, seq[i]))
            i += 1
    return tokens

def decode_tokens(tokens):
    """For debugging: reconstruct sequence from tokens (optional)"""
    reconstructed = []
    for tok in tokens:
        if tok[0] == 'lit':
            reconstructed.append(tok[2])
        else:
            _, start, dist, length = tok
            start_ref = start - dist
            for k in range(length):
                reconstructed.append(reconstructed[start_ref + k])
    return reconstructed