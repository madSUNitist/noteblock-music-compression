import pytest
from nbslim.sia_family import cosiatec_compress, cosiatec_compress_py, _rust_available
from .conftest import NBS_DIR

def _total_encoding_units(tec) -> int:
    """Return total encoding units for a single leaf‑level TEC (no sub_tecs)."""
    # Basic COSIATEC does not produce recursive TECs; compute pattern + translators directly
    return len(tec.pattern) + len(tec.translators)

@pytest.mark.skipif(not NBS_DIR.exists(), reason="nbs_files directory not found")
def test_cosiatec_compress_rust(nbs_file_and_points):
    path, points = nbs_file_and_points
    orig_set = set(points)
    orig_count = len(points)
    for restrict in (False, True):
        tecs = cosiatec_compress(points, restrict)
        # Union of coverage of all TECs
        cov = set()
        for tec in tecs:
            cov.update(tec.coverage)
        assert cov == orig_set, f"Lossy: {path}"
        # Overall compression ratio = original points / total encoding units
        total_units = sum(_total_encoding_units(tec) for tec in tecs)
        ratio = orig_count / total_units if total_units > 0 else 0.0
        assert ratio >= 1.0

@pytest.mark.skipif(not NBS_DIR.exists(), reason="nbs_files directory not found")
def test_cosiatec_compress_python(nbs_file_and_points):
    path, points = nbs_file_and_points
    orig_set = set(points)
    orig_count = len(points)
    for restrict in (False, True):
        tecs = cosiatec_compress_py(points, restrict)
        cov = set()
        for tec in tecs:
            cov.update(tec.coverage)
        assert cov == orig_set, f"Lossy: {path}"
        total_units = sum(len(tec.pattern) + len(tec.translators) for tec in tecs)
        ratio = orig_count / total_units if total_units > 0 else 0.0
        assert ratio >= 1.0