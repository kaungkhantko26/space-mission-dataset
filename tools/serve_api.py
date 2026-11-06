#!/usr/bin/env python3
"""Local backend for the STRICT verified dataset (Python standard library only; no install needed).
    python3 tools/serve_api.py [--port 8000] [--host 127.0.0.1]

GET  /health
GET  /collections                                   -> names + counts
GET  /collections/{c}?q=text&field=value&field_gte=&field_lte=&sort=-field&limit=20&offset=0&fields=id,name
GET  /collections/{c}/{id}
GET  /light-time?target=mars                        -> one-way light-time range from verified orbits
POST /delta-v   {"isp_s":310,"m0_kg":1000,"mf_kg":400}  or  {"isp_s":310,"delta_v_m_s":4000,"mf_kg":500}
POST /hohmann   {"body":"earth","altitude1_km":400,"altitude2_km":35786}   (uses verified GM and radius)
CORS is open. Everything served is verified (see data_class / field_verification / provenance); nothing estimated or fictional."""
import json, os, sys, math, argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,".."); V=os.path.join(ROOT,"verified")
G0=9.80665
def load():
    cols={}
    for f in sorted(os.listdir(V)):
        if f.endswith(".json") and f not in ("quality_report.json","validation_report.json"): cols[f[:-5]]=json.load(open(os.path.join(V,f)))
    return cols
RAW=load(); COL={k:v["records"] for k,v in RAW.items()}
C=json.load(open(os.path.join(V,"combined","verified_space_mission_data.json"))); BANNER=C["metadata"]["quality"]["statement"]
BODY={r["id"]:r for k in ("planets","moons") for r in COL[k]}
def get(o,path):
    for k in path.split("."):
        if not isinstance(o,dict) or k not in o: return None
        o=o[k]
    return o
def num(x):
    try: return float(x)
    except: return None
def query_collection(name,q):
    p=lambda k:(q.get(k) or [None])[0]; text=p("q"); reserved={"q","sort","limit","offset","fields"}; out=[]
    for r in COL[name]:
        if text and text.lower() not in json.dumps(r).lower(): continue
        ok=True
        for k,vals in q.items():
            if k in reserved: continue
            vv=vals[0]
            if k.endswith("_gte") or k.endswith("_lte"):
                x=get(r,k[:-4]); n=num(vv)
                if x is None or n is None or (k.endswith("_gte") and x<n) or (k.endswith("_lte") and x>n): ok=False
            else:
                v=get(r,k)
                if v is None or str(v).lower()!=vv.lower(): ok=False
            if not ok: break
        if ok: out.append(r)
    s=p("sort")
    if s:
        key=s.lstrip("-"); have=[r for r in out if get(r,key) is not None]; miss=[r for r in out if get(r,key) is None]
        have.sort(key=lambda r:get(r,key),reverse=s.startswith("-")); out=have+miss
    total=len(out); off=int(p("offset") or 0); lim=min(int(p("limit") or 100),5000); out=out[off:off+lim]
    if p("fields"): out=[{f:get(r,f) for f in p("fields").split(",")} for r in out]
    resp=dict(collection=name,total=total,offset=off,limit=lim,data_status=BANNER,records=out)
    if RAW[name].get("provenance"): resp["provenance"]=RAW[name]["provenance"]
    return resp
def delta_v(b):
    isp=float(b["isp_s"])
    if "delta_v_m_s" in b:
        MR=math.exp(float(b["delta_v_m_s"])/(isp*G0)); mf=float(b["mf_kg"]); return dict(mass_ratio=MR,m0_kg=mf*MR,propellant_kg=mf*(MR-1),note="ideal Tsiolkovsky; no tank mass or losses")
    return dict(delta_v_m_s=isp*G0*math.log(float(b["m0_kg"])/float(b["mf_kg"])),note="ideal Tsiolkovsky; no gravity/drag losses")
def hohmann(b):
    body=BODY[b["body"]]; mu=body["gravitational_parameter_km3_s2"]; R=body["mean_radius_m"]/1e3; r1=R+float(b["altitude1_km"]); r2=R+float(b["altitude2_km"]); at=(r1+r2)/2
    v1=math.sqrt(mu/r1); v2=math.sqrt(mu/r2); d1=abs(math.sqrt(mu*(2/r1-1/at))-v1); d2=abs(v2-math.sqrt(mu*(2/r2-1/at)))
    return dict(body=b["body"],gm_km3_s2=mu,gm_data_class=body["data_class"],mean_radius_km=R,circular_velocity_1_m_s=v1*1e3,dv1_m_s=d1*1e3,dv2_m_s=d2*1e3,total_m_s=(d1+d2)*1e3,transfer_time_s=math.pi*math.sqrt(at**3/mu),
                data_class="derived",note="coplanar circular-to-circular impulsive transfer from verified GM and radius")
class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def send(self,code,obj):
        data=json.dumps(obj,ensure_ascii=False,default=str).encode()
        self.send_response(code); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_OPTIONS(self): self.send(204,{})
    def do_GET(self):
        u=urlparse(self.path); q=parse_qs(u.query); parts=[x for x in u.path.split("/") if x]
        try:
            if not parts or parts==["health"]: return self.send(200,dict(status="ok",mode="STRICT: verified data only",data_status=BANNER,endpoints=["/collections","/collections/{c}","/collections/{c}/{id}","/light-time","POST /delta-v","POST /hohmann"]))
            if parts==["collections"]: return self.send(200,{k:len(v) for k,v in COL.items()})
            if parts[0]=="collections" and len(parts)==2:
                return self.send(200,query_collection(parts[1],q)) if parts[1] in COL else self.send(404,dict(error="unknown collection",collections=list(COL)))
            if parts[0]=="collections" and len(parts)==3:
                r=[x for x in COL.get(parts[1],[]) if x.get("id")==parts[2]]; return self.send(200,dict(collection=parts[1],record=r[0],data_status=BANNER)) if r else self.send(404,dict(error="not found"))
            if parts==["light-time"]:
                t=(q.get("target") or [None])[0]; rs=[x for x in C["analysis"]["light_time"] if t is None or x["target"]==t]; return self.send(200,dict(records=rs)) if rs else self.send(404,dict(error="targets: "+", ".join(x["target"] for x in C["analysis"]["light_time"])))
            return self.send(404,dict(error="not found"))
        except Exception as e: return self.send(400,dict(error=str(e)))
    def do_POST(self):
        try:
            n=int(self.headers.get("Content-Length") or 0); body=json.loads(self.rfile.read(n) or b"{}"); p=urlparse(self.path).path.strip("/")
            if p=="delta-v": return self.send(200,delta_v(body))
            if p=="hohmann": return self.send(200,hohmann(body))
            return self.send(404,dict(error="not found"))
        except Exception as e: return self.send(400,dict(error=str(e)))
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--port",type=int,default=8000); ap.add_argument("--host",default="127.0.0.1"); a=ap.parse_args()
    print(f"Space Mission API (verified data only) on http://{a.host}:{a.port}  (Ctrl+C to stop)"); ThreadingHTTPServer((a.host,a.port),H).serve_forever()
