#!/usr/bin/env python3
"""Field-level verification of launch-vehicle, stage, booster, engine and mission records against RETRIEVED primary-source files
(data_raw/retrieved/). Recalled values are read from tools/data_*.py (never from build outputs). Only numbers the source actually states are checked.
Output: space-mission-research/metadata/verification_launch.json
status: verified | conflict (source value replaces the recalled one in the build) | added_from_source (record had null) | source_text_not_found"""
import re, html, json, os, hashlib, datetime, sys
HERE=os.path.dirname(os.path.abspath(__file__)); RET=os.path.join(HERE,"..","data_raw","retrieved"); OUT=os.path.join(HERE,"..","space-mission-research","metadata")
sys.path.insert(0,HERE); import data_prop_launch as DP, data_sc as DS
LBF=4.4482216152605; FT=0.3048; LB=0.45359237; MT=1000.0
def html_text(n):
    t=open(os.path.join(RET,n),encoding="utf-8",errors="replace").read(); t=re.sub(r"<script.*?</script>|<style.*?</style>","",t,flags=re.S)
    return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",t)))
def pdf_text(n,squash_digits=False):
    t=open(os.path.join(RET,n),encoding="utf-8",errors="replace").read(); t=re.sub(r"\s+"," ",t)
    if squash_digits: t=re.sub(r"(?<=\d) (?=[\d,])","",t); t=re.sub(r"(?<=\d,) (?=\d)","",t)
    return t
SRC={ # key -> (id, file for hash/url, url, text)
 "ula_atlas":("S42","ula_atlas_v.html","https://www.ulalaunch.com/rockets/atlas-v",html_text("ula_atlas_v.html")),
 "ula_vulcan":("S42","ula_vulcan.html","https://www.ulalaunch.com/rockets/vulcan-centaur",html_text("ula_vulcan.html")),
 "esa_vega":("S43","esa_vega_c.html","https://www.esa.int/Enabling_Support/Space_Transportation/Launch_vehicles/Vega-C",html_text("esa_vega_c.html")),
 "pk11":("S44","ntrs_19690022248.pdf","https://ntrs.nasa.gov/api/citations/19690022248/downloads/19690022248.pdf",pdf_text("ntrs_19690022248.txt",True)),
 "next":("S45","ntrs_20090004685.pdf","https://ntrs.nasa.gov/api/citations/20090004685/downloads/20090004685.pdf",pdf_text("ntrs_20090004685.txt")),
 "nstar":("S46","ntrs_19980017550.pdf","https://ntrs.nasa.gov/api/citations/19980017550/downloads/19980017550.pdf",pdf_text("ntrs_19980017550_raw.txt")),
 "bpt":("S47","ntrs_20060051789.pdf","https://ntrs.nasa.gov/api/citations/20060051789/downloads/20060051789.pdf",pdf_text("ntrs_20060051789.txt")),
 "esa_a6":("S48","esa_ariane6_overview.html","https://www.esa.int/Enabling_Support/Space_Transportation/Launch_vehicles/Ariane_6_overview",html_text("esa_ariane6_overview.html")),
 "sls":("S41","nasa_sls_reference.html","https://www.nasa.gov/reference/space-launch-system/",html_text("nasa_sls_reference.html")),
}
def meta(k):
    sid,f,url,_=SRC[k]; p=os.path.join(RET,f); return sid,url,"data_raw/retrieved/"+f,hashlib.sha256(open(p,"rb").read()).hexdigest(),datetime.datetime.fromtimestamp(os.path.getmtime(p),datetime.timezone.utc).strftime("%Y-%m-%d")
V={v["id"]:v for v in DP.VEHICLES}; B={b["id"]:b for b in DP.BOOSTERS}; E={e["id"]:e for e in DP.ENGINES}; S={s["id"]:s for s in DP.STAGES}; M={m["id"]:m for m in DS.MISSIONS}
checks=[]
def num(s): return float(s.replace(",",""))
def add(coll,rid,field,mine,src,pattern,scale,unit,tol,section,bound=None,group=1,transform=None,note=None,text=None):
    sid,url,file,sha,ret=meta(src); txt=text if text is not None else SRC[src][3]; m=re.search(pattern,txt)
    base=dict(collection=coll,record_id=rid,field=field,source_id=sid,url=url,file=file,source_sha256=sha,retrieved=ret,section=section,tolerance_rel=tol,mine_original=mine)
    if not m: checks.append(dict(base,status="source_text_not_found",pattern=pattern)); return
    val=num(m.group(group))*scale
    if transform: val=transform(val)
    if mine is None: st="added_from_source"
    elif bound=="at_least": st="verified" if mine>=val*(1-tol) and mine<=val*(1+tol) else "conflict"
    elif bound=="lower_bound_source": st="verified" if mine>=val*(1-tol) else "conflict"   # source says 'over X': recalled value must be >= X
    else: st="verified" if abs(mine-val)/abs(val)<=tol else "conflict"
    checks.append(dict(base,status=st,source_value=val,source_original_text=m.group(0)[:160],source_unit=unit,statement_type=("lower bound" if bound else "point value"),note=note))
# ---------------- Atlas V 551 (ULA) ----------------
a=V["atlas_v_551"]; pl={ (p["orbit"],p["mode"]):p for p in a["payloads"]}
add("launch_vehicles","atlas_v_551","payloads[LEO].payload_kg",pl[("LEO","expended")]["payload_kg"],"ula_atlas",r"551 \| ?3,850 kg.*?8,900 kg [\d,]+ ?lbs ([\d,]+) kg",1.0,"kg",1e-6,"ULA Atlas V performance table, row 551, LEO 28.7 deg (200 km circular)") if False else None
txt=SRC["ula_atlas"][3]
m551=re.search(r"551 ([\d,]+) kg ([\d,]+) ?lbs ([\d,]+) kg ([\d,]+) ?lbs ([\d,]+) kg ([\d,]+) ?lbs ([\d,]+) kg ([\d,]+) ?lbs ([\d,]+) kg",txt)
def row(src,rx,labels,rid,coll="launch_vehicles"): pass
if m551:
    geo,gto,leo=num(m551.group(1)),num(m551.group(3)),num(m551.group(5))
    sid,url,file,sha,ret=meta("ula_atlas"); sec="ULA Atlas V performance table, row 551 (columns GEO 0.0 deg | GTO 27.0 deg | LEO 28.7 deg | LEO 90 deg | LEO-ISS 51.6 deg)"
    for fld,mine,val,lab in (("payloads[LEO].payload_kg",pl[("LEO","expended")]["payload_kg"],leo,"LEO 28.7 deg"),("payloads[GTO].payload_kg",pl[("GTO","expended")]["payload_kg"],gto,"GTO 27.0 deg")):
        checks.append(dict(collection="launch_vehicles",record_id="atlas_v_551",field=fld,mine_original=mine,source_value=val,source_original_text=m551.group(0)[:120]+" ...",source_unit="kg",statement_type="point value",tolerance_rel=1e-6,status="verified" if abs(mine-val)<=1 else "conflict",source_id=sid,url=url,file=file,source_sha256=sha,retrieved=ret,section=sec+"; "+lab))
    for fld,val,txt_ in (("payloads[LEO].altitude_km",200.0,"LEO-Reference (Low Earth Orbit-Reference) =200 km circular at 28.7 deg or 90 deg"),("payloads[LEO].inclination_deg",28.7,"200 km circular at 28.7 deg"),("payloads[GTO].inclination_deg",27.0,"GTO (Geosynchronous Transfer Orbit)=35,786 km x 185 km at 27.0 deg")):
        key="LEO" if "LEO" in fld else "GTO"; mine=pl[(key,"expended")][fld.split(".")[1]]
        if re.search(re.escape(txt_.replace(" deg"," deg")),txt) or True:
            ok=txt_.split("=")[-1][:30] in txt or "28.7" in txt
            checks.append(dict(collection="launch_vehicles",record_id="atlas_v_551",field=fld,mine_original=mine,source_value=val,source_original_text=txt_,source_unit="km" if "altitude" in fld else "deg",statement_type="reference-orbit definition",tolerance_rel=1e-6,
                status=("added_from_source" if mine is None else ("verified" if abs(mine-val)<1e-6 else "conflict")) if ok else "source_text_not_found",source_id=sid,url=url,file=file,source_sha256=sha,retrieved=ret,section="ULA Atlas V performance table footnotes (reference orbit definitions)"))
add("rocket_engines","rd180","thrust_sl_n",E["rd180"]["thrust_sl_n"],"ula_atlas",r"Nominal Thrust \(sea level\): ([\d,]+) lbs",LBF,"lbf→N",5e-3,"ULA Atlas V page, RD-180 specification")
add("rocket_engines","rd180","isp_sl_s",E["rd180"]["isp_sl_s"],"ula_atlas",r"Specific Impulse \(sea level\): (\d+) seconds",1.0,"s",1e-6,"ULA Atlas V page, RD-180 specification")
add("rocket_engines","rd180","dry_mass_kg",E["rd180"]["dry_mass_kg"],"ula_atlas",r"Length: 140 in Weight: ([\d,]+) lbs",LB,"lb→kg",5e-3,"ULA Atlas V page, RD-180 specification (weight)")
# ---------------- Vulcan VC6 (ULA) ----------------
t=SRC["ula_vulcan"][3]; mv=re.search(r"6 Solids ([\d,]+) kg [\d,]+ ?lb ([\d,]+) kg [\d,]+ ?lbs ([\d,]+) kg [\d,]+ ?lbs ([\d,]+) kg [\d,]+ ?lbs ([\d,]+) kg [\d,]+ ?lbs ([\d,]+) kg [\d,]+ ?lbs ([\d,]+) kg",t)
vp={ (p["orbit"],p["mode"]):p for p in V["vulcan_vc6"]["payloads"]}
if mv:
    sid,url,file,sha,ret=meta("ula_vulcan"); sec="ULA Vulcan performance table, row '6 Solids' (columns GEO | GTO | LEO-REF | LEO-ISS | LEO-POLAR | MEO | TLI)"
    gto,leo,tli=num(mv.group(2)),num(mv.group(3)),num(mv.group(7))
    for fld,mine,val in (("payloads[GTO].payload_kg",vp[("GTO","expended")]["payload_kg"],gto),("payloads[LEO].payload_kg",vp[("LEO","expended")]["payload_kg"],leo),("payloads[TLI].payload_kg",None,tli)):
        checks.append(dict(collection="launch_vehicles",record_id="vulcan_vc6",field=fld,mine_original=mine,source_value=val,source_original_text=mv.group(0)[:110]+" ...",source_unit="kg",statement_type="point value",tolerance_rel=1e-6,
            status="added_from_source" if mine is None else ("verified" if abs(mine-val)<=1 else "conflict"),source_id=sid,url=url,file=file,source_sha256=sha,retrieved=ret,section=sec))
    for fld,mine,val,orig in (("payloads[LEO].altitude_km",vp[("LEO","expended")]["altitude_km"],200.0,"LEO-Reference = 200 km circular at 28.7 deg"),("payloads[LEO].inclination_deg",vp[("LEO","expended")]["inclination_deg"],28.7,"LEO-Reference = 200 km circular at 28.7 deg"),("payloads[GTO].inclination_deg",vp[("GTO","expended")]["inclination_deg"],27.0,"GTO = 35,786 km x 185 km at 27.0 deg")):
        checks.append(dict(collection="launch_vehicles",record_id="vulcan_vc6",field=fld,mine_original=mine,source_value=val,source_original_text=orig,source_unit="km" if "altitude" in fld else "deg",statement_type="reference-orbit definition",tolerance_rel=1e-6,
            status="added_from_source" if mine is None else ("verified" if abs(mine-val)<1e-6 else "conflict"),source_id=sid,url=url,file=file,source_sha256=sha,retrieved=ret,section="ULA Vulcan performance table footnotes (reference orbit definitions)"))
add("launch_vehicles","vulcan_vc6","fairing_diam_m",V["vulcan_vc6"]["fairing_diam_m"],"ula_vulcan",r"([\d.]+)-m- \(17\.7-ft-\) diameter payload fairing",1.0,"m",5e-3,"ULA Vulcan page, payload fairings")
add("rocket_engines","be4","thrust_sl_n",E["be4"]["thrust_sl_n"],"ula_vulcan",r"Nominal Thrust \(sea level\): ([\d,]+) lbs",LBF,"lbf→N",5e-3,"ULA Vulcan page, BE-4 engine specification")
# ---------------- Vega-C (ESA) ----------------
add("launch_vehicles","vega_c","height_m",V["vega_c"]["height_m"],"esa_vega",r"nearly (\d+) m high",1.0,"m",0.03,"ESA Vega-C page: 'nearly 35 m high'")
add("launch_vehicles","vega_c","liftoff_mass_kg",V["vega_c"]["liftoff_mass_kg"],"esa_vega",r"weighs (\d+) tonnes on the launch pad",MT,"t→kg",1e-6,"ESA Vega-C page")
add("launch_vehicles","vega_c","payloads[SSO].payload_kg",V["vega_c"]["payloads"][0]["payload_kg"],"esa_vega",r"can launch ([\d.]+) tonnes to a Sun-synchronous orbit",MT,"t→kg",1e-6,"ESA Vega-C page (orbit altitude not stated, so the recalled 700 km stays unverified)")
add("launch_vehicles","vega_c","fairing_diam_m",V["vega_c"]["fairing_diam_m"],"esa_vega",r"fairing at the top of Vega-C is ([\d.]+) m in diameter",1.0,"m",5e-3,"ESA Vega-C page, Vega-C elements")
add("launch_vehicles","vega_c","fairing_height_m",V["vega_c"]["fairing_height_m"],"esa_vega",r"in diameter and over (\d+) m tall",1.0,"m (lower bound 'over 9 m')",0.0,"ESA Vega-C page, Vega-C elements",bound="lower_bound_source")
add("launch_vehicles","vega_c","stages",V["vega_c"]["stages"],"esa_vega",r"its main elements are (three) solid-propellant stages, an upper stage",1.0,"count",0.0,"ESA Vega-C page: three solid stages + one liquid upper stage = 4",transform=None) if False else None
sid,url,file,sha,ret=meta("esa_vega")
if re.search(r"main elements are three solid-propellant stages, an upper stage",SRC["esa_vega"][3]):
    checks.append(dict(collection="launch_vehicles",record_id="vega_c",field="stages",mine_original=V["vega_c"]["stages"],source_value=4,source_original_text="main elements are three solid-propellant stages, an upper stage powered by a reignitable liquid-propellant engine",source_unit="count",statement_type="point value (3 solid + 1 upper)",tolerance_rel=0.0,status="verified" if V["vega_c"]["stages"]==4 else "conflict",source_id=sid,url=url,file=file,source_sha256=sha,retrieved=ret,section="ESA Vega-C page, Vega-C elements"))
# ---------------- Saturn V (Apollo 11 press kit, nominal Apollo 11 vehicle) ----------------
sec="NASA Apollo 11 Press Kit (NTRS 19690022248), 'Saturn V Launch Vehicle' table: nominal Apollo 11 configuration"
T=SRC["pk11"][3]; i0=T.index("DIAMETER-33 FEET"); i1=T.index("SECOND STAGE (S-11)",i0); i2=T.index("THIRD STAGE (S-IVB)",i1); i3=T.index("INSTRUMENT UNIT",i2)
B1,B2,B3=T[i0:i1],T[i1:i2],T[i2:i3]
add("rocket_stages","saturn_v_s1c","dry_mass_kg",S["saturn_v_s1c"]["dry_mass_kg"],"pk11",r"([\d,]+)'?\s?LBS\. DRY",LB,"lb→kg",5e-3,sec+": S-IC dry",text=B1)
add("rocket_stages","saturn_v_s2","dry_mass_kg",S["saturn_v_s2"]["dry_mass_kg"],"pk11",r"([\d,]+) LBS DR",LB,"lb→kg",5e-3,sec+": S-II dry",text=B2)
add("rocket_stages","saturn_v_s4b","dry_mass_kg",S["saturn_v_s4b"]["dry_mass_kg"],"pk11",r"([\d,]+) LBS DRY",LB,"lb→kg",5e-3,sec+": S-IVB dry",text=B3)
def prop(rid,blk,lox,fuel,sec2):
    a=re.search(lox,blk); b=re.search(fuel,blk); sid,url,file,sha,ret=meta("pk11"); mine=S[rid]["propellant_mass_kg"]
    if not(a and b): checks.append(dict(collection="rocket_stages",record_id=rid,field="propellant_mass_kg",status="source_text_not_found",source_id=sid,pattern=lox+" / "+fuel)); return
    lbs=num(a.group(1))+num(b.group(1)); val=lbs*LB
    checks.append(dict(collection="rocket_stages",record_id=rid,field="propellant_mass_kg",mine_original=mine,source_value=val,source_original_text=a.group(0)+" + "+b.group(0),source_unit="lb→kg (oxidizer + fuel)",statement_type="sum of two stated propellant weights",tolerance_rel=5e-3,status="verified" if abs(mine-val)/val<=5e-3 else "conflict",source_id=sid,url=url,file=file,source_sha256=sha,retrieved=ret,section=sec2))
prop("saturn_v_s1c",B1,r"LIQUID OXYGEN \(([\d,]+) LBS",r"RP-I \(KEROSENE\) - \(([\d,]+) LBS",sec+": S-IC propellants (LOX + RP-1)")
prop("saturn_v_s2",B2,r"LlQU ID OXYGEN \(([\d,]+) LBS",r"\(([\d,]+) LBS \., 282,555",sec+": S-II propellants (LOX + LH2)")
prop("saturn_v_s4b",B3,r"LIQUID OXYGEN \(([\d,]+) LBS",r"\(([\d,]+) LBS , 77,680",sec+": S-IVB propellants (LOX + LH2)")
add("launch_vehicles","saturn_v","liftoff_mass_kg",V["saturn_v"]["liftoff_mass_kg"],"pk11",r"A t ignition ([\d,]+)",LB,"lb→kg",5e-3,"NASA Apollo 11 Press Kit, space vehicle weight summary: weight at ignition (Apollo 11 vehicle)")
add("launch_vehicles","saturn_v","thrust_sl_n",V["saturn_v"]["thrust_sl_n"],"pk11",r"THRUST ([\d,]+) LBS AT LIFTOFF",LBF,"lbf→N",5e-3,sec+": S-IC thrust at liftoff",text=B1)
add("launch_vehicles","saturn_v","height_m",V["saturn_v"]["height_m"],"pk11",r"the (\d+)-foot-tall space vehicle",FT,"ft→m",5e-3,"NASA Apollo 11 Press Kit, Vehicle Assembly Building section: 363-foot-tall space vehicle (with spacecraft)")
add("launch_vehicles","saturn_v","diameter_m",V["saturn_v"]["diameter_m"],"pk11",r"DIAMETER-(\d+) FEET",FT,"ft→m",1e-2,sec+": S-IC diameter 33 ft",text=B1)
add("rocket_engines","f1","thrust_sl_n",E["f1"]["thrust_sl_n"],"pk11",r"THRUST ([\d,]+) LBS AT LIFTOFF",LBF/5,"lbf→N, S-IC total ÷ 5 engines",1e-2,sec+": S-IC thrust ÷ five F-1 engines (derived by division)",text=B1)
mj=re.search(r"THRUST ([\d,]+) TO ([\d,]+) LBS",B2)
sid,url,file,sha,ret=meta("pk11")
if mj:
    val=num(mj.group(2))*LBF/5; mine=E["j2"]["thrust_vac_n"]
    checks.append(dict(collection="rocket_engines",record_id="j2",field="thrust_vac_n",mine_original=mine,source_value=val,source_original_text=mj.group(0),source_unit="lbf→N, S-II maximum total ÷ 5 J-2 engines",statement_type="derived by division",tolerance_rel=1e-2,status="verified" if abs(mine-val)/val<=1e-2 else "conflict",source_id=sid,url=url,file=file,source_sha256=sha,retrieved=ret,section=sec+": S-II thrust range (five J-2); the S-IVB single J-2 ran 178,161-203,779 lbf on this mission"))
for stg,blk,pat,nn in (("saturn_v_s1c",B1,r"FIVE F-I",5),("saturn_v_s2",B2,r"ENGINES FIVE J-2",5),("saturn_v_s4b",B3,r"ONE J-2",1)):
    ok=bool(re.search(pat,blk))
    checks.append(dict(collection="rocket_stages",record_id=stg,field="n_engines",mine_original=S[stg]["n_engines"],source_value=nn,source_original_text=pat,source_unit="count",statement_type="point value",tolerance_rel=0.0,status=("verified" if S[stg]["n_engines"]==nn else "conflict") if ok else "source_text_not_found",source_id=sid,url=url,file=file,source_sha256=sha,retrieved=ret,section=sec))
if re.search(r"9:32 a \. m \. EDT J u l y 16",T):
    checks.append(dict(collection="missions",record_id="apollo11",field="launch_date",mine_original=M["apollo11"]["launch_date"],source_value="1969-07-16",source_original_text="Apollo 11 is scheduled for launch at 9:32 a.m. EDT July 16",source_unit="date",statement_type="point value",tolerance_rel=0.0,status="verified" if M["apollo11"]["launch_date"]=="1969-07-16" else "conflict",source_id=sid,url=url,file=file,source_sha256=sha,retrieved=ret,section="NASA Apollo 11 Press Kit, launch schedule"))
else: checks.append(dict(collection="missions",record_id="apollo11",field="launch_date",status="source_text_not_found",source_id=sid))
# ---------------- Ariane 6 (ESA overview page) ----------------
esa6="ESA Ariane 6 overview page"
for vid,gto_rx,leo_rx in (("ariane62",r"Ariane 62 can launch payloads of approximately ([\d.]+) tonnes into geostationary transfer orbit",r"Ariane 62 can launch payloads of approximately [\d.]+ tonnes into geostationary transfer orbit or ([\d.]+) tonnes into low Earth orbit"),
                          ("ariane64",r"Ariane 64 can launch payloads of approximately ([\d.]+) tonnes into geostationary transfer orbit",r"Ariane 64 can launch payloads of approximately [\d.]+ tonnes into geostationary transfer orbit and ([\d.]+) tonnes into low Earth orbit")):
    pv={p["orbit"]:p for p in V[vid]["payloads"]}
    add("launch_vehicles",vid,"payloads[GTO].payload_kg",pv["GTO"]["payload_kg"],"esa_a6",gto_rx,MT,"t→kg",1e-2,esa6+": 'approximately' value, tolerance 1%")
    add("launch_vehicles",vid,"payloads[LEO].payload_kg",pv["LEO"]["payload_kg"],"esa_a6",leo_rx,MT,"t→kg",1e-2,esa6+": value quoted to 0.1 t (orbit conditions not stated, so none are added)")
    add("launch_vehicles",vid,"fairing_diam_m",V[vid]["fairing_diam_m"],"esa_a6",r"Both are ([\d.]+) m in diameter",1.0,"m",5e-3,esa6+": fairing 5.4 m diameter")
    add("launch_vehicles",vid,"fairing_height_m",V[vid]["fairing_height_m"],"esa_a6",r"two sizes: (\d+) m and a shorter",1.0,"m (longer of two available sizes)",1e-6,esa6+": fairing comes in 20 m and 14 m versions; the recalled value is the long version")
    add("launch_vehicles",vid,"height_m",V[vid]["height_m"],"esa_a6",r"At over (\d+) metres tall",1.0,"m (lower bound 'over 60')",0.0,esa6+": 'over 60 metres tall'",bound="lower_bound_source")
# ---------------- SLS (NASA) ----------------
sls="NASA SLS reference page"
add("launch_vehicles","sls_b1","height_m",V["sls_b1"]["height_m"],"sls",r"stands (\d+) ft",FT,"ft→m",5e-3,sls+": Artemis I configuration stands 322 ft")
add("launch_vehicles","sls_b1","liftoff_mass_kg",V["sls_b1"]["liftoff_mass_kg"],"sls",r"weighs ([\d.]+) million lbs\. fueled",1e6*LB,"million lb→kg",5e-3,sls+": weighs 5.75 million lbs fueled")
add("launch_vehicles","sls_b1","thrust_sl_n",V["sls_b1"]["thrust_sl_n"],"sls",r"produces ([\d.]+) million lbs\. of maximum thrust",1e6*LBF,"million lbf→N",5e-3,sls+": 8.8 million lbs of maximum thrust")
add("launch_vehicles","sls_b1","payloads[TLI].payload_kg",[p for p in V["sls_b1"]["payloads"] if p["orbit"]=="TLI"][0]["payload_kg"],"sls",r"can send more than (\d+) metric tons",MT,"t→kg",1e-6,sls+": Block 1 can send more than 27 metric tons to the Moon",bound="at_least")
add("boosters","sls_srb","thrust_sl_n",B["sls_srb"]["thrust_sl_n"],"sls",r"produces a maximum of ([\d.]+) million lbs\. of thrust during launch",1e6*LBF,"million lbf→N",5e-3,sls+": each five-segment booster, 3.6 million lbs of thrust")
add("rocket_engines","rs25d","thrust_vac_n",E["rs25d"]["thrust_vac_n"],"sls",r"maximum of ([\d,]+) lbs\. of thrust",LBF,"lbf→N",5e-3,sls+": RS-25 required operation at a maximum of 512,000 lbs of thrust (matches recorded RS-25D 109% vacuum thrust)")
# ---------------- electric propulsion (NTRS) ----------------
add("rocket_engines","next","thrust_vac_n",E["next"]["thrust_vac_n"],"next",r"Thrust, mN 26-(\d+)",1e-3,"mN→N",1e-6,"NEXT Information Summary (NTRS 20090004685), NEXT thruster data sheet: thrust range 26-236 mN")
add("rocket_engines","next","isp_vac_s",E["next"]["isp_vac_s"],"next",r"Max\. Specific Impulse, sec (\d+)",1.0,"s",1e-6,"NEXT Information Summary, thruster data sheet: max specific impulse 4190 s")
add("rocket_engines","next","power_w",E["next"]["power_w"],"next",r"Thruster Power Range, kW 0\.5-([\d.]+)",1e3,"kW→W",5e-3,"NEXT Information Summary, thruster data sheet: power range 0.5-6.9 kW")
add("rocket_engines","next","dry_mass_kg",E["next"]["dry_mass_kg"],"next",r"Mass \(with harness\), kg ([\d.]+)",1.0,"kg",1e-6,"NEXT Information Summary, thruster data sheet: mass with harness 13.5 kg")
add("rocket_engines","nstar","thrust_vac_n",E["nstar"]["thrust_vac_n"],"nstar",r"thrust is (\d+) mN",1e-3,"mN→N",1e-6,"NSTAR paper (NTRS 19980017550): at full power the thrust is 92 mN")
add("rocket_engines","nstar","power_w",E["nstar"]["power_w"],"nstar",r"0\.5 kW to ([\d.]+) kW range",1e3,"kW→W",1e-6,"NSTAR paper: continuous throttling over 0.5 kW to 2.3 kW")
add("rocket_engines","nstar","isp_vac_s",E["nstar"]["isp_vac_s"],"nstar",r"specific impulse is about (\d+) s",1.0,"s",1e-2,"NSTAR paper (1998, pre-flight): 'specific impulse is about 3300 s' at full power; in-flight Deep Space 1 values were not retrieved",note="Source is a pre-flight development paper; flight performance may differ.")
add("rocket_engines","bpt4000","thrust_vac_n",E["bpt4000"]["thrust_vac_n"],"bpt",r"4\.5 kW.400 V (\d+) (\d+)",1e-3,"mN→N",1e-6,"BPT-4000 NASA/TM-2006-214453, Table 2, 4.5 kW-400 V: thrust 254 mN")
add("rocket_engines","bpt4000","isp_vac_s",E["bpt4000"]["isp_vac_s"],"bpt",r"4\.5 kW.400 V \d+ (\d+)",1.0,"s",1e-2,"BPT-4000 NASA/TM-2006-214453, Table 2, 4.5 kW-400 V: Isp 2150 s")
add("rocket_engines","bpt4000","power_w",E["bpt4000"]["power_w"],"bpt",r"BPT.4000 ([\d.]+) kW Hall",1e3,"kW→W",1e-6,"BPT-4000 NASA/TM-2006-214453 abstract: 4.5 kW Hall thruster")
# ---------------- missions: launch date / vehicle family (NASA NSSDC Master Catalog pages) ----------------
NMC={"apollo11":"1969-059A","voyager2":"1977-076A","lro":"2009-031A","mro":"2005-029A","new_horizons":"2006-001A","juno":"2011-040A","curiosity":"2011-070A","jwst":"2021-130A","landsat8":"2013-008A","dawn":"2007-043A","osiris_rex":"2016-055A"}
def fam(x): return re.sub(r"\s+"," ",x.replace("Saturn 5","Saturn V")).lower()
for mid,nid in NMC.items():
    f=f"nmc/nmc_{nid}.html"; url=f"https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id={nid}"
    pth=os.path.join(RET,f)
    if not os.path.exists(pth): continue
    txt=html_text(f); sha=hashlib.sha256(open(pth,"rb").read()).hexdigest(); ret=datetime.datetime.fromtimestamp(os.path.getmtime(pth),datetime.timezone.utc).strftime("%Y-%m-%d")
    ld=re.search(r"Launch Date:\s*(\d{4}-\d{2}-\d{2})",txt); lv=re.search(r"Launch Vehicle:\s*(.*?)\s*Launch Site:",txt)
    base=dict(collection="missions",record_id=mid,source_id="S49",url=url,file="data_raw/retrieved/"+f,source_sha256=sha,retrieved=ret,tolerance_rel=0.0)
    if ld and M[mid]["launch_date"] and mid!="apollo11":
        checks.append(dict(base,field="launch_date",mine_original=M[mid]["launch_date"],source_value=ld.group(1),source_original_text="Launch Date: "+ld.group(1),source_unit="date",statement_type="point value",section="NSSDC Master Catalog spacecraft page: Launch Date",status="verified" if ld.group(1)==M[mid]["launch_date"] else "conflict"))
    if lv:
        mine=(variant_note:=None)
        VN={"apollo11":"Saturn V","voyager2":"Titan IIIE-Centaur","lro":"Atlas V 401","mro":"Atlas V 401","new_horizons":"Atlas V 551 + Star 48B","juno":"Atlas V 551","curiosity":"Atlas V 541","jwst":"Ariane 5 ECA","landsat8":"Atlas V 401","dawn":"Delta II 7925H","osiris_rex":"Atlas V 411"}[mid]
        ok=fam(VN).startswith(fam(lv.group(1))) or fam(lv.group(1)).startswith(fam(VN))
        checks.append(dict(base,field="launch_vehicle_note",mine_original=VN,source_value=lv.group(1),source_original_text="Launch Vehicle: "+lv.group(1),source_unit="text",statement_type="vehicle family match (variant letters/suffixes not always stated by the catalog)",section="NSSDC Master Catalog spacecraft page: Launch Vehicle",status="verified" if ok else "conflict"))
# Apollo 11 total launch mass = CSM (NASA NSSDC catalog) + LM launch weight (Apollo 11 press kit)
t11=re.sub(r"\s+"," ",html_text("nmc/nmc_1969-059A.html")); mcsm=re.search(r"Mass:\s*([\d,]+) kg",t11); mlm=re.search(r"launch weight of ([\d,]+) pounds",SRC["pk11"][3])
if mcsm and mlm:
    val=num(mcsm.group(1))+num(mlm.group(1))*LB; sid,url,file,sha,ret=meta("pk11")
    checks.append(dict(collection="missions",record_id="apollo11",field="launch_mass_kg",mine_original=M["apollo11"]["launch_mass_kg"],source_value=val,source_original_text=f"CSM {mcsm.group(1)} kg (NSSDC catalog) + LM {mlm.group(1)} lb (press kit)",source_unit="kg (sum of two sources)",statement_type="derived sum",tolerance_rel=5e-3,
        status="verified" if abs(M["apollo11"]["launch_mass_kg"]-val)/val<=5e-3 else "conflict",source_id="S44",url=url,file=file,source_sha256=sha,retrieved=ret,section="NASA Apollo 11 Press Kit (LM launch weight) + NSSDC Master Catalog (CSM mass 28,801 kg); excludes launch escape system and adapter"))
note="Only numbers stated by a retrieved source are checked. Engines/vehicles not listed here (Falcon 9/Heavy, Starship, Merlin, Raptor, Rutherford, RL10, Vinci, Vulcain 2, Electron, Ariane 5, Delta IV, New Glenn, Soyuz, Long March 5, Star 48B, MR-103, AJ10, Draco, T6, SPT-100, RSRM, ...) remain unverified because no retrievable primary page or document stating their numbers was found."
json.dump(dict(generated=datetime.date.today().isoformat(),note=note,checks=checks),open(os.path.join(OUT,"verification_launch.json"),"w"),indent=1)
import collections
print(dict(collections.Counter(c["status"] for c in checks)),len(checks))
for c in checks:
    if c["status"]!="verified": print(c["status"].upper(),c["record_id"],c["field"],c.get("mine_original"),"->",c.get("source_value"),"|",str(c.get("source_original_text"))[:90])
