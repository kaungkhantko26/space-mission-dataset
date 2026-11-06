#!/usr/bin/env python3
"""Builds space-mission-research/ from tools/data_*.py. Deterministic. Run: python3 tools/build.py"""
import json, math, os, random, datetime, statistics, sys, re, copy
sys.path.insert(0, os.path.dirname(__file__))
from astro import *
import data_celestial as DC, data_prop_launch as DP, data_sc as DS, opt_model as O, ingest_external as IX

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "space-mission-research")
VERSION = "0.1.0"; BUILD_DATE = "2026-11-06"
def W(path, obj):
    p = os.path.join(ROOT, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f: json.dump(obj, f, indent=1, ensure_ascii=False, sort_keys=False)
    return obj
def meta(kind, desc, records):
    return {"schema_version": VERSION, "dataset": kind, "description": desc, "generated": BUILD_DATE, "retrieval_status": "NOT_RETRIEVED: values recalled from published references; network access to source hosts was blocked in the build environment. See metadata/quality_report.json.", "record_count": len(records), "records": records}
def tag(r, cls="unverified", conf="medium", src=None):
    r.setdefault("data_class", cls); r.setdefault("confidence", conf); r.setdefault("source_ids", src or []); r["retrieval_status"] = "not_retrieved"; return r

# ---------------- sources ----------------
SRC = [
 ("S01","NASA NSSDC Planetary Fact Sheets","NASA GSFC NSSDC","https://nssdc.gsfc.nasa.gov/planetary/factsheet/","Planet physical/orbital parameters"),
 ("S02","JPL SSD Planetary Physical Parameters","NASA JPL SSD","https://ssd.jpl.nasa.gov/planets/phys_par.html","GM, radii, rotation"),
 ("S03","JPL SSD Planetary Satellite Physical Parameters","NASA JPL SSD","https://ssd.jpl.nasa.gov/sats/phys_par/","Moon GM, radii"),
 ("S04","JPL SSD Approximate Positions of the Planets (Standish)","NASA JPL SSD","https://ssd.jpl.nasa.gov/planets/approx_pos.html","J2000 mean elements, valid 1800-2050"),
 ("S05","IAU 2015 Resolution B3 nominal solar and planetary values","IAU","https://www.iau.org/Iau/Publications/Resolutions","Nominal GM_sun, R_sun"),
 ("S06","SpaceX vehicle pages / Falcon user's guide","SpaceX","https://www.spacex.com/vehicles/","Falcon 9/Heavy, Starship, Merlin, Raptor, Draco"),
 ("S07","ULA Atlas V / Vulcan / Delta IV user guides; Blue Origin New Glenn pages","ULA / Blue Origin","https://www.ulalaunch.com/","Atlas V, Vulcan, Delta IV, RD-180, BE-4, New Glenn"),
 ("S08","NASA SLS fact sheet; Shuttle/SLS booster references","NASA","https://www.nasa.gov/sls","SLS Block 1, RS-25, boosters"),
 ("S09","NASA SP-4206 Stages to Saturn; Saturn V Flight Manual","NASA","https://ntrs.nasa.gov/","Saturn V stages, F-1, J-2, SPS"),
 ("S10","Rocket Lab Electron Payload User's Guide","Rocket Lab","https://www.rocketlabcorp.com/launch/electron/","Electron, Rutherford"),
 ("S11","Arianespace Ariane 6 / Vega-C user's manuals; ESA","Arianespace / ESA","https://www.arianespace.com/","Ariane 5/6, Vega-C, Vinci, Vulcain 2"),
 ("S12","Manufacturer datasheets and secondary compilations (Aerojet Rocketdyne, Northrop Grumman, Roscosmos, CASC)","various","https://www.rocket.com/","RS-25D, Star 48B, MR-103, AJ10, Soyuz, Long March 5"),
 ("S13","Aerojet Rocketdyne RL10 datasheet","Aerojet Rocketdyne","https://www.rocket.com/space/liquid-engines/rl10-engine","RL10"),
 ("S14","NASA/JPL/GRC electric propulsion literature (NSTAR flight, NEXT, SmallSat SOA propulsion chapter)","NASA","https://www.nasa.gov/smallsat-institute/sst-soa/","Ion and Hall thrusters"),
 ("S15","Propellant property handbooks (e.g. NIST Chemistry WebBook)","NIST","https://webbook.nist.gov/chemistry/","Densities"),
 ("S16","NASA State-of-the-Art Small Spacecraft Technology report (2026)","NASA SSTP","https://www.nasa.gov/smallsat-institute/sst-soa/","Component technology classes (power, ADCS, thermal, comms, structures)"),
 ("S17","NASA RPS program: MMRTG and GPHS-RTG fact sheets","NASA / DOE","https://rps.nasa.gov/","RTG masses/power"),
 ("S18","BAE Systems RAD750 datasheet","BAE Systems","https://www.baesystems.com/","Flight processor"),
 ("S19","New Horizons mission payload papers (Space Science Reviews)","NASA APL/SwRI","https://pluto.jhuapl.edu/","New Horizons instruments"),
 ("S20","MRO instrument papers (HiRISE, CRISM, SHARAD)","NASA JPL / JGR","https://mars.nasa.gov/mro/","MRO payload"),
 ("S21","Mars Global Surveyor MOLA instrument papers","NASA GSFC","https://pds.nasa.gov/","MOLA"),
 ("S22","Lunar Reconnaissance Orbiter LROC/mission references","NASA GSFC / ASU","https://lroc.im-ldi.com/","LROC NAC, LRO"),
 ("S23","MSL / Curiosity mission references (SAM)","NASA JPL / GSFC","https://mars.nasa.gov/msl/","MSL, SAM"),
 ("S24","Landsat 8 mission documentation","NASA / USGS","https://www.usgs.gov/landsat-missions","OLI, TIRS"),
 ("S25","Sentinel-2 mission documentation","ESA","https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-2","MSI"),
 ("S26","DSN Telecommunications Link Design Handbook (810-005)","NASA JPL","https://deepspace.jpl.nasa.gov/dsndocs/810-005/","DSN antenna gains/G-T"),
 ("S27","ESA ESTRACK ground station network","ESA","https://www.esa.int/Enabling_Support/Operations/ESA_Ground_Stations","ESTRACK"),
 ("S28","KSAT network information","KSAT","https://www.ksat.no/","Svalbard"),
 ("S29","NASA LLCD / DSOC optical communications releases","NASA","https://www.nasa.gov/mission/deep-space-optical-communications-dsoc/","Optical comm demonstrations"),
 ("S30","Voyager mission references","NASA JPL","https://voyager.jpl.nasa.gov/","Voyager"),
 ("S31","Cassini-Huygens mission references","NASA JPL / ESA","https://science.nasa.gov/mission/cassini/","Cassini"),
 ("S32","Juno mission references","NASA JPL","https://www.nasa.gov/mission/juno/","Juno"),
 ("S33","JWST mission references","NASA GSFC / STScI","https://science.nasa.gov/mission/webb/","JWST"),
 ("S34","OSIRIS-REx mission references","NASA GSFC / Univ. Arizona","https://www.nasa.gov/osiris-rex","OSIRIS-REx"),
 ("S35","MarCO mission references","NASA JPL","https://www.jpl.nasa.gov/missions/mars-cube-one-marco","MarCO"),
 ("S40","JPL Small-Body Database (SBDB) API","NASA JPL SSD","https://ssd-api.jpl.nasa.gov/doc/sbdb.html","GM, diameter, rotation, osculating elements of Bennu, Ceres, Vesta, Pluto, Eris"),
 ("S41","NASA Space Launch System reference page","NASA","https://www.nasa.gov/reference/space-launch-system/","SLS Block 1 height, fueled mass, thrust, TLI capacity; booster and RS-25 thrust"),
 ("S42","ULA Atlas V and Vulcan Centaur web pages (performance tables, engine specifications)","United Launch Alliance","https://www.ulalaunch.com/rockets/atlas-v","Atlas V 551 and Vulcan VC6 payload capability with reference orbits; RD-180 and BE-4 specifications"),
 ("S43","ESA Vega-C launcher page","ESA","https://www.esa.int/Enabling_Support/Space_Transportation/Launch_vehicles/Vega-C","Vega-C height, mass, SSO payload, fairing, stage count"),
 ("S44","NASA Apollo 11 Press Kit (NTRS 19690022248)","NASA","https://ntrs.nasa.gov/citations/19690022248","Saturn V stage masses, propellants, thrust, vehicle weight, launch date"),
 ("S45","NEXT Ion Propulsion System Information Summary (NTRS 20090004685)","NASA GRC","https://ntrs.nasa.gov/citations/20090004685","NEXT thruster data sheet"),
 ("S46","NSTAR ion thruster and power processor paper (NTRS 19980017550)","NASA GRC / Hughes","https://ntrs.nasa.gov/citations/19980017550","NSTAR thrust, power, Isp (pre-flight)"),
 ("S47","BPT-4000 Hall thruster NASA/TM-2006-214453 (NTRS 20060051789)","NASA GRC / Aerojet","https://ntrs.nasa.gov/citations/20060051789","BPT-4000 thrust, Isp, power"),
 ("S48","ESA Ariane 6 overview page","ESA","https://www.esa.int/Enabling_Support/Space_Transportation/Launch_vehicles/Ariane_6_overview","Ariane 62/64 GTO and LEO capability, fairing, height"),
 ("S36","User-supplied SpaceX launch table (data_raw/spacex_launch_data.csv); user indicated Kaggle dataset scoleman/spacex-launch-data","user upload","https://www.kaggle.com/datasets/scoleman/spacex-launch-data","Falcon 9/Heavy launches 2010-06-04..2018-06-04; underlying origin and license NOT verified"),
 ("S37","User-supplied NASA Facilities table (data_raw/NASA_Facilities.csv)","user upload","https://data.nasa.gov/","485 NASA facilities with coordinates; appears to be the NASA open-data facilities table, not verified"),
 ("S39","Launch-pad coordinates recalled from public maps/references","recalled","https://www.nasa.gov/","3 launch sites, ~0.01 deg accuracy, not retrieved"),
 ("G01","Project-defined game/analysis assumptions (this repository)","this repository","tools/opt_model.py","Fictional credits, estimated catalog values, scenario assumptions"),
]
sources = [dict(id=i,title=t,organization=o,url=u,covers=c,retrieved=False,retrieval_date=None,page_or_section=None,note="Canonical landing page recorded for where to verify; the document was NOT opened in this build.") for i,t,o,u,c in SRC]
sources[-1].update(retrieved=None, note="Internal assumption record, not an external source.")

# ---------------- celestial ----------------
def body_rec(id,name,cat,mu,r_mean,r_eq,mass,g,rot_h,parent,a_km,e,i,per,temp,mag,src):
    d=dict(id=id,name=name,category=cat,parent_id=parent,mu_m3_s2=mu*1e9,gravitational_parameter_km3_s2=mu,mean_radius_m=r_mean*1e3,equatorial_radius_m=(r_eq*1e3 if r_eq else None),
           mass_kg=mass,surface_gravity_m_s2=g,rotation_period_h=rot_h,semi_major_axis_m=(a_km*1e3 if a_km else None),eccentricity=e,inclination_deg=i,orbital_period_days=per,
           mean_surface_temperature_k=temp,equatorial_magnetic_field_t=mag)
    # derived
    d["derived"]=dict(escape_velocity_m_s=v_esc(mu,r_mean)*1e3,circular_velocity_surface_m_s=v_circ(mu,r_mean)*1e3,
                      gravity_from_mu_m_s2=mu*1e9/(r_mean*1e3)**2,
                      derived_from="v_esc=sqrt(2*mu/R_mean); v_circ=sqrt(mu/R_mean); g=mu/R^2 (spherical, non-rotating approximation)",
                      solar_irradiance_w_m2=(1361.0/(a_km/AU_KM)**2 if (parent in (None,"sun") and a_km) else None))
    return tag(d,"unverified","medium",src)
planets=[]; moons=[]; asteroids=[]; elements=[]
planets.append(tag(dict(id="sun",name="Sun",category="star",parent_id=None,gravitational_parameter_km3_s2=DC.SUN["mu"],mu_m3_s2=DC.SUN["mu"]*1e9,mean_radius_m=DC.SUN["r_mean"]*1e3,mass_kg=DC.SUN["mass"],surface_gravity_m_s2=DC.SUN["g"],rotation_period_h=DC.SUN["rot_h"],mean_surface_temperature_k=DC.SUN["temp_mean_k"],note=DC.SUN["note"],
    derived=dict(escape_velocity_m_s=v_esc(DC.SUN["mu"],DC.SUN["r_mean"])*1e3,solar_constant_1au_w_m2=1361.0,derived_from="v_esc=sqrt(2mu/R)")),"unverified","medium",DC.SUN["src"]))
for p in DC.PLANETS:
    id,name,mu,rm,re_,mass,g,rot,aau,e,i,per,t,mag=p
    planets.append(body_rec(id,name,"planet",mu,rm,re_,mass,g,rot,"sun",aau*AU_KM,e,i,per,t,mag,["S01","S02"]))
    elements.append(tag(dict(body_id=id,epoch="J2000.0 (JD 2451545.0)",frame="ecliptic of J2000, heliocentric mean elements (EM barycenter for Earth)",semi_major_axis_au=aau,eccentricity=e,inclination_deg=i,
        validity="Standish approximate elements, nominal validity 1800-2050; secular rates NOT included here",time_dependence="time-dependent (slow secular drift)"),"unverified","medium",["S04"]))
for s in DC.SMALL:
    id,name,cat,mu,rm,mass,g,rot,aau,e,i,per,t=s
    r=body_rec(id,name,cat,mu,rm,None,mass,g,rot,"sun",aau*AU_KM,e,i,per,t,None,["S01","S03"]); r["confidence"]="low"
    (asteroids if cat=="asteroid" else planets).append(r)
    elements.append(tag(dict(body_id=id,epoch=None,frame="heliocentric ecliptic",semi_major_axis_au=aau,eccentricity=e,inclination_deg=i,validity="Approximate osculating/mean values; reference epoch not recorded",time_dependence="time-dependent"),"unverified","low",["S03"]))
for m in DC.MOONS:
    id,name,par,mu,rm,mass,g,a,per,e,i=m
    r=body_rec(id,name,"moon",mu,rm,None,mass,g,None,par,a,e,i,abs(per),None,None,["S03"]); r["rotation_period_h"]=None
    r["retrograde_orbit"]=per<0; r["tidally_locked_assumed"]=id in ("moon","io","europa","ganymede","callisto","titan","enceladus","triton","charon","phobos","deimos")
    r["derived"]["solar_irradiance_w_m2"]=None
    moons.append(r)
    elements.append(tag(dict(body_id=id,epoch=None,frame="parent-centric (parent equator or Laplace plane, not recorded per body)",semi_major_axis_km=a,eccentricity=e,inclination_deg=i,validity="Mean values",time_dependence="time-dependent"),"unverified","low",["S03"]))
atm=[tag(dict(a),"unverified","low" if a["id"] in ("pluto","mercury","moon","titan") else "medium",["S01"]) for a in DC.ATMOS]

# ---------------- apply retrieved-source verification (celestial) ----------------
VERF = os.path.join(ROOT, "metadata", "verification_celestial.json")
MANIFEST = os.path.join(ROOT, "..", "data_raw", "retrieved", "MANIFEST.json")
VER = json.load(open(VERF)) if os.path.exists(VERF) else None
VERL = json.load(open(os.path.join(ROOT, 'metadata', 'verification_launch.json'))) if os.path.exists(os.path.join(ROOT, 'metadata', 'verification_launch.json')) else None
MAN = {m["file"]: m for m in json.load(open(MANIFEST))} if os.path.exists(MANIFEST) else {}
verified_ids = set()
def apply_verification():
    import collections
    allrecs = {b["id"]: b for b in planets + moons + asteroids}
    elmap = {e["body_id"]: e for e in elements}
    keymap = {"mean_radius_m":"mean_radius_m","equatorial_radius_m":"equatorial_radius_m","mass_kg":"mass_kg","gravitational_parameter_km3_s2":"gravitational_parameter_km3_s2",
              "surface_gravity_m_s2":"surface_gravity_m_s2","rotation_period_h":"rotation_period_h","orbital_period_days":"orbital_period_days","semi_major_axis_m":"semi_major_axis_m","eccentricity":"eccentricity","inclination_deg":"inclination_deg"}
    by = collections.defaultdict(list)
    others = collections.defaultdict(list)
    for c in VER["checks"]:
        if c.get("primary", True): by[c["record_id"]].append(c)
        else: others[(c["record_id"], c["field"])].append(dict(source_id=c["source_id"], source_url=c["url"], source_original_text=c["source_original_text"], source_value=c["source_value"], status_vs_recalled=c["status"], section=c["section"]))
    for rid, cs in by.items():
        rec = allrecs.get(rid)
        if rec is None: continue
        fv = rec.setdefault("field_verification", {}); elfv = {}
        for c in cs:
            f = c["field"]
            if f.startswith("derived.") or c["status"] == "not_recorded": continue
            m = MAN.get(c["file"], {})
            info = dict(status="verified" if c["status"] == "verified" else "conflict_resolved_to_source", source_id=c["source_id"], source_url=c["url"], retrieved=c["retrieved"], source_sha256=m.get("sha256"),
                        section=c["section"], source_original_text=c["source_original_text"], source_value=c["source_value"], source_unit=c["source_unit"], conversion=c.get("conversion"), tolerance_rel=c["tolerance_rel"], recalled_value=c["mine_original"])
            if others.get((rid, f)): info["other_sources"] = others[(rid, f)]; info["sources_disagree"] = any(o["source_value"] != c["source_value"] and abs(o["source_value"] - c["source_value"]) > 1e-9 * abs(c["source_value"]) * 1e3 for o in others[(rid, f)]); info["selection_reason"] = c.get("selection_reason")
            if f.startswith("orbital_elements."):
                key = f.split(".", 1)[1]; el = elmap[rid]
                if c["status"] == "conflict": el[key] = c["source_value"]
                if c.get("source_epoch_jd"): el["epoch"] = f"JD {c['source_epoch_jd']} (osculating, SBDB)"; el["validity"] = "osculating elements at the stated epoch (JPL SBDB); time-dependent"
                elfv[key] = info
                bk = {"semi_major_axis_au": "semi_major_axis_m", "eccentricity": "eccentricity", "inclination_deg": "inclination_deg"}[key]
                if c["status"] == "conflict": rec[bk] = c["source_value"] * AU_KM * 1e3 if key == "semi_major_axis_au" else c["source_value"]
                fv[bk] = info
                continue
            key = keymap[f]
            if c["status"] == "conflict":
                rec[key] = c["source_value"]
                if key == "gravitational_parameter_km3_s2": rec["mu_m3_s2"] = c["source_value"] * 1e9
            fv[key] = info
        # recompute derived values from (possibly corrected) verified inputs
        mu = rec["gravitational_parameter_km3_s2"]; R = rec["mean_radius_m"] / 1e3
        d = rec.setdefault("derived", {}); d["escape_velocity_m_s"] = v_esc(mu, R) * 1e3
        if rec.get("category") != "star":
            d["circular_velocity_surface_m_s"] = v_circ(mu, R) * 1e3; d["gravity_from_mu_m_s2"] = mu * 1e9 / (R * 1e3) ** 2
            if rec.get("parent_id") in (None, "sun") and rec.get("semi_major_axis_m"): d["solar_irradiance_w_m2"] = 1361.0 / (rec["semi_major_axis_m"] / 1e3 / AU_KM) ** 2
        if "mu" in rec["derived"]: pass
        core = ["gravitational_parameter_km3_s2", "mean_radius_m"]
        if all(k in fv for k in core):
            rec["data_class"] = "verified"; rec["confidence"] = "high"; rec["retrieval_status"] = "retrieved"; verified_ids.add(rid)
            rec["source_ids"] = sorted({i["source_id"] for i in fv.values()} | ({"S01"} if rid in ("sun",) else set()))
            rec["verification_scope"] = "core physical fields (GM, mean radius, and mass/gravity/rotation/orbit where listed in field_verification) were checked against retrieved JPL/NASA pages; fields in unverified_fields were NOT"
        cand = ["mass_kg", "surface_gravity_m_s2", "rotation_period_h", "orbital_period_days", "semi_major_axis_m", "eccentricity", "inclination_deg", "mean_surface_temperature_k", "equatorial_magnetic_field_t", "equatorial_radius_m"]
        rec["unverified_fields"] = [k for k in cand if rec.get(k) is not None and k not in fv]
        if rid in elmap and elfv:
            el = elmap[rid]; el["field_verification"] = elfv
            if all(k in elfv for k in ("semi_major_axis_au", "eccentricity", "inclination_deg")):
                el["data_class"] = "verified"; el["confidence"] = "high"; el["retrieval_status"] = "retrieved"; el["source_ids"] = sorted({i["source_id"] for i in elfv.values()})
if VER: apply_verification()

def patch_sources():
    """Replace recalled launch/engine values with sourced ones BEFORE records and derived values are built."""
    if not VERL: return
    tables = {"launch_vehicles": DP.VEHICLES, "rocket_stages": DP.STAGES, "boosters": DP.BOOSTERS, "rocket_engines": DP.ENGINES}
    for c in VERL["checks"]:
        if c["status"] not in ("conflict", "added_from_source") or c["collection"] not in tables: continue
        rec = next((r for r in tables[c["collection"]] if r["id"] == c["record_id"]), None)
        if rec is None: continue
        f = c["field"]; v = c["source_value"]
        m = re.match(r"payloads\[(\w+)\]\.(\w+)$", f)
        if m:
            orbit, key = m.groups(); cand = [p for p in rec["payloads"] if p["orbit"] == orbit]
            p_ = next((p for p in cand if p["mode"].startswith("expended")), cand[0] if cand else None)
            if p_ is None:
                p_ = dict(orbit=orbit, payload_kg=None, altitude_km=None, inclination_deg=None, mode="expended", assumption=("C3 = -2 km2/s2 (ULA definition)" if orbit == "TLI" else "added from retrieved source")); rec["payloads"].append(p_)
            p_[key] = v
        else: rec[f] = v
patch_sources()
def apply_launch(coll, recs):
    """Attach field-level provenance (values were already corrected by patch_sources) and classify records whose core fields are ALL verified."""
    if not VERL: return
    byid = {r["id"]: r for r in recs}
    for c in VERL["checks"]:
        if c["collection"] != coll or c["status"] not in ("verified", "conflict", "added_from_source") or c["record_id"] not in byid: continue
        r = byid[c["record_id"]]; f = c["field"]
        info = dict(status={"verified": "verified", "conflict": "conflict_resolved_to_source", "added_from_source": "added_from_source"}[c["status"]], source_id=c["source_id"], source_url=c["url"], retrieved=c["retrieved"], source_sha256=c["source_sha256"], section=c["section"],
                    source_original_text=c["source_original_text"], source_value=c["source_value"], source_unit=c["source_unit"], statement_type=c["statement_type"], tolerance_rel=c["tolerance_rel"], recalled_value=c["mine_original"], note=c.get("note"))
        r.setdefault("field_verification", {})[f] = info
        r["verified_field_count"] = len(r["field_verification"])
    core = {"rocket_engines": ["thrust_vac_n", "thrust_sl_n", "isp_vac_s", "isp_sl_s", "dry_mass_kg", "power_w"], "rocket_stages": ["dry_mass_kg", "propellant_mass_kg", "n_engines"]}.get(coll)
    for r in recs:
        if "field_verification" not in r: continue
        fv = r["field_verification"]
        r["unverified_fields"] = [k for k in ([k for k in (core or []) if r.get(k) is not None] + (["payloads"] if coll == "launch_vehicles" else [])) if k not in fv and k != "payloads"] if core else None
        if core and all(k in fv for k in core if r.get(k) is not None):
            r["data_class"] = "verified"; r["confidence"] = "high"; r["retrieval_status"] = "retrieved"
            r["source_ids"] = sorted({i["source_id"] for i in fv.values()})
            r["verification_scope"] = "all core numeric fields of this record were checked against retrieved sources (see field_verification); descriptive fields (status, propellant name, heritage) were not"
        else:
            r["verification_scope"] = "partial: only the fields in field_verification were checked against a retrieved source; the record as a whole remains unverified"
W("celestial/planets.json",meta("planets","Sun, planets and dwarf planets (SI)",planets))
W("celestial/moons.json",meta("moons","Major moons (SI)",moons))
W("celestial/asteroids.json",meta("asteroids","Selected small bodies (SI)",asteroids))
W("celestial/orbital_elements.json",meta("orbital_elements","Orbital elements with reference epochs where recorded",elements))
W("celestial/atmospheres.json",meta("atmospheres","Atmosphere summaries; gas giants at the 1-bar reference level. Not altitude profiles.",atm))
BODY={b["id"]:b for b in planets+moons+asteroids}

# ---------------- propulsion ----------------
engines=[]
for e in DP.ENGINES:
    r=dict(e); r["source_ids"]=r.pop("src"); r["confidence"]=r.pop("conf"); r["data_class"]="unverified"; r["retrieval_status"]="not_retrieved"
    d={}
    F=r["thrust_vac_n"]; I=r["isp_vac_s"]
    if F and I: d["mass_flow_vac_kg_s"]=F/(I*G0)
    if F and r["dry_mass_kg"]: d["engine_thrust_to_weight_vac"]=F/(r["dry_mass_kg"]*G0)
    if r["thrust_sl_n"] and r["isp_sl_s"]: d["mass_flow_sl_kg_s"]=r["thrust_sl_n"]/(r["isp_sl_s"]*G0)
    if r["type"] in("ion","hall_effect") and r["power_w"] and F: d["thrust_per_power_mN_per_kW"]=F*1e3/(r["power_w"]/1e3)
    r["derived"]=d; r["derived_from"]="mdot=F/(Isp*g0); TWR=F/(m*g0); thrust/power"
    engines.append(r)
if True:
    # flag the Raptor SL=vac placeholder
    for r in engines:
        if r["id"]=="raptor2": r["thrust_vac_n"]=None; r["note"]+=" (vacuum thrust left null rather than copying the sea-level value.)"; r["derived"].pop("mass_flow_vac_kg_s",None); r["derived"].pop("engine_thrust_to_weight_vac",None)
        if r["id"] in ("raptor2",) and r["thrust_sl_n"] and r["isp_sl_s"]: r["derived"]["engine_thrust_to_weight_sl"]=r["thrust_sl_n"]/(r["dry_mass_kg"]*G0)
chem=[e for e in engines if e["type"] not in ("ion","hall_effect")]; elec=[e for e in engines if e["type"] in ("ion","hall_effect")]
propellants=[tag(dict(p),"unverified",p["conf"],p["src"]) for p in DP.PROPELLANTS]
for p in propellants: p.pop("conf",None); p.pop("src",None)
apply_launch("rocket_engines", engines); W("propulsion/rocket_engines.json",meta("rocket_engines","Chemical engines/motors/thrusters (SI)",chem))
W("propulsion/electric_propulsion.json",meta("electric_propulsion","Ion and Hall thrusters at recorded operating point (SI)",elec))
W("propulsion/propellants.json",meta("propellants","Propellant densities",propellants))
ENG={e["id"]:e for e in engines}

# ---------------- launch ----------------
vehicles=[]
for v in DP.VEHICLES:
    r=dict(v); r["source_ids"]=r.pop("src"); r["confidence"]=r.pop("conf"); r["data_class"]="unverified"; r["retrieval_status"]="not_retrieved"
    d={}
    if r["liftoff_mass_kg"] and r["thrust_sl_n"]: d["liftoff_thrust_to_weight"]=r["thrust_sl_n"]/(r["liftoff_mass_kg"]*G0)
    if r["liftoff_mass_kg"]:
        d["payload_fraction_by_orbit"]=[dict(orbit=p["orbit"],mode=p["mode"],payload_to_liftoff=p["payload_kg"]/r["liftoff_mass_kg"]) for p in r["payloads"]]
    for p in r["payloads"]:
        if r["price_usd"] and p["orbit"] in("LEO","SSO"): d["usd_per_kg_"+p["orbit"].lower()+"_"+p["mode"].split()[0]]=r["price_usd"]/p["payload_kg"]
    r["derived"]=d; r["derived_from"]="T/W=F/(m g0); payload fraction; price/payload (price year in price_year)"
    vehicles.append(r)
stages=[]
for s in DP.STAGES:
    r=dict(s); r["source_ids"]=r.pop("src"); r["confidence"]=r.pop("conf"); r["data_class"]="unverified"; r["retrieval_status"]="not_retrieved"
    e=ENG[r["engine_id"]]; r["derived"]=dict(inert_mass_fraction=r["dry_mass_kg"]/(r["dry_mass_kg"]+r["propellant_mass_kg"]),stage_thrust_vac_n=(e["thrust_vac_n"]*r["n_engines"] if e["thrust_vac_n"] else None),
        stage_thrust_sl_n=(e["thrust_sl_n"]*r["n_engines"] if e["thrust_sl_n"] else None),isp_vac_s=e["isp_vac_s"])
    stages.append(r)
boosters=[]
for b in DP.BOOSTERS:
    r=dict(b); r["source_ids"]=r.pop("src"); r["confidence"]=r.pop("conf"); r["data_class"]="unverified"; r["retrieval_status"]="not_retrieved"; boosters.append(r)
payload_caps=[]
for v in vehicles:
    for p in v["payloads"]:
        payload_caps.append(tag(dict(vehicle_id=v["id"],**p,reference_conditions_complete=all(p[k] is not None for k in("altitude_km","inclination_deg")),
            warning="Capabilities are NOT directly comparable unless altitude, inclination, site and recovery mode match."),"unverified",v["confidence"],v["source_ids"]))
apply_launch("launch_vehicles", vehicles); apply_launch("boosters", boosters); W("launch/launch_vehicles.json",meta("launch_vehicles","Launch vehicles (SI)",vehicles))
apply_launch("rocket_stages", stages); W("launch/rocket_stages.json",meta("rocket_stages","Stage masses; engine links to propulsion/",stages))
W("launch/boosters.json",meta("boosters","Strap-on / solid boosters",boosters))
W("launch/payload_capabilities.json",meta("payload_capabilities","Payload capability per reference orbit; missing conditions are null",payload_caps))
VEH={v["id"]:v for v in vehicles}

# ---------------- spacecraft ----------------
def comp_out(c):
    r=dict(c); r["source_ids"]=r.pop("src"); r["retrieval_status"]="not_retrieved"; return r
comps=[comp_out(c) for c in DS.COMPONENTS]
bycat=lambda *cats:[c for c in comps if c["category"] in cats]
W("spacecraft/power_systems.json",meta("power_systems","Power sources/generation",bycat("power_source")+[c for c in comps if c["id"].startswith("sa_")]))
W("spacecraft/batteries.json",meta("batteries","Energy storage classes",bycat("battery")))
W("spacecraft/solar_arrays.json",meta("solar_arrays","Solar array technology classes",[c for c in comps if c["category"]=="solar_array"]))
W("spacecraft/onboard_computers.json",meta("onboard_computers","Flight computers",bycat("onboard_computer")))
W("spacecraft/attitude_control.json",meta("attitude_control","ADCS hardware classes",bycat("attitude_control")))
W("spacecraft/thermal_control.json",meta("thermal_control","Thermal hardware classes",bycat("thermal_control")))
ground=[tag(dict(g),"unverified",g["conf"],g["src"]) for g in DS.GROUND]
for g in ground: g.pop("conf",None); g.pop("src",None)
optical=[tag(dict(o),"unverified",o["conf"],o["src"]) for o in DS.OPTICAL]
for o in optical: o.pop("conf",None); o.pop("src",None)
W("spacecraft/communications.json",{**meta("communications","Spacecraft comm hardware classes, ground stations, optical demonstrations",bycat("communications")),"ground_stations":ground,"optical_demonstrations":optical})
W("spacecraft/structures.json",meta("structures","Structure/tankage/shielding classes",bycat("structure","radiation_protection")))
# fix: solar arrays counted in power_systems too -> dedupe by id in combined later

# ---------------- instruments ----------------
ins=[]
for i in DS.INSTRUMENTS:
    r=dict(i); r["source_ids"]=r.pop("src"); r["retrieval_status"]="not_retrieved"
    r["derived"]=dict(power_to_mass_w_per_kg=(r["power_w"]/r["mass_kg"] if r["power_w"] and r["mass_kg"] else None))
    ins.append(r)
grp=lambda *t:[i for i in ins if i["instrument_type"] in t]
W("instruments/cameras.json",meta("cameras","Optical/multispectral/thermal imagers",grp("optical_camera","multispectral_camera","thermal_imager","multispectral_imager_spectrometer")))
W("instruments/spectrometers.json",meta("spectrometers","Spectrometers",grp("uv_spectrometer","imaging_spectrometer","mass_spectrometer_gas_chromatograph")))
W("instruments/radar.json",meta("radar","Radar/lidar",grp("sounding_radar","lidar_altimeter")))
W("instruments/sensors.json",meta("sensors","Particle/dust/radio science",grp("particle_detector","dust_detector","radio_science")))
cmp_rows=[dict(id=i["id"],name=i["name"],type=i["instrument_type"],mission=i["heritage_mission"],mass_kg=i["mass_kg"],power_w=i["power_w"],w_per_kg=i["derived"]["power_to_mass_w_per_kg"]) for i in ins]
nh=[i for i in ins if i["heritage_mission"]=="New Horizons"]
nh_m=sum(i["mass_kg"] for i in nh); nh_p=sum(i["power_w"] for i in nh)
nh_launch=[m for m in DS.MISSIONS if m["id"]=="new_horizons"][0]["launch_mass_kg"]
W("instruments/instrument_comparison.json",{**meta("instrument_comparison","Comparison table; null = not recorded",cmp_rows),
  "case_study_new_horizons_payload":dict(instruments=[i["id"] for i in nh],payload_mass_kg=nh_m,payload_power_w=nh_p,spacecraft_launch_mass_kg=nh_launch,payload_mass_fraction=nh_m/nh_launch,
     data_class="derived",derived_from="sum of recorded instrument masses/powers; launch mass from missions dataset (all inputs unverified)")})

# ---------------- missions ----------------
missions=[]
variant={"lro":"Atlas V 401","mro":"Atlas V 401","curiosity":"Atlas V 541","landsat8":"Atlas V 401","sentinel2a":"Vega","osiris_rex":"Atlas V 411","marco":"Atlas V 401 (rideshare with InSight)","juno":"Atlas V 551","new_horizons":"Atlas V 551 + Star 48B","jwst":"Ariane 5 ECA","apollo11":"Saturn V","voyager2":"Titan IIIE-Centaur","cassini":"Titan IVB-Centaur","dawn":"Delta II 7925H"}
for m in DS.MISSIONS:
    r=dict(m); r["source_ids"]=r.pop("src"); r["retrieval_status"]="not_retrieved"; r["data_class"]="unverified"
    vid=r["launch_vehicle_id"]; r["launch_vehicle_note"]=variant.get(r["id"])
    if vid not in VEH or (r["id"] in variant and variant[r["id"]] not in ("Atlas V 551","Saturn V","Ariane 5 ECA","Atlas V 551 + Star 48B")): r["launch_vehicle_id"]=None
    if r["id"]=="voyager2": r["power_system"]="3 x MHW-RTG (~470 W at launch, approximate)"
    r["derived"]=dict(dry_to_launch_mass=(r["dry_mass_kg"]/r["launch_mass_kg"] if r["dry_mass_kg"] else None),propellant_plus_other_fraction=(1-r["dry_mass_kg"]/r["launch_mass_kg"] if r["dry_mass_kg"] else None))
    missions.append(r)
apply_launch("missions", missions); W("missions/historical_missions.json",meta("historical_missions","Historical missions (actual, not hypothetical). launch_vehicle_id is set only when the exact vehicle variant exists in launch/; otherwise null with launch_vehicle_note.",missions))

# ---------------- external user-supplied data ----------------
spx,sha_spx=IX.spacex(); spx_an=IX.spacex_analysis(spx); launch_sites=IX.sites(spx); fac,sha_fac=IX.facilities(); fac_an=IX.fac_analysis(fac)
W("missions/spacex_launch_history.json",{**meta("spacex_launch_history","Normalized user-supplied SpaceX launch table (57 rows, 2010-2018). Historical observations, not vehicle specifications.",spx),"input_file":"data_raw/spacex_launch_data.csv","input_sha256":sha_spx})
W("missions/launch_sites.json",meta("launch_sites","Launch pads appearing in the launch table; coordinates recalled",launch_sites))
W("infrastructure/nasa_facilities.json",{**meta("nasa_facilities","Normalized user-supplied NASA facilities table (485 rows); category is keyword-derived",fac),"input_file":"data_raw/NASA_Facilities.csv","input_sha256":sha_fac})
W("analysis/spacex_launch_analysis.json",spx_an); W("analysis/nasa_facilities_analysis.json",fac_an)

# ---------------- reference astro numbers ----------------
E=BODY["earth"]; MN=BODY["moon"]; MA=BODY["mars"]; SU=planets[0]
ref=dict(mu_earth=E["gravitational_parameter_km3_s2"],r_earth=E["mean_radius_m"]/1e3,mu_moon=MN["gravitational_parameter_km3_s2"],r_moon=MN["mean_radius_m"]/1e3,mu_mars=MA["gravitational_parameter_km3_s2"],r_mars=MA["mean_radius_m"]/1e3)
rLEO=ref["r_earth"]+400
traj=[]
# Earth-orbit
v_leo=v_circ(ref["mu_earth"],rLEO); rg=42164.0
h1,h2,ht,tt=hohmann(ref["mu_earth"],rLEO,rg)
traj.append(dict(id="leo400_circular",description="400 km circular LEO (Earth mean radius)",velocity_m_s=v_leo*1e3,period_s=period(ref["mu_earth"],rLEO)))
traj.append(dict(id="leo400_to_geo_hohmann",description="Coplanar Hohmann LEO(400 km)->GEO (r=42,164 km); no plane change",dv1_m_s=h1*1e3,dv2_m_s=h2*1e3,total_m_s=ht*1e3,transfer_time_h=tt/3600))
traj.append(dict(id="plane_change_28p5_at_geo",description="Plane change 28.5 deg at GEO speed",dv_m_s=plane_change(v_circ(ref["mu_earth"],rg),28.5)*1e3))
sc_list=O.build_scenarios(ref)
sc_by={s["id"]:s for s in sc_list}
lunar=sc_by["lunar_orbiter"]
traj.append(dict(id="leo400_to_moon_100km",description="Patched-conic TLI + LOI (see optimization scenario basis)",total_m_s=lunar["dv_ms"]-100,basis=lunar["dv_basis"]))
au=AU_KM
for tid in ["venus","mars","jupiter","saturn","uranus","neptune"]:
    r2=[p for p in planets if p["id"]==tid][0]["semi_major_axis_m"]/1e3
    d1,d2,dt,tt=hohmann(MU_SUN,au,r2)  # heliocentric: dv1 departure excess, dv2 arrival excess (circular-orbit approx)
    vinf_dep=d1; vinf_arr=d2; B=[p for p in planets if p["id"]==tid][0]
    rp=B["mean_radius_m"]/1e3+400
    dep=depart_dv_from_circular(ref["mu_earth"],rLEO,vinf_dep)
    cap_circ=math.sqrt(vinf_arr**2+2*B["gravitational_parameter_km3_s2"]/rp)-math.sqrt(B["gravitational_parameter_km3_s2"]/rp)
    synodic_d=synodic(365.25636,B["orbital_period_days"])
    traj.append(dict(id=f"earth_to_{tid}_hohmann",description=f"Circular coplanar heliocentric Hohmann Earth->{B['name']} (approximation; real transfers use eccentric, inclined orbits)",
        v_infinity_departure_m_s=vinf_dep*1e3,c3_km2_s2=vinf_dep**2,v_infinity_arrival_m_s=vinf_arr*1e3,
        departure_dv_from_400km_leo_m_s=dep*1e3,capture_dv_to_400km_circular_m_s=cap_circ*1e3,transfer_time_days=tt/86400,synodic_period_days=synodic_d,
        launch_window_recurrence_days=synodic_d,data_class="derived"))
for t in traj: t.setdefault("data_class","derived"); t["derived_from"]="two-body / patched-conic formulas in tools/astro.py"; t["inputs_data_class"]="unverified"
W("missions/trajectory_reference.json",meta("trajectory_reference","Derived delta-v and transfer references (educational approximations)",traj))

# mission requirements & profiles from scenarios
profiles=[]; reqs=[]
for s in sc_list:
    profiles.append(dict(id=s["id"],name=s["name"],body=s["body"],type="synthetic_hypothetical",period_s=s["period_s"],eclipse_s=s["eclipse_s"],sun_distance_au=s["sun_au"],delta_v_onboard_m_s=s["dv_ms"],delta_v_basis=s["dv_basis"],
        design_life_yr=s["life_yr"],comm_distance_m=s["dist_m"],downlink_hours_per_day=s["dl_hours_per_day"],data_class="derived",note="Hypothetical configuration for analysis; NOT a historical mission."))
    reqs.append(dict(id="req_"+s["id"],scenario_id=s["id"],budget_credits=s["budget"],min_science_points=s["min_science"],radiation_dose_krad=s["dose_krad"],radiation_dose_basis=s["dose_basis"],
        launch_vehicle_options=[v["id"] for v in s["vehicles"]],data_class="fictional" ,note="Budget (credits) and science weights are fictional educational values; see optimization_constraints.json"))
W("missions/mission_profiles.json",meta("mission_profiles","Hypothetical analysis scenarios",profiles))
W("missions/mission_requirements.json",meta("mission_requirements","Scenario requirements (synthetic)",reqs))

# ---------------- analysis ----------------
# mass analysis
mass=dict(vehicle_stack_accounting=[],mission_mass_fractions=[],notes=[])
for v in vehicles:
    ss=[s for s in stages if s["vehicle_id"]==v["id"]]
    if not ss or not v["liftoff_mass_kg"]: continue
    stack=sum(s["dry_mass_kg"]+s["propellant_mass_kg"] for s in ss)
    mass["vehicle_stack_accounting"].append(dict(vehicle_id=v["id"],liftoff_mass_kg=v["liftoff_mass_kg"],sum_of_recorded_stage_masses_kg=stack,residual_kg=v["liftoff_mass_kg"]-stack,
        residual_meaning="payload + fairing + interstages + strap-on boosters + any propellant not in stage record; large/negative residual flags inconsistent inputs",
        note="Strap-on boosters not included in stage sum." if v["id"] in("sls_b1","falcon_heavy") else "",data_class="derived"))
for m in missions:
    if m["dry_mass_kg"]: mass["mission_mass_fractions"].append(dict(mission_id=m["id"],launch_mass_kg=m["launch_mass_kg"],dry_mass_kg=m["dry_mass_kg"],dry_fraction=m["dry_mass_kg"]/m["launch_mass_kg"],propellant_fraction=1-m["dry_mass_kg"]/m["launch_mass_kg"],data_class="derived"))
rows=sorted(mass["mission_mass_fractions"],key=lambda x:x["propellant_fraction"])
mass["notes"].append("For spacecraft with recorded dry mass, wet-dry difference is propellant plus pressurant/consumables; separation not available in records.")
# stage-level propulsion analysis
prop=dict(stack_ideal_delta_v=[],engine_comparison=[],notes=["Ideal delta-v ignores gravity, drag and steering losses; ascent to LEO typically needs ~9.3-9.5 km/s of real delta-v (commonly cited range, not retrieved)."])
for v in vehicles:
    ss=[s for s in stages if s["vehicle_id"]==v["id"]]
    if not ss or not v["liftoff_mass_kg"]: continue
    ss=sorted(ss,key=lambda s:["S-IC","S-II","S-IVB","Core stage","Stage 1","Stage 2"].index(s["stage"]) if s["stage"] in ["S-IC","S-II","S-IVB","Core stage","Stage 1","Stage 2"] else 9)
    m0=v["liftoff_mass_kg"]; hi=lo=0; det=[]
    for s in ss:
        e=ENG[s["engine_id"]]; mf=m0-s["propellant_mass_kg"]
        ivac=e["isp_vac_s"]; isl=e["isp_sl_s"] or ivac
        first=(s is ss[0])
        dv_hi=ivac*G0*math.log(m0/mf); dv_lo=(isl if first else ivac)*G0*math.log(m0/mf)
        det.append(dict(stage=s["stage"],m0_kg=m0,mf_kg=mf,mass_ratio=m0/mf,dv_vac_isp_m_s=dv_hi,dv_sl_isp_m_s=dv_lo,burn_time_s_est=s["propellant_mass_kg"]/(e["thrust_vac_n"]*s["n_engines"]/(e["isp_vac_s"]*G0)) if e["thrust_vac_n"] else None))
        hi+=dv_hi; lo+=dv_lo; m0=mf-s["dry_mass_kg"]
    prop["stack_ideal_delta_v"].append(dict(vehicle_id=v["id"],stages=det,total_ideal_dv_low_m_s=lo,total_ideal_dv_high_m_s=hi,
        assumptions="Liftoff mass is the recorded value; payload+fairing+interstage mass stays in m0 (not dropped); strap-on boosters ignored (ideal dv understated for SLS/FH if boosters not modeled); uses recorded stage masses (see mass accounting residual).",
        data_class="derived",inputs_data_class="unverified"))
for e in engines:
    prop["engine_comparison"].append(dict(id=e["id"],type=e["type"],propellant=e["propellant"],isp_vac_s=e["isp_vac_s"],thrust_vac_n=e["thrust_vac_n"],engine_twr_vac=e["derived"].get("engine_thrust_to_weight_vac"),status=e["status"]))
# electric vs chemical: mass ratio for example dv
ex=[]
for dv in (150,1000,4000):
    for name,isp in (("monoprop 220 s",220),("biprop 310 s",310),("LOX/LH2 vac 450 s",450),("NSTAR 3100 s",3100),("Hall 1600 s",1600)):
        ex.append(dict(delta_v_m_s=dv,system=name,isp_s=isp,propellant_fraction_of_initial=1-1/mass_ratio(dv,isp),data_class="derived"))
prop["propellant_fraction_examples"]=ex
W("analysis/mass_analysis.json",mass); W("analysis/propulsion_analysis.json",prop); W("propulsion/propulsion_analysis.json",prop)

# power
power=dict(solar_flux=[],crossover=None,eclipse=[],assumptions=["Solar constant 1361 W/m2 at 1 AU; inverse-square scaling; panel packing 0.85; BOL cell efficiency per class record."])
for b in ["mercury","venus","earth","mars","jupiter","saturn","uranus","neptune"]:
    a=BODY[b]["semi_major_axis_m"]/1e3/AU_KM; f=1361.0/a**2
    power["solar_flux"].append(dict(body_id=b,distance_au=a,flux_w_m2=f,array_w_m2_3j_bol=f*0.29*0.85,array_w_m2_si_bol=f*0.15*0.85,array_w_per_kg_if_80w_kg_at_1au=80/a**2,data_class="derived"))
for name,hh,body in [("LEO 500 km","500","earth"),("LEO 400 km","400","earth"),("GEO","35786","earth"),("Lunar orbit 100 km","100","moon"),("Mars orbit 400 km","400","mars")]:
    R=BODY[body]["mean_radius_m"]/1e3; hv=float(hh); mu=BODY[body]["gravitational_parameter_km3_s2"]
    P=period(mu,R+hv); fr=eclipse_fraction(mu,R,hv)
    power["eclipse"].append(dict(orbit=name,period_s=P,max_eclipse_fraction=fr,max_eclipse_s=fr*P,assumption="Circular orbit, beta=0, cylindrical shadow; real max eclipse depends on season/beta angle; Earth penumbra neglected",data_class="derived"))
rtg_m=[c for c in comps if c["id"]=="rtg_mmrtg"][0]; rtg_g=[c for c in comps if c["id"]=="rtg_gphs"][0]
power["crossover"]=dict(solar_w_per_kg_at_1au=80,mmrtg_w_per_kg=rtg_m["power_generation_w"]/rtg_m["mass_kg"],gphs_rtg_w_per_kg=rtg_g["power_generation_w"]/rtg_g["mass_kg"],
    distance_au_mmrtg=math.sqrt(80/(rtg_m["power_generation_w"]/rtg_m["mass_kg"])),distance_au_gphs=math.sqrt(80/(rtg_g["power_generation_w"]/rtg_g["mass_kg"])),
    caveat="Compares array-only specific power to RTG unit specific power; ignores batteries, PMAD, degradation (RTG ~1.6%/yr for GPHS by Pu-238 decay + thermocouple), pointing, radiation environment and cost. Indicative only.",data_class="estimated")
W("analysis/power_analysis.json",power)

# comms
comm=dict(light_time=[],free_space_loss=[],link_budget_examples=[],assumptions=["Eb/N0 required 2.0 dB (coded) + 3 dB margin, 2 dB misc losses; ground G/T per scenario (estimated)."])
dist=[("Moon (mean)",3.844e8),("Mars min",0.37*AU_KM*1e3),("Mars max",2.67*AU_KM*1e3),("Jupiter (mean)",5.2*AU_KM*1e3),("Saturn (mean)",9.54*AU_KM*1e3),("Neptune (mean)",30.07*AU_KM*1e3)]
for n,d in dist:
    comm["light_time"].append(dict(target=n,distance_m=d,one_way_s=d/C,round_trip_s=2*d/C,data_class="derived"))
    comm["free_space_loss"].append(dict(target=n,s_band_2p2ghz_db=fspl_db(d,2.2e9),x_band_8p4ghz_db=fspl_db(d,8.4e9),ka_band_32ghz_db=fspl_db(d,32e9),data_class="derived"))
for n,d in dist:
    for dia,tx in ((1.0,20),(3.0,100)):
        gt=parabolic_gain_db(dia,8.4e9); eirp=10*math.log10(tx)+gt; GT=53.0
        base=eirp+GT-fspl_db(d,8.4e9)-2.0+228.6-2.0
        r=10**((base-3.0)/10)
        comm["link_budget_examples"].append(dict(target=n,spacecraft_dish_m=dia,tx_w=tx,band="X 8.4 GHz",sc_gain_dbi=gt,eirp_dbw=eirp,ground_gt_db_k=GT,max_data_rate_bps_with_3db_margin=r,daily_volume_gbit_8h_pass=r*8*3600*0.8/1e9,data_class="derived",inputs_data_class="estimated"))
W("analysis/communication_analysis.json",comm)

# feasibility / bottlenecks across scenarios (from optimization enumeration)
G=O.GLOBAL
all_runs={}
for sc in sc_list:
    D=O.enumerate_designs(G,sc); all_runs[sc["id"]]=D
feas=[]
for sc in sc_list:
    D=all_runs[sc["id"]]
    import collections
    cnt=collections.Counter(vv for d in D for vv in d["violations"])
    feas.append(dict(scenario_id=sc["id"],designs_evaluated=len(D),designs_feasible=sum(d["feasible"] for d in D),feasible_fraction=sum(d["feasible"] for d in D)/len(D),
        constraint_violation_counts_over_all_designs=dict(cnt),delta_v_m_s=sc["dv_ms"],note="Counts overlap (one design may violate several constraints)."))
W("analysis/feasibility_analysis.json",dict(scenarios=feas,method="exhaustive enumeration, see optimization/optimization_models.json"))

# ---------------- optimization outputs ----------------
exp=[]; pareto_out=[]; confs=[]
for sc in sc_list:
    D=all_runs[sc["id"]]
    for k,(nm,f,sg) in O.OBJECTIVES.items():
        b=O.solve(D,k)
        exp.append(dict(id=f"opt_{sc['id']}_{k}",scenario_id=sc["id"],objective=k,objective_name=nm,objective_field=f,sense="minimize" if sg==1 else "maximize",
            feasibility_status="feasible_optimum_found" if b else "infeasible",solver="exhaustive enumeration (deterministic; ties: cost, mass, design string)",
            optimality_claim="global optimum within the finite catalog and model; NOT a claim about all possible spacecraft",
            objective_value=(b[f] if b else None),result=({kk:vv for kk,vv in b.items() if kk!="design"} if b else None),selected_components=(b["design"] if b else None),
            input_dataset_version=VERSION,seed=None,data_class="derived",inputs_data_class="estimated+fictional"))
    b=O.balanced(D)
    exp.append(dict(id=f"opt_{sc['id']}_balanced",scenario_id=sc["id"],objective="balanced",objective_name="Balanced compromise (equal-weight normalized L2 distance to utopia in mass, cost, science)",
        sense="minimize",feasibility_status="feasible_optimum_found" if b else "infeasible",solver="exhaustive enumeration",optimality_claim="optimal for the stated scalarization only",
        objective_value=None,result=({kk:vv for kk,vv in b.items() if kk!="design"} if b else None),selected_components=(b["design"] if b else None),input_dataset_version=VERSION,seed=None,data_class="derived",inputs_data_class="estimated+fictional"))
    fr=O.pareto(D); pareto_out.append(dict(scenario_id=sc["id"],objectives=["wet_kg (min)","cost (min)","science (max)"],front_size=len(fr),
        points=[dict(wet_kg=d["wet_kg"],cost=d["cost"],science=d["science"],link_margin_db=d["link_margin_db"],design=d["design"]) for d in sorted(fr,key=lambda d:d["wet_kg"])],note="Non-dominated feasible designs (duplicates by objective tuple removed)."))
# sensitivity (one-at-a-time, re-optimization)
def run(Gp,scp):
    D=O.enumerate_designs(Gp,scp); return D
def summ(D):
    f=[d for d in D if d["feasible"]]
    if not f: return dict(feasible=0,min_mass=None,min_cost=None,max_science=None)
    return dict(feasible=len(f),min_mass=min(d["wet_kg"] for d in f),min_cost=min(d["cost"] for d in f),max_science=max(d["science"] for d in f))
sens=[]
perturbs=[("mga","mass growth allowance",lambda g,s,x:g.update(mga=x),[0.10,0.30]),
          ("dv_margin","delta-v margin",lambda g,s,x:g.update(dv_margin=x),[0.0,0.10]),
          ("power_margin","power margin",lambda g,s,x:g.update(power_margin=x),[0.05,0.25]),
          ("launch_margin","launch capacity margin",lambda g,s,x:g.update(launch_margin=x),[0.0,0.2]),
          ("budget_scale","budget x",lambda g,s,x:s.update(budget=s["budget"]*x),[0.8,1.2]),
          ("gt_shift_db","ground G/T shift (dB)",lambda g,s,x:s.update(gt_db={k:v+x for k,v in s["gt_db"].items()}),[-3,3]),
          ("distance_scale","comm distance x",lambda g,s,x:s.update(dist_m=s["dist_m"]*x),[0.5,1.5]),
          ("dv_scale","mission delta-v x",lambda g,s,x:s.update(dv_ms=s["dv_ms"]*x),[0.9,1.1])]
for sc in sc_list:
    base=summ(all_runs[sc["id"]])
    for key,desc,fn,vals in perturbs:
        for x in vals:
            g=copy.deepcopy(G); s=copy.deepcopy(sc); fn(g,s,x); r=summ(run(g,s))
            sens.append(dict(scenario_id=sc["id"],parameter=key,description=desc,value=x,baseline=base,result=r,
                delta_min_mass_pct=(100*(r["min_mass"]-base["min_mass"])/base["min_mass"] if r["min_mass"] and base["min_mass"] else None),
                delta_min_cost_pct=(100*(r["min_cost"]-base["min_cost"])/base["min_cost"] if r["min_cost"] and base["min_cost"] else None),
                delta_max_science_pct=(100*(r["max_science"]-base["max_science"])/base["max_science"] if r["max_science"] and base["max_science"] else None)))
# Monte Carlo on balanced + max_science designs
rng=random.Random(20261106); mc=[]
catmap=dict(arrays={a["id"]:a for a in O.ARRAYS},bats={a["id"]:a for a in O.BATTERIES},comps={a["id"]:a for a in O.COMPUTERS},comms={a["id"]:a for a in O.COMMS},props={a["id"]:a for a in O.PROPS})
def eval_design(Gp,sc,dsg):
    sel=[ [i["id"] for i in sc["instruments"]].index(x) for x in dsg["instruments"]]
    return O.evaluate(Gp,sc,sel,catmap["comps"][dsg["computer"]],catmap["comms"][dsg["comm"]],catmap["arrays"][dsg["array"]],catmap["bats"][dsg["battery"]],catmap["props"][dsg["propulsion"]],[v for v in sc["vehicles"] if v["id"]==dsg["vehicle"]][0])
N=2000
for sc in sc_list:
    D=all_runs[sc["id"]]
    for label,b in (("balanced",O.balanced(D)),("max_science",O.solve(D,"max_science")),("max_feasibility_margin",O.solve(D,"max_feasibility_margin"))):
        if not b: continue
        ok=0; wets=[]; costs=[]; reasons=collections.Counter()
        for _ in range(N):
            g=copy.deepcopy(G); s=copy.deepcopy(sc)
            g["mga"]=rng.uniform(0.10,0.35); g["dv_margin"]=rng.uniform(0.0,0.10); g["power_margin"]=rng.uniform(0.05,0.25)
            sh=rng.gauss(0,1.5); s["gt_db"]={k:v+sh for k,v in s["gt_db"].items()}
            s["dv_ms"]*=rng.triangular(0.95,1.10,1.0)
            r=eval_design(g,s,b["design"])
            cscale=rng.triangular(0.9,1.4,1.0)   # cost growth is asymmetric
            hw_cost=r["cost"]*cscale
            fails=[v for v in r["violations"] if v!="exceeds_budget"]
            if hw_cost>s["budget"]: fails.append("exceeds_budget")
            for v in fails: reasons[v]+=1
            if not fails: ok+=1
            wets.append(r["wet_kg"]); costs.append(hw_cost)
        mc.append(dict(scenario_id=sc["id"],design_label=label,design=b["design"],samples=N,seed=20261106,p_feasible=ok/N,wet_kg_mean=statistics.mean(wets),wet_kg_p95=sorted(wets)[int(.95*N)],cost_mean=statistics.mean(costs),cost_p95=sorted(costs)[int(.95*N)],
            failure_reason_counts=dict(reasons),
            distributions="mga~U(0.10,0.35); dv_margin~U(0,0.10); power_margin~U(0.05,0.25); G/T shift~N(0,1.5 dB); dv scale~Tri(0.95,1.10,1.0); cost scale~Tri(0.9,1.4,1.0) (asymmetric cost growth, assumed)",data_class="estimated"))
W("optimization/sensitivity_results.json",dict(method="One-at-a-time perturbation with full re-optimization (exhaustive)",results=sens))
W("analysis/uncertainty_analysis.json",dict(method="Monte Carlo, fixed design under parameter uncertainty",results=mc,note="Distributions are assumptions, not measured uncertainties of source data."))
W("optimization/pareto_frontiers.json",dict(results=pareto_out))
W("optimization/optimized_configurations.json",meta("optimized_configurations","Optimization experiments (27 = 3 scenarios x 9 formulations)",exp))
# models + constraints
models=dict(schema_version=VERSION,formulation="Discrete design selection with analytic sizing; maximize/minimize single objective subject to constraints; exhaustive enumeration of catalog product.",
  decision_variables=["instrument subset (binary per instrument, at least one)","flight computer","comm antenna/transmitter","solar array technology","battery technology","propulsion type","launch vehicle"],
  derived_variables=["array BOL power","battery Wh","propellant mass (rocket equation with tank fraction)","wet mass","cost","science (min(1, downlink/generated) x sum of weights)","link rate"],
  objectives={k:dict(name=v[0],field=v[1],sense="minimize" if v[2]==1 else "maximize") for k,v in O.OBJECTIVES.items()},
  equations=["MR = exp(dv*(1+dv_margin)/(Isp*g0))","m_prop = m_dry*(MR-1)/(1-tank_frac*(MR-1)); wet = dry + tank_frac*m_prop + m_prop","P_arr_EOL = P_avg*(1+T_ecl/(T_day*eta_bat))*(1+margin); P_BOL = P_EOL/(1-deg*life)","array mass = (P_BOL*r^2/..) / sp (flux scaling 1/r^2)","battery Wh = P_avg*T_ecl/(DoD*eta)","dry = (sum subsystems + structure_frac + thermal_frac + array + battery)*(1+MGA)","R = min(caps, 10^((EIRP+G/T-FSPL-L+228.6-EbN0-margin)/10))","cost = hardware*(1+integration) + launch"],
  not_modeled=["thermal balance beyond fixed fraction/heater","reliability / redundancy (no evidence-based reliability data collected)","attitude control detail","launch fairing volume","trajectory/launch-window timing","peak vs average power coincidence","eclipse seasonal variation","NASA cost models"],
  solver=dict(name="exhaustive enumeration",seed=None,settings="deterministic; Python implementation tools/opt_model.py; JavaScript port in docs/app.js"),
  method_notes=dict(pareto="non-dominated filter on (wet mass, cost, -science)",sensitivity="OAT with re-optimization",monte_carlo="seed 20261106, 2000 samples per design",
     why_not_LP_MILP="Sizing equations are nonlinear (exponential rocket equation, log link budget); the catalog is small enough for exact enumeration which also yields Pareto sets without solver assumptions."))
W("optimization/optimization_models.json",models)
cons=dict(global_parameters=G,global_parameter_data_class="estimated (design practice assumptions; margins are conventional values, not retrieved from a standard)",
   catalog=dict(arrays=O.ARRAYS,batteries=O.BATTERIES,computers=O.COMPUTERS,comms=O.COMMS,propulsion=O.PROPS),scenarios=sc_list,
   cost_note="Costs in 'credits' are FICTIONAL, except launch costs where basis says published price/10,000 USD.",
   science_note="Instrument 'value' is a fictional educational weight (1-10) expressing relative contribution to the scenario objective set; it is not a measured science metric.")
W("optimization/optimization_constraints.json",cons)

# engineering constraints (derived from records): >= 50
ec=[]
for v in vehicles:
    for p in v["payloads"]: ec.append(dict(id=f"c_payload_{v['id']}_{p['orbit']}_{p['mode'].split()[0]}",type="mass",statement=f"Payload to {p['orbit']} <= {p['payload_kg']} kg on {v['name']} ({p['mode']})",bound_kg=p["payload_kg"],conditions_complete=p["altitude_km"] is not None and p["inclination_deg"] is not None,data_class="unverified"))
for e in engines:
    if e["thrust_vac_n"] and e["dry_mass_kg"]: ec.append(dict(id=f"c_twr_{e['id']}",type="propulsion",statement=f"{e['name']} engine thrust/weight (vac) = {e['derived']['engine_thrust_to_weight_vac']:.1f}",data_class="derived"))
for e in elec: ec.append(dict(id=f"c_power_{e['id']}",type="power",statement=f"{e['name']} requires ~{e['power_w']} W at recorded operating point",bound_w=e["power_w"],data_class="unverified"))
for s in sc_list:
    ec.append(dict(id=f"c_dv_{s['id']}",type="delta_v",statement=f"{s['name']}: onboard delta-v {s['dv_ms']:.0f} m/s (+{G['dv_margin']*100:.0f}% margin)",data_class="derived" if "derived" in s["dv_basis"] else "estimated"))
    ec.append(dict(id=f"c_ecl_{s['id']}",type="power",statement=f"Max eclipse {s['eclipse_s']/60:.1f} min per {s['period_s']/60:.1f} min orbit",data_class="derived"))
    ec.append(dict(id=f"c_rad_{s['id']}",type="radiation",statement=f"Computer tolerance >= {s['dose_krad']*G['rad_design_margin']:.0f} krad (dose {s['dose_krad']} x RDM {G['rad_design_margin']})",data_class="estimated"))
    ec.append(dict(id=f"c_budget_{s['id']}",type="budget",statement=f"Total cost <= {s['budget']} credits",data_class="fictional"))
for k,v in G.items(): ec.append(dict(id=f"c_global_{k}",type="margin_or_assumption",statement=f"{k} = {v}",data_class="estimated"))
for b in ["venus","mars","jupiter"]:
    ec.append(dict(id=f"c_flux_{b}",type="power",statement=f"Solar flux at {b} = {1361.0/(BODY[b]['semi_major_axis_m']/1e3/AU_KM)**2:.0f} W/m2",data_class="derived"))
W("missions/engineering_constraints.json",meta("engineering_constraints","Constraint statements derived from the datasets and scenarios",ec))

# ---------------- metadata ----------------
used=set()
for coll in (spx,fac,launch_sites,planets,moons,asteroids,atm,engines,propellants,vehicles,stages,boosters,comps,ins,ground,optical,missions,payload_caps,elements): 
    for r in coll: used.update(r.get("source_ids",[]))
for s in sources: s["used_by_records"]= s["id"] in used
if VER:
    import collections as _c
    used_src=_c.defaultdict(set)
    for c in VER["checks"]+[dict(x,file=x["file"]) for x in (VERL["checks"] if VERL else []) if x["status"] in ("verified","conflict","added_from_source")]:
        if c["status"]!="not_recorded": used_src[c["source_id"]].add((c["url"],c["retrieved"],c.get("source_sha256") or MAN.get(c["file"],{}).get("sha256")))
    for s in sources:
        if s["id"] in used_src:
            s["retrieved"]=True; s["retrieval_date"]=max(r for _,r,_ in used_src[s["id"]]); s["retrieved_pages"]=[dict(url=u,retrieved=r,sha256=h) for u,r,h in sorted(used_src[s["id"]])]
            s["page_or_section"]="see field_verification on each record"; s["note"]="Pages retrieved and parsed; each value comparison is stored in metadata/verification_celestial.json and in the record's field_verification."
W("metadata/sources.json",meta("sources","Source catalog (none retrieved this build)",sources))
# units
W("metadata/units.json",dict(si_base=dict(mass="kg",length="m",time="s",force="N",power="W",energy="J (or Wh where named)",temperature="K",velocity="m/s",isp="s",mu="m^3/s^2 (also km^3/s^2 in gravitational_parameter_km3_s2)",irradiance="W/m^2",magnetic_field="T",pressure="Pa"),
   conventions=["Field names carry unit suffixes (_kg, _m, _n, _w, _s, _m_s, _km3_s2).","null means not recorded; never zero-filled.","Angles in degrees.","credits = fictional game currency."]))
# data dictionary (auto from field names)
dd={}
for fn,coll in (("planets",planets),("moons",moons),("rocket_engines",chem),("electric_propulsion",elec),("launch_vehicles",vehicles),("rocket_stages",stages),("components",comps),("instruments",ins),("historical_missions",missions)):
    dd[fn]=sorted({k for r in coll for k in r.keys()})
W("metadata/data_dictionary.json",dict(common_fields=dict(data_class="verified|derived|estimated|fictional|unverified",confidence="subjective recall confidence: high|medium|low",source_ids="ids into metadata/sources.json (where the figure is expected to be verifiable)",retrieval_status="not_retrieved in this build",derived="values computed by tools/ from recorded inputs; see derived_from"),fields_per_dataset=dd))
# completeness + counts
def completeness(coll,fields):
    out={}
    for f in fields:
        n=sum(1 for r in coll if r.get(f) is not None); out[f]=round(100*n/len(coll),1)
    return out
counts=dict(celestial_bodies=len(planets)+len(moons)+len(asteroids),engines_and_propulsion=len(engines),launch_vehicles=len(vehicles),stages_and_boosters=len(stages)+len(boosters),spacecraft_components=len(comps),
   instruments=len(ins),historical_missions=len(missions),spacex_launch_records=len(spx),nasa_facilities=len(fac),nasa_antenna_facilities=len(fan_ant:=[r for r in fac if r['antenna']]),launch_sites=len(launch_sites),ground_comm_systems=len(ground)+len(optical),engineering_constraints=len(ec),optimization_examples=len(exp))
targets=dict(celestial_bodies=40,engines_and_propulsion=40,launch_vehicles=20,stages_and_boosters=40,spacecraft_components=100,instruments=50,historical_missions=30,ground_comm_systems=15,engineering_constraints=50,optimization_examples=20)
all_recs=planets+moons+asteroids+chem+elec+vehicles+stages+boosters+comps+ins+missions+ground+spx+fac+launch_sites
cls=collections.Counter(r.get("data_class") for r in all_recs)
quality=dict(build_date=BUILD_DATE,version=VERSION,retrieval=dict(sources_listed=len(sources)-1,sources_retrieved=sum(1 for x in sources if x.get("retrieved") is True),reason="Retrieved: JPL SSD planetary/satellite physical parameters, JPL approximate planet elements, JPL SBDB API, NASA NSSDC fact sheets, NASA SLS page, NASA Apollo 11 press kit and three NTRS electric-propulsion documents, ULA Atlas V/Vulcan pages and the ESA Vega-C page (see metadata/sources.json). Not retrievable or not stating the numbers: SpaceX pages (JavaScript-rendered), api.spacexdata.com (HTTP 522), Rocket Lab, Aerojet Rocketdyne (403), Blue Origin (429), Arianespace manual; those records remain unverified."),
   record_counts=counts,targets=targets,target_attainment_pct={k:round(100*counts[k]/targets[k],1) for k in counts if k in targets},
   data_class_counts=dict(cls),verified_records=cls.get("verified",0),launch_field_checks=(dict(total=len(VERL["checks"]),verified=sum(1 for c in VERL["checks"] if c["status"]=="verified"),conflicts_resolved_to_source=sum(1 for c in VERL["checks"] if c["status"]=="conflict"),added_from_source=sum(1 for c in VERL["checks"] if c["status"]=="added_from_source"),source_text_not_found=sum(1 for c in VERL["checks"] if c["status"]=="source_text_not_found")) if VERL else None),field_checks=(dict(total=len(VER["checks"]),verified=sum(1 for c in VER["checks"] if c["status"]=="verified"),conflicts_resolved_to_source=sum(1 for c in VER["checks"] if c["status"]=="conflict" and c.get("primary",True) and not c["field"].startswith("derived."))) if VER else None),
   statement=(f"{cls.get('verified',0)} records are verified (25 celestial bodies at core level; engines and stages whose core numeric fields were all checked) against retrieved JPL, NASA (NTRS, SLS page, Apollo 11 press kit), ULA and ESA pages. {sum(1 for c in VER['checks'] if c['status']=='verified')} celestial and {sum(1 for c in VERL['checks'] if c['status']=='verified')} launch/engine field checks matched; {sum(1 for c in VER['checks'] if c['status']=='conflict' and c.get('primary',True) and not c['field'].startswith('derived.'))} celestial and {sum(1 for c in VERL['checks'] if c['status']=='conflict')} launch/engine recalled values were wrong or outdated and were replaced by the sourced value. Launch vehicles are verified field by field only (see verified_field_count); everything not checked (e.g. Falcon, Starship, Electron, Ariane, most engines, spacecraft components, instruments, missions) is still unverified, as are two user-supplied tables. Derived values inherit the status of their inputs. Optimization catalog values are estimated/fictional.") if VER and VERL else "NO record is verified.",
   completeness_pct=dict(engines=completeness(engines,["thrust_vac_n","thrust_sl_n","isp_vac_s","isp_sl_s","dry_mass_kg","burn_s"]),vehicles=completeness(vehicles,["liftoff_mass_kg","thrust_sl_n","price_usd","fairing_diam_m","height_m"]),
        instruments=completeness(ins,["mass_kg","power_w"]),missions=completeness(missions,["launch_mass_kg","dry_mass_kg","cost_musd_nominal"]),moons=completeness(moons,["rotation_period_h"]),components=completeness(comps,["mass_kg","power_consumption_w","power_generation_w","energy_capacity_wh"])),
   conflicts_resolved=[dict(record_id=c["record_id"],field=c["field"],recalled_value=c["mine_original"],source_value=c["source_value"],source_id=c["source_id"],source_text=c["source_original_text"],url=c["url"]) for c in (VER["checks"] if VER else []) if c["status"]=="conflict" and c.get("primary",True) and not c["field"].startswith("derived.")],
   known_conflicts=[dict(topic="SpaceX launch table coverage",note="User-supplied file ends at flight 56 (2018-06-04); 57 rows. Reliability (56/57) and landing statistics describe the 2010-2018 development era only and must not be extrapolated to Block 5. Origin/license of the Kaggle-derived file is unverified."),dict(topic="NASA facilities table",note="86 rows lack a status, 1 status is the truncated value 'Under' (assumed Under Rehabilitation), 340 lack URLs, and 256 of 485 fall into the 'other' category of the keyword classifier (category is derived, unreviewed)."),dict(topic="CCAFS LC-40 vs SLC-40",note="Launch-site strings differ across rows; treated as the same pad (assumption)."),dict(topic="Deimos GM vs mass",note="Recorded GM (9.62e-5 km3/s2) and mass (1.4762e15 kg) disagree by ~2.4% via GM=G*M; both retained, GM preferred for orbital use; resolve against JPL SSD sat_phys_par."),dict(topic="Small-body surface gravity",note="For irregular bodies (Phobos, Deimos, Bennu, Enceladus) g=mu/R^2 is a spherical approximation; recorded g is a mean/typical value and is not verified."),dict(topic="Saturn V liftoff thrust",values=["~33.4 MN (design)","~34.5-35.1 MN (flight-reported)"],preferred="33.4 MN design value recorded; flight values vary by mission"),
        dict(topic="Falcon 9 mass accounting",note="Recorded liftoff mass minus recorded stage masses leaves ~31 t, more than payload+fairing implies; at least one input (stage dry mass or liftoff mass) is likely off. See analysis/mass_analysis.json."),
        dict(topic="Electron stage masses",note="Recorded stage dry+propellant masses sum exactly to liftoff mass, leaving no room for payload/fairing; ideal dv in propulsion_analysis (~11.6-12 km/s) is therefore an overestimate and not a credible ascent number. Needs retrieval of the payload user's guide."),
        dict(topic="SLS stack ideal delta-v",note="Core-stage-only accounting (boosters excluded); stack residual is dominated by booster/upper-stage mass, so the ideal-dv total is not a vehicle capability."),
        dict(topic="Mission launch vehicle variants",note="Several missions flew Atlas V 401/411/541 variants not in the launch dataset; launch_vehicle_id is null for them.")],
   missing_categories=["hybrid rocket motors","most reaction wheels / star trackers as named products with specs","magnetometers/seismometers/mass spectrometers beyond SAM","optical comm hardware specs","radiation environment per body","terrain characteristics","per-field provenance with page numbers and original units/measurements (not available without retrieval)"],
   validations_run="see validation_report.json (generated by tools/validate.py)")
W("metadata/quality_report.json",quality)
# provenance: record-level
prov=[]
for fn,coll in (("celestial",planets+moons+asteroids),("propulsion",engines),("launch",vehicles+stages+boosters),("spacecraft",comps),("instruments",ins),("missions",missions),("launch_history",spx),("infrastructure",fac)):
    for r in coll: prov.append(dict(record_id=r.get("id"),dataset=fn,data_class=r.get("data_class"),confidence=r.get("confidence"),source_ids=r.get("source_ids"),retrieval_status="not_retrieved",retrieval_date=None,original_value="not separately stored (recalled; SI-converted at write time)",verification_status="unverified" if r.get("data_class")!="estimated" else "estimated",derived_fields=list(r.get("derived",{}).keys()) if isinstance(r.get("derived"),dict) else []))
W("metadata/provenance.json",meta("provenance","Record-level provenance",prov))

# ---------------- combined ----------------
comp_unique={}
for c in comps: comp_unique[c["id"]]=c
combined=dict(schema_version=VERSION,generated=BUILD_DATE,note="Generated by tools/build.py from the individual datasets; no duplicate ids within a collection.",
  celestial=dict(planets=planets,moons=moons,asteroids=asteroids,orbital_elements=elements,atmospheres=atm),
  propulsion=dict(rocket_engines=chem,electric_propulsion=elec,propellants=propellants),
  launch=dict(launch_vehicles=vehicles,rocket_stages=stages,boosters=boosters,payload_capabilities=payload_caps),
  spacecraft=dict(components=list(comp_unique.values()),ground_stations=ground,optical_demonstrations=optical),
  instruments=ins,missions=dict(historical=missions,profiles=profiles,requirements=reqs,trajectory_reference=traj,engineering_constraints=ec),
  analysis=dict(mass=mass,propulsion=prop,power=power,communications=comm,feasibility=feas),
  optimization=dict(models=models,constraints=cons,experiments=exp,pareto=pareto_out,sensitivity=sens,uncertainty=mc),
  launch_history=dict(launches=spx,sites=launch_sites,analysis=spx_an),infrastructure=dict(nasa_facilities=fac,analysis=fac_an),
  verification=dict(celestial=VER,launch=VERL,retrieved_files=list(MAN.values())),
  metadata=dict(sources=sources,quality=quality))
W("combined/all_space_mission_data.json",combined)
# website copy
os.makedirs(os.path.join(ROOT,"..","docs","data"),exist_ok=True)
import shutil; shutil.copy(os.path.join(ROOT,"combined","all_space_mission_data.json"),os.path.join(ROOT,"..","docs","data","all_space_mission_data.json"))
print("built", counts)
