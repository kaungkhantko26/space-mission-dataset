#!/usr/bin/env python3
"""Build ML-ready training files from the VERIFIED dataset only -> training/.

Nothing here is invented: every row is a flattened verified record, a template question whose answer is a verified
field (or a derived value computed from verified fields), or a deterministic physics calculation (rocket equation,
Hohmann transfer) from verified GM/radius/Isp.  Splits are deterministic (hash of id, or chronological for launches).
"""
import csv, hashlib, json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
V = os.path.join(ROOT, "verified")
OUT = os.path.join(ROOT, "training")
G0 = 9.80665
os.makedirs(OUT, exist_ok=True)


def load(c):
    return json.load(open(os.path.join(V, c + ".json")))["records"]


def split_of(key):
    h = int(hashlib.sha256(key.encode()).hexdigest(), 16) % 10
    return "test" if h == 0 else "val" if h == 1 else "train"


def write_csv(name, rows, cols):
    with open(os.path.join(OUT, name), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_jsonl(name, rows):
    with open(os.path.join(OUT, name), "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def num(x):
    return f"{x:.6g}"


# ---------- 1. launch outcome classification (chronological split) ----------
sx = sorted(load("spacex_launch_history"), key=lambda r: r["date_utc"])
seen, rows = {}, []
for i, r in enumerate(sx):
    v = r["vehicle_variant"] and r["vehicle"] or r["vehicle"]
    prior = seen.get(v, 0)
    seen[v] = prior + 1
    label = 1 if r["status"] == "Launch Successful" else 0 if "Failure" in r["status"] else None
    if label is None:
        continue  # partial failures / other statuses excluded from the binary label
    rows.append(dict(id=r["id"], date_utc=r["date_utc"], year=int(r["date_utc"][:4]), vehicle=r["vehicle"],
                     vehicle_family=r["vehicle_family"], mission_type=r["mission_type"], orbit=r["orbit_abbrev"],
                     pad=r["pad"], location=r["location"], prior_launches_of_vehicle=prior, success=label))
n = len(rows)
for i, r in enumerate(rows):
    r["split"] = "train" if i < int(n * .75) else "val" if i < int(n * .875) else "test"
write_csv("launch_outcome.csv", rows, list(rows[0].keys()))
launch_rows = len(rows)
launch_fail = sum(1 for r in rows if r["success"] == 0)

# ---------- 2. launcher spec regression / lookup ----------
lv = []
for r in load("launch_vehicle_configs"):
    d = {k: r.get(k) for k in ("id", "full_name", "family", "manufacturer", "manufacturer_country", "active", "reusable",
                               "length_m", "diameter_m", "launch_mass_t", "liftoff_thrust_kn", "leo_capacity_kg",
                               "gto_capacity_kg", "launch_cost_usd", "total_launches", "successful_launches",
                               "failed_launches")}
    t = r.get("total_launches") or 0
    d["success_rate"] = round(r["successful_launches"] / t, 4) if t >= 5 and r.get("successful_launches") is not None else None
    d["usd_per_kg_leo"] = round(r["launch_cost_usd"] / r["leo_capacity_kg"], 2) if r.get("launch_cost_usd") and r.get("leo_capacity_kg") else None
    d["split"] = split_of(r["id"])
    lv.append(d)
write_csv("launcher_specs.csv", lv, list(lv[0].keys()))

# ---------- 3. component numeric long table ----------
comp = []
for r in load("smallsat_components"):
    for k, v in (r.get("numeric") or {}).items():
        comp.append(dict(id=r["id"], domain=r["domain"], table_id=r["table_id"], organization=r["organization_or_item"],
                         product=r["product"], quantity=k, value=v, split=split_of(r["id"])))
write_csv("component_numeric.csv", comp, list(comp[0].keys()))

# ---------- 4. fact Q&A (chat format) ----------
FIELDS = {
    "planets": [("mean_radius_m", "mean radius", "m"), ("gravitational_parameter_km3_s2", "gravitational parameter GM", "km^3/s^2"),
                ("surface_gravity_m_s2", "surface gravity", "m/s^2"), ("mass_kg", "mass", "kg"),
                ("orbital_period_days", "orbital period", "days"), ("rotation_period_h", "rotation period", "hours")],
    "moons": [("mean_radius_m", "mean radius", "m"), ("gravitational_parameter_km3_s2", "gravitational parameter GM", "km^3/s^2"),
              ("surface_gravity_m_s2", "surface gravity", "m/s^2"), ("mass_kg", "mass", "kg"),
              ("orbital_period_days", "orbital period", "days")],
    "electric_propulsion": [("isp_vac_s", "vacuum specific impulse", "s"), ("thrust_vac_n", "thrust", "N"), ("power_w", "input power", "W")],
    "rocket_engines": [("isp_vac_s", "vacuum specific impulse", "s"), ("thrust_vac_n", "vacuum thrust", "N")],
    "launch_vehicle_configs": [("leo_capacity_kg", "LEO payload capacity (Launch Library, reference orbit unstated)", "kg"),
                               ("gto_capacity_kg", "GTO payload capacity (Launch Library, reference orbit unstated)", "kg"),
                               ("liftoff_thrust_kn", "liftoff thrust", "kN"), ("launch_cost_usd", "launch cost", "USD"),
                               ("launch_mass_t", "launch mass", "t")],
}
qa = []


def add_qa(coll, rec, field, q, a, value, unit, cls="verified"):
    qa.append(dict(id=f"qa_{coll}_{rec['id']}_{field}", split=split_of(rec["id"]), data_class=cls,
                   source_collection=coll, source_id=rec["id"], field=field, value=value, unit=unit,
                   messages=[{"role": "user", "content": q}, {"role": "assistant", "content": a}]))


for coll, specs in FIELDS.items():
    for rec in load(coll):
        nm = rec.get("full_name") or rec.get("name") or rec["id"]
        for field, label, unit in specs:
            v = rec.get(field)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                add_qa(coll, rec, field, f"What is the {label} of {nm}?", f"{nm}: {label} = {num(v)} {unit}.", v, unit)
        for dk, label, unit in (("escape_velocity_m_s", "escape velocity from the surface", "m/s"),
                                ("circular_velocity_surface_m_s", "circular orbital speed at the surface", "m/s")):
            v = (rec.get("derived") or {}).get(dk)
            if isinstance(v, (int, float)):
                add_qa(coll, rec, "derived." + dk, f"What is the {label} of {nm}?",
                       f"{nm}: {label} = {num(v)} {unit} (derived from verified GM and radius).", v, unit, "derived")
        if coll == "launch_vehicle_configs":
            t, s = rec.get("total_launches") or 0, rec.get("successful_launches")
            if t >= 5 and s is not None:
                add_qa(coll, rec, "success_rate", f"What fraction of {nm} launches succeeded?",
                       f"{nm}: {s} of {t} launches succeeded ({100*s/t:.1f}%), per Launch Library 2.", round(s / t, 4), "fraction", "derived")
for rec in load("nasa_instruments"):
    for f, unit, lab in (("mass_kg_from_text", "kg", "mass"), ("power_w_from_text", "W", "power")):
        sent = rec.get(f.replace("_from_text", "_sentence"))
        if rec.get(f) is not None and sent:
            add_qa("nasa_instruments", rec, f, f"What mass/power does NASA state for the {rec['name']} instrument on {rec['mission_name']}? ({lab})",
                   f"{lab} = {num(rec[f])} {unit}. NASA text: \"{sent}\"", rec[f], unit)
cnt = {}
for r in load("smallsat_components"):
    cnt[(r["table_id"], r["organization_or_item"], r["product"])] = cnt.get((r["table_id"], r["organization_or_item"], r["product"]), 0) + 1
for r in load("smallsat_components"):
    if cnt[(r["table_id"], r["organization_or_item"], r["product"])] != 1 or r["domain"] not in ("propulsion", "power", "communications", "gnc"):
        continue
    for k, v in (r.get("numeric") or {}).items():
        title = r["table_title"][:70]
        add_qa("smallsat_components", r, k, f"In the NASA small-spacecraft report table \"{title}\", what is {k} for {r['organization_or_item']} {r['product']}?",
               f"{k} = {num(v)} (vendor-reported in the NASA SoA report).", v, k)
write_jsonl("qa_pairs.jsonl", qa)

# ---------- 5. physics calculation examples (derived, deterministic) ----------
phys = []
bodies = [b for b in load("planets") + load("moons") if b.get("gravitational_parameter_km3_s2") and b.get("mean_radius_m") and b["id"] != "sun"]
for b in bodies:
    mu, R = b["gravitational_parameter_km3_s2"] * 1e9, b["mean_radius_m"]
    for a1, a2 in ((200e3, 400e3), (300e3, 1000e3), (400e3, 35786e3), (500e3, 5000e3), (1000e3, 20000e3)):
        r1, r2 = R + a1, R + a2
        v1, v2 = math.sqrt(mu / r1), math.sqrt(mu / r2)
        dv1 = v1 * (math.sqrt(2 * r2 / (r1 + r2)) - 1)
        dv2 = v2 * (1 - math.sqrt(2 * r1 / (r1 + r2)))
        tof = math.pi * math.sqrt((r1 + r2) ** 3 / (8 * mu))
        q = f"A spacecraft is in a circular orbit {a1/1e3:.0f} km above {b['name']}. How much delta-v does a Hohmann transfer to a circular orbit {a2/1e3:.0f} km above {b['name']} need, and how long does it take?"
        a = (f"Using GM = {num(b['gravitational_parameter_km3_s2'])} km^3/s^2 and mean radius {num(R/1e3)} km: r1 = {num(r1/1e3)} km, r2 = {num(r2/1e3)} km. "
             f"dv1 = {dv1:.1f} m/s, dv2 = {dv2:.1f} m/s, total = {dv1+dv2:.1f} m/s, transfer time = {tof/3600:.2f} h.")
        phys.append(dict(id=f"phys_hohmann_{b['id']}_{int(a1/1e3)}_{int(a2/1e3)}", split=split_of("phys_" + b["id"]), data_class="derived",
                         task="hohmann", inputs=dict(body=b["id"], alt1_km=a1 / 1e3, alt2_km=a2 / 1e3),
                         outputs=dict(dv1_m_s=dv1, dv2_m_s=dv2, total_m_s=dv1 + dv2, time_of_flight_s=tof),
                         messages=[{"role": "user", "content": q}, {"role": "assistant", "content": a}]))
engines = [e for e in load("electric_propulsion") + load("rocket_engines") if isinstance(e.get("isp_vac_s"), (int, float))]
for e in engines:
    for m0, mf in ((1000, 800), (1000, 500), (2000, 1200), (500, 400), (5000, 2500)):
        dv = e["isp_vac_s"] * G0 * math.log(m0 / mf)
        q = f"A {m0} kg spacecraft with a {e['name']} (vacuum Isp {num(e['isp_vac_s'])} s) burns down to {mf} kg. What ideal delta-v and how much propellant?"
        a = f"dv = Isp*g0*ln(m0/mf) = {num(e['isp_vac_s'])} * 9.80665 * ln({m0}/{mf}) = {dv:.1f} m/s; propellant = {m0-mf} kg."
        phys.append(dict(id=f"phys_rocket_{e['id']}_{m0}_{mf}", split=split_of("phys_" + e["id"]), data_class="derived", task="rocket_equation",
                         inputs=dict(engine=e["id"], isp_s=e["isp_vac_s"], m0_kg=m0, mf_kg=mf), outputs=dict(dv_m_s=dv, propellant_kg=m0 - mf),
                         messages=[{"role": "user", "content": q}, {"role": "assistant", "content": a}]))
write_jsonl("physics_examples.jsonl", phys)

# ---------- manifest ----------
files = {}
for fn in sorted(os.listdir(OUT)):
    if fn.endswith((".csv", ".jsonl")) and fn != "image_prompts.csv":
        p = os.path.join(OUT, fn)
        files[fn] = dict(sha256=hashlib.sha256(open(p, "rb").read()).hexdigest(), bytes=os.path.getsize(p))


def counts(rows):
    c = {}
    for r in rows:
        c[r["split"]] = c.get(r["split"], 0) + 1
    return c


manifest = dict(
    note="Built only from verified/ by tools/make_training.py. Splits: launches chronological 75/12.5/12.5; others by sha256(id) mod 10 (test=0,val=1).",
    tables=dict(launch_outcome=dict(rows=launch_rows, failures=launch_fail, splits=counts(rows)),
                launcher_specs=dict(rows=len(lv), splits=counts(lv)), component_numeric=dict(rows=len(comp), splits=counts(comp)),
                qa_pairs=dict(rows=len(qa), splits=counts(qa)), physics_examples=dict(rows=len(phys), splits=counts(phys))),
    files=files)
json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
print(json.dumps({k: v["rows"] for k, v in manifest["tables"].items()}))
