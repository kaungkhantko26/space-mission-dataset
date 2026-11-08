#!/usr/bin/env python3
"""Cross-check the Kaggle 'All Space Missions from 1957' file against Launch Library 2 (verified/launch_history_all.json).
Kaggle values are NOT published; only the agreement statistics are (training/reliability/kaggle_crosscheck.json).
Match key: UTC date + normalised vehicle name (text before ' | ')."""
import csv, datetime, json, os, re, collections
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
K = os.path.join(ROOT, "data_raw", "retrieved", "kaggle", "all_space_missions", "Space_Corrected.csv")
norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
ll = collections.defaultdict(list)
for r in json.load(open(f"{ROOT}/verified/launch_history_all.json"))["records"]:
    ll[r["date_utc"][:10]].append(r)
rows = list(csv.DictReader(open(K, encoding="utf-8", errors="ignore")))
st = lambda s: {"Success": "Launch Successful", "Failure": "Launch Failure", "Prelaunch Failure": "Launch Failure", "Partial Failure": "Launch was a Partial Failure"}.get(s)
n = matched = agree = 0; dis = []; by_year = collections.Counter(); unmatched_year = collections.Counter()
for r in rows:
    m = re.match(r"\w+ (\w+ \d+, \d{4}) (\d+:\d+) UTC", r["Datum"] or "")
    if not m: continue
    d = datetime.datetime.strptime(m.group(1), "%b %d, %Y").date()
    veh = norm((r["Detail"] or "").split("|")[0])
    n += 1
    cands = [x for dd in (d, d - datetime.timedelta(days=1), d + datetime.timedelta(days=1)) for x in ll.get(dd.isoformat(), [])]
    hit = [x for x in cands if norm(x["vehicle"]) and (norm(x["vehicle"]) in veh or veh in norm(x["vehicle"]) or norm(x["vehicle_family"] or "~") in veh)]
    if not hit:
        unmatched_year[d.year // 10 * 10] += 1; continue
    matched += 1
    ok = any(x["status"] == st(r["Status Mission"]) for x in hit)
    agree += ok
    if not ok: dis.append(dict(date=str(d), kaggle_detail=r["Detail"], kaggle_status=r["Status Mission"], ll2_status=[x["status"] for x in hit]))
rep = dict(kaggle_rows=len(rows), parsed=n, matched_to_ll2=matched, outcome_agrees=agree, outcome_agreement_rate=round(agree / matched, 4) if matched else None,
           unmatched_by_decade=dict(sorted(unmatched_year.items())), disagreements_sample=dis[:25], disagreements_total=len(dis),
           note="Kaggle file used only to cross-check Launch Library 2 outcomes; Kaggle values (including its cost column) are not redistributed.")
json.dump(rep, open(os.path.join(ROOT, "training", "reliability", "kaggle_crosscheck.json"), "w"), indent=2)
print(json.dumps({k: rep[k] for k in ("kaggle_rows", "parsed", "matched_to_ll2", "outcome_agrees", "outcome_agreement_rate", "disagreements_total")}))
