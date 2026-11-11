#!/usr/bin/env python3
"""Cross-check a third-party CSV dataset (minm01210-svg/space-mission-) against the VERIFIED collections.
Usage: python3 tools/crosscheck_external.py <path-to-clone>  -> reports/external_crosscheck_minm01210.json
Only agreement statistics, conflicts and 'not added' reasons are published; the external files are NOT redistributed (the repository has no licence file)."""
import csv, glob, hashlib, json, math, os, subprocess, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
X = sys.argv[1] if len(sys.argv) > 1 else "/home/user/minm01210-svg/space-mission-"
V = lambda c: {r["id"]: r for r in json.load(open(f"{ROOT}/verified/{c}.json"))["records"]}
rd = lambda f: list(csv.DictReader(open(f"{X}/{f}")))
fl = lambda v: float(v) if v not in ("", None, " ") else None
res, conflicts = [], []


def cmp(table, key, field, ext, ver, rel=1e-3):
    if ext is None or ver is None: return
    ok = math.isclose(ext, ver, rel_tol=rel, abs_tol=1e-9)
    res.append(ok)
    if not ok: conflicts.append(dict(table=table, key=key, field=field, external=ext, verified=ver))


pl = {**V("planets"), **V("moons")}
for r in rd("celestial_bodies.csv"):
    b = pl[r["body_id"]]
    for ef, vf, sc in (("mu_km3_s2", "gravitational_parameter_km3_s2", 1), ("mean_radius_km", "mean_radius_m", 1e3), ("equatorial_radius_km", "equatorial_radius_m", 1e3), ("mass_kg", "mass_kg", 1),
                       ("surface_gravity_m_s2", "surface_gravity_m_s2", 1), ("rotation_period_h", "rotation_period_h", 1), ("orbital_period_days", "orbital_period_days", 1), ("eccentricity", "eccentricity", 1)):
        cmp("celestial_bodies", r["body_id"], ef, fl(r[ef]), (b.get(vf) / sc) if isinstance(b.get(vf), (int, float)) else None, 5e-3)
eng = {**V("rocket_engines"), **V("electric_propulsion")}
for r in rd("propulsion_specs.csv"):
    e = eng.get(r["propulsion_id"])
    if e:
        for ef, vf in (("thrust_vac_n", "thrust_vac_n"), ("thrust_sea_level_n", "thrust_sl_n"), ("isp_vac_s", "isp_vac_s"), ("isp_sea_level_s", "isp_sl_s"), ("power_w", "power_w"), ("dry_mass_kg", "dry_mass_kg")):
            cmp("propulsion_specs", r["propulsion_id"], ef, fl(r[ef]), e.get(vf))
veh = V("launch_vehicles"); cap = V("payload_capabilities")
for r in rd("launch_vehicle_specs.csv"):
    v = veh.get(r["vehicle_id"])
    if not v: continue
    for ef, vf in (("liftoff_mass_kg", "liftoff_mass_kg"), ("liftoff_thrust_n", "thrust_sl_n"), ("height_m", "height_m"), ("diameter_m", "fairing_diam_m")):
        cmp("launch_vehicle_specs", r["vehicle_id"], ef, fl(r[ef]), v.get(vf))
    for orb, ef in (("LEO", "leo_payload_kg"), ("GTO", "gto_payload_kg"), ("TLI", "tli_payload_kg")):
        c = cap.get(f"{r['vehicle_id']}_{orb.lower()}")
        cmp("launch_vehicle_specs", r["vehicle_id"], ef, fl(r[ef]), c["payload_kg"] if c else None)
# launch sites vs Launch Library pads
pads = list(V("launch_pads").values())
site_hits = []
for r in rd("launch_site_specs.csv"):
    lat, lon = fl(r["latitude_deg"]), fl(r["longitude_deg"])
    best = min(pads, key=lambda p: (p["latitude_deg"] - lat) ** 2 + (p["longitude_deg"] - lon) ** 2)
    dkm = 111.0 * math.hypot(best["latitude_deg"] - lat, (best["longitude_deg"] - lon) * math.cos(math.radians(lat)))
    site_hits.append(dict(site=r["site_id"], nearest_ll2_pad=best["name"], location=best["location"], distance_km=round(dkm, 2), within_5km=dkm <= 5))
# transfer references vs our trajectories (200 km LEO -> they use 400 km LEO, so compare totals / times)
tr = {r["id"]: r for r in csv.DictReader(open(f"{ROOT}/training/trajectories/transfers.csv"))}
tcmp = []
for r in rd("transfer_reference.csv"):
    mine = {"earth_leo400_moon100": "earth_to_moon", "earth_leo400_mars400_1sol": "earth_to_mars", "earth_leo400_earth_geo": "leo_to_geo"}.get(r["transfer_id"])
    if mine and mine in tr:
        t = tr[mine]
        tcmp.append(dict(transfer=r["transfer_id"], external_total_dv_m_s=fl(r["total_dv_m_s"]), ours_total_dv_m_s_200km_leo_circular_capture=fl(t["total_dv_m_s"]),
                         external_days=fl(r["transfer_time_days"]), ours_days=fl(t["transfer_time_days"]), note="different parking orbits (400 km vs 200 km LEO; their Mars capture is a 1-sol ellipse)"))
files = {os.path.basename(f): hashlib.sha256(open(f, "rb").read()).hexdigest() for f in sorted(glob.glob(f"{X}/*.csv")) + [f"{X}/dataset_manifest.json"]}
commit = subprocess.run(["git", "-C", X, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
rep = dict(external_repository="https://github.com/minm01210-svg/Space-mission-", commit=commit, licence="none found in the repository", compared_values=len(res), agree=sum(res), conflicts=conflicts,
           launch_sites_vs_launch_library_pads=site_hits, transfer_reference_vs_ours=tcmp, file_sha256=files,
           added_to_dataset=["launch_pads (202 pads with coordinates from Launch Library 2 records, verified; external site coordinates were cross-checked against them)"],
           not_added=[dict(item="atmospheric_properties.csv (Earth standard atmosphere, Mars exponential)", reason="no retrieved source to verify; Mars values duplicate NSSDC data already in atmospheres"),
                      dict(item="launch_site_specs azimuth ranges", reason="marked placeholders by the authors; no source"),
                      dict(item="rocket_stage_specs SLS core stage (130,000 kg dry, 1,530,000 kg propellant, Isp 421 s)", reason="marked 'approximate configuration reference'; not found in retrieved NASA SLS page"),
                      dict(item="orbit_targets / mission_burn_plan / spacecraft templates / ephemeris template / validation_cases", reason="empty templates, team design inputs, or order-of-magnitude cases; no new verifiable data"),
                      dict(item="transfer_reference.csv", reason="derived by the authors from the same GM/orbit constants; our own derived transfers (training/trajectories) already cover and agree")])
os.makedirs(f"{ROOT}/reports", exist_ok=True)
json.dump(rep, open(f"{ROOT}/reports/external_crosscheck_minm01210.json", "w"), indent=2)
print(json.dumps(dict(compared=len(res), agree=sum(res), conflicts=conflicts, sites=site_hits, transfers=tcmp), indent=1))
