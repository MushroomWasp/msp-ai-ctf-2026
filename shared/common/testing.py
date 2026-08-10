from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_module_from_path(path: str | Path) -> ModuleType:
    target = Path(path)
    spec = importlib.util.spec_from_file_location(target.stem, target)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {target}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
