"""Python quickstart on the VERIFIED dataset (standard library only; works offline).
    python3 examples/python_quickstart.py
Every record here is verified or ingested directly from a retrieved source; check `field_verification` / `provenance` for where."""
import json, os, math
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
V = os.path.join(ROOT, "verified")
load = lambda name: json.load(open(os.path.join(V, name + ".json")))["records"]
G0 = 9.80665

# 1) Verified constants with provenance
mars = next(p for p in load("planets") if p["id"] == "mars")
src = mars["field_verification"]["gravitational_parameter_km3_s2"]
print(f"Mars GM = {mars['gravitational_parameter_km3_s2']} km3/s2  [{mars['data_class']}; {src['source_url']}; retrieved {src['retrieved']}]")

# 2) Propellant for a 4 km/s burn on a 500 kg spacecraft with each verified electric thruster
for e in load("electric_propulsion"):
    mr = math.exp(4000 / (e["isp_vac_s"] * G0))
    print(f"  {e['name']}: Isp {e['isp_vac_s']} s -> {500*(mr-1):.0f} kg propellant, thrust {e['thrust_vac_n']*1000:.0f} mN, needs {e['power_w']} W")

# 3) Real asteroid targets: lowest-delta-v NHATS targets at least 100 m across
nh = [r for r in load("nhats_targets") if r["min_delta_v_km_s"] and (r["size_max_m"] or 0) >= 100]
for r in sorted(nh, key=lambda r: r["min_delta_v_km_s"])[:5]:
    print(f"  {r['designation']}: min dv {r['min_delta_v_km_s']} km/s over {r['min_delta_v_trip_days']} days, size {r['size_min_m']}-{r['size_max_m']} m")

# 4) Verified launch capacities with their stated reference orbit
for p in load("payload_capabilities"):
    cond = f"{p.get('altitude_km','?')} km, {p.get('inclination_deg','?')} deg"
    print(f"  {p['vehicle_id']}: {p['payload_kg']:,.0f} kg to {p['orbit']} ({cond})")

# 5) Saturn V stage masses straight from the Apollo 11 press kit
for s in load("rocket_stages"):
    print(f"  {s['stage']}: dry {s['dry_mass_kg']:,.0f} kg, propellant {s['propellant_mass_kg']:,.0f} kg, {s['n_engines']} engine(s)")
