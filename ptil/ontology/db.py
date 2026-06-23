import sqlite3
import os
import logging
import threading
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "ptil.db")


def get_db_path() -> str:
    return DB_PATH


class OntologyDB:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: Optional[str] = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, db_path: Optional[str] = None):
        if self._initialized:
            new_path = db_path or DB_PATH
            if new_path != self.db_path:
                self.close()
                self.db_path = new_path
            return
        self._initialized = True
        self.db_path = db_path or DB_PATH
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def root_exists(self, root_name: str) -> bool:
        cur = self.connect().execute("SELECT 1 FROM roots WHERE name = ?", (root_name,))
        return cur.fetchone() is not None

    def role_exists(self, role_name: str) -> bool:
        cur = self.connect().execute("SELECT 1 FROM roles WHERE name = ?", (role_name,))
        return cur.fetchone() is not None

    def get_root_id(self, root_name: str) -> Optional[int]:
        cur = self.connect().execute("SELECT id FROM roots WHERE name = ?", (root_name,))
        row = cur.fetchone()
        return row["id"] if row else None

    def get_role_id(self, role_name: str) -> Optional[int]:
        cur = self.connect().execute("SELECT id FROM roles WHERE name = ?", (role_name,))
        row = cur.fetchone()
        return row["id"] if row else None

    def get_compatible_roles(self, root_name: str) -> Set[str]:
        cur = self.connect().execute(
            "SELECT compatible_roles FROM roots WHERE name = ?", (root_name,)
        )
        row = cur.fetchone()
        if row is None:
            return set()
        roles_str = row["compatible_roles"]
        if not roles_str:
            return set()
        return set(r.strip() for r in roles_str.split(",") if r.strip())

    def get_all_roots(self) -> List[str]:
        cur = self.connect().execute("SELECT name FROM roots ORDER BY id")
        return [row["name"] for row in cur.fetchall()]

    def get_all_roles(self) -> List[str]:
        cur = self.connect().execute("SELECT name FROM roles ORDER BY id")
        return [row["name"] for row in cur.fetchall()]

    def get_root_for_predicate(self, predicate: str, language: str = "en") -> Optional[str]:
        cur = self.connect().execute(
            "SELECT r.name FROM predicates p JOIN roots r ON p.root_id = r.id "
            "WHERE p.predicate = ? AND (p.language = ? OR p.language = 'en') "
            "ORDER BY p.weight DESC LIMIT 1",
            (predicate.lower().strip(), language),
        )
        row = cur.fetchone()
        return row["name"] if row else None

    def get_predicate_roots(self, predicate: str, language: str = "en") -> List[Tuple[str, float]]:
        cur = self.connect().execute(
            "SELECT r.name, p.weight FROM predicates p JOIN roots r ON p.root_id = r.id "
            "WHERE p.predicate = ? AND (p.language = ? OR p.language = 'en') "
            "ORDER BY p.weight DESC",
            (predicate.lower().strip(), language),
        )
        return [(row["name"], row["weight"]) for row in cur.fetchall()]

    def get_role_parent(self, role_name: str) -> Optional[str]:
        cur = self.connect().execute(
            "SELECT p.name FROM roles r JOIN roles p ON r.parent_id = p.id "
            "WHERE r.name = ?", (role_name,)
        )
        row = cur.fetchone()
        return row["name"] if row else None

    def get_descendant_roles(self, role_name: str) -> List[str]:
        cur = self.connect().execute(
            "WITH RECURSIVE descendants AS ("
            "SELECT id, name FROM roles WHERE parent_id = (SELECT id FROM roles WHERE name = ?) "
            "UNION ALL "
            "SELECT r.id, r.name FROM roles r JOIN descendants d ON r.parent_id = d.id"
            ") SELECT name FROM descendants",
            (role_name,),
        )
        return [row["name"] for row in cur.fetchall()]

    def is_predicate_known(self, predicate: str) -> bool:
        cur = self.connect().execute(
            "SELECT 1 FROM predicates WHERE predicate = ?", (predicate.lower().strip(),)
        )
        return cur.fetchone() is not None
