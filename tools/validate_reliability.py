#!/usr/bin/env python3
"""Check training/reliability against verified/launch_history_all.json: counts, leak-free features, chronological split, hashes."""
import csv, collections, hashlib, json, os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
T = os.path.join(ROOT, "training", "reliability")
ok = True
def check(n, c, d=""):
    global ok; print(("PASS " if c else "FAIL ") + n, d); ok &= bool(c)
L = [r for r in json.load(open(f"{ROOT}/verified/launch_history_all.json"))["records"] if r["status"] in ("Launch Successful", "Launch Failure", "Launch was a Partial Failure", "Launch Partial Failure")]
rows = list(csv.DictReader(open(f"{T}/launch_outcomes_all.csv")))
check("one outcome row per verified launch", len(rows) == len(L) and len({r["id"] for r in rows}) == len(rows), len(rows))
check("outcome labels match verified status", all((r["outcome"] == "success") == (x["status"] == "Launch Successful") for r, x in zip(rows, sorted(L, key=lambda x: (x["date_utc"], x["ll2_uuid"])))))
d = {s: [r["date_utc"] for r in rows if r["split"] == s] for s in ("train", "val", "test")}
check("chronological split, no future leakage", max(d["train"]) <= min(d["val"]) and max(d["val"]) <= min(d["test"]))
seen = collections.Counter(); bad = 0
for r in rows:
    bad += int(r["prior_launches_vehicle"]) != seen[r["vehicle"]]; seen[r["vehicle"]] += 1
check("prior_launches_vehicle counts only earlier launches", bad == 0, f"{bad} mismatches")
fr = list(csv.DictReader(open(f"{T}/failure_reasons.csv")))
check("failure_reasons covers every non-success", len(fr) == sum(r["outcome"] != "success" for r in rows), len(fr))
v = list(csv.DictReader(open(f"{T}/reliability_by_vehicle.csv")))
check("vehicle table launches sum to total", sum(int(x["launches"]) for x in v) == len(L))
check("success + failure + partial = launches; rate in [0,1]", all(int(x["successes"]) + int(x["failures"]) + int(x["partial_failures"]) == int(x["launches"]) and 0 <= float(x["ci95_low"]) <= float(x["success_rate"]) <= float(x["ci95_high"]) <= 1 for x in v))
man = json.load(open(f"{T}/manifest.json"))
check("manifest hashes match", all(hashlib.sha256(open(f"{T}/{f}", "rb").read()).hexdigest() == m["sha256"] for f, m in man["files"].items()))
blob = open(f"{T}/failure_reasons.csv").read()
import re
check("no emails/phones", not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+|\(\d{3}\)\s?\d{3}-\d{4}", blob))
sys.exit(0 if ok else 1)
