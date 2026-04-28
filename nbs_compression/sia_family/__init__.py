from typing import Tuple, Optional

import logging

from functools import wraps

logger = logging.getLogger(__name__)

# Logger decorator
_WARNED_KEYS = set()

def warn_python_impl(key: str, message: str, logger: Optional[logging.Logger] = None):
    if key in _WARNED_KEYS:
        return
    _WARNED_KEYS.add(key)
    if logger is None:
        logger = logging.getLogger(__name__)
    logger.warning(message)
    
def warn_python_impl_deco(message: str):
    def decorator(func):
        key = f"{func.__module__}.{func.__name__}"
        @wraps(func)
        def wrapper(*args, **kwargs):
            warn_python_impl(key, message)
            return func(*args, **kwargs)
        return wrapper
    return decorator

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
    logger.info("Rust extension loaded successfully.")
    
from .sia import sia as sia_py
from .siatec import siatec as siatec_py, is_better_tec as is_better_tec_py
from .cosiatec import cosiatec as cosiatec_py, compress_to_encoding as compress_to_encoding_py
from .recursia import recur_sia_cosiatec as recur_sia_cosiatec_py
from .tec import TEC as TEC_py

# Expose public API
__all__ = [
    "Point",
    "Vector",
    "sia", "sia_py", 
    "siatec", "siatec_py", 
    "cosiatec", "cosiatec_py", 
    "recur_sia_cosiatec", "recur_sia_cosiatec_py", 
    "compress_to_encoding", "compress_to_encoding_py", 
    "is_better_tec", "is_better_tec_py", 
    "TEC", "TEC_py"
]