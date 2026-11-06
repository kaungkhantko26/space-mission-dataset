"""Python quickstart — works offline (reads the combined JSON) and needs only the standard library.
    python3 examples/python_quickstart.py
For live HTTP use the client in tools/spacemission_client.py or the local backend (python3 tools/serve_api.py)."""
import json, os, math
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
D = json.load(open(os.path.join(ROOT, "space-mission-research", "combined", "all_space_mission_data.json")))

# 1) Records come with provenance. Use only verified values where you can.
mars = next(p for p in D["celestial"]["planets"] if p["id"] == "mars")
print("Mars:", mars["data_class"], "GM =", mars["gravitational_parameter_km3_s2"], "km3/s2;",
      "fields still unverified:", mars["unverified_fields"])

# 2) Best-Isp chemical engine that has an Isp recorded
engines = [e for e in D["propulsion"]["rocket_engines"] if e["isp_vac_s"]]
best = max(engines, key=lambda e: e["isp_vac_s"])
print("Highest vacuum Isp:", best["name"], best["isp_vac_s"], "s  [", best["data_class"], "]")

# 3) Rocket equation: propellant for 4 km/s on a 500 kg (dry) spacecraft with that engine
dv, mf = 4000.0, 500.0
mr = math.exp(dv / (best["isp_vac_s"] * 9.80665))
print(f"Propellant for {dv:.0f} m/s: {mf * (mr - 1):.0f} kg (ideal, no tank mass)")

# 4) Launch vehicles that can send >= 1500 kg to GTO (capacity records state their reference orbit)
for v in D["launch"]["launch_vehicles"]:
    for p in v["payloads"]:
        if p["orbit"] == "GTO" and p["payload_kg"] >= 1500 and p["mode"].startswith("expended"):
            print(f"  {v['name']}: {p['payload_kg']:,} kg GTO ({v['status']}, {v['data_class']})")

# 5) Optimizer results are precomputed for 3 scenarios x 9 objectives
for e in D["optimization"]["experiments"]:
    if e["scenario_id"] == "lunar_orbiter" and e["objective"] == "balanced":
        r = e["result"]
        print("Balanced lunar orbiter:", round(r["wet_kg"]), "kg,", round(r["cost"]), "credits (fictional),", round(r["science"], 1), "science points")
        print("  design:", e["selected_components"])
