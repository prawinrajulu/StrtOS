# Redirect top-level 'app' package to actual backend implementation
import os, sys
# Resolve path to the real backend/app directory (project root sibling to this package)
_backend_app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app"))
# Prepend to sys.path if not already present
if _backend_app_dir not in sys.path:
    sys.path.insert(0, _backend_app_dir)
# Extend package __path__ so submodules are discovered in the backend directory
__path__.append(_backend_app_dir)
