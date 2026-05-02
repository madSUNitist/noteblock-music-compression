import pytest
from nbslim.sia_family import (
    recursive_cosiatec_compress, recursive_cosiatec_compress_py,
    _rust_available
)
from .conftest import NBS_DIR

MIN_PATTERN_SIZE = 2

def _total_encoding_units_recursive(tec) -> int:
    """Recursively compute total encoding units for a TEC (supports sub_tecs)."""
    if not tec.sub_tecs:  # leaf
        return len(tec.pattern) + len(tec.translators)
    else:
        # Non-leaf: pattern is encoded by sub_tecs, only translators count directly,
        # plus the sum of encoding units of all sub_tecs.
        units = len(tec.translators)
        for sub in tec.sub_tecs:
            units += _total_encoding_units_recursive(sub)
        return units

@pytest.mark.skipif(not NBS_DIR.exists(), reason="nbs_files directory not found")
def test_recursive_cosiatec_compress_rust(nbs_file_and_points):
    path, points = nbs_file_and_points
    orig_set = set(points)
    orig_count = len(points)
    for restrict in (False, True):
        for sweepline_optimization in (False, True):
            tecs = recursive_cosiatec_compress(points, restrict, MIN_PATTERN_SIZE, sweepline_optimization)
            # Union of coverage of all TECs
            cov = set()
            for tec in tecs:
                cov.update(tec.coverage)
            assert cov == orig_set, f"Lossy recursive coverage: {path}"
            # Total encoding units (recursive sum)
            total_units = sum(_total_encoding_units_recursive(tec) for tec in tecs)
            overall_ratio = orig_count / total_units if total_units > 0 else 0.0
            assert overall_ratio >= 1.0

@pytest.mark.skipif(not NBS_DIR.exists(), reason="nbs_files directory not found")
def test_recursive_cosiatec_compress_python(nbs_file_and_points):
    path, points = nbs_file_and_points
    orig_set = set(points)
    orig_count = len(points)
    for restrict in (False, True):
        tecs = recursive_cosiatec_compress_py(points, restrict, MIN_PATTERN_SIZE)
        cov = set()
        for tec in tecs:
            cov.update(tec.coverage)
        assert cov == orig_set, f"Lossy recursive coverage: {path}"
        # Can directly use the Python class's _total_encoding_units method
        total_units = sum(_total_encoding_units_recursive(tec) for tec in tecs)
        overall_ratio = orig_count / total_units if total_units > 0 else 0.0
        assert overall_ratio >= 1.0