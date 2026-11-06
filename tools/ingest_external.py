"""Normalizes user-supplied external files (data_raw/) into dataset records + analysis. Pure stdlib, deterministic."""
import csv, re, os, math, statistics, collections, hashlib, datetime
HERE=os.path.dirname(os.path.abspath(__file__)); RAW=os.path.join(HERE,"..","data_raw")
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def wilson(k,n,z=1.96):
    p=k/n; d=1+z*z/n; c=p+z*z/(2*n); h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return (c-h)/d,(c+h)/d
SITE={"CCAFS LC-40":"ccsfs_slc40","CCAFS SLC-40":"ccsfs_slc40","VAFB SLC-4E":"vsfb_slc4e","KSC LC-39A":"ksc_lc39a"}
ORB=[("Heliocentric","heliocentric"),("Sun","sun_earth_l1"),("Polar LEO","polar_leo"),("LEO (ISS)","leo_iss"),("LEO","leo"),("GTO","gto"),("SSO","sso"),("HEO","heo")]
def orbit_class(s):
    for k,v in ORB:
        if s.startswith(k): return v
    return None
def parse_landing(s):
    parts=[p.strip() for p in re.split(r",\s*(?=(?:Success|Failure|No attempt|Controlled|Uncontrolled|Precluded))",s)]
    out=[]
    for p in parts:
        m=re.match(r"(Success|Failure|No attempt|Controlled|Uncontrolled|Precluded)\s*(?:\(([^)]*)\))?",p)
        res,loc=(m.group(1),(m.group(2) or "").strip()) if m else (None,None)
        kind={"ground pad":"ground_pad","drone ship":"drone_ship","ocean":"ocean","parachute":"parachute"}.get(loc,None)
        out.append(dict(raw=p,result=(res or "").lower().replace(" ","_") or None,location=kind))
    return out
def spacex():
    p=os.path.join(RAW,"spacex_launch_data.csv"); rows=list(csv.DictReader(open(p,newline="",encoding="utf-8")))
    recs=[]
    for r in rows:
        fn=r["Flight Number"].strip(); rid="spx_fh%02d"%int(fn.split()[1]) if fn.startswith("FH") else "spx_f%03d"%int(fn)
        bv=r["Booster Version"]; fam=re.match(r"\s*(F9 (?:v1\.0|v1\.1|FT|B4|B5))",bv); serials=re.findall(r"B\d{4}(?:\.\d)?",bv)
        family="FH" if fn.startswith("FH") else (fam.group(1) if fam else None)
        raw_m=r["Payload Mass (kg)"].strip(); approx=raw_m.startswith("~"); mm=re.sub(r"[~,\s]","",raw_m)
        mass=float(mm) if re.fullmatch(r"\d+(\.\d+)?",mm) else None
        t=r["Time (UTC)"].strip(); hh,mi,*ss=t.split(":"); t="%02d:%s:%s"%(int(hh),mi,ss[0] if ss else "00")
        mo=r["Mission Outcome"].strip(); mon="success_payload_unclear" if "unclear" in mo else ("failure_in_flight" if mo.startswith("Failure") else ("success" if mo.startswith("Success") else None))
        land=parse_landing(r["Landing Outcome"].strip()); att=[l for l in land if l["result"] in("success","failure") and l["location"] in("ground_pad","drone_ship")]
        reflight=None
        if serials and "." in serials[0]: reflight=int(serials[0].split(".")[1])
        recs.append(dict(id=rid,flight_label=fn,date_utc=r["Date"],time_utc=t,booster_family=family,booster_serials=serials,booster_version_raw=" ".join(bv.split()),
            launch_site_raw=r["Launch Site"],launch_site_id=SITE.get(r["Launch Site"].strip()),payload=" ".join(r["Payload"].split()),payload_mass_kg=mass,payload_mass_approximate=approx,payload_mass_raw=raw_m or None,
            orbit_raw=r["Orbit"].strip(),orbit_class=orbit_class(r["Orbit"].strip()),customer_raw=" ".join(r["Customer"].split()),mission_outcome_raw=" ".join(mo.split()),mission_outcome=mon,
            landing_outcome_raw=" ".join(r["Landing Outcome"].split()),landings=land,landing_attempts=len(att),landing_successes=sum(1 for l in att if l["result"]=="success"),
            booster_flight_number=(reflight if reflight else (1 if serials else None)),
            record_type="historical",data_class="unverified",confidence="medium",source_ids=["S36"],retrieval_status="user_supplied_not_independently_verified"))
    return recs,sha(p)
def spacex_analysis(recs):
    n=len(recs); ok=sum(1 for r in recs if r["mission_outcome"] in("success","success_payload_unclear")); lo,hi=wilson(ok,n)
    by_year=collections.OrderedDict()
    for r in recs:
        y=r["date_utc"][:4]; d=by_year.setdefault(y,dict(launches=0,landing_attempts=0,landing_successes=0)); d["launches"]+=1; d["landing_attempts"]+=r["landing_attempts"]; d["landing_successes"]+=r["landing_successes"]
    for d in by_year.values(): d["landing_success_rate"]=(d["landing_successes"]/d["landing_attempts"]) if d["landing_attempts"] else None
    fam=collections.Counter(r["booster_family"] for r in recs)
    orb={}
    for r in recs:
        if r["payload_mass_kg"] is not None: orb.setdefault(r["orbit_class"],[]).append(r["payload_mass_kg"])
    orbs={k:dict(n=len(v),min_kg=min(v),median_kg=statistics.median(v),max_kg=max(v),mean_kg=statistics.mean(v)) for k,v in orb.items()}
    la=sum(r["landing_attempts"] for r in recs); ls=sum(r["landing_successes"] for r in recs)
    lalo,lahi=wilson(ls,la) if la else (None,None)
    reused=sum(1 for r in recs if r["booster_flight_number"] and r["booster_flight_number"]>1)
    return dict(source_ids=["S36"],data_class="derived",inputs_data_class="unverified",coverage=dict(first=recs[0]["date_utc"],last=recs[-1]["date_utc"],launches=n,caveat="File ends at flight 56 (2018-06-04); later launches, Block 5 maturity and all reuse statistics after mid-2018 are absent. Do not extrapolate."),
      mission_reliability=dict(successes=ok,launches=n,point_estimate=ok/n,wilson95_low=lo,wilson95_high=hi,definition="success or success (payload status unclear) over all rows; one in-flight failure (CRS-7)",scope="Falcon 9 / Falcon Heavy, 2010-2018 only"),
      launches_by_year=by_year,booster_family_counts=dict(fam),
      landing=dict(attempts=la,successes=ls,success_rate=ls/la if la else None,wilson95_low=lalo,wilson95_high=lahi,definition="ground-pad or drone-ship attempts only; ocean tests and parachute recoveries excluded"),
      reflown_rows=dict(count=reused,fraction=reused/n,definition="rows whose booster serial carries a '.N' suffix with N>1"),
      payload_mass_by_orbit_class=orbs,mass_unknown_rows=sum(1 for r in recs if r["payload_mass_kg"] is None))
SITES=[dict(id="ccsfs_slc40",name="Cape Canaveral SFS Space Launch Complex 40",lat=28.5619,lon=-80.5773,operator_note="listed as 'CCAFS LC-40' then 'CCAFS SLC-40' in the file; treated as the same pad (assumption)"),
       dict(id="ksc_lc39a",name="Kennedy Space Center Launch Complex 39A",lat=28.6082,lon=-80.6041,operator_note="NASA KSC"),
       dict(id="vsfb_slc4e",name="Vandenberg SFB Space Launch Complex 4 East",lat=34.632,lon=-120.611,operator_note="polar/SSO launches")]
def sites(recs):
    out=[]
    for s in SITES:
        rs=[r for r in recs if r["launch_site_id"]==s["id"]]
        out.append(dict(s,launches_in_file=len(rs),first_launch=min(r["date_utc"] for r in rs),last_launch=max(r["date_utc"] for r in rs),orbit_classes=sorted({r["orbit_class"] for r in rs}),
            data_class="unverified",confidence="low",source_ids=["S36","S39"],retrieval_status="not_retrieved",note="Coordinates recalled to ~0.01 deg, not retrieved; launch counts from user file."))
    return out
CAT=[("antenna_ground_station",r"antenna|ground station|tracking|telemetry|deep space"),("wind_tunnel",r"wind tunnel|tunnel|shock tube|arc jet|arc-jet|ballistic"),("thermal_vacuum",r"vacuum|thermal vac|space environment|solar simulat"),
     ("propulsion_test",r"test stand|engine|propulsion|rocket|combustion|propellant"),("launch_infrastructure",r"launch|pad\b|crawler|vehicle assembly|mobile launcher|runway|shuttle|landing"),("acoustic_vibration_structural",r"acoustic|vibration|structur|fatigue|load|sonic|impact"),
     ("materials_lab",r"material|chemical|metallurg|lab\b|laborator")]
def category(name):
    for c,rx in CAT:
        if re.search(rx,name,re.I): return c
    return "other"
def d(s):
    s=s.strip()
    if not s: return None
    return datetime.datetime.strptime(s,"%m/%d/%Y %I:%M:%S %p").date().isoformat()
def facilities():
    p=os.path.join(RAW,"NASA_Facilities.csv"); rows=list(csv.DictReader(open(p,newline="",encoding="utf-8-sig")))
    recs=[]; seen=collections.Counter()
    for i,r in enumerate(rows,1):
        m=re.match(r"^\s*(\S*)\s*\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)\s*$",r["Location"]); lat=float(m.group(2)) if m else None; lon=float(m.group(3)) if m else None
        name=" ".join(r["Facility"].split()); st=r["Status"].strip()
        stn={"Active":"active","Inactive":"inactive","Under Rehabilitation":"under_rehabilitation","Under":"under_rehabilitation"}.get(st,None)
        cat=category(name); ant=None
        if cat=="antenna_ground_station":
            dm=re.search(r"(\d+(?:\.\d+)?)\s*m\b",name,re.I); bd=re.search(r"\b(S|X|Ka|Ku|C|L|UHF|VHF)[- ]?band",name,re.I)
            ant=dict(diameter_m=float(dm.group(1)) if dm else None,band=bd.group(1) if bd else None)
        key=hashlib.sha1(("|".join([r["Center"],name,r["City"]])).encode()).hexdigest()[:6]; seen[key]+=1
        recs.append(dict(id="nf_%04d"%i,center=r["Center"].strip(),facility=name,category=cat,category_basis="keyword rules on facility name (derived, may be wrong)",status=stn,status_raw=st or None,
            occupied_date=d(r["Occupied"]),record_date=d(r["Record Date"]),last_update=d(r["Last Update"]),url=(r["URL Link"].strip() or None),city=r["City"].strip() or None,state=r["State"].strip() or None,zipcode=r["Zipcode"].strip() or None,
            lat=lat,lon=lon,location_raw=r["Location"],antenna=ant,duplicate_key=key,data_class="unverified",confidence="medium",source_ids=["S37"],retrieval_status="user_supplied_not_independently_verified"))
    dup=[k for k,v in seen.items() if v>1]
    for r in recs: r["possible_duplicate"]=r["duplicate_key"] in dup
    return recs,sha(p)
def fac_analysis(recs):
    c=collections.Counter
    return dict(source_ids=["S37"],data_class="derived",inputs_data_class="unverified",records=len(recs),by_center=dict(c(r["center"] for r in recs).most_common()),by_category=dict(c(r["category"] for r in recs).most_common()),
        by_status=dict(c((r["status"] or "not_recorded") for r in recs).most_common()),by_state=dict(c(r["state"] for r in recs).most_common(15)),
        quality=dict(missing_status=sum(1 for r in recs if r["status"] is None),truncated_status_values=sum(1 for r in recs if r["status_raw"]=="Under"),missing_url=sum(1 for r in recs if not r["url"]),missing_occupied_date=sum(1 for r in recs if not r["occupied_date"]),
            possible_duplicates=sum(1 for r in recs if r["possible_duplicate"]),coords_parsed=sum(1 for r in recs if r["lat"] is not None),
            note="category is keyword-derived and unreviewed; 'other' is the fallback; status 'Under' is assumed to be a truncated 'Under Rehabilitation'."),
        antennas=[dict(id=r["id"],facility=r["facility"],center=r["center"],diameter_m=r["antenna"]["diameter_m"],band=r["antenna"]["band"],status=r["status"]) for r in recs if r["antenna"]])
