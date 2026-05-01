[English](README.md) | 简体中文

# NBSlim

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/nbslim.svg)](https://pypi.org/project/nbslim/)
[![Rust](https://img.shields.io/badge/rust-1.95.0%2B-blue.svg)](https://www.rust-lang.org)
[![build](https://img.shields.io/github/actions/workflow/status/madSUNitist/NBSlim/main.yaml?branch=main)](https://github.com/madSUNitist/NBSlim/actions)

Created for efficient implementation of logic redstone music by [@kemiamu](https://space.bilibili.com/3494363168508256).

A tool for compressing Note Block Studio (.nbs) music files to efficiently store and play polyphonic music in Minecraft.

By discovering and compressing repetitive patterns in music, it significantly reduces the number of note blocks, allowing you to easily reuse existing note block structures in your builds, reduce repetitive work, and improve building efficiency.

## Performance Optimisation

Core algorithms such as SIA, SIATEC, COSIATEC, and RecurSIA are re-implemented in Rust, achieving approximately **10x** speedup, and provide Python bindings via a **native Rust interface + lightweight wrapper**. At runtime, it first tries to use the precompiled Rust implementation; if unavailable, it falls back to the Python implementation.

**Key optimisation**: The SIA algorithm is optimised from storing $O(n^2)$ point pairs to **online HashMap aggregation**, solving memory explosion issues for large NBS files.

Due to the non-uniqueness of pattern representation in SIA and non-determinism of hash iteration, results from Python and Rust may occasionally differ (occasionally by 1 TEC). This will be fixed in the future.

## Core Algorithms

### COSIATEC

COSIATEC (Compression SIATEC) is a greedy lossless compression algorithm. It first uses SIATEC to find all translationally repeatable patterns (translational equivalence classes) in the current set of music points, then selects the one with the highest compression ratio, removes the notes it covers from the dataset, and repeats the process until all notes are encoded. The output is a series of non-overlapping TECs, each represented by a pattern and a set of translation vectors. This algorithm is suitable for fast compression and effectively identifies obvious repeated segments.

### RecurSIA

RecurSIA introduces recursion into COSIATEC. It recursively applies the same compression process to the pattern of each TEC, thereby discovering nested sub-pattern repetitions within the pattern. This enables RecurSIA to capture deeper musical structures (e.g., small motifs within phrases), achieving higher compression ratios than COSIATEC. Recursion depth can be controlled via the `min_pattern_size` parameter to balance compression effectiveness and computational overhead.

## Requirements

```plaintext
pynbs>=1.1.0
```

To build from source, you also need:
- rust 1.95.0+
- `maturin>=1.13,<2.0`

## Quick Start

Install with `pip`:
```pwsh
uv pip install nbslim
```

Or download the latest `.whl` file from the release:
```pwsh
uv pip install path/to/.whl
```

### Read `.nbs` file

```python
from nbslim.utils import notes_to_points
import pynbs

nbs_file_path = 'your_song.nbs'

song = pynbs.read(nbs_file_path)
points, note_dict = notes_to_points(song.notes)
```
Here `note_dict` stores the multiset mapping from `(tick, pitch)` to notes, used to recover note information unrelated to compression when writing back.

### Compression

#### COSIATEC

```python
from nbslim.sia_family import cosiatec_compress

tecs = cosiatec_compress(points, restrict_dpitch_zero=True)
```

#### RecurSIA

```python
from nbslim.sia_family import recursive_cosiatec_compress

tecs = recursive_cosiatec_compress(points, restrict_dpitch_zero=True, min_pattern_size=2)
```

### View compression results

```python
from nbslim.utils import compression_stats

print("Result:")
for i, tec in enumerate(tecs):
    print(f'TEC {i}')
    print(tec.summary(indent=2))
print()

stats = compression_stats(tecs, points)
print(f"Overall compression ratio: {stats['compression_ratio']:.3f} "
      f"(Original: {stats['original_count']}, Encoded units: {stats['encoded_units']})")
```

### Rebuild and save as a new `.nbs` file

```python
from nbslim.utils import tecs_to_nbs, merge_tecs

# Optional: merge all small TECs with coverage size <= 10 (default behaviour)
merged_tecs = merge_tecs(tecs)
new_file = tecs_to_nbs(merged_tecs, note_dict, song.header.__dict__)
new_file.save('.'.join(nbs_file_path.split('.')[:-1]) + '_rebuild.nbs')
```

`tecs_to_nbs` automatically handles layer allocation and `song_layers` settings without manual intervention.

## Build Rust extension from source

```pwsh
git clone git@github.com:madSUNitist/NBSlim.git
cd nbslim
uv sync
uv tool install maturin
uv run maturin develop --release
```

## API Reference

### Core functions

| Function | Description |
|----------|-------------|
| `find_mtps(dataset, restrict_dpitch_zero)` | SIA algorithm, returns all maximal translatable patterns (vector → list of starting points) |
| `build_tecs_from_mtps(dataset, restrict_dpitch_zero)` | SIATEC algorithm, builds translational equivalence classes from MTPs |
| `cosiatec_compress(dataset, restrict_dpitch_zero)` | COSIATEC greedy compression, returns a list of TECs covering the dataset |
| `recursive_cosiatec_compress(dataset, restrict_dpitch_zero, min_pattern_size)` | RecurSIA recursive compression, supports nested patterns |

### Class

- **`TranslationalEquivalence`**: translational equivalence class
  - `pattern`: list of pattern points (sorted)
  - `translators`: set of translation vectors
  - `sub_tecs`: list of sub‑TECs from recursive compression
  - `coverage`: property, returns all points covered by this TEC
  - `compression_ratio`: property, compression ratio
  - `compactness(points)`: returns compactness
  - `summary(indent=0)`: returns a formatted recursive summary string

### Utility functions

| Function | Description |
|----------|-------------|
| `notes_to_points(notes)` | Converts `.nbs` note list to `(points, note_dict)`. `points` for compression, `note_dict` for reconstruction |
| `tecs_to_nbs(tecs, note_dict, header)` | Rebuilds an `.nbs` file object from compression results |
| `merge_tecs(tecs, filter)` | Merges all small TECs satisfying `filter` into one miscellaneous TEC (default filter: `lambda tec: len(tec.coverage) <= 10`) |
| `compression_stats(tecs, original_points)` | Computes compression statistics, returns a dict with `original_count`, `encoded_units`, and `compression_ratio` |

### Pure Python fallback

All functions also have pure Python implementations with a `_py` suffix (e.g. `find_mtps_py`), used automatically when the Rust extension is unavailable.

## Reference

1. Meredith, D., Lemström, K., & Wiggins, G. A. (2002). Algorithms for discovering repeated patterns in multidimensional representations of polyphonic music.
2. Meredith, D. (2013). COSIATEC and SIATECCompress: Pattern discovery by geometric compression.
3. Meredith, D. (2019). RecurSIA-RRT: Recursive translatable point-set pattern discovery with removal of redundant translators. arXiv preprint arXiv:1906.12286v2.