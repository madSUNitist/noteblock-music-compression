import pytest
import pynbs
from pathlib import Path
from typing import List, Tuple, Set
from nbslim.sia_family import Point
from nbslim.utils import notes_to_points

NBS_DIR = Path(__file__).parent.parent / "nbs_files" / "test"

def load_all_nbs_points() -> List[Tuple[Path, List[Point]]]:
    if not NBS_DIR.exists():
        return []
    points_list = []
    for nbs_path in NBS_DIR.glob("*.nbs"):
        song = pynbs.read(nbs_path)
        points, _ = notes_to_points(song.notes)
        points_list.append((nbs_path, points))
    return points_list

@pytest.fixture(scope="session", params=load_all_nbs_points())
def nbs_file_and_points(request):
    return request.param