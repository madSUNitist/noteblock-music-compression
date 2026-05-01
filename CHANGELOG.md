# Changelog

## [0.2.5] - 2026-05-01 - 修修补补

### Fixed

#### `tec.py/tec.rs`
- 修复了 `.__repr__` 的 rust 实现和 python 实现不一致的问题

#### `utils.py`
- 修复了误将 `_total_encoding_units(sub)` 写成 `sub._total_encoding_units()` 导致 `AttributeError` 的问题