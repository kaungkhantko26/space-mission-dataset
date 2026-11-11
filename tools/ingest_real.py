"""Direct ingestion of real source tables from retrieved files (no recalled values). Used by make_verified.py.
  soa_components(): NASA State-of-the-Art Small Spacecraft Technology report 2026 (nasa.gov/smallsat-institute/sst-soa) product tables."""
import re, html, os, glob, hashlib, datetime
HERE=os.path.dirname(os.path.abspath(__file__)); RET=os.path.join(HERE,"..","data_raw","retrieved")
clean=lambda c: re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",c))).strip()
def grid(tb):
    """Expand rowspan/colspan into a rectangular list of rows (list of str)."""
    rows=[]; pending={}   # col -> [remaining_rows, text]
    for tr in re.findall(r"<tr.*?</tr>",tb,flags=re.S|re.I):
        cells=re.findall(r"<t[dh]([^>]*)>(.*?)</t[dh]>",tr,flags=re.S|re.I); row=[]; col=0
        def fill():
            nonlocal col
            while col in pending and pending[col][0]>0:
                row.append(pending[col][1]); pending[col][0]-=1; col+=1
        for attrs,inner in cells:
            fill()
            rs=re.search(r'rowspan="?(\d+)',attrs); cs=re.search(r'colspan="?(\d+)',attrs); txt=clean(inner)
            rs=int(rs.group(1)) if rs else 1; cs=int(cs.group(1)) if cs else 1
            for k in range(cs):
                row.append(txt)
                if rs>1: pending[col]=[rs-1,txt]
                col+=1
        fill()
        if row: rows.append(row)
    return rows
DOMAIN={"in-space_propulsion":"propulsion","power-subsystems":"power","guidance-navigation-and-control":"guidance_navigation_control","soa-communications":"communications","small-spacecraft-avionics":"avionics",
        "structures-materials-and-mechanisms":"structures_materials_mechanisms","thermal-control":"thermal_control","platforms":"platforms","integration-launch-and-deployment":"launch_integration_deployment",
        "deorbit-systems":"deorbit","ground-data-systems-and-mission-operations":"ground_systems","identification-and-tracking-systems":"tracking"}
UNIT=re.compile(r"[\[(]\s*([^\])]{1,18}?)\s*[\])]\s*\*?$")
def num(s):
    s=s.replace(",","").replace("−","-").replace("–","-").strip().rstrip("*†‡ ")
    return float(s) if re.fullmatch(r"-?\d+(\.\d+)?",s) else None
def soa_components():
    recs=[]; tables_meta=[]; files={}
    for f in sorted(glob.glob(os.path.join(RET,"soa","*.html"))):
        ch=os.path.basename(f)[:-5]; dom=DOMAIN.get(ch)
        if not dom: continue
        raw=open(f,"rb").read(); sha=hashlib.sha256(raw).hexdigest(); ret=datetime.datetime.fromtimestamp(os.path.getmtime(f),datetime.timezone.utc).strftime("%Y-%m-%d")
        files[ch]=dict(file=f"data_raw/retrieved/soa/{ch}.html",url=f"https://www.nasa.gov/smallsat-institute/sst-soa/{ch}",source_sha256=sha,retrieved=ret)
        for ti,tb in enumerate(re.findall(r"<table.*?</table>",raw.decode("utf-8","replace"),flags=re.S|re.I)):
            g=grid(tb)
            if len(g)<4 or not g[0][0].startswith("Table"): continue
            title=g[0][0]; m=re.match(r"Table\s+([\d\-‑–]+)\s*(?:\(cont\.\))?\s*:?\s*(.*)",title); tid=(m.group(1) if m else str(ti)).replace("‑","-").replace("–","-"); tname=(m.group(2) if m else title)
            if "Contact Information" in title: continue
            hdr=g[1]; ncol=len(hdr)
            if ncol<3: continue
            unit_row=g[2] if len(g)>2 and sum(1 for c in g[2] if c.strip() in ("—","-","–") or UNIT.search(c) or c.strip()=="Notes")>=max(2,ncol//3) and not re.search(r"[A-Za-z]{4,}",g[2][1] if len(g[2])>1 else "") else None
            data=g[3:] if unit_row else g[2:]
            heads=[]
            for i,h in enumerate(hdr):
                u=unit_row[i] if unit_row and i<len(unit_row) and unit_row[i] not in ("—","-","–","") else ""
                heads.append((h+(" "+u if u and u not in h else "")).strip())
            n=0
            for r in data:
                if len(r)<ncol: r=r+[""]*(ncol-len(r))
                if len(set(x for x in r if x))<=1: continue    # section/blank rows
                n+=1; attrs={heads[i]:r[i] for i in range(ncol) if r[i] not in ("","—")}
                numeric={}
                for i in range(ncol):
                    v=num(r[i]) if r[i] else None; mu=UNIT.search(heads[i])
                    if v is not None and mu: numeric[re.sub(r"\s*[\[(].*$","",heads[i]).strip()+" ["+mu.group(1)+"]"]=v
                first=r[0]; recid=f"soa_{dom}_{tid.replace('-','_')}_t{ti:02d}_{n:03d}"
                recs.append(dict(id=recid,domain=dom,chapter=ch,table_id=tid,table_title=tname,organization_or_item=first,product=(r[1] if ncol>1 else None),attributes=attrs,numeric=numeric,
                                 data_class="verified",confidence="high",source_ids=["S54"],retrieval_status="retrieved",
                                 note="Vendor-reported values as compiled by the NASA SoA report; not NASA-tested. Values are strings exactly as published; 'numeric' holds parsed numbers where the header gives a unit."))
            tables_meta.append(dict(domain=dom,chapter=ch,table_id=tid,title=tname,columns=heads,rows=n))
    return recs,tables_meta,files

EMAIL=re.compile(r"[\w.+-]+@[\w.-]+\.\w+")
def page_text(path):
    t=open(path,encoding="utf-8",errors="replace").read(); t=re.sub(r"<script.*?</script>|<style.*?</style>","",t,flags=re.S)
    return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",t))).strip()
def fileinfo(path,url):
    return dict(file=os.path.relpath(path,os.path.join(RET,"..","..")).replace(os.sep,"/"),url=url,source_sha256=hashlib.sha256(open(path,"rb").read()).hexdigest(),retrieved=datetime.datetime.fromtimestamp(os.path.getmtime(path),datetime.timezone.utc).strftime("%Y-%m-%d"))
MENT=re.compile(r"(\d+(?:\.\d+)?)\s*(kg|W|watts?|cm|mm|km|nm|micrometers?|microns|Hz|kHz|MHz|GHz|mrad|milliradians?|arcsec|bps|kbps|Mbps|bits/s|m/pixel|km/pixel|m/s|km/s)\b")
def nmc_missions():
    """NSSDC Master Catalog spacecraft pages + experiment (instrument) pages. Personnel names/emails are NOT ingested."""
    base=os.path.join(RET,"nmc"); ms=[]; exps=[]
    for f in sorted(glob.glob(os.path.join(base,"nmc_*.html"))):
        cid=os.path.basename(f)[4:-5]; s=page_text(f)
        if "Launch Date:" not in s: continue
        nm=re.search(r"Details\s+\w+,\s+\d{1,2}\s+\w+\s+\d{4}\s+(.*?)\s+NSSDCA/COSPAR ID:",s)
        g=lambda lab,end: (re.search(lab+r":\s*(.*?)\s*(?:"+end+")",s) or [None,None])[1]
        desc=re.search(r"NSSDCA/COSPAR ID:\s*"+re.escape(cid)+r"\s*(.*?)\s*Alternate Names",s)
        mass=re.search(r"Mass:\s*([\d,.]+)\s*kg",s); power=re.search(r"Nominal Power:\s*([\d,.]+)\s*W",s)
        costs=[dict(sentence=x.strip(),amount=float(m_.group(1).replace(",","")),unit=m_.group(2)) for x in re.split(r"(?<=[.!?])\s+",desc.group(1) if desc else "") for m_ in [re.search(r"\$\s?([\d.,]+)\s*(million|billion)",x)] if m_]
        rec=dict(id="nmc_"+cid.lower().replace("-","_"),cospar_id=cid,cost_mentions_in_text=costs,cost_note="cost_mentions_in_text are sentences from the NASA catalog description that state a dollar amount (planned, estimated or total); the scope and year are whatever the sentence says.",name=nm.group(1).strip() if nm else None,launch_date=g("Launch Date","Launch Vehicle"),launch_vehicle=g("Launch Vehicle","Launch Site"),launch_site=g("Launch Site","Mass:|Nominal Power|Funding"),
                 catalog_mass_kg=float(mass.group(1).replace(",","")) if mass else None,nominal_power_w=float(power.group(1).replace(",","")) if power else None,funding_agency=g("Funding Agency","Discipline|Additional"),discipline=g("Discipline","Additional Information|Launch"),
                 description=EMAIL.sub("[email removed]",desc.group(1))[:4000] if desc else None,mass_note="catalog_mass_kg is the value printed in the NSSDC catalog; the catalog does not say whether it is dry, launch or payload mass, and its meaning differs between missions.",
                 data_class="verified",confidence="high",source_ids=["S49"],retrieval_status="retrieved",provenance=fileinfo(f,f"https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id={cid}"))
        ms.append(rec)
    for f in sorted(glob.glob(os.path.join(base,"exp","20*-[0-9A-Z][0-9A-Z].html"))+glob.glob(os.path.join(base,"exp","19*-[0-9A-Z][0-9A-Z].html"))):
        eid=os.path.basename(f)[:-5]; s=page_text(f); sc=eid.rsplit("-",1)[0]
        nm=re.search(r"Details\s+\w+,\s+\d{1,2}\s+\w+\s+\d{4}\s+(.*?)\s+NSSDCA ID:",s); mn=re.search(r"Mission Name:\s*(.*?)\s+(?:Principal Investigators?:|Description)",s)
        d=re.search(r"Description\s+(.*?)(?:\s+Alternate Names|\s+Questions and comments|\s+NSSDCA Master Catalog Search)",s)
        text=EMAIL.sub("[email removed]",d.group(1)) if d else None
        if not nm: continue
        sent=[x.strip() for x in re.split(r"(?<=[.!?])\s+",text or "")]
        mass_s=[(x,re.search(r"(\d+(?:\.\d+)?)\s*kg",x)) for x in sent if re.search(r"\b(mass|weigh\w*)\b",x,flags=re.I) and re.search(r"\d\s*kg",x)]
        pow_s=[(x,re.search(r"(\d+(?:\.\d+)?)\s*(?:W|watts?)\b",x)) for x in sent if re.search(r"\b(power|consum\w*)\b",x,flags=re.I) and re.search(r"\d\s*(?:W|watts?)\b",x)]
        exps.append(dict(id="nmc_exp_"+eid.lower().replace("-","_"),mass_kg_from_text=(float(mass_s[0][1].group(1)) if mass_s else None),mass_sentence=(mass_s[0][0][:400] if mass_s else None),power_w_from_text=(float(pow_s[0][1].group(1)) if pow_s else None),power_sentence=(pow_s[0][0][:400] if pow_s else None),
                 spec_note="mass/power fields are taken from the first sentence in the NASA description that states a mass in kg or a power in W; they may describe a sub-unit or a mode. Read the sentence.",nssdca_id=eid,spacecraft_cospar_id=sc,spacecraft_id="nmc_"+sc.lower().replace("-","_"),name=nm.group(1).strip(),mission_name=mn.group(1).strip() if mn else None,description=text[:6000] if text else None,
                 numeric_mentions_in_text=[dict(value=float(v),unit=u,context=text[max(0,m.start()-50):m.end()+20]) for m in MENT.finditer(text or "") for v,u in [m.groups()]][:25],
                 text_extraction_note="numeric_mentions_in_text are regex matches of 'number unit' in the catalog prose, with context; they are not structured specifications.",
                 data_class="verified",confidence="high",source_ids=["S49"],retrieval_status="retrieved",provenance=fileinfo(f,f"https://nssdc.gsfc.nasa.gov/nmc/experiment/display.action?id={eid}")))
    return ms,exps
ATM_FIELDS=[("surface_pressure","Surface pressure"),("surface_density","Surface density"),("scale_height","Scale height"),("total_atmosphere_mass","Total mass of atmosphere"),("average_temperature","Average temperature"),("diurnal_temperature_range","Diurnal temperature range"),("wind_speeds","Wind speeds"),("mean_molecular_weight","Mean molecular weight")]
NSSDC_LABELS=["Solar irradiance","J 2","Bond albedo","Geometric albedo","Black-body temperature","Obliquity to orbit","Length of day","Sidereal rotation period","Mean density","Surface gravity (mean)","Surface acceleration (eq)","Escape velocity","Ellipticity","Moment of inertia","Number of natural satellites","Planetary ring system","Synodic period","Mean orbital velocity","Min. orbital velocity","Max. orbital velocity","Perihelion","Aphelion","Equatorial radius","Polar radius","Core radius","Topographic range"]
def nssdc_params():
    """Rows of the NASA NSSDC planetary fact sheets for the Sun-orbiting planets and the Moon, exactly as published (planet column only)."""
    out={}
    for body in ("mercury","venus","earth","mars","jupiter","saturn","uranus","neptune","moon"):
        f=os.path.join(RET,f"nssdc_{body}.html")
        if not os.path.exists(f): continue
        t=open(f,encoding="utf-8",errors="replace").read(); pub={}
        for tb in re.findall(r"<table.*?</table>",t,flags=re.S|re.I):
            for tr in re.findall(r"<tr.*?</tr>",tb,flags=re.S|re.I):
                c=[clean(x) for x in re.findall(r"<t[dh].*?</t[dh]>",tr,flags=re.S|re.I)]
                if len(c)>=2 and any(c[0].startswith(l) for l in NSSDC_LABELS) and c[0] not in pub and c[1]: pub[c[0]]=c[1]
        if not pub:   # plain-text layout (e.g. Earth sheet): "<label> <value>" pairs in reading order
            txt=page_text(f)
            for l in NSSDC_LABELS:
                m=re.search(r"("+re.escape(l)+r"(?:\s*\([^)]*\))*)\s+(-?\d[\d,]*\.?\d*)\b",txt)
                if m and m.group(1).strip() not in pub: pub[m.group(1).strip()]=m.group(2)
        num_=lambda v:(lambda m:float(m.group(0).replace(",","")) if m else None)(re.match(r"-?[\d,]*\.?\d+",v.replace("−","-")))
        out[body]=dict(published=pub,numeric={k:num_(v) for k,v in pub.items() if num_(v) is not None},provenance=fileinfo(f,f"https://nssdc.gsfc.nasa.gov/planetary/factsheet/{body}fact.html"))
    return out
def atmospheres():
    out=[]
    for body in ("mercury","venus","earth","mars","jupiter","saturn","uranus","neptune","moon","pluto"):
        f=os.path.join(RET,f"nssdc_{body}.html")
        if not os.path.exists(f): continue
        s=page_text(f); i=s.find("Atmosphere"); 
        if i<0 and "Surface pressure" not in s and "Atmospheric composition" not in s: continue
        names=[l for _,l in ATM_FIELDS]+["Atmospheric composition"]
        def val(label):
            m=re.search(label+r"[^:]{0,60}:\s*(.*?)(?=\s(?:"+"|".join(re.escape(n) for n in names+["Number of natural satellites","Planetary ring system","Orbital","Discoverer","Atmosphere\b"])+r")|\s[A-Z][a-z]+ [a-z ]{3,30}:|$)",s)
            return m.group(1).strip() if m else None
        fields={k:val(l) for k,l in ATM_FIELDS}; comp=re.search(r"Atmospheric composition[^:]{0,80}:?\s*(.*?)(?=\s(?:Mean molecular weight|Surface pressure|Wind speeds|Scale height|Surface density|Total mass|Average temperature|Diurnal)|\sNumber of natural|$)",s)
        fields["atmospheric_composition"]=comp.group(1).strip() if comp else None
        fields={k:v[:600] for k,v in fields.items() if v}
        if not fields: continue
        def first_num(txt):
            m=re.search(r"([-+]?\d+(?:\.\d+)?)\s*([A-Za-z/%\^0-9 ]{0,12})",txt or ""); return (float(m.group(1)),m.group(2).strip()) if m else (None,None)
        pm=re.match(r"\s*~?\s*(\d+(?:\.\d+)?)\s*(bars?|mbar|mb|kPa|Pa|microbars?)\b",fields.get("surface_pressure") or ""); pv=float(pm.group(1)) if pm else None; pu=pm.group(2) if pm else None
        sh,_=first_num(fields.get("scale_height")); tv,_=first_num(fields.get("average_temperature")); tu="K" if re.search(r"\dK\b|\d\s*K\b",fields.get("average_temperature") or "") else None
        out.append(dict(id=f"atm_{body}",body_id=body,published=fields,parsed=dict(surface_pressure_value=pv,surface_pressure_unit=pu,scale_height_km=sh,average_temperature_value=tv,average_temperature_unit=tu),
                        parse_note="'published' holds the text exactly as printed on the NASA NSSDC fact sheet; 'parsed' holds the first number and unit of selected fields (check units: bars, mb, kPa, K).",
                        data_class="verified",confidence="high",source_ids=["S01"],retrieval_status="retrieved",provenance=fileinfo(f,f"https://nssdc.gsfc.nasa.gov/planetary/factsheet/{body}fact.html")))
    return out

import json as _json
def _fi(path,url): return fileinfo(path,url)
def ll2_launchers():
    """Launch Library 2 launcher configurations (community-curated aggregator; units per LL2: length/diameter m, launch_mass t, capacities kg, thrust kN)."""
    out=[]
    for f in sorted(glob.glob(os.path.join(RET,"ll2","configs_*.json")),key=lambda x:int(re.search(r"_(\d+)\.json",x).group(1))):
        d=_json.load(open(f)); P=fileinfo(f,"https://ll.thespacedevs.com/2.2.0/config/launcher/")
        for r in d["results"]:
            mf=r.get("manufacturer") or {}
            out.append(dict(id=f"ll2_cfg_{r['id']}",ll2_id=r["id"],name=r["name"],full_name=r.get("full_name"),family=r.get("family"),variant=r.get("variant"),alias=r.get("alias") or None,manufacturer=mf.get("name"),manufacturer_country=mf.get("country_code"),
                active=r.get("active"),reusable=r.get("reusable"),maiden_flight=r.get("maiden_flight"),length_m=r.get("length"),diameter_m=r.get("diameter"),launch_mass_t=r.get("launch_mass"),leo_capacity_kg=r.get("leo_capacity"),gto_capacity_kg=r.get("gto_capacity"),
                liftoff_thrust_kn=r.get("to_thrust"),apogee_km=r.get("apogee"),launch_cost_usd=(int(r["launch_cost"]) if str(r.get("launch_cost") or "").isdigit() else r.get("launch_cost")),min_stage=r.get("min_stage"),max_stage=r.get("max_stage"),
                total_launches=r.get("total_launch_count"),successful_launches=r.get("successful_launches"),failed_launches=r.get("failed_launches"),pending_launches=r.get("pending_launches"),attempted_landings=r.get("attempted_landings"),successful_landings=r.get("successful_landings"),
                reference_orbit_note="LL2 does not state altitude or inclination for leo_capacity_kg / gto_capacity_kg; do not compare across vehicles as if conditions were equal.",
                info_url=r.get("info_url"),wiki_url=r.get("wiki_url"),data_class="verified",source_authority="aggregator: The Space Devs Launch Library 2 (community-curated; cites manufacturers and agencies)",confidence="medium",source_ids=["S55"],retrieval_status="retrieved",provenance=P))
    return out
def ll2_spacex_launches():
    out=[]
    for f in sorted(glob.glob(os.path.join(RET,"ll2","sx_*.json")),key=lambda x:int(re.search(r"_(\d+)\.json",x).group(1))):
        d=_json.load(open(f)); P=fileinfo(f,"https://ll.thespacedevs.com/2.2.0/launch/previous/?lsp__id=121")
        for r in d["results"]:
            rk=((r.get("rocket") or {}).get("configuration") or {}); ms=r.get("mission") or {}; pad=r.get("pad") or {}; orb=(ms.get("orbit") or {})
            out.append(dict(id=f"ll2_launch_{r['id'][:8]}",ll2_uuid=r["id"],name=r["name"],date_utc=r.get("net"),status=(r.get("status") or {}).get("name"),status_abbrev=(r.get("status") or {}).get("abbrev"),failure_reason=r.get("failreason") or None,
                vehicle=rk.get("full_name") or rk.get("name"),vehicle_family=rk.get("family"),vehicle_variant=rk.get("variant"),mission=ms.get("name"),mission_type=ms.get("type"),orbit=orb.get("name"),orbit_abbrev=orb.get("abbrev"),
                pad=pad.get("name"),location=(pad.get("location") or {}).get("name"),launch_provider=(r.get("launch_service_provider") or {}).get("name"),
                data_class="verified",source_authority="aggregator: The Space Devs Launch Library 2",confidence="medium",source_ids=["S55"],retrieval_status="retrieved",provenance=P))
    return out
def ll2_all_launches():
    """Every past orbital/suborbital launch of every provider from Launch Library 2 (aggregator)."""
    out=[]
    fs=sorted(glob.glob(os.path.join(RET,"ll2","all_*.json")),key=lambda x:int(re.search(r"all_(\d+)\.json",x).group(1)))
    for f in fs:
        d=_json.load(open(f)); P=fileinfo(f,"https://ll.thespacedevs.com/2.2.0/launch/previous/?limit=100&mode=normal")
        for r in d["results"]:
            rk=((r.get("rocket") or {}).get("configuration") or {}); ms=r.get("mission") or {}; pad=r.get("pad") or {}; orb=(ms.get("orbit") or {}); lsp=r.get("launch_service_provider") or {}
            out.append(dict(id=f"ll2all_{r['id'][:8]}",ll2_uuid=r["id"],name=r["name"],date_utc=r.get("net"),status=(r.get("status") or {}).get("name"),failure_reason=r.get("failreason") or None,
                vehicle=rk.get("full_name") or rk.get("name"),vehicle_family=rk.get("family"),vehicle_variant=rk.get("variant"),mission=ms.get("name"),mission_type=ms.get("type"),orbit=orb.get("name"),orbit_abbrev=orb.get("abbrev"),
                pad=pad.get("name"),location=(pad.get("location") or {}).get("name"),country_code=(pad.get("location") or {}).get("country_code"),launch_provider=lsp.get("name"),provider_type=lsp.get("type"),
                data_class="verified",source_authority="aggregator: The Space Devs Launch Library 2",confidence="medium",source_ids=["S55"],retrieval_status="retrieved",provenance=P))
    seen=set(); res=[]
    for r in sorted(out,key=lambda r:(r["date_utc"] or "",r["ll2_uuid"])):
        if r["ll2_uuid"] in seen: continue
        seen.add(r["ll2_uuid"]); res.append(r)
    return res
def ll2_pads():
    """Launch pads (coordinates, location, country, launch counts) from the Launch Library 2 launch records already retrieved (aggregator)."""
    pads={}
    fs=sorted(glob.glob(os.path.join(RET,"ll2","all_*.json")),key=lambda x:int(re.search(r"all_(\d+)\.json",x).group(1)))
    for f in fs:
        d=_json.load(open(f)); P=fileinfo(f,"https://ll.thespacedevs.com/2.2.0/launch/previous/?limit=100&mode=normal")
        for r in d["results"]:
            pad=r.get("pad") or {}; loc=pad.get("location") or {}
            try: lat=float(pad["latitude"]); lon=float(pad["longitude"])
            except (KeyError,TypeError,ValueError): continue
            if not (-90<=lat<=90 and -180<=lon<=180) or (lat==0 and lon==0): continue
            k=pad["id"]
            if k not in pads:
                pads[k]=dict(id=f"ll2_pad_{k}",ll2_pad_id=k,name=pad.get("name"),location=loc.get("name"),country_code=loc.get("country_code"),latitude_deg=lat,longitude_deg=lon,
                    launches_in_dataset=0,ll2_total_launch_count=pad.get("total_launch_count"),first_launch_utc=r.get("net"),last_launch_utc=r.get("net"),
                    data_class="verified",source_authority="aggregator: The Space Devs Launch Library 2",confidence="medium",source_ids=["S55"],retrieval_status="retrieved",provenance=P)
            q=pads[k]; q["launches_in_dataset"]+=1
            if r.get("net"):
                q["first_launch_utc"]=min(q["first_launch_utc"],r["net"]); q["last_launch_utc"]=max(q["last_launch_utc"],r["net"])
    return sorted(pads.values(),key=lambda q:(-q["launches_in_dataset"],q["name"] or ""))
FLUIDS={"oxygen":("C7782447","O2"),"hydrogen":("C1333740","H2"),"methane":("C74828","CH4"),"xenon":("C7440633","Xe"),"nitrogen":("C7727379","N2"),"helium":("C7440597","He")}
def fluids():
    out=[]
    for name,(cas,formula) in FLUIDS.items():
        f=os.path.join(RET,"nist",f"{name}.tsv")
        if not os.path.exists(f): continue
        L=[l.split("\t") for l in open(f).read().splitlines() if l.strip()]; h=L[0]; rows=[dict(zip(h,r)) for r in L[1:]]
        col=lambda k:[c for c in h if c.startswith(k)][0]
        T,Pc,Dl,Dv=col("Temperature"),col("Pressure"),col("Density (l"),col("Density (v")
        pr=[(float(r[Pc]),r) for r in rows]; P0=0.101325
        lo=[x for x in pr if x[0]<=P0]; hi=[x for x in pr if x[0]>=P0]
        if lo and hi and lo[-1][0]!=hi[0][0]:
            a,b=lo[-1],hi[0]; w=(P0-a[0])/(b[0]-a[0]); ip=lambda k: float(a[1][k])+w*(float(b[1][k])-float(a[1][k])); boil=dict(temperature_k=ip(T),liquid_density_kg_m3=ip(Dl),vapor_density_kg_m3=ip(Dv),pressure_mpa=P0,method="linear interpolation in pressure between the two bracketing NIST saturation rows")
        else: boil=None
        first,last=rows[0],rows[-1]
        out.append(dict(id=f"nist_{name}",fluid=name,formula=formula,cas_id=cas,normal_boiling_point=boil,lowest_tabulated_saturation_state=dict(temperature_k=float(first[T]),pressure_mpa=float(first[Pc]),liquid_density_kg_m3=float(first[Dl])),
                        highest_tabulated_saturation_state=dict(temperature_k=float(last[T]),pressure_mpa=float(last[Pc]),liquid_density_kg_m3=float(last[Dl]),note="critical point"),rows_in_source_table=len(rows),
                        data_class="verified",source_authority="NIST Chemistry WebBook (thermophysical properties of fluids)",confidence="high",source_ids=["S56"],retrieval_status="retrieved",provenance=fileinfo(f,f"https://webbook.nist.gov/cgi/fluid.cgi?ID={cas}&Type=SatP")))
    return out
if __name__=="__main__":
    r,t,f=soa_components(); print(len(r),"records from",len(t),"tables"); import collections; print(collections.Counter(x["domain"] for x in r)); print("unique ids",len({x["id"] for x in r})==len(r))
    m,e=nmc_missions(); print(len(m),"missions",len(e),"experiments"); print(m[0]["name"],m[0]["launch_date"],m[0]["launch_vehicle"],m[0]["catalog_mass_kg"]); print(e[0]["name"],e[0]["numeric_mentions_in_text"][:2])
    l=ll2_launchers(); x=ll2_spacex_launches(); fl=fluids(); print(len(l),"launcher configs",len(x),"spacex launches",len(fl),"fluids"); f9=[c for c in l if c["name"]=="Falcon 9"][:2]; print([(c["full_name"],c["leo_capacity_kg"],c["gto_capacity_kg"],c["launch_mass_t"],c["liftoff_thrust_kn"],c["length_m"],c["diameter_m"]) for c in f9]); print(x[0]["date_utc"],x[0]["name"],x[-1]["date_utc"],x[-1]["name"],x[-1]["status"]); print([ (z["fluid"],round(z["normal_boiling_point"]["temperature_k"],2),round(z["normal_boiling_point"]["liquid_density_kg_m3"],1)) for z in fl if z["normal_boiling_point"]])
    a=atmospheres(); print(len(a),"atmospheres"); print(a[3]["published"],a[3]["parsed"])
    for x in r[:2]: print(x["id"],x["organization_or_item"],x["product"],list(x["attributes"].items())[:4],x["numeric"])
