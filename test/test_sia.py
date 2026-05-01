import pytest
from nbslim.sia_family import find_mtps, find_mtps_py, _rust_available
from .conftest import NBS_DIR

@pytest.mark.skipif(not NBS_DIR.exists(), reason="nbs_files directory not found")
def test_find_mtps_consistency(nbs_file_and_points):
    """Check that Rust and Python implementations give identical results."""
    _, points = nbs_file_and_points
    for restrict in [False, True]:
        py_result = find_mtps_py(points, restrict)
        if _rust_available:
            rust_result = find_mtps(points, restrict)   # rust version when available
            # Convert dict to comparable form: sorted list of (vector, sorted pattern)
            py_norm = sorted((v, sorted(pat)) for v, pat in py_result.items())
            rust_norm = sorted((v, sorted(pat)) for v, pat in rust_result.items())
            assert py_norm == rust_norm
        else:
            pytest.skip("Rust extension not available")