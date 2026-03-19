import importlib, pkgutil
from typing import List, Any

def load_skills(path: str = __path__[0]) -> List[Any]:
    skills = []
    for _finder, name, _ispkg in pkgutil.iter_modules([path]):
        if name.endswith('_skill'):
            module_name = f"{__name__}.{name}"
            try:
                mod = importlib.import_module(module_name)
                if hasattr(mod, 'can_handle') and hasattr(mod, 'run'):
                    skills.append(mod)
            except Exception:
                # Skip modules that fail to import to keep loader robust
                continue
    return skills
