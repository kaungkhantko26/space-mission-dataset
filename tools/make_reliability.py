#!/usr/bin/env python3
"""Real launch success/failure data for ALL providers (verified/launch_history_all.json, Launch Library 2) -> training/reliability/.

Outputs
  launch_outcomes_all.csv     one row per launch; leak-free features (only earlier launches); chronological split
  failure_reasons.csv         every failure/partial failure with NASA-free source text + keyword-derived cause category
  reliability_by_*.csv        success rates with Wilson 95% intervals (vehicle, family, provider, country, year, orbit)
  maturity_curve.csv          success rate by launch number of a vehicle family (infant mortality)
  reliability_qa.jsonl        chat Q&A from the tables
  baseline_report.json        how well simple predictors score (so you know what 'good' means)
"""
import csv, hashlib, json, math, os, re, collections

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "training", "reliability"); os.makedirs(OUT, exist_ok=True)
L = json.load(open(os.path.join(ROOT, "verified", "launch_history_all.json")))["records"]
L = [r for r in L if r["date_utc"] and r["status"] in ("Launch Successful", "Launch Failure", "Launch was a Partial Failure", "Launch Partial Failure")]
L.sort(key=lambda r: (r["date_utc"], r["ll2_uuid"]))
CLS = lambda s: "success" if s == "Launch Successful" else "failure" if s == "Launch Failure" else "partial_failure"

CAUSES = [("engine/propulsion", r"engine|thrust|turbopump|combust|propuls|nozzle|motor|burn|pressuri|fuel|oxidi|valve|leak|ignition|shutdown"),
          ("stage separation/fairing", r"separat|fairing|shroud|staging|deploy"),
          ("guidance/control/software", r"guidance|control|software|navigation|attitude|gyro|computer|steering|trajectory|autopilot|avionic|sensor|electrical|power system|short"),
          ("structure/aerodynamic", r"structur|break|disintegr|aerodynamic|vibration|explod|burst|rupture|crack|buckl"),
          ("upper stage/orbit insertion", r"upper stage|second stage|third stage|orbit|insertion|apogee|fregat|centaur|kick")]


def cause(txt):
    t = (txt or "").lower()
    if not t.strip(): return "not stated"
    for name, pat in CAUSES:
        if re.search(pat, t): return name
    return "other/unclassified"


def wilson(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(max(0, c - h), 4), round(min(1, c + h), 4))


split_of = lambda i, n: "train" if i < int(n * .70) else "val" if i < int(n * .85) else "test"
n = len(L)
veh, fam, prov = (collections.defaultdict(lambda: [0, 0]) for _ in range(3))   # [launches, failures]
first = {}; last_prov = {}
rows = []
for i, r in enumerate(L):
    v, f, p = r["vehicle"] or "?", r["vehicle_family"] or r["vehicle"] or "?", r["launch_provider"] or "?"
    y, d = int(r["date_utc"][:4]), r["date_utc"][:10]
    prior = lambda t: t[0]
    smooth = lambda t, base=0.05: (t[1] + base * 3) / (t[0] + 3)   # additive smoothing toward 5% prior
    first.setdefault(f, d)
    age = (int(d[:4]) - int(first[f][:4])) * 365 + (int(d[5:7]) - int(first[f][5:7])) * 30
    rows.append(dict(id=r["id"], date_utc=r["date_utc"], year=y, split=split_of(i, n), outcome=CLS(r["status"]), success=int(r["status"] == "Launch Successful"),
                     provider=p, provider_type=r.get("provider_type"), country=r.get("country_code"), vehicle=v, vehicle_family=f, orbit=r["orbit_abbrev"],
                     mission_type=r["mission_type"], pad=r["pad"],
                     prior_launches_vehicle=veh[v][0], prior_failures_vehicle=veh[v][1], prior_launches_family=fam[f][0], prior_failures_family=fam[f][1],
                     prior_launches_provider=prov[p][0], prior_failures_provider=prov[p][1], smoothed_prior_failure_rate_family=round(smooth(fam[f]), 4),
                     smoothed_prior_failure_rate_vehicle=round(smooth(veh[v]), 4), family_age_days=max(0, age), data_class="derived_features_of_verified"))
    bad = r["status"] != "Launch Successful"
    for t in (veh[v], fam[f], prov[p]):
        t[0] += 1; t[1] += bad
cols = list(rows[0].keys())
with open(os.path.join(OUT, "launch_outcomes_all.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)

# failures
fr = []
for r in L:
    if r["status"] != "Launch Successful":
        fr.append(dict(id=r["id"], date_utc=r["date_utc"][:10], outcome=CLS(r["status"]), vehicle=r["vehicle"], provider=r["launch_provider"], orbit=r["orbit_abbrev"],
                       pad=r["pad"], failure_reason_text=r["failure_reason"] or "", cause_category=cause(r["failure_reason"]), category_source="keyword_rules_on_source_text"))
with open(os.path.join(OUT, "failure_reasons.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(fr[0].keys())); w.writeheader(); w.writerows(fr)


# reliability tables
def table(name, key):
    g = collections.defaultdict(lambda: [0, 0, 0])
    for r in L:
        k = key(r)
        if k is None: continue
        g[k][0] += 1; g[k][1] += r["status"] == "Launch Successful"; g[k][2] += r["status"] == "Launch Failure"
    out = []
    for k, (t, s, f) in sorted(g.items(), key=lambda kv: -kv[1][0]):
        lo, hi = wilson(s, t)
        out.append(dict(**{name: k}, launches=t, successes=s, failures=f, partial_failures=t - s - f, success_rate=round(s / t, 4), ci95_low=lo, ci95_high=hi,
                        low_sample_warning=int(t < 20)))
    with open(os.path.join(OUT, f"reliability_by_{name}.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    return out


T = {nm: table(nm, fn) for nm, fn in (("vehicle", lambda r: r["vehicle"]), ("family", lambda r: r["vehicle_family"]), ("provider", lambda r: r["launch_provider"]),
                                      ("country", lambda r: r.get("country_code")), ("year", lambda r: int(r["date_utc"][:4])), ("orbit", lambda r: r["orbit_abbrev"]),
                                      ("mission_type", lambda r: r["mission_type"]))}

# maturity curve: success rate by the launch number of a family
cnt = collections.Counter(); g = collections.defaultdict(lambda: [0, 0])
for r in L:
    f = r["vehicle_family"] or r["vehicle"]; cnt[f] += 1; k = cnt[f]
    b = "1-5" if k <= 5 else "6-10" if k <= 10 else "11-25" if k <= 25 else "26-100" if k <= 100 else "100+"
    g[b][0] += 1; g[b][1] += r["status"] == "Launch Successful"
mc = [dict(launch_number_in_family=b, launches=g[b][0], successes=g[b][1], success_rate=round(g[b][1] / g[b][0], 4), ci95_low=wilson(g[b][1], g[b][0])[0], ci95_high=wilson(g[b][1], g[b][0])[1])
      for b in ("1-5", "6-10", "11-25", "26-100", "100+") if g[b][0]]
with open(os.path.join(OUT, "maturity_curve.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(mc[0].keys())); w.writeheader(); w.writerows(mc)

# Q&A
qa = []
for nm, label in (("vehicle", "vehicle"), ("family", "rocket family"), ("provider", "launch provider"), ("country", "country")):
    for t in T[nm]:
        if t["launches"] >= 5:
            k = t[nm]
            qa.append(dict(id=f"relqa_{nm}_{hashlib.md5(str(k).encode()).hexdigest()[:8]}", split="test" if int(hashlib.md5(str(k).encode()).hexdigest(), 16) % 10 == 0 else "val" if int(hashlib.md5(str(k).encode()).hexdigest(), 16) % 10 == 1 else "train",
                           data_class="derived", messages=[{"role": "user", "content": f"What is the launch success rate of the {label} {k}?"},
                                                           {"role": "assistant", "content": f"{k}: {t['successes']} of {t['launches']} launches succeeded ({100*t['success_rate']:.1f}%, 95% interval {100*t['ci95_low']:.1f}-{100*t['ci95_high']:.1f}%), "
                                                            f"{t['failures']} failures, {t['partial_failures']} partial failures (Launch Library 2)." + (" Small sample - treat with caution." if t["low_sample_warning"] else "")}]))
cc = collections.Counter(x["cause_category"] for x in fr)
qa.append(dict(id="relqa_causes", split="train", data_class="derived", messages=[{"role": "user", "content": "What are the most common reasons launches fail?"},
                                                                                {"role": "assistant", "content": "Among %d failed or partially failed launches, the stated causes fall into (keyword-classified from source text): " % len(fr) + "; ".join(f"{k} {v}" for k, v in cc.most_common()) + "."}]))
qa.append(dict(id="relqa_maturity", split="train", data_class="derived", messages=[{"role": "user", "content": "Do new rockets fail more often than mature ones?"},
                                                                                  {"role": "assistant", "content": "Success rate by launch number within a rocket family: " + "; ".join(f"launches {m['launch_number_in_family']}: {100*m['success_rate']:.1f}% (n={m['launches']})" for m in mc) + "."}]))
with open(os.path.join(OUT, "reliability_qa.jsonl"), "w") as fh:
    for q in qa: fh.write(json.dumps(q) + "\n")


# baseline predictors on the chronological test split
def auc(y, s):
    pos = [a for a, b in zip(s, y) if b == 1]; neg = [a for a, b in zip(s, y) if b == 0]
    if not pos or not neg: return None
    sc = sorted(range(len(s)), key=lambda i: s[i]); rank = {}
    i = 0
    while i < len(sc):
        j = i
        while j + 1 < len(sc) and s[sc[j + 1]] == s[sc[i]]: j += 1
        for k in range(i, j + 1): rank[sc[k]] = (i + j) / 2 + 1
        i = j + 1
    R = sum(rank[i] for i in range(len(y)) if y[i] == 1)
    return (R - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


tr = [r for r in rows if r["split"] == "train"]; te = [r for r in rows if r["split"] == "test"]
fail_te = [1 - r["success"] for r in te]; base = sum(1 - r["success"] for r in tr) / len(tr)
brier = lambda p, y: sum((a - b) ** 2 for a, b in zip(p, y)) / len(y)
rep = dict(test_launches=len(te), test_failure_rate=round(sum(fail_te) / len(te), 4), train_failure_rate=round(base, 4),
           brier_always_train_base_rate=round(brier([base] * len(te), fail_te), 5),
           brier_family_prior_failure_rate=round(brier([r["smoothed_prior_failure_rate_family"] for r in te], fail_te), 5),
           brier_vehicle_prior_failure_rate=round(brier([r["smoothed_prior_failure_rate_vehicle"] for r in te], fail_te), 5),
           auc_family_prior_failure_rate=auc(fail_te, [r["smoothed_prior_failure_rate_family"] for r in te]),
           auc_vehicle_prior_failure_rate=auc(fail_te, [r["smoothed_prior_failure_rate_vehicle"] for r in te]),
           auc_young_family_age=auc(fail_te, [-r["family_age_days"] for r in te]),
           note="Failure is the positive class. A learned model should beat these simple baselines on the chronological test split; AUC 0.5 = no skill.")
json.dump(rep, open(os.path.join(OUT, "baseline_report.json"), "w"), indent=2)

man = {f: dict(sha256=hashlib.sha256(open(os.path.join(OUT, f), "rb").read()).hexdigest(), bytes=os.path.getsize(os.path.join(OUT, f))) for f in sorted(os.listdir(OUT)) if f.endswith((".csv", ".jsonl", ".json")) and f != "manifest.json"}
json.dump(dict(source="verified/launch_history_all.json", launches=n, failures=sum(r["outcome"] == "failure" for r in rows), partial=sum(r["outcome"] == "partial_failure" for r in rows),
               files=man), open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
print(json.dumps(dict(launches=n, failures=sum(r["outcome"] == "failure" for r in rows), partial=sum(r["outcome"] == "partial_failure" for r in rows), causes=dict(cc), baseline=rep)))
