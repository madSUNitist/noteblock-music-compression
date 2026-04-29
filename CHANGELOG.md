# Changelog

## [0.2.2] - 2026-04-29 — 重命名

### 🔄 Changed

- **统一包名**：采用 `nbslim` 作为包名，更优雅简洁，直观漂亮。

### 📚 Documentation

- 更新 `README.md` 代码示例，使用新的包名称
- 添加 `CHANGELOG.md` 详细记录版本变动
- 补充内存优化的技术说明

### 🚀 Migration Guide

旧代码需将函数名替换为新 API：

```python
# old
from nbs_compression.sia_family import find_mtps, build_tecs_from_mtps, cosiatec_compress, recursive_cosiatec_compress, TranslationalEquivalence

# new
from nbslim.sia_family import find_mtps, build_tecs_from_mtps, cosiatec_compress, recursive_cosiatec_compress, TranslationalEquivalence
```