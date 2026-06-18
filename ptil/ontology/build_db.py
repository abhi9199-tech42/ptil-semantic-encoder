import sqlite3
import os
import logging

from .schema import ROOT_DEFINITIONS, ROLE_DEFINITIONS, ROOT_ROLE_MAP
from .seed_data import PREDICATE_MAP, PREDICATE_WEIGHTS
from .db import DB_PATH

logger = logging.getLogger(__name__)


def build_database(db_path: str = DB_PATH) -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS roots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            compatible_roles TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            parent_id INTEGER REFERENCES roles(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS predicates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            predicate TEXT NOT NULL,
            root_id INTEGER NOT NULL REFERENCES roots(id),
            weight REAL NOT NULL DEFAULT 1.0,
            language TEXT NOT NULL DEFAULT 'en'
        )
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_predicates_predicate
        ON predicates(predicate)
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_predicates_language
        ON predicates(language)
    """)

    existing_roots = set()
    for row in cur.execute("SELECT name FROM roots").fetchall():
        existing_roots.add(row[0])

    for name, desc in ROOT_DEFINITIONS:
        if name not in existing_roots:
            roles = ROOT_ROLE_MAP.get(name, "")
            cur.execute(
                "INSERT INTO roots (name, description, compatible_roles) VALUES (?, ?, ?)",
                (name, desc, roles),
            )

    existing_roles = set()
    for row in cur.execute("SELECT name FROM roles").fetchall():
        existing_roles.add(row[0])

    role_name_to_id = {}
    for name, desc, parent in ROLE_DEFINITIONS:
        role_name_to_id[name] = None
        if name not in existing_roles:
            cur.execute(
                "INSERT INTO roles (name, description) VALUES (?, ?)",
                (name, desc),
            )
            role_name_to_id[name] = cur.lastrowid

    for row in cur.execute("SELECT id, name FROM roles").fetchall():
        role_name_to_id[row[1]] = row[0]

    for name, desc, parent_name in ROLE_DEFINITIONS:
        if parent_name and role_name_to_id.get(parent_name):
            cur.execute(
                "UPDATE roles SET parent_id = ? WHERE name = ?",
                (role_name_to_id[parent_name], name),
            )

    root_name_to_id = {}
    for row in cur.execute("SELECT id, name FROM roots").fetchall():
        root_name_to_id[row[1]] = row[0]

    cur.execute("DELETE FROM predicates")
    count = 0
    for predicate, root_name in PREDICATE_MAP.items():
        root_id = root_name_to_id.get(root_name)
        if root_id is None:
            logger.warning(f"Unknown root '{root_name}' for predicate '{predicate}', skipping")
            continue
        weight = PREDICATE_WEIGHTS.get(predicate, 1.0)
        language = "en"
        cur.execute(
            "INSERT INTO predicates (predicate, root_id, weight, language) VALUES (?, ?, ?, ?)",
            (predicate, root_id, weight, language),
        )
        count += 1

    conn.commit()
    conn.close()
    logger.info(f"Built ontology database: {count} predicates, "
                f"{len(ROOT_DEFINITIONS)} roots, {len(ROLE_DEFINITIONS)} roles")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    build_database()
