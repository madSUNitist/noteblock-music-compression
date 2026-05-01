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
        find_mtps, 
        build_tecs_from_mtps, 
        cosiatec_compress,
        recursive_cosiatec_compress,
        
        TranslationalEquivalence
    )
    _rust_available = True
    print("[sia_family] Using Rust-accelerated implementations (via _core).")
except ImportError as e:
    print(f"[sia_family] Rust extension not found: {e}. Falling back to pure Python implementations.")
    # Fallback: import from local modules
    from .sia import find_mtps
    from .siatec import build_tecs_from_mtps
    from .cosiatec import cosiatec_compress
    from .recursia import recursive_cosiatec_compress
    from .tec import TranslationalEquivalence

    _rust_available = False

# Log more details
if _rust_available:
    logger.info("Rust extension loaded successfully.")

from .sia import find_mtps as find_mtps_py
from .siatec import build_tecs_from_mtps as build_tecs_from_mtps_py
from .cosiatec import cosiatec_compress as cosiatec_compress_py
from .recursia import recursive_cosiatec_compress as recursive_cosiatec_compress_py

from .tec import TranslationalEquivalence as TranslationalEquivalence_py

# Expose public API
__all__ = [
    "Point",
    "Vector",
    
    "find_mtps", "find_mtps_py", 
    "build_tecs_from_mtps", "build_tecs_from_mtps_py", 
    "cosiatec_compress", "cosiatec_compress_py",
    "recursive_cosiatec_compress", "recursive_cosiatec_compress_py",     
    
    "TranslationalEquivalence", "TranslationalEquivalence_py", 

    "_rust_available"
]