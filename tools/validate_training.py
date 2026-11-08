#!/usr/bin/env python3
"""Check training/ against verified/: every QA value equals its source field, ids unique, splits disjoint, hashes match, no personal data."""
import csv, hashlib, json, math, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
T, V = os.path.join(ROOT, "training"), os.path.join(ROOT, "verified")
ok = True


def check(name, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + name, detail)
    ok &= bool(cond)


recs = {}
def rec(c, i):
    if c not in recs:
        recs[c] = {r["id"]: r for r in json.load(open(f"{V}/{c}.json"))["records"]}
    return recs[c][i]


def get(r, path):
    for p in path.split("."):
        r = r[p]
    return r


qa = [json.loads(l) for l in open(f"{T}/qa_pairs.jsonl")]
check("qa ids unique", len({q["id"] for q in qa}) == len(qa), len(qa))
bad = 0
for q in qa:
    r = rec(q["source_collection"], q["source_id"])
    if q["field"] == "success_rate":
        exp = round(r["successful_launches"] / r["total_launches"], 4)
    elif q["field"] in ("mass_kg_from_text", "power_w_from_text"):
        exp = r[q["field"]]
    elif q["source_collection"] == "smallsat_components":
        exp = r["numeric"][q["field"]]
    else:
        exp = get(r, q["field"])
    if not math.isclose(exp, q["value"], rel_tol=1e-9) or q["data_class"] not in ("verified", "derived"):
        bad += 1
check("every QA value equals its verified source field", bad == 0, f"{bad} mismatches")
check("answers contain the value to 6 sig. figs", all(f"{q['value']:.6g}" in q["messages"][1]["content"] or q["field"] == "success_rate" for q in qa))

ph = [json.loads(l) for l in open(f"{T}/physics_examples.jsonl")]
check("physics ids unique", len({p["id"] for p in ph}) == len(ph), len(ph))
check("hohmann totals consistent", all(abs(p["outputs"]["dv1_m_s"] + p["outputs"]["dv2_m_s"] - p["outputs"]["total_m_s"]) < 1e-6 for p in ph if p["task"] == "hohmann"))
check("rocket eq: dv>0 and propellant=m0-mf", all(p["outputs"]["dv_m_s"] > 0 and p["outputs"]["propellant_kg"] == p["inputs"]["m0_kg"] - p["inputs"]["mf_kg"] for p in ph if p["task"] == "rocket_equation"))
check("same body never in two splits (physics)", len({(p["inputs"].get("body") or p["inputs"].get("engine"), p["split"]) for p in ph}) == len({p["inputs"].get("body") or p["inputs"].get("engine") for p in ph}))

lo = list(csv.DictReader(open(f"{T}/launch_outcome.csv")))
check("launch outcome ids unique", len({r["id"] for r in lo}) == len(lo), len(lo))
d = {s: [r["date_utc"] for r in lo if r["split"] == s] for s in ("train", "val", "test")}
check("launch split is chronological (no leakage)", max(d["train"]) <= min(d["val"]) and max(d["val"]) <= min(d["test"]))
check("launch labels binary", {r["success"] for r in lo} <= {"0", "1"})
for fn, key in (("launcher_specs.csv", "id"), ("component_numeric.csv", None)):
    rows = list(csv.DictReader(open(f"{T}/{fn}")))
    if key:
        check(fn + " ids unique", len({r[key] for r in rows}) == len(rows), len(rows))
    else:
        by = {}
        for r in rows:
            by.setdefault(r["id"], set()).add(r["split"])
        check(fn + " one split per record", all(len(s) == 1 for s in by.values()), len(rows))

man = json.load(open(f"{T}/manifest.json"))
check("manifest hashes match files", all(hashlib.sha256(open(f"{T}/{f}", "rb").read()).hexdigest() == m["sha256"] for f, m in man["files"].items()))
blob = "".join(open(f"{T}/{f}", errors="ignore").read() for f in man["files"])
check("no emails or phone numbers", not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+|\(\d{3}\)\s?\d{3}-\d{4}", blob))
sys.exit(0 if ok else 1)
