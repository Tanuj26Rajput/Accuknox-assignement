"""
Problem 3 - Import users (name, email) from a CSV file into SQLite.
 
Design choices (assumptions):
  * CSV has a header row with columns: name,email
  * email is the natural unique key (case-insensitive) -> duplicates are skipped
  * rows with a blank name or an invalid email are rejected and reported
  * whole import runs in one transaction (all-or-nothing on unexpected errors)
Usage: python csv_to_sqlite.py users.csv [--db users.db]
"""
import argparse
import csv
import re
import sqlite3
 
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
 
 
def init_db(conn):
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
               id    INTEGER PRIMARY KEY AUTOINCREMENT,
               name  TEXT NOT NULL,
               email TEXT NOT NULL UNIQUE COLLATE NOCASE
           )"""
    )
 
 
def import_csv(csv_path, db_path):
    stats = {"read": 0, "inserted": 0, "duplicates": 0, "invalid": 0}
    with open(csv_path, newline="", encoding="utf-8-sig") as f, sqlite3.connect(db_path) as conn:
        init_db(conn)
        reader = csv.DictReader(f)
        if not {"name", "email"} <= set(reader.fieldnames or []):
            raise SystemExit("CSV must have 'name' and 'email' columns.")
        for line_no, row in enumerate(reader, start=2):
            stats["read"] += 1
            name, email = (row["name"] or "").strip(), (row["email"] or "").strip()
            if not name or not EMAIL_RE.match(email):
                stats["invalid"] += 1
                print(f"[reject] line {line_no}: {row}")
                continue
            cur = conn.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", (name, email))
            stats["inserted" if cur.rowcount else "duplicates"] += 1
    return stats
 
 
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_file")
    ap.add_argument("--db", default="users.db")
    args = ap.parse_args()
    s = import_csv(args.csv_file, args.db)
    print(f"Read {s['read']} | inserted {s['inserted']} | duplicates skipped {s['duplicates']} | invalid {s['invalid']}")
    with sqlite3.connect(args.db) as conn:
        for row in conn.execute("SELECT id, name, email FROM users ORDER BY id"):
            print(row)
 
 
if __name__ == "__main__":
    main()
