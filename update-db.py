# -*- coding: utf-8 -*-
"""
update-db.py
- Replace seeded data for a single tab from a CSV.
- Backs up app.db and seed.sql, rewrites the correct INSERT block in seed.sql,
  rebuilds the SQLite DB by executing schema.sql + seed.sql via Python's sqlite3,
  and prints a quick preview.

Usage:
  python3 update-db.py -f 2025-ALEF-BEIT.csv
"""

import argparse
import csv
import datetime as dt
import os
import re
import shutil
import sqlite3
import sys
from typing import Dict, List, Optional, Tuple

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DEFAULT_DB = os.path.join(PROJECT_ROOT, "app/app.db")
DEFAULT_SCHEMA = os.path.join(PROJECT_ROOT, "schema.sql")
DEFAULT_SEED = os.path.join(PROJECT_ROOT, "seed.sql")

# --- Your 6 content tabs (intro "home" is not part of this list) ---
# number -> (label_he, logical_id, db_table, seed_block_marker)
TAB_CHOICES = {
    1: ("גן",         "docs",       "docs",       "docs"),
    2: ("בית א׳-ב׳",  "tasks",      "tasks",      "tasks"),
    3: ("בית ג׳-ד׳",  "notes",      "notes",      "notes"),
    4: ("בית ה׳-ו׳",  "alerts",     "alerts",     "alerts"),
    5: ("בית חט״ב",   "links",      "links",      "links"),
    6: ("תיכון",      "hs",         "highschool", "highschool"),
}

# Expected column order for INSERTs (no id; id is auto)
TABLE_COLUMNS = [
    "course_name",
    "teacher_name",
    "intended_for",
    "course_info",
    "requirments",
    "category",
    "allow_valenteres",
    "valentieres_age",
    "max_valetires",
    "additional_info",
]

# Optional header normalization: accept common variants (English + Hebrew)
HEADER_ALIASES = {
    "course_name": {"course_name", "corese_name", "course", "course title", "שם קורס", "שם שיעור"},
    "teacher_name": {"teacher_name", "teacher", "מורה", "שם מורה"},
    "intended_for": {"intended_for", "target", "מיועד ל"},
    "course_info": {"course_info", "description", "about", "תיאור", "מידע על הקורס"},
    "requirments": {"requirments", "requirements", "דרישות"},
    "category": {"category", "קטגוריה"},
    "allow_valenteres": {"allow_valenteres", "allow_volunteers", "מתנדבים"},
    "valentieres_age": {"valentieres_age", "volunteers_age", "גיל מתנדבים"},
    "max_valetires": {"max_valetires", "max_volunteers", "מקס מתנדבים", "כמות מתנדבים מקס"},
    "additional_info": {"additional_info", "notes", "מידע נוסף"},
}

TRUTHY = {"1", "true", "yes", "y", "on", "כן", "נכון"}

def parse_args():
    ap = argparse.ArgumentParser(description="Replace a tab's seed data from a CSV and rebuild the DB.")
    ap.add_argument("-f", "--file", required=True, help="Path to CSV (UTF-8).")
    ap.add_argument("--db", default=DEFAULT_DB, help="Path to SQLite DB (default: /app/app.db)")
    ap.add_argument("--schema", default=DEFAULT_SCHEMA, help="Path to schema.sql")
    ap.add_argument("--seed", default=DEFAULT_SEED, help="Path to seed.sql")
    ap.add_argument("--no-rebuild", action="store_true", help="Only update seed.sql, do not rebuild DB")
    return ap.parse_args()

def backup_file(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = f"{path}.bak.{ts}"
    shutil.copy2(path, backup)
    return backup

def normalize_headers(fieldnames: List[str]) -> Dict[str, str]:
    """Map CSV headers to our canonical column names."""
    mapping: Dict[str, str] = {}
    lower = {fn.strip(): fn for fn in fieldnames if fn is not None}
    for canon, aliases in HEADER_ALIASES.items():
        found = None
        for alias in aliases:
            # search case-insensitively
            for raw in lower:
                if raw.lower() == alias.lower():
                    found = lower[raw]
                    break
            if found:
                break
        if found:
            mapping[canon] = found
    return mapping

def to_sql_literal(val, numeric_as_null=False) -> str:
    """Render a Python value to an SQL literal string (with proper escaping)."""
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val)
    s = str(val).strip()
    if s == "":
        return "NULL" if numeric_as_null else "''"
    # numeric_as_null means: if not parseable number, leave as quoted string; else as number
    if numeric_as_null:
        try:
            int_val = int(s)
            return str(int_val)
        except ValueError:
            pass
    # escape single quotes
    s = s.replace("'", "''")
    return f"'{s}'"

def parse_bool(val) -> int:
    if val is None:
        return 0
    s = str(val).strip().lower()
    return 1 if s in TRUTHY else 0

def read_csv_rows(csv_path: str) -> List[Dict[str, str]]:
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit("CSV appears to have no header row.")
        mapping = normalize_headers(reader.fieldnames)
        rows = []
        for raw in reader:
            row = {}
            for col in TABLE_COLUMNS:
                src = mapping.get(col)
                row[col] = raw.get(src, "") if src else ""
            # trim whitespace
            row = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            # REQUIRE: both course_name and teacher_name must exist; otherwise skip
            if not row.get("course_name") or not row.get("teacher_name"):
                continue
            # DEFAULT: if category missing/blank, set to "כללי"
            if not row.get("category"):
                row["category"] = "כללי"
            rows.append(row)
        return rows

def get_allowed_categories(db_path: str) -> List[str]:
    if not os.path.exists(db_path):
        return []
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = lambda c, r: r[0]
            cats = conn.execute("SELECT name FROM categories ORDER BY name").fetchall()
        return list(cats)
    except Exception:
        return []

def map_categories(rows: List[Dict[str, str]], allowed: List[str]) -> Tuple[List[Dict[str, str]], List[Tuple[str, int]]]:
    """Ensure category is allowed; if blank or unknown, map to 'כללי'."""
    unknowns = {}
    allowed_set = set(allowed or [])
    for r in rows:
        cat_raw = (r.get("category") or "").strip()
        if cat_raw == "":
            r["category"] = "כללי"
            continue
        if allowed_set and cat_raw not in allowed_set:
            unknowns[cat_raw] = unknowns.get(cat_raw, 0) + 1
            r["category"] = "כללי"
        else:
            r["category"] = cat_raw
    report = sorted(unknowns.items(), key=lambda x: (-x[1], x[0]))
    return rows, report

def generate_insert_sql(table: str, rows: List[Dict[str, str]]) -> str:
    header = f"INSERT INTO {table}(" + ",".join(TABLE_COLUMNS) + ") VALUES\n"
    values_sql = []
    for r in rows:
        allow = parse_bool(r.get("allow_valenteres"))
        max_vol = r.get("max_valetires")
        # render each column with correct type handling
        vals = [
            to_sql_literal(r.get("course_name")),
            to_sql_literal(r.get("teacher_name")),
            to_sql_literal(r.get("intended_for")),
            to_sql_literal(r.get("course_info")),
            to_sql_literal(r.get("requirments")),
            to_sql_literal(r.get("category")),
            str(allow),  # integer 0/1 without quotes
            to_sql_literal(r.get("valentieres_age")),
            to_sql_literal(max_vol, numeric_as_null=True),
            to_sql_literal(r.get("additional_info")),
        ]
        values_sql.append("(" + ", ".join(vals) + ")")
    return header + ",\n".join(values_sql) + ";\n"

def replace_seed_block(seed_text: str, table: str, new_insert_sql: str) -> str:
    """
    Replace the INSERT block for a table in seed.sql.
    We assume the file contains:
      -- ******** <table> ********
      INSERT INTO <table>(...) VALUES
      (...),
      (...);
    """
    marker = f"-- ******** {table} ********"
    start = seed_text.find(marker)
    if start == -1:
        raise SystemExit(f"Could not find marker for table '{table}' in seed.sql")

    # Find the INSERT line following the marker
    insert_re = re.compile(
        rf"(INSERT\s+INTO\s+{re.escape(table)}\s*\([^;]+?\);\s*)",
        re.IGNORECASE | re.DOTALL
    )
    after_marker = seed_text[start:]
    m = insert_re.search(after_marker)
    if not m:
        raise SystemExit(f"Could not find INSERT block for table '{table}' after its marker in seed.sql")

    # Compute absolute indices to replace
    insert_abs_start = start + m.start(1)
    insert_abs_end = start + m.end(1)

    # Reconstruct the file text
    before = seed_text[:insert_abs_start]
    after = seed_text[insert_abs_end:]
    return before + new_insert_sql + after

def rebuild_db(db_path: str, schema_path: str, seed_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(open(schema_path, "r", encoding="utf-8").read())
        conn.executescript(open(seed_path, "r", encoding="utf-8").read())
        conn.commit()

def preview_rows(db_path: str, table: str, limit: int = 5):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    print(f"\nPreview from '{table}' (top {limit}):")
    for r in rows:
        d = dict(r)
        print(f"- id={d.get('id')}, course_name={d.get('course_name')}, teacher_name={d.get('teacher_name')}, category={d.get('category')}")

def main():
    args = parse_args()

    if not os.path.exists(args.file):
        print(f"CSV not found: {args.file}")
        sys.exit(1)

    print("Which tab do you want to replace?")
    for n in sorted(TAB_CHOICES):
        print(f"{n}. {TAB_CHOICES[n][0]}")
    try:
        choice = int(input("Enter number (1-6): ").strip())
    except Exception:
        print("Invalid selection.")
        sys.exit(1)
    if choice not in TAB_CHOICES:
        print("Invalid selection.")
        sys.exit(1)

    label_he, logical_id, table, marker = TAB_CHOICES[choice]
    print(f"\nSelected: {label_he}  → table: {table}")

    # Backups
    db_backup = backup_file(args.db)
    seed_backup = backup_file(args.seed)
    if db_backup:
        print(f"Backed up DB to: {db_backup}")
    if seed_backup:
        print(f"Backed up seed to: {seed_backup}")

    # Load CSV and normalize
    csv_rows = read_csv_rows(args.file)

    # Validate/massage categories against current DB categories (if DB exists)
    allowed = get_allowed_categories(args.db)
    csv_rows, unknown_report = map_categories(csv_rows, allowed)
    if unknown_report:
        print("\nWARNING: Some categories in the CSV were not in categories table and were mapped to 'כללי':")
        for name, count in unknown_report:
            print(f"  - {name} ({count} rows)")

    if not csv_rows:
        print("No data rows found in CSV.")
        sys.exit(1)

    new_sql = generate_insert_sql(table, csv_rows)

    # Read, replace block, and write seed.sql
    seed_text = open(args.seed, "r", encoding="utf-8").read()
    try:
        updated_seed = replace_seed_block(seed_text, marker, new_sql)
    except SystemExit as e:
        print(str(e))
        sys.exit(1)

    with open(args.seed, "w", encoding="utf-8", newline="\n") as f:
        f.write(updated_seed)
    print(f"\nUpdated seed.sql for table '{table}'.")

    # Rebuild DB unless skipped
    if not args.no_rebuild:
        print("\nRebuilding database from schema.sql + seed.sql ...")
        rebuild_db(args.db, args.schema, args.seed)
        print("Rebuild complete.")
        preview_rows(args.db, table, limit=5)
    else:
        print("\nSkipping DB rebuild (--no-rebuild).")

    print("\nDone.")

if __name__ == "__main__":
    main()