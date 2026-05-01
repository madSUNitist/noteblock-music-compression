[English](README.md) | 简体中文

# NBSlim

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/nbslim.svg)](https://pypi.org/project/nbslim/)
[![Rust](https://img.shields.io/badge/rust-1.95.0%2B-blue.svg)](https://www.rust-lang.org)
[![build](https://img.shields.io/github/actions/workflow/status/madSUNitist/NBSlim/main.yaml?branch=main)](https://github.com/madSUNitist/NBSlim/actions)

为高效实现 [@kemiamu](https://space.bilibili.com/3494363168508256) 的逻辑红石音乐而作。

用于压缩 Note Block Studio (.nbs) 音乐文件的工具，以在 Minecraft 中高效存储和播放多音轨音乐。

通过发现并压缩音乐中的重复模式，显著减小音符盒数量，让你在游戏内布局时可以轻松复用已有的音符盒结构，减少重复劳动，提升建造效率。

## 性能优化

SIA、SIATEC、COSIATEC、RecurSIA 等核心算法均使用 Rust 语言重写，实现了约 **10 倍** 的提速，并通过**原生 Rust 接口 + 轻量 wrapper** 提供 Python 绑定。运行时优先尝试使用预编译的 Rust 实现；若失败则退回 Python 实现。

**关键优化**：SIA 算法从存储 $O(n^2)$ 个点对优化为 **在线 HashMap 聚合分组**，解决了大规模 NBS 文件的内存爆炸问题。

由于 SIA 模式表示的非唯一性与哈希迭代不确定性，Python 与 Rust 的运行结果可能略有不同（偶尔相差 1 TEC），这将在将来得到修复。

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
- rust 1.95.0+
- `maturin>=1.13,<2.0`

## Quick Start

使用 `pip` 安装：
```pwsh
uv pip install nbslim
```

或从 release 中下载最新的 `.whl` 文件：
```pwsh
uv pip install path/to/.whl
```

### 读取 `.nbs` 文件

```python
from nbslim.utils import notes_to_points
import pynbs

nbs_file_path = 'your_song.nbs'

song = pynbs.read(nbs_file_path)
points, note_dict = notes_to_points(song.notes)
```
这里 `note_dict` 存储压缩的 `(tick, pitch)` 到音符的多重集映射，用于在写回时候恢复和压缩无关的音符信息。

### 压缩

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

### 查看压缩结果

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

### 重建并保存为新的 `.nbs` 文件

```python
from nbslim.utils import tecs_to_nbs, merge_tecs

# 可选：合并所有 coverage 大小 <= 10 的小 TEC（默认行为）
merged_tecs = merge_tecs(tecs)
new_file = tecs_to_nbs(merged_tecs, note_dict, song.header.__dict__)
new_file.save('.'.join(nbs_file_path.split('.')[:-1]) + '_rebuild.nbs')
```

`tecs_to_nbs` 会自动处理层数分配和 `song_layers` 设置，无需手动干预。

## 从源码构建 rust 扩展

```pwsh
git clone git@github.com:madSUNitist/NBSlim.git
cd nbslim
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

### 类

- **`TranslationalEquivalence`**：平移等价类
  - `pattern`: 基模式点列表（已排序）
  - `translators`: 平移向量集合
  - `sub_tecs`: 递归压缩得到的子 TEC 列表
  - `coverage`: 属性，返回该 TEC 覆盖的所有点
  - `compression_ratio`: 属性，压缩比
  - `compactness(points)`: 返回紧凑度
  - `summary(indent=0)`: 返回格式化的递归摘要字符串

### 工具函数

| 函数名 | 说明 |
|--------|------|
| `notes_to_points(notes)` | 将 `.nbs` 音符列表转换为 `(points, note_dict)`，`points` 用于压缩，`note_dict` 用于重建 |
| `tecs_to_nbs(tecs, note_dict, header)` | 将压缩结果重建为 `.nbs` 文件对象 |
| `merge_tecs(tecs, filter)` | 合并所有满足 `filter` 的小 TEC 为一个杂项 TEC（默认 filter 为 `lambda tec: len(tec.coverage) <= 10`） |
| `compression_stats(tecs, original_points)` | 计算压缩统计信息，返回包含 `original_count`、`encoded_units` 和 `compression_ratio` 的字典 |

### 纯 python 后备版本

所有函数均提供纯 Python 实现，以 `_py` 后缀命名（如 `find_mtps_py`），当 Rust 扩展不可用时自动使用。

## Reference

1. Meredith, D., Lemström, K., & Wiggins, G. A. (2002). Algorithms for discovering repeated patterns in multidimensional representations of polyphonic music.
2. Meredith, D. (2013). COSIATEC and SIATECCompress: Pattern discovery by geometric compression.
3. Meredith, D. (2019). RecurSIA-RRT: Recursive translatable point-set pattern discovery with removal of redundant translators. arXiv preprint arXiv:1906.12286v2.