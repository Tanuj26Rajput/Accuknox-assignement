"""
Problem 1 - Fetch books from a REST API, store in SQLite, display them.
 
Default source: Open Library Search API (public, no key needed)
    https://openlibrary.org/search.json?q=<topic>&fields=title,author_name,first_publish_year
"""
import argparse
import sqlite3
import sys

import requests
 
DEFAULT_URL = "https://openlibrary.org/search.json"
DB_PATH = "books.db"
 
def fetch_books(url, params=None, retries=3, timeout=15):
    """GET the url and return decoded JSON. Retries on network / 5xx errors."""
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as e:
            last_err = e
            print(f"[warn] attempt {attempt}/{retries} failed: {e}", file=sys.stderr)
    raise SystemExit(f"Could not fetch data: {last_err}")
 
 
def normalise(payload):
    """Map different JSON shapes to [(title, author, year), ...]."""
    items = payload.get("docs", payload) if isinstance(payload, dict) else payload
    books = []
    for it in items:
        title = (it.get("title") or "").strip()
        if not title:
            continue                                    # skip unusable rows
        author = it.get("author")
        if author is None:
            names = it.get("author_name") or []         # Open Library returns a list
            author = ", ".join(names) if names else "Unknown"
        year = it.get("year") or it.get("publication_year") or it.get("first_publish_year")
        books.append((title, author, int(year) if year else None))
    return books
 
 
def init_db(conn):
    conn.execute(
        """CREATE TABLE IF NOT EXISTS books (
               id     INTEGER PRIMARY KEY AUTOINCREMENT,
               title  TEXT NOT NULL,
               author TEXT NOT NULL,
               year   INTEGER,
               UNIQUE (title, author, year)
           )"""
    )
 
 
def store_books(conn, books):
    """Insert with parameterised SQL; duplicates are ignored so re-runs are idempotent."""
    before = conn.total_changes
    conn.executemany("INSERT OR IGNORE INTO books (title, author, year) VALUES (?, ?, ?)", books)
    conn.commit()
    return conn.total_changes - before
 
 
def display_books(conn):
    rows = conn.execute("SELECT id, title, author, year FROM books ORDER BY year, title").fetchall()
    print(f"\n{'ID':<4} {'Title':<45} {'Author':<30} {'Year':<5}")
    print("-" * 86)
    for i, t, a, y in rows:
        print(f"{i:<4} {t[:44]:<45} {a[:29]:<30} {y if y else '-':<5}")
    print(f"\n{len(rows)} book(s) in {DB_PATH}")
 
 
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--topic", default="python")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()
 
    params = None
    if args.url == DEFAULT_URL:
        params = {"q": args.topic, "limit": args.limit,
                  "fields": "title,author_name,first_publish_year"}
 
    books = normalise(fetch_books(args.url, params))
    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)
        added = store_books(conn, books)
        print(f"Fetched {len(books)} book(s), inserted {added} new.")
        display_books(conn)
 
 
if __name__ == "__main__":
    main()