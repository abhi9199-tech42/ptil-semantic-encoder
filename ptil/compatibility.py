from typing import Dict, Set
from .models import ROOT, Role
from .ontology.db import OntologyDB


_db = OntologyDB()


def _load_compatibility() -> Dict[ROOT, Set[Role]]:
    compat = {}
    for root_name in _db.get_all_roots():
        try:
            root = ROOT[root_name]
            role_names = _db.get_compatible_roles(root_name)
            roles = {Role[r] for r in role_names if r in Role.__members__}
            compat[root] = roles
        except KeyError:
            continue
    return compat


ROOT_ROLE_COMPATIBILITY: Dict[ROOT, Set[Role]] = _load_compatibility()


def is_role_compatible(root: ROOT, role: Role) -> bool:
    return role in ROOT_ROLE_COMPATIBILITY.get(root, set())


def get_compatible_roles(root: ROOT) -> Set[Role]:
    return ROOT_ROLE_COMPATIBILITY.get(root, set()).copy()
