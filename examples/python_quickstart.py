"""Python quickstart on the verified, game-scoped dataset (standard library only; works offline).
    python3 examples/python_quickstart.py
Shows how the game's balances map to data: orbit, launch vehicle, propulsion, power, communication, budget, risk."""
import json, os, math
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
V = os.path.join(ROOT, "verified")
load = lambda name: json.load(open(os.path.join(V, name + ".json")))["records"]
G0 = 9.80665

# ORBIT: verified constants with provenance
mars = next(p for p in load("planets") if p["id"] == "mars")
src = mars["field_verification"]["gravitational_parameter_km3_s2"]
print(f"Mars GM {mars['gravitational_parameter_km3_s2']} km3/s2 [{mars['data_class']}; {src['source_url']}]")
# POWER: published solar irradiance per planet (NASA NSSDC)
for p in load("planets"):
    irr = p.get("nssdc_fact_sheet", {}).get("numeric", {}).get("Solar irradiance (W/m 2 )")
    if irr: print(f"  {p['id']}: {irr} W/m2")
# PROPULSION: propellant needed for 4 km/s on a 500 kg spacecraft (rocket equation)
for e in load("electric_propulsion"):
    mr = math.exp(4000 / (e["isp_vac_s"] * G0)); print(f"  {e['name']}: Isp {e['isp_vac_s']} s -> {500*(mr-1):.0f} kg propellant, needs {e['power_w']} W")
# LAUNCH VEHICLE + BUDGET: active vehicles with >=15 t to LEO and a published price, cheapest per kg
cfg = [c for c in load("launch_vehicle_configs") if c["active"] and (c["leo_capacity_kg"] or 0) >= 15000 and isinstance(c["launch_cost_usd"], int)]
for c in sorted(cfg, key=lambda c: c["launch_cost_usd"] / c["leo_capacity_kg"])[:5]:
    print(f"  {c['full_name']}: ${c['launch_cost_usd']/c['leo_capacity_kg']:,.0f}/kg to LEO ({c['source_authority'].split(':')[0]})")
# RISK: launch reliability of SpaceX from the full launch record
sx = load("spacex_launch_history"); ok = sum(1 for r in sx if r["status"] == "Launch Successful"); print(f"SpaceX: {ok}/{len(sx)} launches successful ({100*ok/len(sx):.1f}%)")
# COMMUNICATION: radios with data rate and mass (NASA SoA, vendor-reported)
rad = [r for r in load("smallsat_components") if r["table_title"].startswith("Radios") and "Data Rate [kbps]" in r["numeric"] and "Mass [g]" in r["numeric"]]
print(f"{len(rad)} radios with data rate and mass, e.g.", rad[0]["organization_or_item"], rad[0]["product"], rad[0]["numeric"])
# INSTRUMENTS: those whose NASA description states a mass
for e in [e for e in load("nasa_instruments") if e["mass_kg_from_text"]][:3]:
    print(f"  {e['name']} ({e['mission_name']}): {e['mass_kg_from_text']} kg -- \"{e['mass_sentence'][:70]}...\"")
