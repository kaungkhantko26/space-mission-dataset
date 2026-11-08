#!/usr/bin/env python3
"""Sanity-check training/trajectories against textbook Hohmann values and internal consistency."""
import csv, json, os, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "training", "trajectories")
ok = True
def check(n, c, d=""):
    global ok; print(("PASS " if c else "FAIL ") + n, d); ok &= bool(c)
t = {r["id"]: r for r in csv.DictReader(open(f"{R}/transfers.csv"))}
f = lambda i, k: float(t[i][k])
check("Earth->Mars Hohmann time ~259 d", 255 < f("earth_to_mars", "transfer_time_days") < 262)
check("Earth->Venus ~146 d", 143 < f("earth_to_venus", "transfer_time_days") < 149)
check("Earth->Jupiter ~997 d", 990 < f("earth_to_jupiter", "transfer_time_days") < 1005)
check("Earth->Moon ~5 d, TLI ~3.1 km/s", 4.5 < f("earth_to_moon", "transfer_time_days") < 5.5 and 3000 < f("earth_to_moon", "departure_dv_from_leo_m_s") < 3300)
check("LEO->GEO ~5.3 h, total ~3.9 km/s", abs(f("leo_to_geo", "transfer_time_days") * 24 - 5.3) < .3 and 3800 < f("leo_to_geo", "total_dv_m_s") < 3950)
check("Mars synodic period ~780 d", 770 < f("earth_to_mars", "synodic_period_days") < 790)
check("Mars departure dv ~3.6 km/s", 3500 < f("earth_to_mars", "departure_dv_from_leo_m_s") < 3750)
check("farther planets take longer", [f(f"earth_to_{p}", "transfer_time_days") for p in ("mars", "jupiter", "saturn", "uranus", "neptune")] == sorted(f(f"earth_to_{p}", "transfer_time_days") for p in ("mars", "jupiter", "saturn", "uranus", "neptune")))
P = json.load(open(f"{R}/transfer_paths.json"))["paths"]
check("every transfer has a path starting at the origin and ending opposite", all(P[k]["points"][0][1] == 0 and P[k]["points"][-1][1] == 0 and P[k]["points"][0][0] * P[k]["points"][-1][0] < 0 for k in P), len(P))
check("path start radius = origin orbit radius", all(abs(abs(P[k]["points"][0][0]) - (P[k]["earth_orbit_radius_m"])) / P[k]["earth_orbit_radius_m"] < 1e-3 for k in P))
sys.exit(0 if ok else 1)
