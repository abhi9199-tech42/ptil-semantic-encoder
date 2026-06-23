from typing import Dict, Set
from .models import ROOT, Role


_ROOT_ROLE_COMPATIBILITY = None


def _load_compatibility() -> Dict[ROOT, Set[Role]]:
    from .ontology.db import OntologyDB
    try:
        db = OntologyDB()
        compat = {}
        for root_name in db.get_all_roots():
            try:
                root = ROOT[root_name]
                role_names = db.get_compatible_roles(root_name)
                roles = {Role[r] for r in role_names if r in Role.__members__}
                compat[root] = roles
            except KeyError:
                continue
        return compat
    except Exception:
        return {}


def _get_compatibility() -> Dict[ROOT, Set[Role]]:
    global _ROOT_ROLE_COMPATIBILITY
    if _ROOT_ROLE_COMPATIBILITY is None:
        _ROOT_ROLE_COMPATIBILITY = _load_compatibility()
    return _ROOT_ROLE_COMPATIBILITY


def __getattr__(name):
    if name == "ROOT_ROLE_COMPATIBILITY":
        return _get_compatibility()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def is_role_compatible(root: ROOT, role: Role) -> bool:
    return role in _get_compatibility().get(root, set())


def get_compatible_roles(root: ROOT) -> Set[Role]:
    return _get_compatibility().get(root, set()).copy()
