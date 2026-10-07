"""Serves the React test page and classifies one person with the saved model."""
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "web" / "dist"
BUNDLE = joblib.load(ROOT.parent / "data" / "thyroid_dataset_model.joblib")
MODEL = BUNDLE["model"]
IMPUTER = BUNDLE["imputer"]
SCALER = BUNDLE["scaler"]
COLUMNS = BUNDLE["columns"]
NUMERIC = BUNDLE.get("numeric_columns", list(IMPUTER.feature_names_in_))

YES_NO = [
    "on_thyroxine",
    "query_on_thyroxine",
    "on_antithyroid_medication",
    "thyroid_surgery",
    "I131_treatment",
    "lithium",
    "query_hypothyroid",
    "query_hyperthyroid",
    "pregnant",
    "sick",
    "tumor",
    "psych",
]

LABS = ["TSH", "T3", "TT4", "T4U", "FTI"]

NAMES = {
    "no_problem": "No thyroid problem",
    "hypothyroid": "Hypothyroid",
    "hyperthyroid": "Hyperthyroid",
}

TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".svg": "image/svg+xml",
    ".json": "application/json; charset=utf-8",
}


def number_or_blank(text):
    text = str(text or "").strip()
    if text == "":
        return np.nan
    return float(text)


def classify(form):
    sex = form.get("sex", "")
    if sex not in ("F", "M", "Unknown"):
        raise ValueError("Choose sex.")
    age = number_or_blank(form.get("age"))
    if pd.notna(age) and not float(age).is_integer():
        raise ValueError("Age must be a whole number.")
    # Same rule as the notebook: an age above 100 is missing, then filled later.
    if pd.notna(age) and age > 100:
        age = np.nan
    row = {
        "age": age,
        "sex_M": 1 if sex == "M" else 0,
        "sex_Unknown": 1 if sex == "Unknown" else 0,
    }
    for key in YES_NO:
        answer = str(form.get(key, "")).strip()
        if answer not in ("0", "1"):
            raise ValueError("Answer every clinical question.")
        row[key] = int(answer)
    for key in LABS:
        value = number_or_blank(form.get(key))
        row[key] = value
        row[f"{key}_measured"] = 0 if np.isnan(value) else 1

    frame = pd.DataFrame([row])
    frame[NUMERIC] = IMPUTER.transform(frame[NUMERIC])
    frame = frame.reindex(columns=COLUMNS, fill_value=0)
    frame[NUMERIC] = SCALER.transform(frame[NUMERIC])

    label = MODEL.predict(frame)[0]
    probs = MODEL.predict_proba(frame)[0]
    ordered = sorted(zip(MODEL.classes_, probs), key=lambda item: -item[1])
    return {
        "label": str(label),
        "name": NAMES.get(label, str(label)),
        "probabilities": [
            {"name": NAMES.get(name, str(name)), "value": float(prob)}
            for name, prob in ordered
        ],
    }


def static_file(url_path):
    relative = unquote(url_path).lstrip("/") or "index.html"
    target = (DIST / relative).resolve()
    if DIST.resolve() not in target.parents and target != DIST.resolve():
        return None
    if target.is_dir():
        target = target / "index.html"
    if not target.is_file():
        return None
    return target


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if not DIST.exists():
            body = b"Run npm run build inside the web folder first."
            self._send(500, "text/plain; charset=utf-8", body)
            return
        target = static_file(path)
        if target is None:
            target = DIST / "index.html"
        content_type = TYPES.get(target.suffix, "application/octet-stream")
        self._send(200, content_type, target.read_bytes())

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/predict":
            self._send(404, "application/json", b'{"error":"Not found"}')
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        try:
            form = json.loads(raw or "{}")
            result = classify(form)
            body = json.dumps(result).encode("utf-8")
            self._send(200, "application/json", body)
        except Exception as exc:
            body = json.dumps({"error": f"Could not classify that row: {exc}"}).encode("utf-8")
            self._send(400, "application/json", body)

    def _send(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(fmt % args)


if __name__ == "__main__":
    try:
        server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    except OSError:
        print("The page is already running. Opening http://127.0.0.1:8765")
        webbrowser.open("http://127.0.0.1:8765")
    else:
        print("open http://127.0.0.1:8765")
        webbrowser.open("http://127.0.0.1:8765")
        server.serve_forever()
