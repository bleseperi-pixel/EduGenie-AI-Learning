"""Live end-to-end check against a RUNNING server (uses your real Gemini key).

1) Start the server:   uvicorn main:app --reload
2) In a second terminal:   python smoke_test.py
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000"


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")
    except urllib.error.URLError as e:
        sys.exit(f"Cannot reach {BASE} ({e.reason}). Start the server first: uvicorn main:app --reload")


CHECKS = [
    ("Health", "GET", "/health", None, lambda d: d.get("status") == "ok"),
    ("Q&A", "POST", "/qa", {"question": "Which is the largest ocean?"}, lambda d: "pacific" in d["answer"].lower()),
    ("Explain", "POST", "/explain", {"topic": "Photosynthesis"}, lambda d: len(d["explanation"]) > 20),
    ("Quiz", "POST", "/quiz", {"text": "The Pythagoras Theorem"}, lambda d: len(d["quiz"]) >= 1 and len(d["quiz"][0]["options"]) == 4),
    ("Summarize", "POST", "/summarize", {"text": "Photosynthesis is the process by which green plants use sunlight, water and carbon dioxide to make glucose and oxygen. It happens in chloroplasts, which contain chlorophyll."}, lambda d: len(d["summary"]) > 20),
    ("Learning path", "GET", "/learn/recommendations?topic=" + urllib.parse.quote("SQL"), None, lambda d: len(d["recommendation"]) > 100),
]

failed = 0
for name, method, path, body, ok in CHECKS:
    status, data = call(method, path, body)
    try:
        passed = status == 200 and ok(data)
    except Exception:
        passed = False
    failed += not passed
    detail = "" if passed else f"  -> HTTP {status}: {data.get('error', data)}"
    print(f"{'PASS' if passed else 'FAIL'}  {name}{detail}")

sys.exit(1 if failed else 0)
