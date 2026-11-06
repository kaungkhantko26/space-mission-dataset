#!/usr/bin/env python3
"""Benchmarks: (1) vectorized vs scalar exactness+speed, (2) heuristic solvers vs exact optimum, (3) scaling with instrument count. Deterministic seeds."""
import json, os, sys, time, random, statistics, copy, subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np, opt_model as O, vec_model as V
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","space-mission-research")
comb=json.load(open(ROOT+"/combined/all_space_mission_data.json")); cons=comb["optimization"]["constraints"]; G=cons["global_parameters"]
cat=dict(arrays=O.ARRAYS,batteries=O.BATTERIES,computers=O.COMPUTERS,comms=O.COMMS,props=O.PROPS)
out=dict(environment=dict(python=sys.version.split()[0],numpy=np.__version__,note="Single-run wall-clock times on the build sandbox; relative speedups matter more than absolute numbers."),equivalence=[],timing=[],heuristics=[],scaling=[])
OBJS=list(O.OBJECTIVES)
# 1 equivalence + speed
for sc in cons["scenarios"]:
    t=time.perf_counter(); D=O.enumerate_designs(G,sc,cat); t_s=time.perf_counter()-t
    t=time.perf_counter(); res={k:V.solve_vec(G,sc,cat,k) for k in OBJS}; t_v=time.perf_counter()-t
    mism=[]
    for k in OBJS:
        b=O.solve(D,k); v=res[k]; f=O.OBJECTIVES[k][1]
        if (b is None)!=(v is None) or (b and (b["design"]!=v[1] or abs(b[f]-v[0])>1e-9*max(1,abs(b[f])))): mism.append(k)
    out["equivalence"].append(dict(scenario_id=sc["id"],designs=len(D),objectives_compared=len(OBJS),mismatches=mism,exact_match=not mism))
    # single-pass timing of the vectorized evaluator over all designs
    n=len(sc["instruments"]); masks,B=V._bits(n); ia=V.instr_arrays(sc); t=time.perf_counter()
    for c in V.combos(sc,cat): V.evaluate_masks(G,sc,*c,B,ia)
    t_pass=time.perf_counter()-t
    out["timing"].append(dict(scenario_id=sc["id"],designs=len(D),scalar_python_enumerate_s=t_s,vectorized_one_full_pass_s=t_pass,speedup=t_s/t_pass))
# JS timing
js=subprocess.run(["node","-e","""const M=require('../docs/model.js'),D=require('../space-mission-research/combined/all_space_mission_data.json');const c=D.optimization.constraints;const r=[];
for(const sc of c.scenarios){const t=process.hrtime.bigint();const d=M.enumerate(c.global_parameters,sc,c.catalog);r.push({scenario_id:sc.id,designs:d.length,js_enumerate_s:Number(process.hrtime.bigint()-t)/1e9});}
console.log(JSON.stringify(r));"""],capture_output=True,text=True,cwd=os.path.dirname(os.path.abspath(__file__)))
jt={x["scenario_id"]:x for x in json.loads(js.stdout)}
for t in out["timing"]: t["js_enumerate_s"]=jt[t["scenario_id"]]["js_enumerate_s"]
# 2 heuristics vs exact (objective: balanced-free single objectives max_science, min_cost, max_feasibility_margin)
def rand_design(rng,sc):
    n=len(sc["instruments"]); 
    while True:
        mask=rng.randrange(1,1<<n); 
        prop=rng.choice(cat["props"])
        if prop["electric"] and not sc["allow_electric"]: continue
        return [mask,rng.randrange(3),rng.randrange(5),rng.randrange(2),rng.randrange(2),cat["props"].index(prop),rng.randrange(len(sc["vehicles"]))]
def ev(sc,x):
    mask=x[0]; sel=[i for i in range(len(sc["instruments"])) if mask>>i&1]
    return O.evaluate(G,sc,sel,cat["computers"][x[1]],cat["comms"][x[2]],cat["arrays"][x[3]],cat["batteries"][x[4]],cat["props"][x[5]],sc["vehicles"][x[6]])
def fit(r,field,sgn):  # lower better; infeasible penalised by violation count
    return (0,sgn*r[field]) if r["feasible"] else (1,len(r["violations"])+ (r["cost"]/1e9 if r["cost"]!=float("inf") else 1e3))
def neighbours(sc,x):
    n=len(sc["instruments"]); sizes=[None,3,5,2,2,3,len(sc["vehicles"])]
    for b in range(n): y=list(x); y[0]^=1<<b; 
    for b in range(n):
        y=list(x); y[0]^=1<<b
        if y[0]!=0: yield y
    for p in range(1,7):
        for v in range(sizes[p]):
            if v!=x[p]:
                y=list(x); y[p]=v
                if p==5 and cat["props"][v]["electric"] and not sc["allow_electric"]: continue
                yield y
def run_random(sc,field,sgn,budget,seed):
    rng=random.Random(seed); best=None
    for _ in range(budget):
        x=rand_design(rng,sc); r=ev(sc,x); f=fit(r,field,sgn)
        if best is None or f<best[0]: best=(f,r)
    return best
def run_hill(sc,field,sgn,budget,seed):
    rng=random.Random(seed); used=0; best=None
    while used<budget:
        x=rand_design(rng,sc); r=ev(sc,x); f=fit(r,field,sgn); used+=1
        improved=True
        while improved and used<budget:
            improved=False
            for y in neighbours(sc,x):
                ry=ev(sc,y); used+=1; fy=fit(ry,field,sgn)
                if fy<f: x,r,f,improved=y,ry,fy,True; break
                if used>=budget: break
        if best is None or f<best[0]: best=(f,r)
    return best
def run_ga(sc,field,sgn,budget,seed,pop=40):
    rng=random.Random(seed); P=[rand_design(rng,sc) for _ in range(pop)]; used=0; best=None
    def F(x):
        nonlocal used,best; r=ev(sc,x); used+=1; f=fit(r,field,sgn)
        if best is None or f<best[0]: best=(f,r)
        return f
    sc_=[(F(x),x) for x in P]
    sizes=[None,3,5,2,2,3,len(sc["vehicles"])]; n=len(sc["instruments"])
    while used<budget:
        sc_.sort(key=lambda t:t[0]); elite=[x for _,x in sc_[:pop//2]]; kids=[]
        while len(kids)<pop//2 and used+len(kids)<budget+pop:
            a,b=rng.sample(elite,2); y=[a[i] if rng.random()<.5 else b[i] for i in range(7)]
            y[0]=sum(((a[0]>>i&1) if rng.random()<.5 else (b[0]>>i&1))<<i for i in range(n))
            if rng.random()<.4: y[0]^=1<<rng.randrange(n)
            if y[0]==0: y[0]=1
            if rng.random()<.3:
                p=rng.randrange(1,7); y[p]=rng.randrange(sizes[p])
            if cat["props"][y[5]]["electric"] and not sc["allow_electric"]: y[5]=0
            kids.append(y)
        sc_=sc_[:pop//2]+[(F(y),y) for y in kids]
    return best
SOLVERS=dict(random_search=run_random,hill_climb_restarts=run_hill,genetic_algorithm=run_ga)
TARGETS=[("max_science","science",-1),("min_cost","cost",1),("min_mass","wet_kg",1)]
SEEDS=list(range(20))
for sc in cons["scenarios"]:
    n=len(sc["instruments"]); space=0; 
    for c in V.combos(sc,cat): space+=(1<<n)-1
    for key,field,sgn in TARGETS:
        exact=V.solve_vec(G,sc,cat,key)[0]
        for name,fn in SOLVERS.items():
            for budget in (500,2000):
                vals=[]; feas=0
                for s in SEEDS:
                    f,r=fn(sc,field,sgn,budget,s)
                    if f[0]==0: feas+=1; vals.append(r[field])
                hit=sum(1 for v in vals if abs(v-exact)<=1e-9*max(1,abs(exact)))
                gap=[abs(v-exact)/abs(exact) for v in vals]
                out["heuristics"].append(dict(scenario_id=sc["id"],objective=key,solver=name,evaluations=budget,design_space=space,fraction_of_space_evaluated=budget/space,runs=len(SEEDS),runs_feasible=feas,runs_found_exact_optimum=hit,median_gap_pct=(100*statistics.median(gap) if gap else None),exact_optimum=exact))
# 3 scaling: add synthetic clones of instruments (labelled synthetic) to grow the instrument count
sc0=[s for s in cons["scenarios"] if s["id"]=="lunar_orbiter"][0]
for n in (6,8,10,12,14,16):
    sc=copy.deepcopy(sc0); rng=random.Random(7); base=sc["instruments"]
    while len(sc["instruments"])<n:
        b=rng.choice(base); i=dict(b); i["id"]=b["id"]+f"_syn{len(sc['instruments'])}"; i["mass"]=b["mass"]*rng.uniform(.6,1.4); i["power"]=b["power"]*rng.uniform(.6,1.4); i["value"]=max(1,round(b["value"]*rng.uniform(.5,1.2)));i["cost"]=b["cost"]*rng.uniform(.6,1.4); i["synthetic"]=True; sc["instruments"].append(i)
    sc["instruments"]=sc["instruments"][:n]; sc["min_science"]=sc0["min_science"]; sc["budget"]=sc0["budget"]*(1+0.15*(n-6)/2)
    designs=sum((1<<n)-1 for _ in V.combos(sc,cat))
    t=time.perf_counter(); r=V.solve_vec(G,sc,cat,"max_science"); tv=time.perf_counter()-t
    ts=None
    if n<=8:
        t=time.perf_counter(); D=O.enumerate_designs(G,sc,cat); O.solve(D,"max_science"); ts=time.perf_counter()-t
    out["scaling"].append(dict(instruments=n,designs=designs,vectorized_exact_solve_s=tv,scalar_exact_solve_s=ts,optimum_science=(r[0] if r else None),note="synthetic instrument clones (not real data)"))
json.dump(out,open(ROOT+"/analysis/benchmark_results.json","w"),indent=1)

print(json.dumps(out["equivalence"])); print(json.dumps(out["timing"],indent=0)[:900]); print(json.dumps(out["scaling"]))
for h in out["heuristics"]:
    if h["evaluations"]==2000: print(h["scenario_id"],h["objective"],h["solver"],f'{h["runs_found_exact_optimum"]}/{h["runs"]} exact, feas {h["runs_feasible"]}, med gap {h["median_gap_pct"]}')
