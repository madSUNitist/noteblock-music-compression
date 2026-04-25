# Noteblock Music Compression

为高效实现[@kemiamu](https://space.bilibili.com/3494363168508256) 的逻辑红石音乐而作。

用于压缩 Note Block Studio (.nbs) 音乐文件的工具，以在 Minecraft 中高效存储和播放多音轨音乐。

通过发现并压缩音乐中的重复模式，显著减小音符盒数量，让你在游戏内布局时可以轻松复用已有的音符盒结构，减少重复劳动，提升建造效率。

## 算法简介

### COSIATEC

COSIATEC（Compression SIATEC）是一种基于贪心策略的无损压缩算法。它首先利用 SIATEC 找出当前音乐点集中所有可平移重复的模式（平移等价类 TEC），然后从中选择压缩比最高的一个，将其覆盖的音符从数据集中移除，并重复此过程直到所有音符都被编码。最终输出一系列不重叠的 TEC，每个 TEC 由一个基模式（pattern）和一组平移向量（translators）表示。该算法适合快速压缩，能有效识别明显的重复片段。

### RecurSIA

RecurSIA 在 COSIATEC 的基础上引入了递归思想。它会对每个 TEC 的基模式（pattern）再次递归地应用相同的压缩流程，从而发现嵌套在模式内部的子模式重复。这使得 RecurSIA 能够捕捉到更深层次的音乐结构（例如乐句中包含的小动机），从而获得比 COSIATEC 更高的压缩率。递归深度可通过 `min_pattern_size` 参数控制，以平衡压缩效果与计算开销。

## Requirements

```plaintext
pynbs>=1.1.0
```

## Quick Start

### 读取 `.nbs` 文件

```python
from nbs_compression.sia_family.point import Point
from nbs_compression.utils import notes_to_points

import pynbs

nbs_path = "your_song.nbs"

# 1.1. Read `.nbs` file
song = pynbs.read(nbs_path)
raw_notes = [(tick, note.key, note.instrument) for tick, chord in song for note in chord] # Original note list: (tick, key, instrument)

# 1.2. Convert into `Point`
points = notes_to_points(raw_notes)
```

### 压缩
#### COSIATEC

```python
from nbs_compression.sia_family.cosiatec import cosiatec

# 2. Compress (COSIATEC)
tecs = cosiatec(points, restrict_dpitch_zero=True)
```

#### RecurSIA

```python
from nbs_compression.sia_family.recursia import recur_sia_cosiatec

# 2. Compress (RecurSIA)
tecs = recur_sia_cosiatec(points, restrict_dpitch_zero=True, min_pattern_size=2)
```

### 查看压缩结果

```python
# 3. Check results 
for i, tec in enumerate(tecs):
    print(f"TEC {i+1}: pattern={tec.pattern}, translators={tec.translators}")
    print(f"  Coverage count: {len(tec.coverage)}")
    print(f"  Compression ratio: {tec.compression_ratio:.3f}")

```

### 重建并保存为新的 `.nbs` 文件

压缩后得到的 `TEC` 列表可以重建为原始的 `.nbs` 文件。重建过程中，每个 `TEC` 会分配一个连续的层（layer）区间，区间大小取决于该 `TEC` 内同一 tick 上的最大音符并发数。每个 TEC 内部的音符按 tick 分组，同一 tick 上的不同乐器会被分配到该 TEC 层区间内的不同层上。所有音符按 tick 排序后写入文件，确保符合 NBS 格式要求。

```python
from nbs_compression.utils import tecs_to_nbs

# 4. Rebuild & Write Back
new_file = tecs_to_nbs(tecs, song.header.__dict__)
new_file.save("your_song_compressed.nbs")
```

## Reference

1. Meredith, D., Lemström, K., & Wiggins, G. A. (2002). Algorithms for discovering repeated patterns in multidimensional representations of polyphonic music.

2. Meredith, D. (2013). COSIATEC and SIATECCompress: Pattern discovery by geometric compression.

3. Meredith, D. (2019). RecurSIA-RRT: Recursive translatable point-set pattern discovery with removal of redundant translators. arXiv preprint arXiv:1906.12286v2.