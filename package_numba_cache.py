"""Writable cache locator for Numba code bundled into the frozen application."""
import os
from numba.core.caching import UserWideCacheLocator

class FrozenDataCacheLocator(UserWideCacheLocator):
    def __init__(self, py_func, py_file):
        super().__init__(py_func, py_file)
        self._cache_path = os.path.join(os.environ['NUMBA_CACHE_DIR'], self.get_suitable_cache_subpath(py_file))
