import sys
import logging
from typing import Tuple, List, Dict, Set, Optional

# Define type aliases
Point = Tuple[int, int]
Vector = Tuple[int, int]

# Try to import Rust extension
_rust_available = False

try:
    from ._core import (
        sia,
        siatec,
        cosiatec,
        recur_sia_cosiatec,
        compress_to_encoding,
        is_better_tec,
        TEC,
    )
    _rust_available = True
    print("[sia_family] Using Rust-accelerated implementations (via _core).")
except ImportError as e:
    print(f"[sia_family] Rust extension not found: {e}. Falling back to pure Python implementations.")
    # Fallback: import from local modules
    from .sia import sia
    from .siatec import siatec, is_better_tec
    from .cosiatec import cosiatec, compress_to_encoding
    from .recursia import recur_sia_cosiatec
    from .tec import TEC
    _rust_available = False

# Optionally log more details
if _rust_available:
    logger = logging.getLogger(__name__)
    logger.info("Rust extension loaded successfully.")

# Expose public API
__all__ = [
    "Point",
    "Vector",
    "sia",
    "siatec",
    "cosiatec",
    "recur_sia_cosiatec",
    "compress_to_encoding",
    "is_better_tec",
    "TEC",
]