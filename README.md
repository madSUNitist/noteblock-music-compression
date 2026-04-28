# Noteblock Music Compression

为高效实现 [@kemiamu](https://space.bilibili.com/3494363168508256) 的逻辑红石音乐而作。

用于压缩 Note Block Studio (.nbs) 音乐文件的工具，以在 Minecraft 中高效存储和播放多音轨音乐。

通过发现并压缩音乐中的重复模式，显著减小音符盒数量，让你在游戏内布局时可以轻松复用已有的音符盒结构，减少重复劳动，提升建造效率。

## 性能优化

SIA、SIATEC、COSIATEC、RecurSIA 等核心算法均使用 rust 语言重写，实现了约 **10 倍** 的提速，并通过 PyO3 提供 python 绑定。运行时优先尝试使用预编译的 rust 实现；若失败则退回 python 实现。

**关键优化**：SIA 算法从存储 \( O(n^2) \) 个点对优化为 **在线 HashMap 聚合分组**，解决了大规模 NBS 文件的内存爆炸问题。

由于 SIA 模式表示的非唯一性与哈希迭代不确定性，python 与 rust 的运行结果可能略有不同（偶尔相差 1 TEC），这将在将来得到修复。

## 核心算法

### COSIATEC

COSIATEC（Compression SIATEC）是一种基于贪心策略的无损压缩算法。它首先利用 SIATEC 找出当前音乐点集中所有可平移重复的模式（平移等价类），然后从中选择压缩比最高的一个，将其覆盖的音符从数据集中移除，并重复此过程直到所有音符都被编码。最终输出一系列不重叠的 TEC，每个 TEC 由一个基模式（pattern）和一组平移向量（translators）表示。该算法适合快速压缩，能有效识别明显的重复片段。

### RecurSIA

RecurSIA 在 COSIATEC 的基础上引入了递归思想。它会对每个 TEC 的基模式（pattern）再次递归地应用相同的压缩流程，从而发现嵌套在模式内部的子模式重复。这使得 RecurSIA 能够捕捉到更深层次的音乐结构（例如乐句中包含的小动机），从而获得比 COSIATEC 更高的压缩率。递归深度可通过 `min_pattern_size` 参数控制，以平衡压缩效果与计算开销。

## Requirements

```plaintext
pynbs>=1.1.0
```

如果从源码安装，还需要：
- rust 1.89.0+
- `maturin>=1.13,<2.0`

## Quick Start

从 Release 中下载最新的 `.whl` 文件：
```pwsh
uv pip install path/to/.whl
```

### 读取 `.nbs` 文件

```python
from nbs_compression.utils import notes_to_points
import pynbs

nbs_file_path = 'your_song.nbs'

song = pynbs.read(nbs_file_path)
raw_notes = [(tick, note.key, note.instrument) for tick, chord in song for note in chord]
points, mapping = notes_to_points(raw_notes)
```
这里 `mapping` 存储压缩的 `(tick, pitch)` 到音符的多重集映射，用于在写回时候恢复和压缩无关的音符信息。

### 压缩

#### COSIATEC

```python
from nbs_compression.sia_family import cosiatec_compress

tecs = cosiatec_compress(points, restrict_dpitch_zero=True)
```

#### RecurSIA

```python
from nbs_compression.sia_family import recursive_cosiatec_compress

tecs = recursive_cosiatec_compress(points, restrict_dpitch_zero=True, min_pattern_size=2)
```

### 查看压缩结果

```python
for i, tec in enumerate(tecs):
    print(f"TranslationalEquivalence {i+1}: pattern={tec.pattern}, translators={tec.translators}")
    print(f"  Coverage count: {len(tec.coverage)}")
    print(f"  Compression ratio: {tec.compression_ratio:.3f}")
```

### 重建并保存为新的 `.nbs` 文件

```python
from nbs_compression.utils import tecs_to_nbs

new_file = tecs_to_nbs(tecs, mapping, song.header.__dict__)
new_file.save("your_song_compressed.nbs")
```
这里的 `mapping` 是之前 `notes_to_points` 返回的字典。

## 从源码构建 rust 扩展

```pwsh
git clone git@github.com:madSUNitist/noteblock-music-compression.git
cd logic_music_compression
uv sync
uv tool install maturin
uv run maturin develop --release
```

## API 参考

### 核心函数

| 函数名 | 说明 |
|--------|------|
| `find_mtps(dataset, restrict_dpitch_zero)` | SIA 算法，返回所有最大可平移模式（向量 → 起始点列表） |
| `build_tecs_from_mtps(dataset, restrict_dpitch_zero)` | SIATEC 算法，从 MTP 构建平移等价类列表 |
| `cosiatec_compress(dataset, restrict_dpitch_zero)` | COSIATEC 贪心压缩，返回覆盖数据集的 TEC 列表 |
| `recursive_cosiatec_compress(dataset, restrict_dpitch_zero, min_pattern_size)` | RecurSIA 递归压缩，支持嵌套模式 |
| `is_better_tec(tec1, tec2, dataset_points)` | 比较两个 TEC，返回前者是否更优 |

### 类

- **`TranslationalEquivalence`**：平移等价类
  - `pattern`: 基模式点列表（已排序）
  - `translators`: 平移向量集合
  - `sub_tecs`: 递归压缩得到的子 TEC 列表
  - `coverage`: 属性，返回该 TEC 覆盖的所有点
  - `compression_ratio`: 属性，压缩比
  - `compactness(points)`: 返回紧凑度

### 工具函数

| 函数名 | 说明 |
|--------|------|
| `notes_to_points(notes)` | 将 `.nbs` 音符列表转换为 `(points, mapping)`，`points` 用于压缩，`mapping` 用于重建 |
| `tecs_to_nbs(tecs, mapping, header)` | 将压缩结果重建为 `.nbs` 文件对象 |

### 纯 python 后备版本

所有函数均提供纯 python 实现，以 `_py` 后缀命名（如 `find_mtps_py`），当 rust 扩展不可用时自动使用。

## Reference

1. Meredith, D., Lemström, K., & Wiggins, G. A. (2002). Algorithms for discovering repeated patterns in multidimensional representations of polyphonic music.
2. Meredith, D. (2013). COSIATEC and SIATECCompress: Pattern discovery by geometric compression.
3. Meredith, D. (2019). RecurSIA-RRT: Recursive translatable point-set pattern discovery with removal of redundant translators. arXiv preprint arXiv:1906.12286v2.