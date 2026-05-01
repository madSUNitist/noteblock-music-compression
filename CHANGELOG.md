# Changelog

## [0.2.4] - 2026-04-30 - 重构部分代码

### Changed

#### `tec.py/tec.rs` 
- 移除了 `is_better_tec`；在内部使用了 `tec_sort_key (tec.py)` 和 `SortKey (tec.rs)` 与 `tec_sort_key (tec.rs)` 来生成用于排序的可比较元组
- 为 `TranslationalEquivalence` 实现了 `summary` 方法，用于查看压缩结果

#### `cosiatec.py/cosiatec.rs`
- 基于 `tec_sort_key` 重写了 `cosiatec_compress`

#### `recursia.py/recursia.rs`
- 重写了 `recursive_cosiatec_compress`，消除了冗余的重复逻辑

#### `sia.py/sia.rs`
- 修改了 `find_mtps`，减小了循环次数，减小了时间复杂度的常数项

#### `utils.py`
- 增加了 `merge_tecs` 用以合并过小的 TEC
- 增加 `compression_stats` 用以统计压缩信息

#### 其他
- 用纯血 rust（不依赖 PyO3）实现主要函数，使得引用传递成为可能，减少了 `clone` 开销，并新增 `wrapper.rs`，以 wrapper 的形式再包装成 python 函数
- 新增了基于 pytest 的测试

### Fixed

#### `tec.py/tec.rs`
- 修复了 `TranslationalEquivalence.coverage (tec.py)`, `TranslationalEquivalence.compression_ratio (tec.py)`, `TranslationalEquivalence.compactness (tec.py)` 对递归形式的 TEC 无法得到正确的计算结果的问题

#### `utils.py`
- 修复了由于 `song_layers` 不匹配而导致的新文件无法解析的问题
