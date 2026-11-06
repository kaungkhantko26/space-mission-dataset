#!/usr/bin/env python3
"""Validation: JSON syntax, schemas, ids, cross-refs, physical plausibility, derived-value recomputation, optimization determinism."""
import json, os, sys, math, glob
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from jsonschema import Draft202012Validator
import opt_model as O
from astro import *
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","space-mission-research")
L=lambda p: json.load(open(os.path.join(ROOT,p)))
checks=[]; 
def chk(name,ok,detail=""): checks.append(dict(check=name,passed=bool(ok),detail=detail))
# 1 syntax
files=glob.glob(ROOT+"/**/*.json",recursive=True); bad=[]
for f in files:
    try: json.load(open(f))
    except Exception as e: bad.append((f,str(e)))
chk("json_syntax_all_files",not bad,f"{len(files)} files; failures={bad}")
# 2 schemas
SM={"celestial/planets.json":"planets","celestial/moons.json":"moons","celestial/asteroids.json":"asteroids","propulsion/rocket_engines.json":"rocket_engines","propulsion/electric_propulsion.json":"electric_propulsion",
    "launch/launch_vehicles.json":"launch_vehicles","launch/rocket_stages.json":"rocket_stages","launch/boosters.json":"boosters","missions/historical_missions.json":"historical_missions","optimization/optimized_configurations.json":"experiment"}
for f in ("cameras","spectrometers","radar","sensors"): SM[f"instruments/{f}.json"]="instrument"
for f in ("batteries","solar_arrays","onboard_computers","attitude_control","thermal_control","structures"): SM[f"spacecraft/{f}.json"]="component"
for f,s in SM.items():
    sch=json.load(open(os.path.join(ROOT,"schemas",s+".schema.json"))); errs=list(Draft202012Validator(sch).iter_errors(L(f)))
    chk(f"schema:{f}",not errs,"; ".join(e.message[:80] for e in errs[:3]))
# 3 unique ids + count
comb=L("combined/all_space_mission_data.json")
def ids(coll): return [r.get("id") for r in coll]
colls={"planets":comb["celestial"]["planets"],"moons":comb["celestial"]["moons"],"asteroids":comb["celestial"]["asteroids"],"engines":comb["propulsion"]["rocket_engines"]+comb["propulsion"]["electric_propulsion"],"vehicles":comb["launch"]["launch_vehicles"],
 "stages":comb["launch"]["rocket_stages"],"components":comb["spacecraft"]["components"],"instruments":comb["instruments"],"missions":comb["missions"]["historical"],"ground":comb["spacecraft"]["ground_stations"],"experiments":comb["optimization"]["experiments"]}
for n,c in colls.items(): chk(f"unique_ids:{n}",len(ids(c))==len(set(ids(c))),f"{len(c)} records")
allbody=set(ids(colls["planets"])+ids(colls["moons"])+ids(colls["asteroids"]))
chk("unique_ids:celestial_global",len(allbody)==len(colls["planets"])+len(colls["moons"])+len(colls["asteroids"]))
# 4 cross refs
eng=set(ids(colls["engines"])); veh=set(ids(colls["vehicles"])); insid=set(ids(colls["instruments"])); src={s["id"] for s in comb["metadata"]["sources"]}
chk("xref:stage.engine_id",all(s["engine_id"] in eng for s in colls["stages"]))
chk("xref:stage.vehicle_id",all(s["vehicle_id"] in veh for s in colls["stages"]))
chk("xref:mission.launch_vehicle_id",all(m["launch_vehicle_id"] in veh or m["launch_vehicle_id"] is None for m in colls["missions"]))
chk("xref:mission.instrument_ids",all(i in insid for m in colls["missions"] for i in m["instrument_ids"]))
chk("xref:moon.parent_id",all(m["parent_id"] in allbody for m in colls["moons"]))
chk("xref:source_ids",all(s in src for c in colls.values() for r in c for s in r.get("source_ids",[])))
chk("xref:orbital_elements.body_id",all(e["body_id"] in allbody for e in comb["celestial"]["orbital_elements"]))
chk("xref:atmospheres.id",all(a["id"] in allbody for a in comb["celestial"]["atmospheres"]))
chk("xref:scenario_vehicles",all(v["ref"].split(":")[1] in veh for s in comb["optimization"]["constraints"]["scenarios"] for v in s["vehicles"]))
# 5 plausibility
bad=[]
for b in colls["planets"]+colls["moons"]+colls["asteroids"]:
    if b.get("surface_gravity_m_s2") and b.get("gravitational_parameter_km3_s2") and b["category"]!="star" and b["mean_radius_m"]>5e4:
        g2=b["derived"]["gravity_from_mu_m_s2"]; 
        if abs(g2-b["surface_gravity_m_s2"])/b["surface_gravity_m_s2"]>0.10: bad.append((b["id"],round(g2,4),b["surface_gravity_m_s2"]))
chk("physics:g_vs_mu_over_R2_within_10pct (bodies R>50 km)",not bad,f"outliers: {bad}")
bad=[b["id"] for b in colls["planets"]+colls["moons"]+colls["asteroids"] if b.get("mass_kg") and b.get("gravitational_parameter_km3_s2") and abs(b["gravitational_parameter_km3_s2"]*1e9/6.6743e-11/b["mass_kg"]-1)>0.03]
chk("physics:mass_vs_mu/G_within_3pct (Deimos 2.4% discrepancy is recorded as a known conflict)",not bad,f"mismatch: {bad}")
bad=[e["id"] for e in colls["engines"] if e.get("thrust_vac_n") and e.get("thrust_sl_n") and e["thrust_vac_n"]<e["thrust_sl_n"]]
chk("physics:thrust_vac>=thrust_sl",not bad,str(bad))
bad=[e["id"] for e in colls["engines"] if e.get("isp_vac_s") and e.get("isp_sl_s") and e["isp_vac_s"]<e["isp_sl_s"]]
chk("physics:isp_vac>=isp_sl",not bad,str(bad))
bad=[v["id"] for v in colls["vehicles"] if v["derived"].get("liftoff_thrust_to_weight") and not 1.0<v["derived"]["liftoff_thrust_to_weight"]<2.5]
chk("physics:liftoff_TWR_in_1_to_2.5",not bad,str(bad))
# 6 recompute known values
t={r["id"]:r for r in L("missions/trajectory_reference.json")["records"]}
chk("recompute:LEO400_to_GEO_dv~3.86km/s",abs(t["leo400_to_geo_hohmann"]["total_m_s"]-3857)<40,f'{t["leo400_to_geo_hohmann"]["total_m_s"]:.0f} m/s')
chk("recompute:Earth_escape~11.19km/s",abs([p for p in colls["planets"] if p["id"]=="earth"][0]["derived"]["escape_velocity_m_s"]-11186)<60)
chk("recompute:Earth_Mars_Hohmann_vinf~2.94km/s",abs(t["earth_to_mars_hohmann"]["v_infinity_departure_m_s"]-2945)<30)
chk("recompute:Earth_Mars_transfer~259d",abs(t["earth_to_mars_hohmann"]["transfer_time_days"]-259)<3)
chk("recompute:Mars_synodic~780d",abs(t["earth_to_mars_hohmann"]["synodic_period_days"]-780)<3)
c=L("analysis/communication_analysis.json"); chk("recompute:Moon_light_time~1.28s",abs(c["light_time"][0]["one_way_s"]-1.282)<0.01)
# 7 optimization determinism / consistency
cons=comb["optimization"]["constraints"]; ok=True; msgs=[]
for sc in cons["scenarios"]:
    D=O.enumerate_designs(O.GLOBAL,sc)
    for k,(nm,f,sg) in O.OBJECTIVES.items():
        b=O.solve(D,k); e=[x for x in comb["optimization"]["experiments"] if x["id"]==f"opt_{sc['id']}_{k}"][0]
        if (b is None)!=(e["selected_components"] is None) or (b and (b["design"]!=e["selected_components"] or abs(b[f]-e["objective_value"])>1e-9)): ok=False; msgs.append(e["id"])
        if b: ok&=all(b[x] is not None for x in ("wet_kg","cost")) and b["feasible"] and not b["violations"]
chk("optimization:rerun_matches_saved_and_feasible",ok,str(msgs))
chk("optimization:no_infeasible_experiments",all(e["feasibility_status"]=="feasible_optimum_found" for e in comb["optimization"]["experiments"]))
chk("combined_has_no_verified_claims",not any(r.get("data_class")=="verified" for c in colls.values() for r in c),"by design: nothing was retrieved")
rep=dict(run_date="2026-11-06",passed=sum(c["passed"] for c in checks),total=len(checks),checks=checks,
  not_performed=["Comparison against retrieved authoritative sources (network blocked)","Field-level provenance verification","Independent re-derivation of optimization with an external solver"])
json.dump(rep,open(os.path.join(ROOT,"metadata","validation_report.json"),"w"),indent=1)
import shutil; os.makedirs(os.path.join(ROOT,"..","docs","data"),exist_ok=True); shutil.copy(os.path.join(ROOT,"metadata","validation_report.json"),os.path.join(ROOT,"..","docs","data","validation_report.json"))
for c in checks: print("PASS" if c["passed"] else "FAIL",c["check"],c["detail"][:140])
print(rep["passed"],"/",rep["total"]); sys.exit(0 if rep["passed"]==rep["total"] else 1)
