#!/usr/bin/env python3
"""Build the mission-design training set (training/design/) from VERIFIED component specs + tools/design_rules.py.

Outputs
  components_catalog.csv   verified specs of every component the generator may use (+ source ids)
  designs.csv              N generated designs with computed metrics, outcome, reasons, p_mission_success
  design_chat.jsonl        chat-format review of each design (verdict + calculations + reasons + fix)
  compatibility_pairs.csv  what to attach to what / what not (pairwise rules)
  rules.json               every rule, threshold and whether it is physics on verified data or a game heuristic
  image_prompts.csv        one AI-image prompt per component/destination (for image generators)
Labels are rule-engine output (data_class "derived"), NOT observed real-world mission results.
"""
import csv, hashlib, json, math, os, random, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_rules as DR

ROOT = DR.ROOT
OUT = os.path.join(ROOT, "training", "design")
os.makedirs(OUT, exist_ok=True)
N_DESIGNS = 6000
SEED = 20260108


def load(c):
    return json.load(open(os.path.join(ROOT, "verified", c + ".json")))["records"]


def nm(org, prod):
    org, prod = (org or "").strip(), (prod or "").strip()
    org = re.sub(r"^(.+?)(\s+\1)+$", r"\1", org)
    while org and prod.startswith(org):
        prod = prod[len(org):].strip()
    return f"{org} {prod}".strip()


def pick(num, pattern):
    for k, v in num.items():
        if re.match(pattern, k):
            return k, v
    return None, None


def to_n(num):
    k, v = pick(num, r"Thrust")
    if v is None: return None
    kk = k.replace(" ", "")
    return v / 1000.0 if "[mN]" in kk else v if "[N]" in kk else None


# ---------------- catalog ----------------
cat = {}


def add(**kw):
    base = dict(id=None, type=None, name=None, vendor=None, mass_kg=None, thrust_n=None, isp_s=None, power_w=None,
                rate_kbps=None, freq_mhz=None, gain_dbi=None, leo_capacity_kg=None, gto_capacity_kg=None,
                launch_cost_usd=None, success_rate=None, total_launches=None, subtype=None, source_collection=None, source_id=None)
    base.update(kw)
    cat[base["id"]] = base


for r in load("launch_vehicle_configs"):
    t, s = r.get("total_launches") or 0, r.get("successful_launches")
    if r.get("leo_capacity_kg") and r.get("launch_cost_usd") and t >= 5 and s is not None:
        add(id="L_" + r["id"], type="launcher", name=r["full_name"], vendor=r["manufacturer"], leo_capacity_kg=r["leo_capacity_kg"],
            gto_capacity_kg=r.get("gto_capacity_kg"), launch_cost_usd=r["launch_cost_usd"], success_rate=round(s / t, 4), total_launches=t,
            subtype="reusable" if r.get("reusable") else "expendable", source_collection="launch_vehicle_configs", source_id=r["id"])
        cat["L_" + r["id"]].update(length_m=r.get("length_m"), diameter_m=r.get("diameter_m"))
for r in load("smallsat_components"):
    n = r["numeric"]
    if r["domain"] == "propulsion":
        _, m = pick(n, r"Mass \[kg\]"); _, isp = pick(n, r"Specific Impulse"); th = to_n(n)
        _, pw = pick(n, r"(Thruster )?Power")
        if m and isp and th:
            sub = re.sub(r"\s+", " ", r["table_title"]).strip()
            add(id="T_" + r["id"], type="thruster", name=nm(r['organization_or_item'], r['product']), vendor=nm(r["organization_or_item"], ""),
                mass_kg=m, thrust_n=th, isp_s=isp, power_w=pw, subtype=sub, source_collection="smallsat_components", source_id=r["id"])
    elif r["domain"] == "power" and r["table_id"] == "3-2":
        _, p = pick(n, r"Peak BOL"); _, sp = pick(n, r"Specific Power")
        if p and sp:
            add(id="A_" + r["id"], type="solar_array", name=nm(r['organization_or_item'], r['product']), vendor=nm(r["organization_or_item"], ""),
                mass_kg=p / sp, power_w=p, subtype="solar array (mass = peak power / specific power)", source_collection="smallsat_components", source_id=r["id"])
    elif r["domain"] == "communications" and r["table_id"] == "9-3":
        _, rate = pick(n, r"Data Rate"); _, g = pick(n, r"Mass \[g\]"); _, fq = pick(n, r"Min Frequency")
        if rate and g:
            add(id="R_" + r["id"], type="radio", name=nm(r['organization_or_item'], r['product']), vendor=nm(r["organization_or_item"], ""),
                mass_kg=g / 1000, rate_kbps=rate, freq_mhz=fq, source_collection="smallsat_components", source_id=r["id"])
    elif r["domain"] == "communications" and r["table_id"] == "9-2":
        _, gain = pick(n, r"Gain"); _, g = pick(n, r"Mass \[g\]"); _, fq = pick(n, r"Min Frequency")
        if gain is not None and g:
            add(id="N_" + r["id"], type="antenna", name=nm(r['organization_or_item'], r['product']), vendor=nm(r["organization_or_item"], ""),
                mass_kg=g / 1000, gain_dbi=gain, freq_mhz=fq, source_collection="smallsat_components", source_id=r["id"])
for r in load("nasa_instruments"):
    if r.get("mass_kg_from_text"):
        add(id="I_" + r["id"], type="instrument", name=r["name"], vendor=r["mission_name"], mass_kg=r["mass_kg_from_text"],
            power_w=r.get("power_w_from_text"), subtype=(r.get("description") or "")[:120], source_collection="nasa_instruments", source_id=r["id"])
by = {t: [c for c in cat.values() if c["type"] == t] for t in ("launcher", "thruster", "solar_array", "radio", "antenna", "instrument")}
cols = list(next(iter(cat.values())).keys())
for c in cat.values():
    for k in c:
        if k not in cols: cols.append(k)
with open(os.path.join(OUT, "components_catalog.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(cat.values())

env = DR.environment()
rng = random.Random(SEED)


def split_of(key):
    h = int(hashlib.sha256(key.encode()).hexdigest(), 16) % 10
    return "test" if h == 0 else "val" if h == 1 else "train"


def gen():
    """Random design; with prob 0.65 'guided' (each choice repaired toward feasibility with prob 0.85) so successes are not vanishingly rare."""
    dest = rng.choice(DR.DESTS)
    guided = rng.random() < .65
    rep = lambda: guided and rng.random() < .85
    T = rng.choice(by["thruster"]); n_thr = rng.choice([1, 1, 2, 4])
    insts = rng.sample(by["instrument"], rng.choice([1, 1, 2, 3]))
    R = rng.choice([r for r in by["radio"] if r["rate_kbps"] >= DR.REQ_RATE_KBPS[dest]] if rep() else by["radio"] or by["radio"])
    pool = [a for a in by["antenna"] if DR.band(a["freq_mhz"]) in (None, DR.band(R["freq_mhz"])) or DR.band(R["freq_mhz"]) is None] if rep() else by["antenna"]
    if rep() and dest in ("MOON", "MARS"):
        pool = [a for a in pool if a["gain_dbi"] >= 20] or pool
    N = rng.choice(pool or by["antenna"])
    load = DR.HEUR["bus_base_load_w"] + DR.HEUR["radio_load_w"] + sum(i["power_w"] if i["power_w"] is not None else DR.HEUR["unknown_instrument_w"] for i in insts) \
        + n_thr * (T["power_w"] if T["power_w"] is not None else DR.HEUR["unknown_chem_thruster_w"])
    n_arr = rng.choice([1, 1, 2, 4])
    A = rng.choice(by["solar_array"])
    if rep():
        eff = DR.HEUR["array_efficiency"] * env["irradiance"][dest] / env["irradiance"]["LEO"]
        ok = [a for a in by["solar_array"] if a["power_w"] * n_arr * eff >= DR.HEUR["power_margin"] * load * 1.05]
        A = rng.choice(ok) if ok else max(by["solar_array"], key=lambda a: a["power_w"])
    comp = sum(i["mass_kg"] for i in insts) + n_thr * T["mass_kg"] + n_arr * A["mass_kg"] + R["mass_kg"] + N["mass_kg"]
    dry = comp * (1 + DR.HEUR["structure_overhead"])
    if rng.random() < .7:  # size the propellant near what the destination needs
        need = env["req_dv"][dest] * rng.uniform(1.12, 1.6 if guided else 2.0) if guided else env["req_dv"][dest] * rng.uniform(.6, 1.6)
        prop = round(dry * (math.exp(need / (T["isp_s"] * DR.G0)) - 1), 1)
    else:
        prop = round(dry * rng.uniform(.05, 3), 1)
    total = dry + prop
    key = "gto_capacity_kg" if dest == "GTO" else "leo_capacity_kg"
    L = rng.choice(by["launcher"])
    if rep():
        ok = [l for l in by["launcher"] if l[key] and l[key] * DR.HEUR["mass_margin"] >= total]
        L = rng.choice(ok) if ok else L
    budget = round(math.exp(rng.uniform(math.log(5e6), math.log(2e8))), -5)
    if rep(): budget = round(L["launch_cost_usd"] * rng.uniform(1.0, 1.6), -5)
    d = dict(dest=dest, budget_usd=budget, launcher=L["id"], thruster=T["id"], n_thr=n_thr, array=A["id"], n_arr=n_arr, radio=R["id"],
             antenna=N["id"], instruments=[i["id"] for i in insts], propellant_kg=prop)
    if rng.random() < .06:  # incomplete design (what NOT to do)
        d[rng.choice(["launcher", "thruster", "array", "radio", "antenna", "instruments"])] = None
    return d


PRIORITY = ["MISSING_LAUNCHER", "MISSING_PROPULSION", "MISSING_POWER", "MISSING_RADIO", "MISSING_ANTENNA", "MISSING_INSTRUMENT",
            "LAUNCHER_NO_CAPACITY", "MASS_OVER_CAPACITY", "BUDGET_EXCEEDED", "DELTA_V_SHORT", "THRUST_TOO_LOW", "POWER_SHORT",
            "BAND_MISMATCH", "DATA_RATE_LOW", "LINK_MARGIN_LOW"]
FIX = dict(
    BUDGET_EXCEEDED="choose a cheaper launch vehicle or raise the budget",
    MASS_OVER_CAPACITY="choose a launcher with more capacity or remove mass/propellant",
    LAUNCHER_NO_CAPACITY="choose a launcher with a published capacity for this orbit",
    DELTA_V_SHORT="add propellant (rocket equation) or use a higher-Isp thruster",
    THRUST_TOO_LOW="use more or higher-thrust thrusters, or a chemical engine for big burns",
    POWER_SHORT="add solar array area or remove power-hungry thrusters/instruments",
    BAND_MISMATCH="pair a radio and antenna in the same frequency band",
    DATA_RATE_LOW="choose a radio with a higher data rate",
    LINK_MARGIN_LOW="use a higher-gain antenna or lower data rate/distance")
FIX.update({k: "add the missing subsystem" for k in PRIORITY if k.startswith("MISSING")})

rows, chats = [], []
tries = 0
QUOTA = dict(success=int(N_DESIGNS * .45), failure=N_DESIGNS - int(N_DESIGNS * .45)); have = dict(success=0, failure=0)
while len(rows) < N_DESIGNS and tries < N_DESIGNS * 400:
    tries += 1
    d = gen()
    m, chk = DR.evaluate(d, cat, env)
    failed = [c for c in PRIORITY if any(cc == c and not p for cc, p, _ in chk)]
    ok = not failed
    cls = "success" if ok else "failure"
    if have[cls] >= QUOTA[cls]:
        continue
    have[cls] += 1
    did = "design_%05d" % len(rows)
    row = dict(id=did, split=split_of(did), destination=d["dest"], budget_usd=d["budget_usd"], launcher=d["launcher"], thruster=d["thruster"],
               n_thrusters=d["n_thr"], solar_array=d["array"], n_arrays=d["n_arr"], radio=d["radio"], antenna=d["antenna"],
               instruments="|".join(d["instruments"] or []), propellant_kg=d["propellant_kg"], outcome="success" if ok else "failure",
               primary_reason=failed[0] if failed else "ALL_CHECKS_PASS", all_reasons="|".join(failed),
               p_mission_success=round(m.get("p_launch_success") or 0, 4) if ok else 0.0, data_class="derived", label_source="rule_engine")
    for k in ("component_mass_kg", "dry_mass_kg", "total_mass_kg", "launcher_capacity_kg", "launch_cost_usd", "mass_margin_ratio",
              "dv_available_m_s", "dv_required_m_s", "burn_time_days", "transfer_days", "total_mission_days", "one_way_light_time_min", "array_power_w", "load_w", "link_margin_db", "warn_launcher_overkill"):
        v = m.get(k)
        row[k] = round(v, 3) if isinstance(v, float) else v
    rows.append(row)
    names = lambda ids: ", ".join(f"{cat[i]['name']} ({i})" for i in ids if i in cat)
    desc = (f"Mission to {d['dest']}, budget ${d['budget_usd']/1e6:.1f}M. Launcher: {names([d['launcher']]) or 'none'}. Propulsion: "
            f"{d['n_thr']}x {names([d['thruster']]) or 'none'}, propellant {d['propellant_kg']} kg. Power: {d['n_arr']}x {names([d['array']]) or 'none'}. "
            f"Radio: {names([d['radio']]) or 'none'}. Antenna: {names([d['antenna']]) or 'none'}. Instruments: {names(d['instruments'] or []) or 'none'}.")
    lines = [f"- {'OK ' if p else 'FAIL'} {c}: {t}" for c, p, t in chk]
    if "transfer_days" in m:
        lines.append(f"- INFO TRAJECTORY: Earth LEO -> {d['dest']}: burn {m['burn_time_days']:.0f} d + coast {m['transfer_days']:.1f} d (Hohmann) = {m['total_mission_days']:.0f} d; one-way light time {m['one_way_light_time_min']:.2f} min.")
    fix = "" if ok else " Fixes: " + "; ".join(sorted({FIX[c] for c in failed})) + "."
    verdict = (f"Verdict: SUCCESS. Estimated mission success probability {m['p_launch_success']*100:.1f}% (limited by the launcher's historical launch success rate; all design checks pass)."
               if ok else f"Verdict: FAILURE. Reasons: {', '.join(failed)}.")
    chats.append(dict(id=did, split=row["split"], data_class="derived", label_source="rule_engine", outcome=row["outcome"], reasons=failed,
                      messages=[{"role": "user", "content": "Review this space mission design and tell me whether it succeeds and why. " + desc},
                                {"role": "assistant", "content": "\n".join(lines) + "\n" + verdict + fix}]))
with open(os.path.join(OUT, "designs.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(os.path.join(OUT, "design_chat.jsonl"), "w") as f:
    for c in chats: f.write(json.dumps(c, ensure_ascii=False) + "\n")

# ---------------- compatibility pairs ----------------
pairs = []


def pair(kind, a, b, ok, rule, reason):
    pairs.append(dict(id="pair_%06d" % len(pairs), kind=kind, a=a["id"], a_name=a["name"], b=b["id"], b_name=b["name"], compatible=int(ok), rule=rule,
                      reason=reason, split=split_of(a["id"] + b["id"]), data_class="derived", label_source="rule_engine"))


prng = random.Random(SEED + 1)
for _ in range(1500):  # radio <-> antenna (band)
    r, a = prng.choice(by["radio"]), prng.choice(by["antenna"])
    rb, ab = DR.band(r["freq_mhz"]), DR.band(a["freq_mhz"])
    if rb and ab:
        pair("radio_antenna", r, a, rb == ab, "BAND_MISMATCH", f"radio band {rb}, antenna band {ab}: " + ("same band, attach" if rb == ab else "different bands, do not attach"))
for _ in range(1500):  # thruster <-> solar array power (single each, Earth orbit)
    t, a = prng.choice(by["thruster"]), prng.choice(by["solar_array"])
    need = (t["power_w"] if t["power_w"] is not None else DR.HEUR["unknown_chem_thruster_w"]) + DR.HEUR["bus_base_load_w"] + DR.HEUR["radio_load_w"]
    have = a["power_w"] * DR.HEUR["array_efficiency"]
    pair("thruster_array", t, a, have >= DR.HEUR["power_margin"] * need,
         "POWER_SHORT", f"array {have:.0f} W vs thruster+bus load {need:.0f} W x {DR.HEUR['power_margin']}: " + ("enough power" if have >= DR.HEUR["power_margin"] * need else "not enough power"))
for _ in range(1500):  # launcher <-> payload mass (LEO)
    l, t = prng.choice(by["launcher"]), prng.choice(by["instrument"])
    mass = prng.choice([50, 200, 500, 1000, 3000, 10000, 20000])
    ok = mass <= DR.HEUR["mass_margin"] * l["leo_capacity_kg"]
    pair("launcher_payload_mass_%dkg" % mass, l, t, ok, "MASS_OVER_CAPACITY",
         f"{mass} kg vs 90% of {l['leo_capacity_kg']:.0f} kg LEO capacity: " + ("fits" if ok else "too heavy"))
with open(os.path.join(OUT, "compatibility_pairs.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(pairs[0].keys())); w.writeheader(); w.writerows(pairs)

# ---------------- rules.json ----------------
json.dump(dict(
    note="Labels are rule-engine output. 'physics' rules use verified inputs; every constant in heuristics is a teaching assumption, not real data.",
    heuristics=DR.HEUR, required_data_rate_kbps=DR.REQ_RATE_KBPS, derived_environment=env,
    rules={"MASS_OVER_CAPACITY": "total <= 0.9 x launcher capacity (LEO capacity; GTO capacity for GTO) [physics inputs verified, margin heuristic]",
           "BUDGET_EXCEEDED": "launcher launch_cost_usd <= budget (cost verified from Launch Library; component prices unknown so excluded)",
           "DELTA_V_SHORT": "Isp*g0*ln(m0/mf) >= 1.1 x required dv (rocket equation; required dv from Hohmann/escape on verified GM, radii, semi-major axes)",
           "THRUST_TOO_LOW": "propellant needed for the required dv burned at total thrust must take <= 1 year",
           "POWER_SHORT": "array BOL power x 0.8 x (destination irradiance / Earth irradiance) >= 1.15 x load (irradiance from NASA NSSDC fact sheets)",
           "BAND_MISMATCH": "radio and antenna frequency bands must match when both known",
           "DATA_RATE_LOW": "radio max data rate >= destination requirement (game parameter)",
           "LINK_MARGIN_LOW": "Friis link margin >= 3 dB (5 W Tx, 35 dBi ground antenna, Eb/N0 10 dB are heuristics; frequency, gain, distance verified)",
           "MISSING_*": "launcher, propulsion, solar array, radio, antenna and at least one instrument are required"},
    not_modelled="batteries/eclipse, thermal, attitude control, component prices, launch fairing size, mission duration, radiation, launch window"),
    open(os.path.join(OUT, "rules.json"), "w"), indent=2)

# ---------------- image prompts ----------------
NEG = "text, letters, logos, brand names, watermark, people, cartoon, blurry, low quality, deformed"
STYLE = "photorealistic technical product render, studio lighting, plain light-grey background, centered, high detail"


def size_hint(kg):
    return "very small (CubeSat scale)" if kg < 1 else "small" if kg < 20 else "medium" if kg < 200 else "large"


ip = []


def prompt(id_, cat_, name, ref, specs, text, ar="4:3"):
    ip.append(dict(id=id_, category=cat_, display_name=name, reference_item=ref, key_specs=specs, prompt=text + ", " + STYLE,
                   negative_prompt=NEG, aspect_ratio=ar, note="AI illustration of the component TYPE; not an accurate depiction of the named product."))


for c in cat.values():
    t = c["type"]
    if t == "launcher":
        h = f", about {c['length_m']:.0f} m tall" if c.get("length_m") else ""
        prompt(c["id"], t, c["name"], c["name"], f"LEO capacity {c['leo_capacity_kg']:.0f} kg; cost ${c['launch_cost_usd']/1e6:.0f}M; {c['subtype']}; {c['total_launches']} launches",
               f"An orbital launch rocket{h}, slender multi-stage vehicle standing on a launch pad at dawn, {c['subtype']} booster", "3:4")
    elif t == "thruster":
        kind = c["subtype"].lower()
        shape = ("Hall-effect electric thruster with ring-shaped annular channel" if "hall" in kind else "gridded ion thruster with perforated grid face" if "gridded" in kind
                 else "chemical hydrazine thruster with nozzle and valve" if "hydrazine" in kind or "monoprop" in kind or "biprop" in kind else "cold-gas thruster with small nozzle and valve"
                 if "cold" in kind else "small spacecraft electric thruster module" if "electric" in kind or "electro" in kind or "plasma" in kind else "small spacecraft propulsion unit with nozzle")
        prompt(c["id"], t, c["name"], c["name"], f"thrust {c['thrust_n']:.3g} N; Isp {c['isp_s']:.0f} s; mass {c['mass_kg']:.3g} kg",
               f"A {size_hint(c['mass_kg'])} {shape}, spacecraft hardware, metallic and ceramic parts")
    elif t == "solar_array":
        prompt(c["id"], t, c["name"], c["name"], f"peak {c['power_w']:.0f} W; mass {c['mass_kg']:.1f} kg",
               f"A deployable spacecraft solar array wing, {size_hint(c['mass_kg'])}, blue photovoltaic cells in rectangular panels on a lightweight frame", "16:9")
    elif t == "radio":
        prompt(c["id"], t, c["name"], c["name"], f"max {c['rate_kbps']:.0f} kbps; mass {c['mass_kg']*1000:.0f} g; band {DR.band(c['freq_mhz']) or 'n/a'}",
               "A compact spacecraft communications radio transceiver, machined aluminum box with connectors, no markings")
    elif t == "antenna":
        prompt(c["id"], t, c["name"], c["name"], f"gain {c['gain_dbi']:.1f} dBi; mass {c['mass_kg']*1000:.0f} g; band {DR.band(c['freq_mhz']) or 'n/a'}",
               "A spacecraft antenna, " + ("high-gain parabolic dish antenna" if c["gain_dbi"] >= 15 else "low-gain patch or helical antenna") + ", mounted on a short mast")
    elif t == "instrument":
        prompt(c["id"], t, c["name"], c["vendor"] + " / " + c["name"], f"mass {c['mass_kg']:.1f} kg" + (f"; power {c['power_w']:.0f} W" if c["power_w"] else ""),
               f"A scientific space instrument ({c['name']}), compact sensor package with aperture, bolted to a spacecraft panel")
for b in load("planets") + load("moons"):
    if b["id"] != "sun" and b.get("mean_radius_m"):
        prompt("D_" + b["id"], "destination", b["name"], b["name"], f"radius {b['mean_radius_m']/1e3:.0f} km",
               f"{b['name']} seen from orbit, accurate surface colors and features, space background with stars", "1:1")
with open(os.path.join(ROOT, "training", "image_prompts.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(ip[0].keys())); w.writeheader(); w.writerows(ip)

ok_n = sum(r["outcome"] == "success" for r in rows)
rc = {}
for r in rows:
    for x in r["all_reasons"].split("|"):
        if x: rc[x] = rc.get(x, 0) + 1
print(json.dumps(dict(catalog={t: len(v) for t, v in by.items()}, designs=len(rows), success=ok_n, reasons=rc, pairs=len(pairs),
                      pair_ok=sum(p["compatible"] for p in pairs), image_prompts=len(ip))))
