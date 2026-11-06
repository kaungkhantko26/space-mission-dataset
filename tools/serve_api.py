#!/usr/bin/env python3
"""Local backend for the Space Mission dataset (Python standard library only; no install needed).
    python3 tools/serve_api.py [--port 8000] [--host 127.0.0.1]

GET  /health
GET  /collections                                  -> names + counts
GET  /collections/{c}?q=text&data_class=verified&field=value&sort=-mass_kg&limit=20&offset=0&fields=id,name
GET  /collections/{c}/{id}
GET  /verified                                     -> every record whose data_class is 'verified', all collections
GET  /scenarios                                    -> optimizer scenarios, catalog, global parameters
GET  /optimize?scenario=lunar_orbiter&objective=balanced&budget_scale=1&mga=0.2&dv_margin=0.05&power_margin=0.15&w_mass=1&w_cost=1&w_science=1
GET  /pareto?scenario=lunar_orbiter&budget_scale=1
POST /simulate  {"scenario":"mars_orbiter","design":{...},"samples":2000,"seed":1}   -> Monte Carlo success rate
POST /delta-v   {"isp_s":310,"m0_kg":1000,"mf_kg":400}  or  {"isp_s":310,"delta_v_m_s":4000,"mf_kg":500}
CORS is open. Records keep data_class / confidence / source_ids: please show them in your UI. Same model as docs/model.js (parity-tested)."""
import json, os, sys, math, random, copy, re, argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import opt_model as O
from astro import G0
ROOT=os.path.join(HERE,"..")
D=json.load(open(os.path.join(ROOT,"space-mission-research","combined","all_space_mission_data.json")))
COL={"planets":D["celestial"]["planets"],"moons":D["celestial"]["moons"],"asteroids":D["celestial"]["asteroids"],"orbital_elements":[dict(r,id=r["body_id"]) for r in D["celestial"]["orbital_elements"]],"atmospheres":D["celestial"]["atmospheres"],
 "rocket_engines":D["propulsion"]["rocket_engines"],"electric_propulsion":D["propulsion"]["electric_propulsion"],"propellants":D["propulsion"]["propellants"],
 "launch_vehicles":D["launch"]["launch_vehicles"],"rocket_stages":D["launch"]["rocket_stages"],"boosters":D["launch"]["boosters"],
 "components":D["spacecraft"]["components"],"ground_stations":D["spacecraft"]["ground_stations"],"instruments":D["instruments"],"missions":D["missions"]["historical"],
 "mission_profiles":D["missions"]["profiles"],"engineering_constraints":D["missions"]["engineering_constraints"],"spacex_launches":D["launch_history"]["launches"],"launch_sites":D["launch_history"]["sites"],
 "nasa_facilities":D["infrastructure"]["nasa_facilities"],"experiments":D["optimization"]["experiments"],"sources":D["metadata"]["sources"]}
CONS=D["optimization"]["constraints"]; SC={s["id"]:s for s in CONS["scenarios"]}
CAT=dict(arrays=O.ARRAYS,batteries=O.BATTERIES,computers=O.COMPUTERS,comms=O.COMMS,props=O.PROPS)
BANNER=D["metadata"]["quality"]["statement"]
def get(o,path):
    for k in path.split("."):
        if not isinstance(o,dict) or k not in o: return None
        o=o[k]
    return o
def num(x):
    try: return float(x)
    except: return None
def query_collection(name,q):
    recs=COL[name]; p=lambda k:(q.get(k) or [None])[0]
    text=p("q")
    reserved={"q","sort","limit","offset","fields"}
    out=[]
    for r in recs:
        if text and text.lower() not in json.dumps(r).lower(): continue
        ok=True
        for k,vals in q.items():
            if k in reserved: continue
            v=get(r,k); vv=vals[0]
            if k.endswith("_gte") or k.endswith("_lte"):
                base=k[:-4]; x=get(r,base); n=num(vv)
                if x is None or n is None or (k.endswith("_gte") and x<n) or (k.endswith("_lte") and x>n): ok=False
            elif v is None or str(v).lower()!=vv.lower(): ok=False
            if not ok: break
        if ok: out.append(r)
    s=p("sort")
    if s:
        desc=s.startswith("-"); key=s.lstrip("-")
        out.sort(key=lambda r:(get(r,key) is None,get(r,key) if get(r,key) is not None else 0),reverse=False)
        if desc: out=[r for r in out if get(r,key) is not None][::-1]+[r for r in out if get(r,key) is None]
    total=len(out); off=int(p("offset") or 0); lim=int(p("limit") or 100)
    out=out[off:off+lim]
    if p("fields"):
        fs=p("fields").split(","); out=[{f:get(r,f) for f in fs} for r in out]
    return dict(collection=name,total=total,offset=off,limit=lim,data_status=BANNER,records=out)
def scenario_with(q):
    sc=copy.deepcopy(SC[q["scenario"][0]]); G=dict(CONS["global_parameters"])
    f=lambda k,d: float(q[k][0]) if k in q else d
    sc["budget"]*=f("budget_scale",1.0); sc["min_science"]*=f("science_scale",1.0)
    G["mga"]=f("mga",G["mga"]); G["dv_margin"]=f("dv_margin",G["dv_margin"]); G["power_margin"]=f("power_margin",G["power_margin"]); G["launch_margin"]=f("launch_margin",G["launch_margin"])
    return G,sc
def clean(d):
    if d is None: return None
    r={k:v for k,v in d.items() if k!="design"}; r["design"]=d["design"]
    for k,v in list(r.items()):
        if isinstance(v,float) and (math.isinf(v) or math.isnan(v)): r[k]=None
    return r
def optimize(q):
    G,sc=scenario_with(q); D_=O.enumerate_designs(G,sc,CAT); feas=sum(1 for d in D_ if d["feasible"]); obj=(q.get("objective") or ["balanced"])[0]
    if obj=="balanced": best=O.balanced(D_,dict(wet_kg=float((q.get("w_mass") or [1])[0]),cost=float((q.get("w_cost") or [1])[0]),science=float((q.get("w_science") or [1])[0])))
    elif obj in O.OBJECTIVES: best=O.solve(D_,obj)
    else: raise ValueError("objective must be 'balanced' or one of "+", ".join(O.OBJECTIVES))
    return dict(scenario=sc["id"],objective=obj,designs_evaluated=len(D_),designs_feasible=feas,optimum_scope="global optimum within the finite catalog and model (exhaustive enumeration)",best=clean(best),delta_v_m_s=sc["dv_ms"],data_status=BANNER)
def pareto(q):
    G,sc=scenario_with(q); D_=O.enumerate_designs(G,sc,CAT); fr=sorted(O.pareto(D_),key=lambda d:d["wet_kg"])
    return dict(scenario=sc["id"],objectives=["wet_kg (min)","cost (min)","science (max)"],front_size=len(fr),points=[clean(d) for d in fr])
def simulate(body):
    sc=copy.deepcopy(SC[body["scenario"]]); G=dict(CONS["global_parameters"]); d=body["design"]; N=int(body.get("samples",2000)); rng=random.Random(int(body.get("seed",1)))
    cm={k:{x["id"]:x for x in v} for k,v in dict(a=O.ARRAYS,b=O.BATTERIES,c=O.COMPUTERS,m=O.COMMS,p=O.PROPS).items()}
    sel=[[i["id"] for i in sc["instruments"]].index(x) for x in d["instruments"]]; veh=[v for v in sc["vehicles"] if v["id"]==d["vehicle"]][0]
    ok=0; reasons={}; wets=[]; costs=[]
    for _ in range(N):
        g=dict(G); g["mga"]=rng.uniform(0.10,0.35); g["dv_margin"]=rng.uniform(0,0.10); g["power_margin"]=rng.uniform(0.05,0.25)
        s=copy.deepcopy(sc); sh=rng.gauss(0,1.5); s["gt_db"]={k:v+sh for k,v in s["gt_db"].items()}; s["dv_ms"]*=rng.triangular(0.95,1.10,1.0)
        r=O.evaluate(g,s,sel,cm["c"][d["computer"]],cm["m"][d["comm"]],cm["a"][d["array"]],cm["b"][d["battery"]],cm["p"][d["propulsion"]],veh)
        c=r["cost"]*rng.triangular(0.9,1.4,1.0); fails=[v for v in r["violations"] if v!="exceeds_budget"]
        if c>sc["budget"]: fails.append("exceeds_budget")
        for f in fails: reasons[f]=reasons.get(f,0)+1
        ok+=not fails; wets.append(r["wet_kg"]); costs.append(c)
    wets.sort(); costs.sort(); q=lambda a,p:a[min(len(a)-1,int(p*len(a)))]
    return dict(scenario=sc["id"],samples=N,seed=int(body.get("seed",1)),success_rate=ok/N,failure_reasons=reasons,wet_kg_p50=q(wets,.5),wet_kg_p95=q(wets,.95),cost_p50=q(costs,.5),cost_p95=q(costs,.95),
        assumptions="mga~U(0.10,0.35); dv margin~U(0,0.10); power margin~U(0.05,0.25); G/T~N(0,1.5 dB); dv scale~Tri(0.95,1.10,1.0); cost growth~Tri(0.9,1.4,1.0). Assumed, not measured.")
def delta_v(b):
    isp=float(b["isp_s"])
    if "delta_v_m_s" in b:
        MR=math.exp(float(b["delta_v_m_s"])/(isp*G0)); mf=float(b["mf_kg"]); return dict(mass_ratio=MR,m0_kg=mf*MR,propellant_kg=mf*(MR-1))
    return dict(delta_v_m_s=isp*G0*math.log(float(b["m0_kg"])/float(b["mf_kg"])),note="ideal Tsiolkovsky; no gravity/drag losses")
class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def send(self,code,obj):
        data=json.dumps(obj,ensure_ascii=False,default=str).encode()
        self.send_response(code); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_OPTIONS(self): self.send(204,{})
    def do_GET(self):
        u=urlparse(self.path); q=parse_qs(u.query); parts=[x for x in u.path.split("/") if x]
        try:
            if not parts or parts==["health"]: return self.send(200,dict(status="ok",data_status=BANNER,endpoints=["/collections","/collections/{c}","/collections/{c}/{id}","/verified","/scenarios","/optimize","/pareto","POST /simulate","POST /delta-v"]))
            if parts==["collections"]: return self.send(200,{k:len(v) for k,v in COL.items()})
            if parts[0]=="collections" and len(parts)==2:
                if parts[1] not in COL: return self.send(404,dict(error="unknown collection",collections=list(COL)))
                return self.send(200,query_collection(parts[1],q))
            if parts[0]=="collections" and len(parts)==3:
                r=[x for x in COL.get(parts[1],[]) if x.get("id")==parts[2]]
                return self.send(200,dict(collection=parts[1],record=r[0],data_status=BANNER)) if r else self.send(404,dict(error="not found"))
            if parts==["verified"]: return self.send(200,{k:[r["id"] for r in v if r.get("data_class")=="verified"] for k,v in COL.items() if any(r.get("data_class")=="verified" for r in v)})
            if parts==["scenarios"]: return self.send(200,dict(scenarios=CONS["scenarios"],global_parameters=CONS["global_parameters"],catalog=CONS["catalog"],note=CONS["cost_note"]+" "+CONS["science_note"]))
            if parts==["optimize"]:
                if "scenario" not in q or q["scenario"][0] not in SC: return self.send(400,dict(error="scenario is required",scenarios=list(SC)))
                return self.send(200,optimize(q))
            if parts==["pareto"]:
                if "scenario" not in q or q["scenario"][0] not in SC: return self.send(400,dict(error="scenario is required",scenarios=list(SC)))
                return self.send(200,pareto(q))
            return self.send(404,dict(error="not found"))
        except Exception as e: return self.send(400,dict(error=str(e)))
    def do_POST(self):
        try:
            n=int(self.headers.get("Content-Length") or 0); body=json.loads(self.rfile.read(n) or b"{}"); p=urlparse(self.path).path.strip("/")
            if p=="simulate": return self.send(200,simulate(body))
            if p=="delta-v": return self.send(200,delta_v(body))
            return self.send(404,dict(error="not found"))
        except Exception as e: return self.send(400,dict(error=str(e)))
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--port",type=int,default=8000); ap.add_argument("--host",default="127.0.0.1"); a=ap.parse_args()
    print(f"Space Mission API on http://{a.host}:{a.port}  (Ctrl+C to stop)"); ThreadingHTTPServer((a.host,a.port),H).serve_forever()
