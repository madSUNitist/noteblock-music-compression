English | [简体中文](README.zh.md)

# NBSlim

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/nbslim.svg)](https://pypi.org/project/nbslim/)
[![Rust](https://img.shields.io/badge/rust-1.89.0%2B-blue.svg)](https://www.rust-lang.org)
[![build](https://img.shields.io/github/actions/workflow/status/madSUNitist/NBSlim/main.yaml?branch=main)](https://github.com/madSUNitist/NBSlim/actions)

Created for efficient logical redstone music implementation by [@kemiamu](https://space.bilibili.com/3494363168508256).

A tool to compress Note Block Studio (.nbs) music files for efficient storage and playback of multi‑track music in Minecraft.

By discovering and compressing repeated patterns in the music, it significantly reduces the number of note blocks, allowing you to easily reuse existing note block structures in your in‑game layout, reducing redundant work and improving building efficiency.

## Performance Optimizations

Core algorithms SIA, SIATEC, COSIATEC, RecurSIA are all rewritten in Rust, achieving about **10×** speedup, and provide Python bindings via PyO3. At runtime, the pre‑compiled Rust implementation is tried first; if it fails, it falls back to the Python implementation.

**Key optimization**: The SIA algorithm reduces storage from $O(n^2)$ point pairs to **online HashMap aggregation grouping**, solving the memory explosion problem for large NBS files.

Due to the non‑uniqueness of SIA pattern representation and hash iteration nondeterminism, results from Python and Rust may differ slightly (occasionally by 1 TEC). This will be fixed in the future.

## Core Algorithms

### COSIATEC

COSIATEC (Compression SIATEC) is a greedy lossless compression algorithm. It first uses SIATEC to find all translationally repeatable patterns (translational equivalence classes) in the current note point set, then selects the one with the highest compression ratio, removes the covered notes from the dataset, and repeats until all notes are encoded. The final output is a list of non‑overlapping TECs, each TEC consists of a pattern and a set of translators. This algorithm is suitable for fast compression and effectively identifies obvious repeated segments.

### RecurSIA

RecurSIA introduces recursion on top of COSIATEC. It recursively applies the same compression process to the pattern of each TEC, discovering sub‑pattern repetitions nested inside patterns. This allows RecurSIA to capture deeper musical structure (e.g., small motives inside a phrase), achieving higher compression ratios than COSIATEC. Recursion depth can be controlled by the `min_pattern_size` parameter to balance compression effectiveness and computational cost.

## Requirements

```plaintext
pynbs>=1.1.0
```

If installing from source, you also need:
- Rust 1.89.0+
- `maturin>=1.13,<2.0`

## Quick Start

Install via `pip`:
```pwsh
uv pip install nbslim
```

Or download the latest `.whl` file from releases:
```pwsh
uv pip install path/to/.whl
```

### Reading an `.nbs` file

```python
from nbslim.utils import notes_to_points
import pynbs

nbs_file_path = 'your_song.nbs'

song = pynbs.read(nbs_file_path)
raw_notes = [(tick, note.key, note.instrument) for tick, chord in song for note in chord]
points, mapping = notes_to_points(raw_notes)
```
Here `mapping` stores the multiset mapping from compressed `(tick, pitch)` to original notes, used to restore information unrelated to compression when writing back.

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

### Viewing Compression Results

```python
for i, tec in enumerate(tecs):
    print(f"TranslationalEquivalence {i+1}: pattern={tec.pattern}, translators={tec.translators}")
    print(f"  Coverage count: {len(tec.coverage)}")
    print(f"  Compression ratio: {tec.compression_ratio:.3f}")
```

### Reconstructing and Saving a New `.nbs` File

```python
from nbslim.utils import tecs_to_nbs

new_file = tecs_to_nbs(tecs, mapping, song.header.__dict__)
new_file.save("your_song_compressed.nbs")
```
Here `mapping` is the dictionary returned earlier by `notes_to_points`.

## Building the Rust Extension from Source

```pwsh
git clone git@github.com:madSUNitist/NBSlim.git
cd nbslim
uv sync
uv tool install maturin
uv run maturin develop --release
```

## API Reference

### Core Functions

| Function | Description |
|----------|-------------|
| `find_mtps(dataset, restrict_dpitch_zero)` | SIA algorithm, returns all maximal translatable patterns (vector → list of start points) |
| `build_tecs_from_mtps(dataset, restrict_dpitch_zero)` | SIATEC algorithm, builds translational equivalence classes from MTPs |
| `cosiatec_compress(dataset, restrict_dpitch_zero)` | COSIATEC greedy compression, returns a list of TECs covering the dataset |
| `recursive_cosiatec_compress(dataset, restrict_dpitch_zero, min_pattern_size)` | RecurSIA recursive compression, supports nested patterns |
| `is_better_tec(tec1, tec2, dataset_points)` | Compares two TECs, returns whether the first is better |

### Class

- **`TranslationalEquivalence`**: translational equivalence class
  - `pattern`: the pattern point list (sorted)
  - `translators`: set of translation vectors
  - `sub_tecs`: list of sub‑TECs obtained by recursive compression
  - `coverage`: property, returns all points covered by this TEC
  - `compression_ratio`: property, compression ratio
  - `compactness(points)`: returns compactness

### Utility Functions

| Function | Description |
|----------|-------------|
| `notes_to_points(notes)` | Converts a `.nbs` note list to `(points, mapping)`, where `points` are used for compression and `mapping` for reconstruction |
| `tecs_to_nbs(tecs, mapping, header)` | Reconstructs a `.nbs` file object from compression results |

### Pure Python Fallback

All functions have pure Python implementations with a `_py` suffix (e.g., `find_mtps_py`), automatically used when the Rust extension is unavailable.

## Reference

1. Meredith, D., Lemström, K., & Wiggins, G. A. (2002). Algorithms for discovering repeated patterns in multidimensional representations of polyphonic music.
2. Meredith, D. (2013). COSIATEC and SIATECCompress: Pattern discovery by geometric compression.
3. Meredith, D. (2019). RecurSIA-RRT: Recursive translatable point-set pattern discovery with removal of redundant translators. arXiv preprint arXiv:1906.12286v2.