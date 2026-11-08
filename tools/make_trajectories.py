#!/usr/bin/env python3
"""Earth -> Moon / planet transfer data (derived from VERIFIED GM, radii, semi-major axes) -> training/trajectories/.

Model: coplanar circular-orbit Hohmann transfers, patched conics, 200 km circular LEO departure, capture into a circular
parking orbit (planet 300 km altitude, Moon 100 km).  Idealised: no plane change, eccentricities, gravity assists or launch window dates
(the verified data has mean elements but no mean longitudes, so calendar windows are NOT computed; recurrence is the synodic period).
"""
import csv, hashlib, json, math, os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "training", "trajectories"); os.makedirs(OUT, exist_ok=True)
C = 299792458.0; DAY = 86400.0
load = lambda c: {r["id"]: r for r in json.load(open(f"{ROOT}/verified/{c}.json"))["records"]}
pl, mo = load("planets"), load("moons")
mu = lambda b: b["gravitational_parameter_km3_s2"] * 1e9
muS, muE, RE = mu(pl["sun"]), mu(pl["earth"]), pl["earth"]["mean_radius_m"]
a1 = pl["earth"]["semi_major_axis_m"]; r_leo = RE + 200e3; v_leo = math.sqrt(muE / r_leo)
split_of = lambda k: "test" if int(hashlib.sha256(k.encode()).hexdigest(), 16) % 10 == 0 else "val" if int(hashlib.sha256(k.encode()).hexdigest(), 16) % 10 == 1 else "train"
rows, paths = [], {}


def ellipse(rp, ra, n=91, flip=False):
    a = (rp + ra) / 2; e = (ra - rp) / (ra + rp); pts = []
    for i in range(n):
        nu = math.pi * i / (n - 1); r = a * (1 - e * e) / (1 + e * math.cos(nu))
        ang = nu if not flip else nu
        pts.append([round(r * math.cos(ang), 1), round(r * math.sin(ang), 1)])
    return pts


for pid in ("mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune"):
    p = pl[pid]; a2 = p["semi_major_axis_m"]; at = (a1 + a2) / 2
    tof = math.pi * math.sqrt(at ** 3 / muS)
    vinf_d = math.sqrt(muS / a1) * (math.sqrt(2 * a2 / (a1 + a2)) - 1)
    vinf_a = math.sqrt(muS / a2) * (1 - math.sqrt(2 * a1 / (a1 + a2)))
    dv_dep = math.sqrt(vinf_d ** 2 + 2 * muE / r_leo) - v_leo     # sign: negative vinf_d (inward) uses |.|
    rp = p["mean_radius_m"] + 300e3; vc = math.sqrt(mu(p) / rp)
    dv_cap = math.sqrt(vinf_a ** 2 + 2 * mu(p) / rp) - vc
    T2 = 2 * math.pi * math.sqrt(a2 ** 3 / muS); T1 = 2 * math.pi * math.sqrt(a1 ** 3 / muS)
    syn = abs(1 / (1 / T1 - 1 / T2))
    phase = 180 - 360 * tof / T2   # angle the target must lead Earth at departure (negative = trail)
    rows.append(dict(id=f"earth_to_{pid}", origin="Earth (200 km LEO)", destination=p["name"], kind="heliocentric_hohmann", distance_m=a2,
                     transfer_time_days=tof / DAY, transfer_time_years=tof / DAY / 365.25, departure_dv_from_leo_m_s=dv_dep, vinf_departure_m_s=abs(vinf_d),
                     c3_km2_s2=(vinf_d / 1e3) ** 2, vinf_arrival_m_s=abs(vinf_a), capture_dv_m_s=dv_cap, capture_orbit=f"circular {300} km altitude",
                     total_dv_m_s=dv_dep + dv_cap, synodic_period_days=syn / DAY, phase_angle_deg=phase,
                     one_way_light_time_min_min=abs(a2 - a1) / C / 60, one_way_light_time_max_min=(a2 + a1) / C / 60, flyby_only_dv_m_s=dv_dep))
    pts = ellipse(min(a1, a2), max(a1, a2))
    if a2 < a1:  # inward: start at aphelion (Earth) -> rotate so departure is at angle 0
        pts = [[-x, -y] for x, y in reversed(pts)]
    paths[f"earth_to_{pid}"] = dict(frame="heliocentric ecliptic x,y in metres; Earth at departure on +x axis", points=pts,
                                    target_orbit_radius_m=a2, earth_orbit_radius_m=a1, arrival_angle_deg=180.0 if a2 > a1 else 180.0)
m = mo["moon"]; r2 = m["semi_major_axis_m"]; at = (r_leo + r2) / 2
tof = math.pi * math.sqrt(at ** 3 / muE)
dv1 = v_leo * (math.sqrt(2 * r2 / (r_leo + r2)) - 1)
va = math.sqrt(muE * (2 / r2 - 1 / at)); vm = math.sqrt(muE / r2); vinf = vm - va
rp = m["mean_radius_m"] + 100e3; dv_loi = math.sqrt(vinf ** 2 + 2 * mu(m) / rp) - math.sqrt(mu(m) / rp)
rows.append(dict(id="earth_to_moon", origin="Earth (200 km LEO)", destination="Moon", kind="geocentric_hohmann_patched_conic", distance_m=r2,
                 transfer_time_days=tof / DAY, transfer_time_years=tof / DAY / 365.25, departure_dv_from_leo_m_s=dv1, vinf_departure_m_s=None,
                 c3_km2_s2=None, vinf_arrival_m_s=vinf, capture_dv_m_s=dv_loi, capture_orbit="circular 100 km altitude", total_dv_m_s=dv1 + dv_loi,
                 synodic_period_days=None, phase_angle_deg=None, one_way_light_time_min_min=(r2 - RE) / C / 60, one_way_light_time_max_min=(r2 + RE) / C / 60,
                 flyby_only_dv_m_s=dv1))
paths["earth_to_moon"] = dict(frame="geocentric x,y in metres; departure from LEO on +x axis", points=ellipse(r_leo, r2), target_orbit_radius_m=r2, earth_orbit_radius_m=r_leo, arrival_angle_deg=180.0)
geo = 42164e3; atg = (r_leo + geo) / 2
rows.append(dict(id="leo_to_geo", origin="Earth (200 km LEO)", destination="GEO", kind="geocentric_hohmann", distance_m=geo,
                 transfer_time_days=math.pi * math.sqrt(atg ** 3 / muE) / DAY, transfer_time_years=None, departure_dv_from_leo_m_s=v_leo * (math.sqrt(2 * geo / (r_leo + geo)) - 1),
                 c3_km2_s2=None, vinf_departure_m_s=None, vinf_arrival_m_s=None, capture_dv_m_s=math.sqrt(muE / geo) * (1 - math.sqrt(2 * r_leo / (r_leo + geo))),
                 capture_orbit="circular GEO", total_dv_m_s=None, synodic_period_days=None, phase_angle_deg=None, one_way_light_time_min_min=None, one_way_light_time_max_min=None, flyby_only_dv_m_s=None))
rows[-1]["total_dv_m_s"] = rows[-1]["departure_dv_from_leo_m_s"] + rows[-1]["capture_dv_m_s"]
paths["leo_to_geo"] = dict(frame="geocentric x,y in metres", points=ellipse(r_leo, geo), target_orbit_radius_m=geo, earth_orbit_radius_m=r_leo, arrival_angle_deg=180.0)
cols = list(rows[0].keys())
for r in rows:
    r["data_class"] = "derived"; r["inputs"] = "verified GM, radii, semi-major axes"
    r["split"] = split_of(r["id"])
    for k in cols:
        if isinstance(r[k], float): r[k] = round(r[k], 4)
with open(f"{OUT}/transfers.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols + ["data_class", "inputs", "split"]); w.writeheader(); w.writerows(rows)
json.dump(dict(note="Idealised coplanar Hohmann paths. points are [x,y] metres from the central body (Sun for planets, Earth for Moon/GEO); the path runs from departure at angle 0 to arrival at angle 180 degrees.", paths=paths), open(f"{OUT}/transfer_paths.json", "w"))
qa = []
for r in rows:
    d = r["destination"]
    qa.append(dict(id=f"trajqa_{r['id']}", split=r["split"], data_class="derived", messages=[
        {"role": "user", "content": f"How long does a minimum-energy (Hohmann) transfer from low Earth orbit to {d} take, and how much delta-v does it need?"},
        {"role": "assistant", "content": f"Earth to {d}: transfer time {r['transfer_time_days']:.1f} days ({r['transfer_time_days']/365.25:.2f} years). Departure burn from 200 km LEO: {r['departure_dv_from_leo_m_s']:.0f} m/s"
         + (f"; arrival/capture burn into a {r['capture_orbit']}: {r['capture_dv_m_s']:.0f} m/s; total {r['total_dv_m_s']:.0f} m/s." if r['capture_dv_m_s'] else ".")
         + (f" Launch windows repeat every {r['synodic_period_days']:.0f} days (synodic period); at departure the target must lead Earth by {r['phase_angle_deg']:.1f} deg." if r["synodic_period_days"] else "")
         + (f" One-way light time {r['one_way_light_time_min_min']:.1f} to {r['one_way_light_time_max_min']:.1f} minutes." if r["one_way_light_time_min_min"] else "")}]))
with open(f"{OUT}/trajectory_qa.jsonl", "w") as f:
    for q in qa: f.write(json.dumps(q) + "\n")
print(f"{len(rows)} transfers"); [print(r["id"], round(r["transfer_time_days"], 1), "d  dep", round(r["departure_dv_from_leo_m_s"]), "cap", round(r["capture_dv_m_s"] or 0)) for r in rows]
