#!/usr/bin/env python3
"""Field-level verification of SLS-related launch records against the retrieved NASA SLS reference page (data_raw/retrieved/nasa_sls_reference.html).
Only the numbers that the page actually states are checked. Output: space-mission-research/metadata/verification_launch.json"""
import re, html, json, os, hashlib, datetime
HERE=os.path.dirname(os.path.abspath(__file__)); RET=os.path.join(HERE,"..","data_raw","retrieved"); OUT=os.path.join(HERE,"..","space-mission-research","metadata")
FILE="nasa_sls_reference.html"; URL="https://www.nasa.gov/reference/space-launch-system/"
raw=open(os.path.join(RET,FILE),encoding="utf-8",errors="replace").read()
txt=re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",re.sub(r"<script.*?</script>|<style.*?</style>","",raw,flags=re.S))))
sha=hashlib.sha256(open(os.path.join(RET,FILE),"rb").read()).hexdigest(); ret=datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(RET,FILE)),datetime.timezone.utc).strftime("%Y-%m-%d")
LBF=4.4482216152605; FT=0.3048; LB=0.45359237; MT=1000.0
import sys; sys.path.insert(0,HERE); import data_prop_launch as DP
V={v["id"]:v for v in DP.VEHICLES}; B={b["id"]:b for b in DP.BOOSTERS}; E={e["id"]:e for e in DP.ENGINES}
checks=[]
def find(rx):
    m=re.search(rx,txt); return m
def add(coll,rid,field,mine,pattern,scale,unit,tol,section,bound=None):
    m=find(pattern)
    if not m: checks.append(dict(collection=coll,record_id=rid,field=field,status="source_text_not_found",pattern=pattern)); return
    val=float(m.group(1).replace(",",""))*scale
    if bound=="at_least": ok=mine<=val*(1+tol) and mine>=val*(1-tol)
    else: ok=abs(mine-val)/val<=tol
    checks.append(dict(collection=coll,record_id=rid,field=field,mine_original=mine,source_value=val,source_original_text=m.group(0),source_unit=unit,statement_type=("lower bound ('more than')" if bound=="at_least" else "point value"),
        tolerance_rel=tol,status="verified" if ok else "conflict",source_id="S41",url=URL,file="data_raw/retrieved/"+FILE,source_sha256=sha,retrieved=ret,section=section))
add("launch_vehicles","sls_b1","height_m",V["sls_b1"]["height_m"],r"stands (\d+) ft",FT,"ft→m",5e-3,"SLS reference page: Artemis I configuration stands 322 ft")
add("launch_vehicles","sls_b1","liftoff_mass_kg",V["sls_b1"]["liftoff_mass_kg"],r"weighs ([\d.]+) million lbs\. fueled",1e6*LB,"million lb→kg",5e-3,"SLS reference page: weighs 5.75 million lbs fueled")
add("launch_vehicles","sls_b1","thrust_sl_n",V["sls_b1"]["thrust_sl_n"],r"produces ([\d.]+) million lbs\. of maximum thrust",1e6*LBF,"million lbf→N",5e-3,"SLS reference page: 8.8 million lbs of maximum thrust")
tli=[p for p in V["sls_b1"]["payloads"] if p["orbit"]=="TLI"][0]["payload_kg"]
add("launch_vehicles","sls_b1","payloads[TLI].payload_kg",tli,r"can send more than (\d+) metric tons",MT,"t→kg",1e-6,"SLS reference page: Block 1 can send more than 27 metric tons to the Moon",bound="at_least")
add("boosters","sls_srb","thrust_sl_n",B["sls_srb"]["thrust_sl_n"],r"produces a maximum of ([\d.]+) million lbs\. of thrust during launch",1e6*LBF,"million lbf→N",5e-3,"SLS reference page: each five-segment booster produces a maximum of 3.6 million lbs of thrust")
add("rocket_engines","rs25d","thrust_vac_n",E["rs25d"]["thrust_vac_n"],r"maximum of ([\d,]+) lbs\. of thrust",LBF,"lbf→N",5e-3,"SLS reference page: RS-25 required operation at a maximum of 512,000 lbs of thrust (SLS RS-25 requirement; same level as the recorded RS-25D 109% vacuum thrust)")
note="Only values stated on the retrieved NASA page are checked. Block 1 LEO capacity (95 t), stage masses, Isp, dry masses and all non-SLS vehicles remain unverified."
json.dump(dict(generated=datetime.date.today().isoformat(),note=note,checks=checks),open(os.path.join(OUT,"verification_launch.json"),"w"),indent=1)
for c in checks: print(c["status"],c["record_id"],c["field"],c.get("mine_original"),"vs",c.get("source_value"),"|",c.get("source_original_text"))
