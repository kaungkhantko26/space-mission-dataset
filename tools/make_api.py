#!/usr/bin/env python3
"""Generates a static, versioned JSON API under docs/api/v1/ from the combined dataset (GitHub Pages serves it with CORS *)."""
import json, os, shutil
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,"..","space-mission-research"); OUT=os.path.join(HERE,"..","docs","api","v1")
D=json.load(open(ROOT+"/combined/all_space_mission_data.json"))
shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT)
W=lambda p,o: (os.makedirs(os.path.dirname(os.path.join(OUT,p)),exist_ok=True), json.dump(o,open(os.path.join(OUT,p),"w"),indent=1,ensure_ascii=False))
COL={ # name -> (records, description, id field)
 "planets":(D["celestial"]["planets"],"Sun, planets, dwarf planets (SI)"),"moons":(D["celestial"]["moons"],"Major moons"),"asteroids":(D["celestial"]["asteroids"],"Selected small bodies"),
 "orbital_elements":([dict(r,id=r["body_id"]) for r in D["celestial"]["orbital_elements"]],"Orbital elements with epochs"),"atmospheres":(D["celestial"]["atmospheres"],"Atmosphere summaries"),
 "rocket_engines":(D["propulsion"]["rocket_engines"],"Chemical engines/motors/thrusters"),"electric_propulsion":(D["propulsion"]["electric_propulsion"],"Ion and Hall thrusters"),"propellants":(D["propulsion"]["propellants"],"Propellant densities"),
 "launch_vehicles":(D["launch"]["launch_vehicles"],"Launch vehicles"),"rocket_stages":(D["launch"]["rocket_stages"],"Stages"),"boosters":(D["launch"]["boosters"],"Boosters"),
 "components":(D["spacecraft"]["components"],"Spacecraft component classes and named items"),"ground_stations":(D["spacecraft"]["ground_stations"],"Ground stations"),
 "instruments":(D["instruments"],"Science instruments"),"missions":(D["missions"]["historical"],"Historical missions"),"mission_profiles":(D["missions"]["profiles"],"Hypothetical analysis scenarios"),
 "engineering_constraints":(D["missions"]["engineering_constraints"],"Constraint statements"),"experiments":(D["optimization"]["experiments"],"27 optimization experiments"),"spacex_launches":(D["launch_history"]["launches"],"SpaceX launch table 2010-2018 (user-supplied, normalized)"),"launch_sites":(D["launch_history"]["sites"],"Launch pads"),"nasa_facilities":(D["infrastructure"]["nasa_facilities"],"NASA facilities (user-supplied, normalized; category derived)"),
 "sources":(D["metadata"]["sources"],"Source catalog (none retrieved)"),
}
BANNER=D["metadata"]["quality"]["statement"]
idx=[]; search=[]
for name,(recs,desc) in COL.items():
    ids=[r["id"] for r in recs]; assert len(ids)==len(set(ids)),name
    W(f"{name}.json",dict(collection=name,description=desc,count=len(recs),data_status=BANNER,records=recs))
    for r in recs:
        W(f"{name}/{r['id']}.json",dict(collection=name,data_status=BANNER,record=r))
        search.append(dict(c=name,id=r["id"],name=r.get("name") or r.get("statement") or r["id"]))
    idx.append(dict(collection=name,description=desc,count=len(recs),url=f"{name}.json",record_url_template=f"{name}/{{id}}.json"))
W("search-index.json",dict(count=len(search),items=search))
sc=D["optimization"]["constraints"]["scenarios"]
W("optimization/scenarios.json",dict(scenarios=sc,global_parameters=D["optimization"]["constraints"]["global_parameters"],catalog=D["optimization"]["constraints"]["catalog"],note=D["optimization"]["constraints"]["cost_note"]+" "+D["optimization"]["constraints"]["science_note"]))
for p in D["optimization"]["pareto"]: W(f"optimization/pareto/{p['scenario_id']}.json",p)
W("optimization/sensitivity.json",dict(results=D["optimization"]["sensitivity"]))
W("optimization/uncertainty.json",dict(results=D["optimization"]["uncertainty"]))
W("optimization/models.json",D["optimization"]["models"])
ANALYSIS=dict(D["analysis"]); ANALYSIS["spacex_launch"]=D["launch_history"]["analysis"]; ANALYSIS["nasa_facilities"]=D["infrastructure"]["analysis"]
_bm=os.path.join(ROOT,"analysis","benchmark_results.json")
if os.path.exists(_bm): ANALYSIS["benchmark"]=json.load(open(_bm))
for k,v in ANALYSIS.items(): W(f"analysis/{k}.json",v)
W("missions/trajectory_reference.json",dict(records=D["missions"]["trajectory_reference"]))
W("quality.json",D["metadata"]["quality"])
extra=["search-index.json","optimization/scenarios.json","optimization/sensitivity.json","optimization/uncertainty.json","optimization/models.json","quality.json","missions/trajectory_reference.json"]+[f"optimization/pareto/{p['scenario_id']}.json" for p in D["optimization"]["pareto"]]+[f"analysis/{k}.json" for k in ANALYSIS]
W("index.json",dict(api="Space Mission Research Data API",version="v1",type="static JSON (read-only, CORS-enabled on GitHub Pages)",data_status=BANNER,license_note="Add a LICENSE before redistribution; underlying facts come from public sources that were not retrieved.",
   openapi="openapi.json",collections=idx,other_endpoints=extra,conventions=["SI units; unit-suffixed field names","null = not recorded","every record has data_class/confidence/source_ids/retrieval_status","ids are lowercase snake_case and unique within a collection"]))
# OpenAPI 3.0
rec={"type":"object","required":["id"],"properties":{"id":{"type":"string"},"data_class":{"enum":["verified","derived","estimated","fictional","unverified"]},"confidence":{"enum":["low","medium","high"]},"source_ids":{"type":"array","items":{"type":"string"}},"retrieval_status":{"type":"string"}},"additionalProperties":True}
paths={"/index.json":{"get":{"summary":"API index (collections, endpoints, data status)","responses":{"200":{"description":"OK"}}}},"/search-index.json":{"get":{"summary":"Lightweight id/name index for client-side search","responses":{"200":{"description":"OK"}}}},"/quality.json":{"get":{"summary":"Quality/completeness/known-conflict report","responses":{"200":{"description":"OK"}}}}}
for name,(recs,desc) in COL.items():
    paths[f"/{name}.json"]={"get":{"summary":f"List {name}: {desc}","tags":[name],"responses":{"200":{"description":"Collection","content":{"application/json":{"schema":{"type":"object","properties":{"collection":{"type":"string"},"count":{"type":"integer"},"records":{"type":"array","items":{"$ref":"#/components/schemas/Record"}}}}}}}}}}
    paths[f"/{name}/{{id}}.json"]={"get":{"summary":f"Get one {name} record","tags":[name],"parameters":[{"name":"id","in":"path","required":True,"schema":{"type":"string","enum":[r["id"] for r in recs]}}],"responses":{"200":{"description":"Record"},"404":{"description":"Unknown id"}}}}
for p,s in [("/optimization/scenarios.json","Scenarios, global parameters and component catalog for the optimizer"),("/optimization/sensitivity.json","One-at-a-time sensitivity results"),("/optimization/uncertainty.json","Monte Carlo results"),("/optimization/models.json","Model/equation documentation"),("/missions/trajectory_reference.json","Derived delta-v and transfer references")]:
    paths[p]={"get":{"summary":s,"tags":["optimization & analysis"],"responses":{"200":{"description":"OK"}}}}
paths["/optimization/pareto/{scenario_id}.json"]={"get":{"summary":"Pareto front for a scenario","tags":["optimization & analysis"],"parameters":[{"name":"scenario_id","in":"path","required":True,"schema":{"type":"string","enum":[s["id"] for s in sc]}}],"responses":{"200":{"description":"OK"}}}}
paths["/analysis/{name}.json"]={"get":{"summary":"Analysis result","tags":["optimization & analysis"],"parameters":[{"name":"name","in":"path","required":True,"schema":{"type":"string","enum":list(ANALYSIS.keys())}}],"responses":{"200":{"description":"OK"}}}}
W("openapi.json",{"openapi":"3.0.3","info":{"title":"Space Mission Research Data API","version":"1.0.0","description":"Static read-only JSON API. "+BANNER},"servers":[{"url":"https://kaungkhantko26.github.io/space-mission-dataset/api/v1","description":"GitHub Pages"},{"url":"http://localhost:8000/api/v1","description":"Local (python3 -m http.server in docs/)"}],"paths":paths,"components":{"schemas":{"Record":rec}}})
n=sum(len(r) for r,_ in COL.values()); print("api built:",len(COL),"collections,",n,"records")
