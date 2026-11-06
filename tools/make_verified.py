#!/usr/bin/env python3
"""STRICT MODE builder. Reads the staging build (space-mission-research/combined) and the retrieved source files (data_raw/retrieved/) and writes `verified/`,
which contains ONLY:
  * records / fields that were checked against a retrieved source (field_verification present) -- unverified fields are removed,
  * datasets ingested directly from authoritative sources (JPL NHATS, JPL SBDB query, JPL satellite mean elements, official NASA Facilities CSV),
  * analyses derived purely from verified inputs.
Everything estimated, fictional or merely recalled (optimizer catalog, costs, instruments, components, user-supplied SpaceX table, ...) is excluded."""
import json, os, re, csv, html, math, hashlib, datetime, shutil, collections
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,".."); RET=os.path.join(ROOT,"data_raw","retrieved"); OUT=os.path.join(ROOT,"verified")
S=json.load(open(os.path.join(ROOT,"space-mission-research","combined","all_space_mission_data.json")))
sha=lambda f: hashlib.sha256(open(os.path.join(RET,f),"rb").read()).hexdigest()
rdate=lambda f: datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(RET,f)),datetime.timezone.utc).strftime("%Y-%m-%d")
def prov(f,url,sid): return dict(source_id=sid,source_url=url,source_file="data_raw/retrieved/"+f,source_sha256=sha(f),retrieved=rdate(f))
shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT)
W=lambda p,o:(os.makedirs(os.path.dirname(os.path.join(OUT,p)),exist_ok=True),json.dump(o,open(os.path.join(OUT,p),"w"),indent=1,ensure_ascii=False))
def vclass(r): r["data_class"]="verified"; return r
# ---------- trim helpers ----------
def keep_verified(rec, always=("id","name","category","parent_id","stage","vehicle_id","engine_id","type"), extra=()):
    fv=rec.get("field_verification",{}); out={k:rec[k] for k in always if k in rec}
    for k in fv:
        if "[" in k: continue
        if k in rec and rec[k] is not None: out[k]=rec[k]
    for k in extra:
        if k in rec: out[k]=rec[k]
    out["field_verification"]=fv; out["verified_fields"]=sorted(fv.keys()); out["data_class"]="verified"; out["confidence"]="high"
    out["source_ids"]=sorted({i["source_id"] for i in fv.values()}); out["retrieval_status"]="retrieved"
    return out
# ---------- celestial ----------
def celestial(recs):
    out=[]
    for r in recs:
        if r.get("data_class")!="verified": continue
        t=keep_verified(r,extra=("mu_m3_s2",))
        d=r.get("derived",{}); t["derived"]={k:d[k] for k in ("escape_velocity_m_s","circular_velocity_surface_m_s","gravity_from_mu_m_s2") if k in d}
        if "semi_major_axis_m" in t and d.get("solar_irradiance_w_m2") is not None: t["derived"]["solar_irradiance_w_m2"]=d["solar_irradiance_w_m2"]
        t["derived_note"]="computed from the verified GM, radius and semi-major axis; not independently sourced"
        out.append(t)
    return out
planets=celestial(S["celestial"]["planets"]); moons=celestial(S["celestial"]["moons"]); asteroids=celestial(S["celestial"]["asteroids"])
elements=[]
for e in S["celestial"]["orbital_elements"]:
    if e.get("data_class")=="verified":
        t={k:e[k] for k in ("body_id","epoch","frame","semi_major_axis_au","eccentricity","inclination_deg","validity","time_dependence") if k in e}
        t.update(id=e["body_id"],field_verification=e["field_verification"],data_class="verified",confidence="high",source_ids=e["source_ids"],retrieval_status="retrieved"); elements.append(t)
# ---------- propulsion / launch ----------
def has_fv(r): return bool(r.get("field_verification"))
engines=[keep_verified(r) for r in S["propulsion"]["rocket_engines"] if has_fv(r)]
for e in engines: e.pop("type",None)
electric=[keep_verified(r) for r in S["propulsion"]["electric_propulsion"] if has_fv(r)]
stages=[keep_verified(r,always=("id","vehicle_id","stage","engine_id")) for r in S["launch"]["rocket_stages"] if has_fv(r)]
boosters=[keep_verified(r,always=("id","name","vehicle_id")) for r in S["launch"]["boosters"] if has_fv(r)]
vehicles=[]
for r in S["launch"]["launch_vehicles"]:
    if not has_fv(r): continue
    t=keep_verified(r,always=("id","name"))
    caps={}
    for key in r["field_verification"]:
        m=re.match(r"payloads\[(\w+)\]\.(\w+)$",key)
        if not m: continue
        orbit,fld=m.groups(); cand=[p for p in r["payloads"] if p["orbit"]==orbit]; p_=next((p for p in cand if p["mode"].startswith("expended")),cand[0] if cand else None)
        if p_: caps.setdefault(orbit,dict(orbit=orbit,mode=p_["mode"]))[fld]=p_[fld]
    t["payloads"]=[c for c in caps.values() if "payload_kg" in c]
    if "liftoff_mass_kg" in t and "thrust_sl_n" in t: t["derived"]=dict(liftoff_thrust_to_weight=t["thrust_sl_n"]/(t["liftoff_mass_kg"]*9.80665),derived_note="from two verified fields")
    vehicles.append(t)
payload_caps=[dict(id=f"{v['id']}_{p['orbit']}".lower(),vehicle_id=v["id"],**p,data_class="verified",source_ids=v["source_ids"],note="reference conditions are present only when stated by the source") for v in vehicles for p in v["payloads"]]
missions=[]
for r in S["missions"]["historical"]:
    if not has_fv(r): continue
    t=keep_verified(r,always=("id","name","agency"))
    if "launch_vehicle_note" in t: t["launch_vehicle_family"]=t.pop("launch_vehicle_note")
    missions.append(t)
# ---------- real datasets ingested directly ----------
def num(x):
    try: return float(x)
    except: return None
nh=json.load(open(os.path.join(RET,"nhats_all.json"))); P=prov("nhats_all.json","https://ssd-api.jpl.nasa.gov/nhats.api","S50")
nhats=[]
for i,r in enumerate(nh["data"]):
    nhats.append(dict(id=f"nhats_{i+1:05d}",designation=r["des"],full_name=r["fullname"].strip(),H_mag=num(r["h"]),size_min_m=num(r["min_size"]),size_max_m=num(r["max_size"]),
        min_delta_v_km_s=num(r["min_dv"]["dv"]),min_delta_v_trip_days=r["min_dv"]["dur"],min_duration_days=r["min_dur"]["dur"],min_duration_delta_v_km_s=num(r["min_dur"]["dv"]),
        n_viable_trajectories=r["n_via_traj"],observability_start=r["obs_start"],observability_end=r["obs_end"],orbit_condition_code=r["occ"],radar_snr_arecibo=r["radar_snr_a"],radar_snr_goldstone=r["radar_snr_g"],
        data_class="verified",confidence="high",source_ids=["S50"],retrieval_status="retrieved"))
nh_note="NHATS: Near-Earth Object Human Space Flight Accessible Targets Study (JPL). delta-v in km/s and durations in days are the study's round-trip design values for its stated assumptions; see the NHATS API documentation."
sq=json.load(open(os.path.join(RET,"sbdb_neo_with_diameter.json"))); P2=prov("sbdb_neo_with_diameter.json","https://ssd-api.jpl.nasa.gov/sbdb_query.api","S51")
f=sq["fields"]; neos=[]
for row in sq["data"]:
    d=dict(zip(f,row)); neos.append(dict(id=f"sbdb_{d['spkid']}",spkid=d["spkid"],full_name=d["full_name"].strip(),designation=d["pdes"],kind=d["kind"],orbit_class=d["class"],semi_major_axis_au=num(d["a"]),eccentricity=num(d["e"]),inclination_deg=num(d["i"]),
        H_mag=num(d["H"]),diameter_km=num(d["diameter"]),albedo=num(d["albedo"]),rotation_period_h=num(d["rot_per"]),GM_km3_s2=num(d["GM"]),data_class="verified",confidence="high",source_ids=["S51"],retrieval_status="retrieved"))
t=open(os.path.join(RET,"jpl_sat_elem.html"),encoding="utf-8",errors="replace").read(); tb=re.findall(r"<table.*?</table>",t,flags=re.S|re.I)[0]
rows=[[re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",c))).strip() for c in re.findall(r"<t[dh].*?</t[dh]>",tr,flags=re.S|re.I)] for tr in re.findall(r"<tr.*?</tr>",tb,flags=re.S|re.I)]
hdr=rows[0]; P3=prov("jpl_sat_elem.html","https://ssd.jpl.nasa.gov/sats/elem/","S52"); moon_el=[]
for r in rows[1:]:
    if len(r)<14: continue
    d=dict(zip(hdr,r))
    moon_el.append(dict(id=f"satel_{d['Code']}_{d['Ephemeris'].lower()}",planet=d["Planet"],satellite=d["Satellite"],jpl_code=d["Code"],ephemeris=d["Ephemeris"],frame=d["Frame"],epoch_tdb=d["Epoch (TDB)"],semi_major_axis_km=num(d["a (km)"]),eccentricity=num(d["e"]),
        arg_periapsis_deg=num(d["ω (deg)"]),mean_anomaly_deg=num(d["M (deg)"]),inclination_deg=num(d["i (deg)"]),node_deg=num(d["node (deg)"]),period_days=num(d["P (days)"]),reference=d["Ref."],
        data_class="verified",confidence="high",source_ids=["S52"],retrieval_status="retrieved"))
# official facilities (contact names/phones deliberately NOT ingested)
P4=prov("nasa_facilities_official.csv","https://data.nasa.gov/docs/legacy/NASA_Facilities/NASA_Facilities_rows.csv","S53"); P4["redaction"]="Contact and Phone columns removed before storage; sha256 of the original download: %s"%open(os.path.join(RET,"nasa_facilities_official.REDACTION.txt")).read().split("download: ")[1].split()[0]
fac=[]
for i,r in enumerate(csv.DictReader(open(os.path.join(RET,"nasa_facilities_official.csv"),newline="",encoding="utf-8-sig")),1):
    m=re.match(r"^\s*(\S*)\s*\(\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\)\s*$",r["Location"])
    fac.append(dict(id=f"nf_{i:04d}",center=r["Center"].strip(),facility=" ".join(r["Facility"].split()),status=(r["Status"].strip() or None),occupied=(r["Occupied"].strip() or None),url=(r["URL Link"].strip() or None),
        city=(r["City"].strip() or None),state=(r["State"].strip() or None),zipcode=(r["Zipcode"].strip() or None),lat=float(m.group(2)) if m else None,lon=float(m.group(3)) if m else None,
        record_date=r["Record Date"].strip() or None,last_update=r["Last Update"].strip() or None,data_class="verified",confidence="high",source_ids=["S53"],retrieval_status="retrieved"))
# cross-check the user-supplied file against the official table
u={(x["facility"],x["city"]):x for x in S["infrastructure"]["nasa_facilities"]}; agree=sum(1 for x in fac if (x["facility"],x["city"]) in u and u[(x["facility"],x["city"])]["center"]==x["center"] and abs((u[(x["facility"],x["city"])]["lat"] or 0)-(x["lat"] or 0))<1e-6)
# ---------- derived analyses from verified inputs only ----------
byid={p["id"]:p for p in planets+moons}
AU=149597870.7; C=299792.458
lt=[]
for pid in ("venus","mars","jupiter","saturn","uranus","neptune"):
    if pid in byid and "semi_major_axis_m" in byid[pid] and "earth" in byid:
        a=byid[pid]["semi_major_axis_m"]/1e3; ae=byid["earth"].get("semi_major_axis_m",AU*1e3)/1e3
        lt.append(dict(target=pid,min_distance_km=abs(a-ae),max_distance_km=a+ae,min_one_way_light_time_min=abs(a-ae)/C/60,max_one_way_light_time_min=(a+ae)/C/60,
                       derived_from="verified semi-major axes (circular coplanar approximation) and the exact speed of light",data_class="derived"))
if "moon" in byid and "semi_major_axis_m" in byid["moon"]:
    d=byid["moon"]["semi_major_axis_m"]/1e3; lt.append(dict(target="moon",min_distance_km=d,max_distance_km=d,min_one_way_light_time_min=d/C/60,max_one_way_light_time_min=d/C/60,derived_from="verified Moon semi-major axis",data_class="derived"))
traj=[dict(t) for t in S["missions"]["trajectory_reference"]]
for t in traj:
    if t["id"]=="leo400_to_moon_100km": t["basis"]="patched-conic TLI 3084 m/s + LOI 821 m/s from 400 km LEO to 100 km circular lunar orbit (verified GM and radii); no operations allowance"
    t["inputs_data_class"]="verified"; t["note"]="Idealised two-body/patched-conic values computed from verified GM, radii and semi-major axes."
best_nhats=sorted([n for n in nhats if n["min_delta_v_km_s"] is not None],key=lambda n:n["min_delta_v_km_s"])[:25]
sources=[s for s in S["metadata"]["sources"] if s.get("retrieved") is True]
sources+= [dict(id="S50",title="JPL NHATS Data API",organization="NASA JPL CNEOS",url="https://ssd-api.jpl.nasa.gov/nhats.api",retrieved=True,retrieval_date=P["retrieved"],retrieved_pages=[dict(url=P["source_url"],sha256=P["source_sha256"],retrieved=P["retrieved"])]),
 dict(id="S51",title="JPL SBDB Query API (NEOs with known diameter)",organization="NASA JPL SSD",url="https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html",retrieved=True,retrieval_date=P2["retrieved"],retrieved_pages=[dict(url=P2["source_url"],sha256=P2["source_sha256"],retrieved=P2["retrieved"])]),
 dict(id="S52",title="JPL Planetary Satellite Mean Elements",organization="NASA JPL SSD",url="https://ssd.jpl.nasa.gov/sats/elem/",retrieved=True,retrieval_date=P3["retrieved"],retrieved_pages=[dict(url=P3["source_url"],sha256=P3["source_sha256"],retrieved=P3["retrieved"])]),
 dict(id="S53",title="NASA Facilities (data.nasa.gov legacy CSV; contact columns not ingested)",organization="NASA",url="https://data.nasa.gov/dataset/nasa-facilities",retrieved=True,retrieval_date=P4["retrieved"],retrieved_pages=[dict(url=P4["source_url"],sha256=P4["source_sha256"],retrieved=P4["retrieved"])],note="License listed as 'not specified' on data.nasa.gov.")]
cols=dict(planets=planets,moons=moons,asteroids=asteroids,orbital_elements=elements,rocket_engines=engines,electric_propulsion=electric,launch_vehicles=vehicles,rocket_stages=stages,boosters=boosters,payload_capabilities=payload_caps,
          missions=missions,nasa_facilities=fac,nhats_targets=nhats,neo_catalog=neos,moon_mean_elements=moon_el,sources=sources)
counts={k:len(v) for k,v in cols.items()}
cls=collections.Counter(r.get("data_class") for k,v in cols.items() if k!="sources" for r in v)
q0=S["metadata"]["quality"]
quality=dict(mode="STRICT: verified data only",build_date=datetime.date.today().isoformat(),record_counts=counts,data_class_counts=dict(cls),verified_records=cls.get("verified",0),targets={},target_attainment_pct={},
  retrieval=dict(sources_listed=len(sources),sources_retrieved=len(sources),reason="Only retrieved sources are used; see metadata sources and field_verification on each record."),
  statement=("STRICT MODE: this dataset contains only values that were compared with, or ingested directly from, retrieved authoritative sources (JPL SSD/SBDB/NHATS, NASA NSSDC, NASA SLS page, Apollo 11 press kit, NTRS papers, ULA, ESA, data.nasa.gov). "
             "Unverified, estimated and fictional values (optimizer catalog, costs, instruments, spacecraft components, Falcon/Starship/Electron and most engine specs, user-supplied SpaceX table) were removed. "
             "Derived values are computed only from verified inputs and are labelled derived."),
  conflicts_resolved=q0.get("conflicts_resolved",[]),known_conflicts=[dict(topic="Excluded data",note="Records or fields that could not be verified are excluded, not zero-filled; coverage is therefore partial by design. See staging reports for what was removed and why."),
      dict(topic="NASA facilities cross-check",note=f"The user-supplied NASA_Facilities.csv agrees with the official data.nasa.gov table on {agree} of {len(fac)} facilities (center and coordinates); the official table is used. Official contact names and phone numbers are not ingested.")],
  missing_categories=["instruments","spacecraft components","propellants","atmospheres","ground stations","SpaceX launch history (source not retrievable)","engine and vehicle specifications beyond the verified fields","costs"],completeness_pct={},validations_run="see verified/validation_report.json")
combined=dict(schema_version="verified-1.0.0",mode="STRICT: verified data only",generated=quality["build_date"],note=quality["statement"],
  celestial=dict(planets=planets,moons=moons,asteroids=asteroids,orbital_elements=elements,atmospheres=[]),
  propulsion=dict(rocket_engines=engines,electric_propulsion=electric,propellants=[]),launch=dict(launch_vehicles=vehicles,rocket_stages=stages,boosters=boosters,payload_capabilities=payload_caps),
  spacecraft=dict(components=[],ground_stations=[],optical_demonstrations=[]),instruments=[],
  missions=dict(historical=missions,profiles=[],requirements=[],trajectory_reference=traj,engineering_constraints=[]),
  launch_history=dict(launches=[],sites=[],analysis=None),infrastructure=dict(provenance=P4,nasa_facilities=fac,analysis=dict(records=len(fac),by_center=dict(collections.Counter(x["center"] for x in fac).most_common()),by_status=dict(collections.Counter((x["status"] or "not_recorded") for x in fac).most_common()),antennas=[])),
  real_data=dict(moon_mean_elements=moon_el,moon_mean_elements_provenance=P3,nhats_targets_file="nhats_targets.json",nhats_targets_count=len(nhats),nhats_provenance=P,neo_catalog_file="neo_catalog.json",neo_catalog_count=len(neos),neo_provenance=P2,note=nh_note),
  analysis=dict(light_time=lt,nhats_lowest_delta_v=[dict(designation=n["designation"],min_delta_v_km_s=n["min_delta_v_km_s"],trip_days=n["min_delta_v_trip_days"],size_m=[n["size_min_m"],n["size_max_m"]],H_mag=n["H_mag"]) for n in best_nhats]),
  optimization=dict(constraints=dict(scenarios=[],catalog={},global_parameters={}),experiments=[],pareto=[],sensitivity=[],uncertainty=[],models=None),
  verification=dict(celestial=S["verification"]["celestial"],launch=S["verification"]["launch"],retrieved_files=S["verification"]["retrieved_files"]),
  metadata=dict(sources=sources,quality=quality))
W("combined/verified_space_mission_data.json",combined)
COLPROV={"nhats_targets":P,"neo_catalog":P2,"moon_mean_elements":P3,"nasa_facilities":P4}
for k,v in cols.items(): W(f"{k}.json",dict(collection=k,count=len(v),mode="STRICT: verified data only",**({"provenance":COLPROV[k]} if k in COLPROV else {}),records=v))
W("quality_report.json",quality)
open(os.path.join(OUT,"README.md"),"w").write(f"""# verified/ — strict-mode dataset (generated)
{quality['statement']}

| Collection | Records | What |
|---|---:|---|
""" + "\n".join(f"| `{k}.json` | {n} | {d} |" for (k,n),d in zip(counts.items(),["Sun, planets, dwarf planets (verified fields only)","moons (verified GM/radius/mass)","Bennu, Vesta","planet/dwarf-planet orbital elements","engines (verified fields only)","NEXT, NSTAR, BPT-4000","launch vehicles (verified fields only)","Saturn V stages","SLS booster","verified payload capacities with stated reference orbits","missions: verified launch date / vehicle family","official NASA facilities (data.nasa.gov)","JPL NHATS accessible near-Earth targets (min delta-v, durations)","JPL SBDB near-Earth objects with measured diameter","JPL mean orbital elements of planetary satellites","retrieved sources"]))+"""

Every record has `data_class: verified`, `source_ids`, `retrieval_status: retrieved` and either `field_verification` (per-field source text, URL, SHA-256, tolerance) or a `provenance` block (file, URL, SHA-256, retrieval date). Not generated by hand: run `python3 tools/make_verified.py`.
""")
print("verified:",counts); print("classes:",dict(cls)); print("facilities agree with official:",agree,"/",len(fac))
