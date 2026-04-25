# Noteblock Music Compression

用于压缩 Note Block Studio (.nbs) 音乐文件的工具，为在 Minecraft 中高效存储和播放多音轨音乐而设计

## Requirements

```plaintext
pynbs >= 1.1.0
```

## Usage

### Prepare

```python
import pynbs


nbs_file_path = 'path/to/your/nbs/file.nbs'

notes = []
for tick, chord in pynbs.read(nbs_file_path):
    for note in chord:
        notes.append((tick, note.key))
```

### COSIATEC

```python
from nbs_compression.cosiatec import cosiatec

tecs = cosiatec(notes, restrict_dpitch_zero=True)
print("COSIATEC result:")
for i, tec in enumerate(tecs):
    print(f"TEC {i+1}: pattern={tec.pattern}, translators={tec.translators}")
    print(f"  Coverage count: {len(tec.coverage)}")
    print(f"  Compression ratio: {tec.compression_ratio:.3f}")
```

### RecurSIA

```python
from nbs_compression.sia_family.recursia import recur_sia_cosiatec

tecs = recur_sia_cosiatec(notes, restrict_dpitch_zero=True)
print("RecurSIA result:")
for i, tec in enumerate(tecs):
    print(f"TEC {i+1}: pattern={tec.pattern}, translators={tec.translators}")
    print(f"  Coverage count: {len(tec.coverage)}")
    print(f"  Compression ratio: {tec.compression_ratio:.3f}")
```

## Reference

1. Meredith, D., Lemström, K., & Wiggins, G. A. (2002). Algorithms for discovering repeated patterns in multidimensional representations of polyphonic music.

2. Meredith, D. (2013). COSIATEC and SIATECCompress: Pattern discovery by geometric compression.

3. Meredith, D. (2019). RecurSIA-RRT: Recursive translatable point-set pattern discovery with removal of redundant translators. arXiv preprint arXiv:1906.12286v2.