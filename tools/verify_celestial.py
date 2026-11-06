#!/usr/bin/env python3
"""Field-level verification of celestial data against RETRIEVED source files (data_raw/retrieved/).
Reads only local cached copies (treat as untrusted data; parsed with regex, never executed).
Output: space-mission-research/metadata/verification_celestial.json (+ data_raw/retrieved/MANIFEST.json).
Run `tools/fetch_sources.sh` first (network required)."""
import re, html, json, os, sys, hashlib, math, datetime
HERE=os.path.dirname(os.path.abspath(__file__)); RET=os.path.join(HERE,"..","data_raw","retrieved"); OUT=os.path.join(HERE,"..","space-mission-research","metadata")
sys.path.insert(0,HERE)
import data_celestial as DC
G=6.6743e-11   # CODATA 2018, the value JPL SSD states it used for mass values
AU_KM=149597870.7
def read(n): return open(os.path.join(RET,n),encoding="utf-8",errors="replace").read()
def tables(n):
    out=[]
    for tb in re.findall(r"<table.*?</table>",read(n),flags=re.S|re.I):
        rs=[]
        for tr in re.findall(r"<tr.*?</tr>",tb,flags=re.S|re.I):
            c=[re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",x))).strip() for x in re.findall(r"<t[dh].*?</t[dh]>",tr,flags=re.S|re.I)]
            if c: rs.append(c)
        out.append(rs)
    return out
def num(s):
    m=re.search(r"[-+]?\d[\d,]*\.?\d*(?:[eE][-+]?\d+)?",s.replace("−","-"));
    return float(m.group(0).replace(",","")) if m else None
def decimals(s):
    m=re.search(r"\.(\d+)",s); return len(m.group(1)) if m else 0
# ---- manifest
URLS={"jpl_planets_phys_par.html":"https://ssd.jpl.nasa.gov/planets/phys_par.html","jpl_sats_phys_par.html":"https://ssd.jpl.nasa.gov/sats/phys_par/","jpl_approx_pos.html":"https://ssd.jpl.nasa.gov/planets/approx_pos.html",
 "nssdc_sun.html":"https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html","nssdc_moon.html":"https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html","nssdc_pluto.html":"https://nssdc.gsfc.nasa.gov/planetary/factsheet/plutofact.html",
 "sbdb_bennu.json":"https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=101955&phys-par=1","sbdb_ceres.json":"https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=1&phys-par=1","sbdb_vesta.json":"https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=4&phys-par=1",
 "sbdb_pluto.json":"https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=134340&phys-par=1","sbdb_eris.json":"https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=136199&phys-par=1"}
URLS["nasa_sls_reference.html"]="https://www.nasa.gov/reference/space-launch-system/"
URLS.update({"ula_atlas_v.html":"https://www.ulalaunch.com/rockets/atlas-v","ula_vulcan.html":"https://www.ulalaunch.com/rockets/vulcan-centaur","esa_vega_c.html":"https://www.esa.int/Enabling_Support/Space_Transportation/Launch_vehicles/Vega-C",
 "esa_ariane6_overview.html":"https://www.esa.int/Enabling_Support/Space_Transportation/Launch_vehicles/Ariane_6_overview"})
for _n in ("1969-059A","1977-076A","2009-031A","2005-029A","2006-001A","2011-040A","2011-070A","2021-130A","2013-008A","2007-043A","2016-055A"): URLS[f"nmc/nmc_{_n}.html"]=f"https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id={_n}"
for _id in ("19690022248","19980017550","20090004685","20060051789"): URLS[f"ntrs_{_id}.pdf"]=f"https://ntrs.nasa.gov/api/citations/{_id}/downloads/{_id}.pdf"
for p in "mercury venus earth mars jupiter saturn uranus neptune".split(): URLS[f"nssdc_{p}.html"]=f"https://nssdc.gsfc.nasa.gov/planetary/factsheet/{p}fact.html"
SRCID={"jpl_planets_phys_par.html":"S02","jpl_sats_phys_par.html":"S03","jpl_approx_pos.html":"S04","sbdb":"S40"}
man=[]
for n,u in sorted(URLS.items()):
    p=os.path.join(RET,n)
    if os.path.exists(p): man.append(dict(file="data_raw/retrieved/"+n,url=u,bytes=os.path.getsize(p),sha256=hashlib.sha256(open(p,"rb").read()).hexdigest(),retrieved=datetime.datetime.fromtimestamp(os.path.getmtime(p),datetime.timezone.utc).strftime("%Y-%m-%d")))
json.dump(man,open(os.path.join(RET,"MANIFEST.json"),"w"),indent=1)
RETR={m["file"].split("/")[-1]:m["retrieved"] for m in man}
checks=[]
def chk(rid,field,mine,src,unit_note,orig,file,section,tol,sid,convert_note=None,exact=False):
    if src is None: return
    if mine is None: status="not_recorded"
    else:
        rel=abs(mine-src)/abs(src) if src else abs(mine-src)
        status="verified" if rel<=tol else "conflict"
    checks.append(dict(record_id=rid,field=field,mine_original=mine,source_value=src,source_original_text=orig,source_unit=unit_note,conversion=convert_note,source_id=sid,
        url=URLS[file],file="data_raw/retrieved/"+file,retrieved=RETR.get(file),section=section,tolerance_rel=tol,status=status))
# ---- JPL planets phys par (planets + dwarf planets)
T=tables("jpl_planets_phys_par.html"); JP={}
for tb in T[:2]:
    for r in tb[2:]:
        if len(r)>=11 and r[0] in ("Mercury","Venus","Earth","Mars","Jupiter","Saturn","Uranus","Neptune","Ceres","Pluto","Eris"): JP[r[0].lower()]=dict(row=r,massexp=24 if r[0] in("Mercury","Venus","Earth","Mars","Jupiter","Saturn","Uranus","Neptune") else 18)
for pid,d in JP.items():
    r=d["row"]; sec=f"Table, row {r[0]}"
    bd=[b for b in DC.PLANETS if b[0]==pid] or [b for b in DC.SMALL if b[0]==pid]; b=bd[0]
    if pid in [x[0] for x in DC.PLANETS]: mu,rm,re_,mass,g,rot,aau,e,i,per,temp,mag=b[2],b[3],b[4],b[5],b[6],b[7],b[8],b[9],b[10],b[11],b[12],b[13]
    else: _,_,_,mu,rm,mass,g,rot,aau,e,i,per,temp=b; re_=None
    chk(pid,"mean_radius_m",rm*1e3,num(r[2])*1e3,"km",r[2],"jpl_planets_phys_par.html",sec+" Mean Radius",5e-4,"S02","km→m")
    if re_ is not None: chk(pid,"equatorial_radius_m",re_*1e3,num(r[1])*1e3,"km",r[1],"jpl_planets_phys_par.html",sec+" Equatorial Radius",5e-4,"S02","km→m")
    ms=num(r[3])*10**d["massexp"]; chk(pid,"mass_kg",mass,ms,f"×10^{d['massexp']} kg",r[3],"jpl_planets_phys_par.html",sec+" Mass",5e-4,"S02")
    chk(pid,"gravitational_parameter_km3_s2",mu,ms*G/1e9,"derived: JPL mass × G (CODATA 2018 6.6743e-11)",r[3],"jpl_planets_phys_par.html",sec+" Mass (JPL derives mass from GM with this G)",1e-3 if pid in("pluto","eris","ceres") else 1e-4,"S02","GM = M·G")
    chk(pid,"surface_gravity_m_s2",g,num(r[9]),"m/s^2 (equatorial)",r[9],"jpl_planets_phys_par.html",sec+" Equatorial Gravity",0.015,"S02")
    chk(pid,"derived.escape_velocity_m_s",math.sqrt(2*mu/rm)*1e3,num(r[10])*1e3,"km/s→m/s",r[10],"jpl_planets_phys_par.html",sec+" Escape Velocity (JPL computes from mass and mean radius; tolerance widened to the source rounding)",max(6e-3,0.5*10**-decimals(r[10])/max(num(r[10]),1e-9)),"S02","km/s×1000")
    rot_d=num(r[5]); chk(pid,"rotation_period_h",rot,rot_d*24,"d→h (negative = retrograde)",r[5],"jpl_planets_phys_par.html",sec+" Sidereal Rotation Period",2e-3,"S02","days×24")
    if pid in [x[0] for x in DC.PLANETS]+["ceres","pluto","eris"]: chk(pid,"orbital_period_days",per,num(r[6])*365.25,"y→d (Julian year)",r[6],"jpl_planets_phys_par.html",sec+" Sidereal Orbital Period",2e-3,"S02","years×365.25")
# ---- approx positions (planet elements)
t=read("jpl_approx_pos.html"); m=re.search(r"Mercury\s+0\.38709927.*?Neptune[^\n]*\n[^\n]*",t,flags=re.S); blk=re.sub(r"<[^>]+>"," ",t[t.find("0.38709927")-40:]);
EL={}
for name,key in (("Mercury","mercury"),("Venus","venus"),("EM Bary","earth"),("Mars","mars"),("Jupiter","jupiter"),("Saturn","saturn"),("Uranus","uranus"),("Neptune","neptune")):
    mm=re.search(re.escape(name)+r"\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)",blk)
    if mm: EL[key]=[mm.group(i) for i in (1,2,3)]
for pid,(a,e,i) in EL.items():
    b=[x for x in DC.PLANETS if x[0]==pid][0]
    sec="Table 1 Keplerian elements (J2000, valid 1800-2050)"+(" — row 'EM Bary' (Earth–Moon barycentre)" if pid=="earth" else "")
    chk(pid,"orbital_elements.semi_major_axis_au",b[8],float(a),"au",a,"jpl_approx_pos.html",sec,1e-9,"S04")
    chk(pid,"orbital_elements.eccentricity",b[9],float(e),"",e,"jpl_approx_pos.html",sec,1e-9,"S04")
    chk(pid,"orbital_elements.inclination_deg",b[10],float(i),"deg",i,"jpl_approx_pos.html",sec,1e-9,"S04") if abs(float(i))>1e-3 else checks.append(dict(record_id=pid,field="orbital_elements.inclination_deg",mine_original=b[10],source_value=float(i),source_original_text=i,source_unit="deg",conversion=None,source_id="S04",url=URLS["jpl_approx_pos.html"],file="data_raw/retrieved/jpl_approx_pos.html",retrieved=RETR.get("jpl_approx_pos.html"),section=sec,tolerance_rel=None,status="verified" if abs(b[10]-float(i))<1e-4 else "conflict"))
# ---- NSSDC planet fact sheets: GM, irradiance, orbit period/ecc/incl/semi-major
for pid in "mercury venus earth mars jupiter saturn uranus neptune".split():
    n=f"nssdc_{pid}.html"; lab={}
    for tb in tables(n):
        for r in tb:
            if len(r)>=2 and r[0] and r[0] not in lab: lab[r[0]]=r[1]
    b=[x for x in DC.PLANETS if x[0]==pid][0]
    for k,v in lab.items():
        if k.startswith("GM (x 10 6"): chk(pid,"gravitational_parameter_km3_s2",b[2],num(v)*1e6,"×10^6 km^3/s^2",v,n,"Bulk parameters: GM",2e-4,"S01","×1e6")
        if k.startswith("Volumetric mean radius"): chk(pid,"mean_radius_m",b[3]*1e3,num(v)*1e3,"km",v,n,"Bulk parameters: Volumetric mean radius",5e-4,"S01","km→m")
        if k.startswith("Mass (10 24"): chk(pid,"mass_kg",b[5],num(v)*1e24,"×10^24 kg",v,n,"Bulk parameters: Mass",1e-3,"S01")
        if k.startswith("Sidereal rotation period") and "(hrs)" in k: chk(pid,"rotation_period_h",b[7],num(v),"h",v,n,"Rotational: Sidereal rotation period",2e-3,"S01")
        if k.startswith("Sidereal orbit period"): chk(pid,"orbital_period_days",b[11],num(v),"days",v,n,"Orbital: Sidereal orbit period",1e-3,"S01")
# ---- Sun
lab={}
for tb in tables("nssdc_sun.html"):
    for r in tb:
        if len(r)>=2 and r[0] and r[0] not in lab: lab[r[0]]=r[1]
for k,v in lab.items():
    if k.startswith("GM (x 10 6"): chk("sun","gravitational_parameter_km3_s2",DC.SUN["mu"],num(v)*1e6,"×10^6 km^3/s^2 (5 significant figures only)",v,"nssdc_sun.html","Sun fact sheet: GM",1e-5*3,"S01","×1e6")
    if k.startswith("Volumetric mean radius"): chk("sun","mean_radius_m",DC.SUN["r_mean"]*1e3,num(v)*1e3,"km",v,"nssdc_sun.html","Sun fact sheet: Volumetric mean radius",1e-4,"S01")
    if k.startswith("Mass (10 24"): chk("sun","mass_kg",DC.SUN["mass"],num(v)*1e24,"×10^24 kg",v,"nssdc_sun.html","Sun fact sheet: Mass",1e-3,"S01")
    if k.startswith("Surface gravity"): chk("sun","surface_gravity_m_s2",DC.SUN["g"],num(v),"m/s^2",v,"nssdc_sun.html","Sun fact sheet: Surface gravity",5e-3,"S01")
# ---- JPL satellites
for r in tables("jpl_sats_phys_par.html")[0]:
    if len(r)>=6 and r[1].lower() in [m[0] for m in DC.MOONS]:
        mid=r[1].lower(); mo=[m for m in DC.MOONS if m[0]==mid][0]
        gm=r[3].split(); rad=r[4].split()
        chk(mid,"gravitational_parameter_km3_s2",mo[3],float(gm[0]),"km^3/s^2",r[3],"jpl_sats_phys_par.html","Satellite physical parameters: GM",2e-3 if mid in("phobos","deimos") else 1e-4,"S03")
        chk(mid,"mean_radius_m",mo[4]*1e3,float(rad[0])*1e3,"km",r[4],"jpl_sats_phys_par.html","Satellite physical parameters: Mean Radius",5e-3,"S03","km→m")
        mm=float(gm[0])*1e9/G; chk(mid,"mass_kg",mo[5],mm,"derived: JPL GM / G (CODATA 2018)",r[3],"jpl_sats_phys_par.html","Satellite physical parameters: GM",1e-2,"S03","M = GM/G")
# ---- NSSDC Moon orbit; Mars sheet Phobos/Deimos
lab={}
for tb in tables("nssdc_moon.html"):
    for r in tb:
        if len(r)>=2 and r[0] and r[0] not in lab: lab[r[0]]=r[1]
mo=[m for m in DC.MOONS if m[0]=="moon"][0]
for k,v in lab.items():
    if k.startswith("Semimajor axis"): chk("moon","semi_major_axis_m",mo[7]*1e3,(num(v)*1e9 if "10 6" in k else num(v)*1e6),k,v,"nssdc_moon.html","Moon fact sheet: "+k,2e-3,"S01","→ m")
    if k.startswith("Sidereal orbit period"): chk("moon","orbital_period_days",mo[8],num(v),"days",v,"nssdc_moon.html","Moon fact sheet: "+k,1e-3,"S01")
    if k.startswith("Orbit eccentricity"): chk("moon","eccentricity",mo[9],num(v),"",v,"nssdc_moon.html","Moon fact sheet: "+k,1e-2,"S01")
    if k.startswith("Inclination of orbit to ecliptic") or k.startswith("Orbit inclination (to ecliptic)"): chk("moon","inclination_deg",mo[10],num(v),"deg",v,"nssdc_moon.html","Moon fact sheet: "+k,1e-2,"S01")
for tb in tables("nssdc_mars.html"):
    if tb and tb[0][:3]==["","Phobos","Deimos"]:
        for r in tb[1:]:
            for idx,mid in ((1,"phobos"),(2,"deimos")):
                m_=[m for m in DC.MOONS if m[0]==mid][0]
                if r[0].startswith("Semimajor axis"): chk(mid,"semi_major_axis_m",m_[7]*1e3,num(r[idx])*1e3,"km",r[idx],"nssdc_mars.html","Mars fact sheet, satellites table: Semimajor axis",1e-3,"S01","km→m")
                if r[0].startswith("Sidereal orbit period"): chk(mid,"orbital_period_days",m_[8],num(r[idx]),"days",r[idx],"nssdc_mars.html","Mars fact sheet, satellites table: Sidereal orbit period",1e-3,"S01")
                if r[0].startswith("Orbital eccentricity"): chk(mid,"eccentricity",m_[9],num(r[idx]),"",r[idx],"nssdc_mars.html","Mars fact sheet, satellites table: Orbital eccentricity",0.05,"S01")
                if r[0].startswith("Orbital inclination"): chk(mid,"inclination_deg",m_[10],num(r[idx]),"deg",r[idx],"nssdc_mars.html","Mars fact sheet, satellites table: Orbital inclination",1e-2,"S01")
# ---- SBDB small bodies
for key,pid in (("bennu","bennu"),("ceres","ceres"),("vesta","vesta"),("pluto","pluto"),("eris","eris")):
    n=f"sbdb_{key}.json"; d=json.load(open(os.path.join(RET,n))); pp={p["name"]:p for p in d.get("phys_par",[])}
    sm=[b for b in DC.SMALL if b[0]==pid][0]
    if "GM" in pp: chk(pid,"gravitational_parameter_km3_s2",sm[3],float(pp["GM"]["value"]),pp["GM"].get("units","km^3/s^2"),str(pp["GM"]["value"]),n,"SBDB phys_par GM",2e-3,"S40")
    if "diameter" in pp: chk(pid,"mean_radius_m",sm[4]*1e3,float(pp["diameter"]["value"])/2*1e3,"km (diameter/2)",str(pp["diameter"]["value"]),n,"SBDB phys_par diameter ÷ 2",5e-3,"S40","diameter/2, km→m")
    if "rot_per" in pp: chk(pid,"rotation_period_h",abs(sm[7]),float(pp["rot_per"]["value"]),"h (magnitude; sign convention from the JPL planets table)",str(pp["rot_per"]["value"]),n,"SBDB phys_par rot_per",2e-3,"S40")
    el={e["name"]:e["value"] for e in d["orbit"]["elements"]}
    ep=d["orbit"].get("epoch")
    for nm,idx,fld in (("a",8,"orbital_elements.semi_major_axis_au"),("e",9,"orbital_elements.eccentricity"),("i",10,"orbital_elements.inclination_deg")):
        if nm in el:
            sv=float(el[nm]); dec=decimals(str(el[nm])); mine=round(sm[idx],dec)
            checks.append(dict(record_id=pid,field=fld,mine_original=sm[idx],source_value=sv,source_original_text=str(el[nm]),source_unit="au" if nm=="a" else ("deg" if nm=="i" else ""),conversion=f"compared at the source's printed precision ({dec} decimals)",source_id="S40",
               url=URLS[n],file="data_raw/retrieved/"+n,retrieved=RETR.get(n),section=f"SBDB orbit.elements '{nm}' (osculating, epoch JD {ep})",tolerance_rel=None,status="verified" if abs(mine-sv)<=10**-dec else "conflict",source_epoch_jd=ep))
# ---- choose ONE primary check per (record, field); keep the others as competing/corroborating
PRIORITY={"S02":0,"S03":0,"S04":0,"S01":1,"S40":2}
PREFER={}   # {(record_id, field): (source_id, reason)} — use only when two RETRIEVED sources disagree and a judgment is documented
groups={}
for c in checks: groups.setdefault((c["record_id"],c["field"]),[]).append(c)
for (rid,fld),cs in groups.items():
    pref=PREFER.get((rid,fld))
    cs.sort(key=lambda c:(0 if pref and c["source_id"]==pref[0] else 1,PRIORITY.get(c["source_id"],9)))
    for k,c in enumerate(cs):
        c["primary"]=(k==0)
        if k==0 and pref: c["selection_reason"]=pref[1]
        if k>0: c["competes_with"]=cs[0]["source_id"]
json.dump(dict(generated=datetime.date.today().isoformat(),G_used=G,note="Each check compares a recalled value with a value read from a retrieved local copy of the cited page. status: verified (within tolerance), conflict (outside tolerance; source value is preferred), not_recorded (record lacked the field).",checks=checks),open(os.path.join(OUT,"verification_celestial.json"),"w"),indent=1)
import collections
c=collections.Counter(x["status"] for x in checks); print(dict(c),len(checks),"checks")
for x in checks:
    if x["status"]=="conflict": print("CONFLICT",x["record_id"],x["field"],x["mine_original"],"vs",x["source_value"],"|",x["source_original_text"])
