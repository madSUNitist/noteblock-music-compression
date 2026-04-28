# Changelog

## [0.2.0] - 2025-04-28 — 重构与内存优化版本

### ✨ Added

- Rust 端为 `TranslationalEquivalence` 实现 `std::fmt::Display` trait，方便调试输出
- 在 `__init__.py` 中同时导出纯 Python 版本，以 `*_py` 后缀命名，供用户显式使用
- `notes_to_points`：增加 `mapping` 返回值，保留原始 `pynbs.Note` 对象的完整信息（乐器、力度、声相等），重建时可准确还原

### ⚡ Performance

- **🔴 关键优化：SIA 算法内存从天量爆裂降至可控（240 GB → 几百 MB）**
  - 原 Rust 实现预先生成所有 O(n²) 点对，导致 80,000 点时内存需求高达 240 GB
  - 优化后采用 `HashMap` + `HashSet` 在线聚合分组，内存复杂度降至 O(有效向量数 × 平均起始点数)
  - 对于 80k 点规模，内存稳定在几百 MB 的合理范围
  - 保持完全一致的算法结果，仅优化存储方式

### 🔄 Changed

- **统一 API 命名**（使用更具描述性的全称，避免简写歧义）：
  - `sia()` → `find_mtps()` — 查找最大可平移模式
  - `siatec()` → `build_tecs_from_mtps()` — 从 MTP 构建平移等价类
  - `cosiatec()` → `cosiatec_compress()` — COSIATEC 贪心压缩
  - `recur_sia_cosiatec()` → `recursive_cosiatec_compress()` — 递归版 COSIATEC
  - `TEC` → `TranslationalEquivalence` — 平移等价类
- **统一类型系统**：
  - 点坐标：Pattern 点使用 `(u32, u32)`
  - Translators：使用 `(i32, i32)`
  - 差向量计算安全转换为 `i64`，避免整数溢出
- **重构 `notes_to_points`**：
  - 返回类型变更为 `Tuple[List[Point], defaultdict[Point, List[pynbs.Note]]]`，新增 `mapping` 字典
  - 编码公式改为 `(instrument << 14) | (key * 100 + pitch + 1200)`
  - 新编码支持乐器优先、音高次级的比较语义，同时保留 pitch 微调信息
- **重构 `tecs_to_nbs` 重建逻辑**：
  - 为每个 `TranslationalEquivalence` 分配连续 layer 区间
  - 同一 tick 上的不同乐器分配到该 TEC 层区间内的不同层，确保完整重建

### 🐛 Fixed

- 修复 Rust 扩展加载失败时未正确 fallback 到 Python 实现的 fallback 逻辑
- 修复因同模块导入导致 `'module' object is not callable` 的错误
- 修复 `pitch`（微调）信息丢失导致重建后音符音高与原版不一致的问题
- 修复重建时多音符并发未正确分配到不同层的音轨冲突问题

### 📚 Documentation

- 更新 `README.md` 代码示例，使用新的 API 名称
- 添加 `CHANGELOG.md` 详细记录版本变动
- 补充内存优化的技术说明

### 🔧 Refactor

- **分离坐标与载荷（payload）**：
  - 坐标 `(tick, encoded_y)` 仅用于算法计算
  - 载荷（乐器、力度、声相等）存储于独立的 `mapping` 字典中，通过 `Point` 回溯
  - 算法性能不受影响，同时完整保留了所有原始信息
- 重构 Rust `tec.rs`：确保 `pattern` 在构造时被排序
- 重构 `__init__.py` 导入机制：优先 Rust → 备用 Python，并安全导出 `*_py` 版本
- 优化 `translators` 计算逻辑：将 `candidates` 从基于 `HashSet` 的迭代改为更直接的映射

### 🚀 Migration Guide

旧代码需将函数名替换为新 API：

```python
# 旧版
from nbs_compression.sia_family import sia, siatec, cosiatec, recur_sia_cosiatec, TEC

# 新版
from nbs_compression.sia_family import find_mtps, build_tecs_from_mtps, cosiatec_compress, recursive_cosiatec_compress, TranslationalEquivalence
```