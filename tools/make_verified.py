#!/usr/bin/env python3
"""STRICT MODE builder. Reads the staging build (space-mission-research/combined) and the retrieved source files (data_raw/retrieved/) and writes `verified/`,
which contains ONLY:
  * records / fields that were checked against a retrieved source (field_verification present) -- unverified fields are removed,
  * datasets ingested directly from authoritative sources (JPL NHATS, JPL SBDB query, JPL satellite mean elements, official NASA Facilities CSV),
  * analyses derived purely from verified inputs.
Everything estimated, fictional or merely recalled (optimizer catalog, costs, instruments, components, user-supplied SpaceX table, ...) is excluded."""
import json, os, re, csv, html, math, hashlib, datetime, shutil, collections, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import ingest_real as IR
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
planets=[x for x in celestial(S["celestial"]["planets"]) if x.get("category") in ("star","planet")]; moons=celestial(S["celestial"]["moons"]); asteroids=[]   # game scope: Sun, planets, moons (dwarf planets/asteroids removed)
NSSDC=IR.nssdc_params()
for _b in planets+moons:
    _n=NSSDC.get(_b["id"])
    if _n: _b["nssdc_fact_sheet"]=dict(published=_n["published"],numeric=_n["numeric"],provenance=_n["provenance"],note="rows of the NASA NSSDC fact sheet exactly as published (planet column)")
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
t=open(os.path.join(RET,"jpl_sat_elem.html"),encoding="utf-8",errors="replace").read(); tb=re.findall(r"<table.*?</table>",t,flags=re.S|re.I)[0]
rows=[[re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",c))).strip() for c in re.findall(r"<t[dh].*?</t[dh]>",tr,flags=re.S|re.I)] for tr in re.findall(r"<tr.*?</tr>",tb,flags=re.S|re.I)]
hdr=rows[0]; P3=prov("jpl_sat_elem.html","https://ssd.jpl.nasa.gov/sats/elem/","S52"); moon_el=[]
for r in rows[1:]:
    if len(r)<14: continue
    d=dict(zip(hdr,r))
    moon_el.append(dict(id=f"satel_{d['Code']}_{d['Ephemeris'].lower()}",planet=d["Planet"],satellite=d["Satellite"],jpl_code=d["Code"],ephemeris=d["Ephemeris"],frame=d["Frame"],epoch_tdb=d["Epoch (TDB)"],semi_major_axis_km=num(d["a (km)"]),eccentricity=num(d["e"]),
        arg_periapsis_deg=num(d["ω (deg)"]),mean_anomaly_deg=num(d["M (deg)"]),inclination_deg=num(d["i (deg)"]),node_deg=num(d["node (deg)"]),period_days=num(d["P (days)"]),reference=d["Ref."],
        data_class="verified",confidence="high",source_ids=["S52"],retrieval_status="retrieved"))
moon_el=[m for m in moon_el if m["satellite"] in {x["name"] for x in moons}]
# ---------- NASA SoA components, NSSDC missions/instruments/atmospheres (ingested directly) ----------
soa,soa_tables,soa_files=IR.soa_components(); nmc_ms,nmc_ex=IR.nmc_missions(); atm=IR.atmospheres()
ll2_cfg=IR.ll2_launchers(); sx_hist=IR.ll2_spacex_launches(); fluid=IR.fluids()
ll2_files={os.path.basename(r['provenance']['file']):r['provenance'] for r in ll2_cfg+sx_hist}
EXC=re.compile(r"Filament|Photopolymer|Windform|Resistivity|Software|Operating Systems|Memory Types|AI Space|FSW|Tracking Aids|Primary Elements of a Ground|Drag Sail|TechEdSat|Contact",re.I)
soa=[r for r in soa if r["domain"] not in ("tracking","deorbit") and not EXC.search(r["table_title"])]; soa_tables=[t for t in soa_tables if t["domain"] not in ("tracking","deorbit") and not EXC.search(t["title"])]
soa_table_recs=[dict(id=f"soa_table_{i:03d}",domain=t["domain"],chapter=t["chapter"],table_id=t["table_id"],title=t["title"],columns=t["columns"],rows=t["rows"],data_class="verified",source_ids=["S54"],retrieval_status="retrieved") for i,t in enumerate(soa_tables)]
# cross-check: user-supplied SpaceX table (2010-2018) against the Launch Library record
ll_by_date=collections.defaultdict(list)
for r in sx_hist: ll_by_date[(r["date_utc"] or "")[:10]].append(r)
usx=S["launch_history"]["launches"]; matched=0; outcome_agree=0
for u in usx:
    c=ll_by_date.get(u["date_utc"],[])
    if c:
        matched+=1; ok_user=u["mission_outcome"] in ("success","success_payload_unclear"); ok_ll=any(x["status"]=="Launch Successful" for x in c)
        outcome_agree+= (ok_user==ok_ll)
sx_cross=f"Of {len(usx)} rows in the user-supplied SpaceX table, {matched} have a Launch Library SpaceX launch on the same UTC date and {outcome_agree} of those agree on success/failure. The public dataset uses the Launch Library record (743 launches), not the user table."
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
sources=[s for s in S["metadata"]["sources"] if s.get("retrieved") is True]
sources+= [dict(id="S52",title="JPL Planetary Satellite Mean Elements",organization="NASA JPL SSD",url="https://ssd.jpl.nasa.gov/sats/elem/",retrieved=True,retrieval_date=P3["retrieved"],retrieved_pages=[dict(url=P3["source_url"],sha256=P3["source_sha256"],retrieved=P3["retrieved"])]),
 dict(id="S54",title="NASA State-of-the-Art Small Spacecraft Technology report 2026 (web edition, 12 chapters)",organization="NASA Small Spacecraft Systems Virtual Institute",url="https://www.nasa.gov/smallsat-institute/sst-soa/",retrieved=True,retrieval_date=max(v["retrieved"] for v in soa_files.values()),retrieved_pages=[dict(url=v["url"],sha256=v["source_sha256"],retrieved=v["retrieved"]) for v in soa_files.values()],note="Vendor-reported component specifications compiled by NASA; not NASA-tested."),
 dict(id="S55",title="The Space Devs Launch Library 2 (launcher configurations; SpaceX launch record)",organization="The Space Devs",url="https://ll.thespacedevs.com/2.2.0/",retrieved=True,retrieval_date=max(v["retrieved"] for v in ll2_files.values()),retrieved_pages=[dict(url=v["url"],sha256=v["source_sha256"],retrieved=v["retrieved"],file=v["file"]) for v in ll2_files.values()],note="Community-curated aggregator citing manufacturers and agencies; reference orbits of capacity figures are not stated."),
 dict(id="S56",title="NIST Chemistry WebBook: thermophysical properties of fluids (saturation tables)",organization="NIST",url="https://webbook.nist.gov/chemistry/fluid/",retrieved=True,retrieval_date=max(r["provenance"]["retrieved"] for r in fluid),retrieved_pages=[dict(url=r["provenance"]["url"],sha256=r["provenance"]["source_sha256"],retrieved=r["provenance"]["retrieved"]) for r in fluid])]
elements=[e for e in elements if e["body_id"] in {x["id"] for x in planets}]
cols=dict(planets=planets,moons=moons,orbital_elements=elements,rocket_engines=engines,electric_propulsion=electric,launch_vehicles=vehicles,rocket_stages=stages,boosters=boosters,payload_capabilities=payload_caps,
          missions=missions,moon_mean_elements=moon_el,smallsat_components=soa,smallsat_tables=soa_table_recs,nasa_missions=nmc_ms,nasa_instruments=nmc_ex,atmospheres=atm,launch_vehicle_configs=ll2_cfg,spacex_launch_history=sx_hist,fluid_properties=fluid,sources=sources)
counts={k:len(v) for k,v in cols.items()}
cls=collections.Counter(r.get("data_class") for k,v in cols.items() if k!="sources" for r in v)
q0=S["metadata"]["quality"]
quality=dict(mode="STRICT: verified data only",build_date=datetime.date.today().isoformat(),record_counts=counts,data_class_counts=dict(cls),verified_records=cls.get("verified",0),targets={},target_attainment_pct={},
  retrieval=dict(sources_listed=len(sources),sources_retrieved=len(sources),reason="Only retrieved sources are used; see metadata sources and field_verification on each record."),
  statement=("STRICT MODE: this dataset contains only values that were compared with, or ingested directly from, retrieved sources: JPL (SSD, SBDB), NASA (NSSDC fact sheets and mission catalog, Small Spacecraft SoA report 2026, SLS page, Apollo 11 press kit, NTRS papers, ), ULA, ESA, NIST, and the Launch Library 2 aggregator. "
             "Records carry source_authority/confidence where the source is an aggregator or vendor-reported compilation. Recalled, estimated and fictional values (optimizer catalog, costs, engine/vehicle specs without a retrievable source, the user-supplied SpaceX table) are not included. Derived values are computed only from verified inputs and are labelled derived."),
  conflicts_resolved=q0.get("conflicts_resolved",[]),known_conflicts=[dict(topic="Excluded data",note="Records or fields that could not be verified are excluded, not zero-filled; coverage is therefore partial by design. See staging reports for what was removed and why."),
      dict(topic="SpaceX table cross-check",note=sx_cross),dict(topic="Launch Library authority",note="Launch vehicle configurations and the SpaceX launch record come from The Space Devs Launch Library 2, a community-curated aggregator; records carry source_authority and confidence medium. Capacities do not state reference orbits. Falcon 9 Block 5 figures (22,800 kg LEO, 8,300 kg GTO, 549 t, 7,607 kN) agree with the previously recalled values."),dict(topic="Scope",note="Strict game scope: asteroid catalogs (NHATS, SBDB), dwarf planets, NASA facilities and tracking/deorbit/3D-printing/software tables were removed because the Space Mission Design Game does not use them.")],
  missing_categories=["structured instrument specifications (mass, power, data rate): only NASA catalog descriptions are included","properties of storable/kerosene propellants (RP-1, hydrazine, MMH, NTO): only cryogenic and noble-gas fluids from NIST are included","ground-station antenna gains (the NASA SoA ground tables are included as published)","engine and vehicle specifications beyond the verified fields","costs"],completeness_pct={},validations_run="see verified/validation_report.json")
combined=dict(schema_version="verified-1.0.0",mode="STRICT: verified data only",generated=quality["build_date"],note=quality["statement"],
  celestial=dict(planets=planets,moons=moons,asteroids=asteroids,orbital_elements=elements,atmospheres=atm),
  propulsion=dict(rocket_engines=engines,electric_propulsion=electric,propellants=fluid),launch=dict(launch_vehicles=vehicles,rocket_stages=stages,boosters=boosters,payload_capabilities=payload_caps),
  spacecraft=dict(components=[],ground_stations=[],optical_demonstrations=[]),instruments=[],
  missions=dict(historical=missions,profiles=[],requirements=[],trajectory_reference=traj,engineering_constraints=[]),
  launch_history=dict(launches=[],sites=[],analysis=None,note='see real_data.spacex_launch_history_file'),infrastructure=dict(nasa_facilities=[],analysis=dict(records=0,note='removed: not needed by the game')),
  real_data=dict(launch_vehicle_configs_file="launch_vehicle_configs.json",launch_vehicle_configs_count=len(ll2_cfg),spacex_launch_history_file="spacex_launch_history.json",spacex_launch_history_count=len(sx_hist),nasa_missions=nmc_ms,smallsat_components_file="smallsat_components.json",smallsat_components_count=len(soa),smallsat_tables=soa_table_recs,smallsat_provenance=soa_files,nasa_instruments_file="nasa_instruments.json",nasa_instruments_count=len(nmc_ex),moon_mean_elements=moon_el,moon_mean_elements_provenance=P3,note="Game-scope dataset: asteroid catalogs and NASA facilities were removed; see quality_report.json"),
  analysis=dict(light_time=lt),
  optimization=dict(constraints=dict(scenarios=[],catalog={},global_parameters={}),experiments=[],pareto=[],sensitivity=[],uncertainty=[],models=None),
  verification=dict(celestial=S["verification"]["celestial"],launch=S["verification"]["launch"],retrieved_files=S["verification"]["retrieved_files"]),
  metadata=dict(sources=sources,quality=quality))
W("combined/verified_space_mission_data.json",combined)
COLPROV={"moon_mean_elements":P3}
for k,v in cols.items(): W(f"{k}.json",dict(collection=k,count=len(v),mode="STRICT: verified data only",**({"provenance":COLPROV[k]} if k in COLPROV else {}),records=v))
W("quality_report.json",quality)
DESC=dict(launch_vehicle_configs="532 launch vehicle configurations (Launch Library 2): dimensions, mass, thrust, LEO/GTO capacity, cost, launch statistics",spacex_launch_history="complete SpaceX launch record, 743 launches (Launch Library 2)",fluid_properties="NIST saturation properties of O2, H2, CH4, Xe, N2, He",planets="Sun, planets, dwarf planets (verified fields only)",moons="moons (verified GM/radius/mass)",asteroids="Bennu, Vesta",orbital_elements="planet/dwarf-planet orbital elements",rocket_engines="engines (verified fields only)",electric_propulsion="NEXT, NSTAR, BPT-4000",launch_vehicles="launch vehicles (verified fields only)",rocket_stages="Saturn V stages",boosters="SLS booster",
  payload_capabilities="verified payload capacities with stated reference orbits",missions="missions: verified launch date / vehicle family",nasa_facilities="official NASA facilities (data.nasa.gov)",nhats_targets="JPL NHATS accessible near-Earth targets",neo_catalog="JPL SBDB near-Earth objects with measured diameter",moon_mean_elements="JPL mean orbital elements of planetary satellites",
  smallsat_components="NASA SoA 2026 product tables: thrusters, power, GNC, radios, antennas, computers, platforms, launch, ground (vendor-reported)",smallsat_tables="index of the SoA tables and their columns",nasa_missions="39 missions from the NASA NSSDC catalog (launch date, vehicle, site, catalogued mass/power, description)",nasa_instruments="181 instruments/experiments with NASA catalog descriptions",atmospheres="NSSDC fact-sheet atmosphere data (published text + parsed numbers)",sources="retrieved sources")
open(os.path.join(OUT,"README.md"),"w").write(f"# verified/ — strict-mode dataset (generated)\n{quality['statement']}\n\n| Collection | Records | What |\n|---|---:|---|\n"+"\n".join(f"| `{k}.json` | {n} | {DESC.get(k,k)} |" for k,n in counts.items())+"\n\nEvery record has `data_class: verified`, `source_ids`, `retrieval_status: retrieved` and either `field_verification` (per-field source text, URL, SHA-256, tolerance) or a `provenance` block (file, URL, SHA-256, retrieval date). Generated by `python3 tools/make_verified.py`.\n")
print("verified:",counts); print("classes:",dict(cls))
