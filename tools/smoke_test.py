#!/usr/bin/env python3
"""Starts tools/serve_api.py on a free port and exercises every endpoint (also used by CI). Exit code 0 = all passed."""
import json, subprocess, sys, os, time, urllib.request, urllib.error, socket, sqlite3
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,"..")
s=socket.socket(); s.bind(("127.0.0.1",0)); port=s.getsockname()[1]; s.close()
proc=subprocess.Popen([sys.executable,os.path.join(HERE,"serve_api.py"),"--port",str(port)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
base=f"http://127.0.0.1:{port}"; res=[]
def call(path,body=None):
    req=urllib.request.Request(base+path,data=(json.dumps(body).encode() if body is not None else None),headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=60) as r: return r.status,json.load(r)
    except urllib.error.HTTPError as e: return e.code,json.load(e)
def t(name,ok,detail=""): res.append(ok); print(("PASS" if ok else "FAIL"),name,detail)
try:
    for _ in range(50):
        try: urllib.request.urlopen(base+"/health",timeout=1); break
        except Exception: time.sleep(0.2)
    c,j=call("/health"); t("health",c==200 and j["status"]=="ok")
    c,j=call("/collections"); t("collections lists 20+ collections",c==200 and len(j)>=20 and j["planets"]==12,str(len(j)))
    c,j=call("/collections/rocket_engines?isp_vac_s_gte=440&sort=-isp_vac_s&fields=id,isp_vac_s,data_class"); t("filter+sort+fields",c==200 and all(r["isp_vac_s"]>=440 for r in j["records"]) and j["records"][0]["isp_vac_s"]>=j["records"][-1]["isp_vac_s"],str(j["total"]))
    c,j=call("/collections/planets?data_class=verified&limit=3"); t("filter by data_class=verified",c==200 and j["total"]==12 and len(j["records"])==3)
    c,j=call("/collections/launch_vehicles/saturn_v"); t("record by id (Saturn V liftoff thrust corrected to NASA source)",c==200 and abs(j["record"]["thrust_sl_n"]-34046038.8)<1e3)
    c,j=call("/collections/planets/nope"); t("404 for unknown id",c==404)
    c,j=call("/verified"); t("verified index",c==200 and len(j["planets"])==12 and "rocket_stages" in j,str({k:len(v) for k,v in j.items()}))
    c,j=call("/optimize?scenario=lunar_orbiter&objective=min_mass"); t("optimize min_mass (matches stored experiment)",c==200 and abs(j["best"]["wet_kg"]-[e for e in json.load(open(os.path.join(ROOT,"space-mission-research/optimization/optimized_configurations.json")))["records"] if e["id"]=="opt_lunar_orbiter_min_mass"][0]["objective_value"])<1e-6)
    c,j=call("/optimize?scenario=mars_orbiter&objective=balanced&w_science=3&budget_scale=1.2"); t("optimize balanced with weights",c==200 and j["best"] is not None)
    c,j=call("/optimize?scenario=leo_eo&objective=bogus"); t("bad objective -> 400",c==400)
    c,j=call("/pareto?scenario=leo_eo"); t("pareto front",c==200 and j["front_size"]>=5)
    best=call("/optimize?scenario=leo_eo&objective=max_feasibility_margin")[1]["best"]["design"]
    c,j=call("/simulate",dict(scenario="leo_eo",design=best,samples=500,seed=7)); t("simulate success rate in [0,1]",c==200 and 0<=j["success_rate"]<=1,f'{j["success_rate"]:.3f}')
    c,j=call("/delta-v",dict(isp_s=310,m0_kg=1000,mf_kg=400)); t("delta-v (Tsiolkovsky)",c==200 and abs(j["delta_v_m_s"]-310*9.80665*__import__("math").log(2.5))<1e-6)
    db=os.path.join(ROOT,"exports","space_mission.sqlite")
    if os.path.exists(db):
        con=sqlite3.connect(db); n=con.execute("select count(*) from planets where data_class='verified'").fetchone()[0]; t("sqlite export readable",n==12,str(n))
finally: proc.terminate()
print(f"{sum(res)}/{len(res)} passed"); sys.exit(0 if all(res) else 1)
