"""
Problem 2 - Fetch students' test scores from an API, compute the average,
and draw a bar chart.

Assumed API contract (documented assumption): GET <url> returns
    [{"name": "Aarav", "score": 78}, ...]
Run the bundled mock API first:   python mock_api.py
Then:                             python student_scores.py --url http://127.0.0.1:8000/scores
"""
import argparse
import statistics
import sys
 
import matplotlib
matplotlib.use("Agg")                      # headless-safe; we save a PNG
import matplotlib.pyplot as plt
import requests
 
 
def fetch_scores(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
    except (requests.RequestException, ValueError) as e:
        raise SystemExit(f"Could not fetch scores: {e}")
    clean = []
    for row in data:
        try:
            clean.append((str(row["name"]), float(row["score"])))
        except (KeyError, TypeError, ValueError):
            print(f"[warn] skipping malformed row: {row}", file=sys.stderr)
    if not clean:
        raise SystemExit("No valid score records returned.")
    return clean
 
 
def plot(records, avg, out):
    names, scores = zip(*records)
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(names, scores, color=["#2E7D32" if s >= avg else "#C62828" for s in scores])
    ax.axhline(avg, color="#1F3A5F", linestyle="--", linewidth=1.5, label=f"Average = {avg:.2f}")
    ax.bar_label(bars, fmt="%.0f", padding=2)
    ax.set_ylim(0, 105)
    ax.set_xlabel("Student")
    ax.set_ylabel("Test score")
    ax.set_title("Student test scores (green = at/above average, red = below)")
    ax.legend()
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"Chart saved to {out}")
 
 
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8000/scores")
    ap.add_argument("--out", default="scores_chart.png")
    args = ap.parse_args()
 
    records = fetch_scores(args.url)
    avg = statistics.mean(s for _, s in records)
    print(f"Students: {len(records)}   Average score: {avg:.2f}   "
          f"Highest: {max(records, key=lambda r: r[1])}   Lowest: {min(records, key=lambda r: r[1])}")
    plot(records, avg, args.out)
 
 
if __name__ == "__main__":
    main()
