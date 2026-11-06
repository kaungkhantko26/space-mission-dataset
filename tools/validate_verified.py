#!/usr/bin/env python3
"""Validates verified/ (strict mode): only verified/derived data, provenance present, values re-read from the RAW retrieved files, no personal data."""
import json, os, re, csv, hashlib, html, sys, glob, collections
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,".."); V=os.path.join(ROOT,"verified"); RET=os.path.join(ROOT,"data_raw","retrieved")
L=lambda p: json.load(open(os.path.join(V,p)))
C=L("combined/verified_space_mission_data.json"); checks=[]
def chk(n,ok,d=""): checks.append(dict(check=n,passed=bool(ok),detail=str(d)[:300]))
cols={f[:-5]:L(f) for f in os.listdir(V) if f.endswith(".json") and f not in ("quality_report.json","validation_report.json")}
chk("json_syntax_all_files",True,f"{len(glob.glob(V+'/**/*.json',recursive=True))} files")
# 1 only verified/derived anywhere
bad=[]
def scan(o,path=""):
    if isinstance(o,dict):
        for k,v in o.items():
            if k in ("data_class","inputs_data_class") and v not in ("verified","derived"): bad.append((path,k,v))
            scan(v,path+"/"+k)
    elif isinstance(o,list):
        for i,v in enumerate(o[:5000]): scan(v,path+f"[{i}]")
scan({k:v for k,v in C.items() if k!="metadata"})
chk("no_unverified_estimated_or_fictional_class_anywhere",not bad,bad[:5])
txt=json.dumps({k:v for k,v in C.items() if k not in ("metadata","verification")})
chk("no_fictional_credit_or_estimated_markers",not re.search(r'"(fictional|estimated)"|credits|science_points',txt))
# 2 unique ids
for n,c in cols.items():
    if n=="sources": continue
    ids=[r["id"] for r in c["records"]]; chk(f"unique_ids:{n}",len(ids)==len(set(ids)),len(ids))
# 3 provenance
for n in ("planets","moons","asteroids","rocket_engines","electric_propulsion","launch_vehicles","rocket_stages","boosters","missions"):
    bad=[r["id"] for r in cols[n]["records"] if not r.get("field_verification") or any(not (f.get("retrieved") and f.get("source_sha256") and f.get("source_url")) for f in r["field_verification"].values())]
    chk(f"provenance_complete:{n}",not bad,bad)
for n in ("nhats_targets","neo_catalog","moon_mean_elements","nasa_facilities"):
    p=cols[n].get("provenance"); chk(f"collection_provenance:{n}",bool(p and p["source_sha256"] and p["retrieved"] and p["source_url"]))
    chk(f"source_file_hash_matches:{n}",p and hashlib.sha256(open(os.path.join(ROOT,p["source_file"]),"rb").read()).hexdigest()==p["source_sha256"])
# 4 values re-read from raw files
raw=json.load(open(os.path.join(RET,"nhats_all.json")))["data"]; nh=cols["nhats_targets"]["records"]
chk("nhats_count_equals_raw",len(nh)==len(raw),f"{len(nh)} vs {len(raw)}")
ok=all(abs(n["min_delta_v_km_s"]-float(r["min_dv"]["dv"]))<1e-12 and n["designation"]==r["des"] for n,r in zip(nh,raw)); chk("nhats_every_record_equals_raw_source",ok)
sq=json.load(open(os.path.join(RET,"sbdb_neo_with_diameter.json"))); neo=cols["neo_catalog"]["records"]; fl=sq["fields"]
chk("neo_every_record_equals_raw_source",len(neo)==len(sq["data"]) and all(n["spkid"]==r[fl.index("spkid")] and (n["diameter_km"]==(float(r[fl.index("diameter")]) if r[fl.index("diameter")] is not None else None)) for n,r in zip(neo,sq["data"])))
chk("neo_diameters_all_present",all(n["diameter_km"] is not None and n["diameter_km"]>0 for n in neo))
off=list(csv.DictReader(open(os.path.join(RET,"nasa_facilities_official.csv"),newline="",encoding="utf-8-sig"))); fac=cols["nasa_facilities"]["records"]
chk("facilities_equal_official_rows",len(fac)==len(off) and all(f["center"]==o["Center"].strip() and f["facility"]==" ".join(o["Facility"].split()) for f,o in zip(fac,off)))
chk("facilities_contain_no_personal_contact_data",not any(k in f for f in fac for k in ("contact","phone","Contact","Phone")) and not re.search(r"\b\d{3}[-.]\d{3}[-.]\d{4}\b|@",json.dumps(fac)))
chk("facility_coords_plausible",all(f["lat"] is not None and 17<f["lat"]<72 and -180<f["lon"]<-60 for f in fac))
# 5 celestial values equal to the retrieved-source values recorded in verification_celestial
VC=C["verification"]["celestial"]["checks"]; rec={r["id"]:r for k in ("planets","moons","asteroids") for r in cols[k]["records"]}; bad=[]
for c in VC:
    if c["field"].startswith("derived.") or c["field"].startswith("orbital_elements.") or c["status"]=="not_recorded" or not c.get("primary",True): continue
    r=rec.get(c["record_id"]); v=r.get(c["field"]) if r else None
    if v is None: continue
    tol=c["tolerance_rel"] or 1e-9
    if abs(v-c["source_value"])/abs(c["source_value"])>tol*1.000001: bad.append((c["record_id"],c["field"],v,c["source_value"]))
chk("celestial_values_agree_with_retrieved_source_values",not bad,bad[:4])
chk("celestial_core_fields_present",all("gravitational_parameter_km3_s2" in r and "mean_radius_m" in r for r in rec.values()),len(rec))
# 6 JPL moon elements vs raw html (recount rows)
t=open(os.path.join(RET,"jpl_sat_elem.html"),encoding="utf-8",errors="replace").read(); tb=re.findall(r"<table.*?</table>",t,flags=re.S|re.I)[0]
n_raw=sum(1 for tr in re.findall(r"<tr.*?</tr>",tb,flags=re.S|re.I)[1:] if len(re.findall(r"<t[dh]",tr))>=14)
chk("moon_element_rows_equal_raw_table",len(cols["moon_mean_elements"]["records"])==n_raw,f"{len(cols['moon_mean_elements']['records'])} vs {n_raw}")
# 7 physical plausibility
chk("vehicle_twr_in_1_to_2.5",all(1<v["derived"]["liftoff_thrust_to_weight"]<2.5 for v in cols["launch_vehicles"]["records"] if "derived" in v))
chk("engine_isp_in_range",all(50<e.get("isp_vac_s",100)<10000 for e in cols["rocket_engines"]["records"]+cols["electric_propulsion"]["records"]))
chk("payload_capacities_have_positive_mass",all(p["payload_kg"]>0 for p in cols["payload_capabilities"]["records"]))
chk("nhats_dv_positive_and_sizes_ordered",all(n["min_delta_v_km_s"] is None or n["min_delta_v_km_s"]>0 for n in nh) and all(n["size_min_m"] is None or n["size_max_m"] is None or n["size_min_m"]<=n["size_max_m"] for n in nh))
chk("sources_all_retrieved_with_hashes",all(s.get("retrieved") is True and s.get("retrieved_pages") for s in C["metadata"]["sources"]))
chk("staging_optimizer_and_fictional_data_excluded",C["optimization"]["experiments"]==[] and C["instruments"]==[] and C["spacecraft"]["components"]==[])
rep=dict(passed=sum(c["passed"] for c in checks),total=len(checks),run_date=__import__("datetime").date.today().isoformat(),checks=checks,
  not_performed=["Independent re-derivation of every analysis","Content review of third-party licenses beyond LICENSE-DATA.md"])
json.dump(rep,open(os.path.join(V,"validation_report.json"),"w"),indent=1)
for c in checks: print("PASS" if c["passed"] else "FAIL",c["check"],"" if c["passed"] else c["detail"])
print(rep["passed"],"/",rep["total"]); sys.exit(0 if rep["passed"]==rep["total"] else 1)
