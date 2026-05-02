# Changelog

## [1.0.2] - 2026-05-03

### New

- **sweepline 优化的 SIATEC**（`build_tecs_from_mtps_sweepline`）——为已排序的数据集提供更快的精确平移匹配
- 为 `cosiatec_compress` 和 `recursive_cosiatec_compress` 增加了 `sweepline_optimization` 参数（默认 `True`），用于启用 sweepline 后端

### Changed

- 完善 stub 类型注释
- 完善文档