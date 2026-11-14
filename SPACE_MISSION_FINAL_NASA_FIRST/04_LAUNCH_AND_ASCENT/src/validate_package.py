#!/usr/bin/env python3
"""Structural and cross-reference validation for Workstream 1 package."""
from pathlib import Path
import csv, json, sys
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
errors=[]
all_csv={}
for path in sorted(DATA.glob("*.csv")):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader=csv.DictReader(f)
        headers=reader.fieldnames or []
        if len(headers)!=len(set(headers)):
            errors.append(f"{path.name}: duplicate column names")
        rows=list(reader)
        if not rows and path.name not in {"launch_ascent_profile_template.csv"}:
            errors.append(f"{path.name}: no data rows")
        for i,row in enumerate(rows,start=2):
            if None in row:
                errors.append(f"{path.name}:{i}: extra CSV values")
        all_csv[path.name]=rows
with (DATA/"launch_simulation_constants.json").open(encoding="utf-8") as f:
    json.load(f)
sources={r["source_id"] for r in all_csv["nasa_source_registry.csv"]}
for name, rows in all_csv.items():
    for i,row in enumerate(rows,start=2):
        for key in ("source_id","source_ids"):
            value=row.get(key,"") or ""
            if value:
                ids=[x.strip() for x in value.split(";") if x.strip()]
                for sid in ids:
                    if sid not in sources:
                        errors.append(f"{name}:{i}: unknown source ID {sid}")
# Key checks
atm=all_csv["earth_standard_atmosphere_1976_0_80km_1km.csv"]
if len(atm)!=81: errors.append("Atmosphere table must contain 81 rows")
if [int(round(float(r["geometric_altitude_m"]) / 1000.0)) for r in atm] != list(range(81)):
    errors.append("Atmosphere altitude samples must be 0..80 km at 1 km steps")
if len({r["vehicle_id"] for r in all_csv["rocket_vehicle_catalog.csv"]}) != len(all_csv["rocket_vehicle_catalog.csv"]):
    errors.append("Vehicle catalog contains duplicate vehicle_id")
if len({r["event_id"] for r in all_csv["launch_event_reference.csv"]}) != len(all_csv["launch_event_reference.csv"]):
    errors.append("Launch event table contains duplicate event_id")
for name in ("sls_ascent_reference_profile_approx.csv","sls_ascent_reference_profile_artemis_ii_prelaunch.csv"):
    prof=all_csv[name]
    times=[float(r["time_from_liftoff_s"]) for r in prof]
    if times != sorted(times): errors.append(f"{name}: times are not sorted")
if errors:
    print("\n".join(errors)); sys.exit(1)
print(f"CSV structure, source IDs, atmosphere samples, keys and JSON syntax passed ({len(all_csv)} CSV files).")
