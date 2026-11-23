"""Tiny local REST API so Problems 1 and 2 can be run/tested offline.
   GET /books  -> [{title, author, year}]      GET /scores -> [{name, score}]"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

BOOKS = [
    {"title": "Fluent Python", "author": "Luciano Ramalho", "year": 2015},
    {"title": "Python Crash Course", "author": "Eric Matthes", "year": 2015},
    {"title": "Automate the Boring Stuff with Python", "author": "Al Sweigart", "year": 2015},
    {"title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "year": 2017},
    {"title": "Hands-On Machine Learning", "author": "Aurelien Geron", "year": 2019},
]
SCORES = [
    {"name": "Aarav", "score": 78}, {"name": "Diya", "score": 92}, {"name": "Kabir", "score": 65},
    {"name": "Meera", "score": 88}, {"name": "Rohan", "score": 54}, {"name": "Sanya", "score": 71},
    {"name": "Vikram", "score": 96}, {"name": "Zoya", "score": 83},
]
ROUTES = {"/books": BOOKS, "/scores": SCORES}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = ROUTES.get(self.path.split("?")[0])
        body = json.dumps(data if data is not None else {"error": "not found"}).encode()
        self.send_response(200 if data is not None else 404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print("Mock API on http://127.0.0.1:8000  (Ctrl+C to stop)")
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
