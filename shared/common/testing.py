from __future__ import annotations

import importlib.util
import hashlib
from pathlib import Path
from types import ModuleType


def load_module_from_path(path: str | Path) -> ModuleType:
    target = Path(path)
    unique_name = f"{target.stem}_{hashlib.sha1(str(target.resolve()).encode('utf-8')).hexdigest()}"
    spec = importlib.util.spec_from_file_location(unique_name, target)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {target}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
