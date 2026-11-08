#!/usr/bin/env python3
"""Validate training/design: catalog specs equal verified sources; every design label is reproduced by the rule engine; splits/ids clean."""
import csv, json, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_rules as DR
D = os.path.join(DR.ROOT, "training", "design")
ok = True
def check(n, c, d=""):
    global ok; print(("PASS " if c else "FAIL ") + n, d); ok &= bool(c)
def num(x): return None if x in ("", None) else float(x) if re.match(r"^-?[\d.]+(e[-+]?\d+)?$", x) else x
cat = {}
for r in csv.DictReader(open(f"{D}/components_catalog.csv")):
    cat[r["id"]] = {k: (num(v) if k not in ("id", "type", "name", "vendor", "subtype", "source_collection", "source_id") else v) for k, v in r.items()}
src = {}
for c in ("launch_vehicle_configs", "smallsat_components", "nasa_instruments"):
    src[c] = {r["id"]: r for r in json.load(open(f"{DR.ROOT}/verified/{c}.json"))["records"]}
bad = [i for i, c in cat.items() if c["source_id"] not in src[c["source_collection"]]]
check("every catalog component maps to a verified record", not bad, f"{len(cat)} components")
b2 = 0
for c in cat.values():
    s = src[c["source_collection"]][c["source_id"]]
    if c["type"] == "launcher": b2 += not (math.isclose(c["leo_capacity_kg"], s["leo_capacity_kg"]) and c["launch_cost_usd"] == s["launch_cost_usd"])
    elif c["type"] == "instrument": b2 += not math.isclose(c["mass_kg"], s["mass_kg_from_text"])
    elif c["type"] == "radio": b2 += not math.isclose(c["rate_kbps"], [v for k, v in s["numeric"].items() if k.startswith("Data Rate")][0])
    elif c["type"] == "antenna": b2 += not math.isclose(c["gain_dbi"], [v for k, v in s["numeric"].items() if k.startswith("Gain")][0])
    elif c["type"] == "solar_array": b2 += not math.isclose(c["power_w"], [v for k, v in s["numeric"].items() if "Peak BOL" in k][0])
    elif c["type"] == "thruster": b2 += not math.isclose(c["mass_kg"], s["numeric"]["Mass [kg]"])
check("catalog specs equal verified source values", b2 == 0, f"{b2} mismatches")
rates, ev = DR.cost_rates()
check("cost anchors: NASA sentence found in verified missions; rates ordered", len(ev) == 3 and all(e["nasa_sentence"] for e in ev) and rates[0] < rates[1] < rates[2], [e["usd_per_kg"] for e in ev])
check("catalog est_cost = mass x median rate (non-launchers)", all(abs(c["est_cost_usd"] - round(DR.RATE_MID * c["mass_kg"])) <= 1 for c in cat.values() if c["type"] != "launcher"))
env = DR.environment()
rows = list(csv.DictReader(open(f"{D}/designs.csv")))
mism = 0
for r in rows:
    d = dict(dest=r["destination"], budget_usd=float(r["budget_usd"]), launcher=r["launcher"] or None, thruster=r["thruster"] or None, n_thr=int(r["n_thrusters"]),
             array=r["solar_array"] or None, n_arr=int(r["n_arrays"]), radio=r["radio"] or None, antenna=r["antenna"] or None,
             instruments=[i for i in r["instruments"].split("|") if i], propellant_kg=float(r["propellant_kg"]))
    m, chk = DR.evaluate(d, cat, env)
    failed = {c for c, p, _ in chk if not p}
    mism += not (("failure" if failed else "success") == r["outcome"] and failed == {x for x in r["all_reasons"].split("|") if x})
check("rule engine reproduces every outcome and reason set", mism == 0, f"{len(rows)} designs, {mism} mismatches")
check("design ids unique", len({r["id"] for r in rows}) == len(rows))
check("both classes present", {r["outcome"] for r in rows} == {"success", "failure"})
check("failures always have a reason; successes none", all((r["outcome"] == "failure") == bool(r["all_reasons"]) for r in rows))
check("p_mission_success only on successes", all((float(r["p_mission_success"]) > 0) == (r["outcome"] == "success") for r in rows))
chat = [json.loads(l) for l in open(f"{D}/design_chat.jsonl")]
check("chat rows match designs", [c["id"] for c in chat] == [r["id"] for r in rows] and all(c["outcome"] == r["outcome"] for c, r in zip(chat, rows)))
pr = list(csv.DictReader(open(f"{D}/compatibility_pairs.csv")))
check("pair ids unique and both labels present", len({p["id"] for p in pr}) == len(pr) and {p["compatible"] for p in pr} == {"0", "1"}, len(pr))
ip = list(csv.DictReader(open(f"{DR.ROOT}/training/image_prompts.csv")))
check("image prompts: unique ids, no brand text in prompts", len({p["id"] for p in ip}) == len(ip) and all(p["negative_prompt"] for p in ip), len(ip))
blob = open(f"{D}/design_chat.jsonl").read() + open(f"{D}/components_catalog.csv").read()
check("no emails/phones", not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+|\(\d{3}\)\s?\d{3}-\d{4}", blob))
sys.exit(0 if ok else 1)
