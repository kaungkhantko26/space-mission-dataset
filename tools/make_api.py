#!/usr/bin/env python3
"""Generates the static, versioned JSON API under docs/api/v1/ from the STRICT verified dataset (verified/). Served by GitHub Pages with CORS *."""
import json, os, shutil
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,".."); V=os.path.join(ROOT,"verified"); OUT=os.path.join(ROOT,"docs","api","v1")
C=json.load(open(os.path.join(V,"combined","verified_space_mission_data.json"))); BANNER=C["metadata"]["quality"]["statement"]
shutil.rmtree(os.path.join(ROOT,"docs","api"),ignore_errors=True); os.makedirs(OUT)
W=lambda p,o:(os.makedirs(os.path.dirname(os.path.join(OUT,p)),exist_ok=True),json.dump(o,open(os.path.join(OUT,p),"w"),separators=(",",":"),ensure_ascii=False))
DESC=dict(planets="Sun, planets, dwarf planets (verified fields only)",moons="Moons (verified GM, radius, mass)",asteroids="Bennu, Vesta (verified)",orbital_elements="Planet/dwarf-planet orbital elements (verified)",
 rocket_engines="Engines with verified fields only",electric_propulsion="NEXT, NSTAR, BPT-4000 (verified)",launch_vehicles="Launch vehicles, verified fields only",rocket_stages="Saturn V stages (verified)",boosters="SLS booster (verified field)",
 payload_capabilities="Verified payload capacities with stated reference orbits",missions="Missions: verified launch dates / vehicle families",nasa_facilities="Official NASA Facilities table (data.nasa.gov; contact data not ingested)",
 nhats_targets="JPL NHATS accessible near-Earth targets: min delta-v, durations (7,185)",neo_catalog="JPL SBDB near-Earth objects with measured diameter (1,265)",moon_mean_elements="JPL mean orbital elements of planetary satellites",smallsat_components="NASA SoA 2026 component/product tables (1,724 rows; vendor-reported)",smallsat_tables="Index of SoA tables and columns",nasa_missions="39 missions from the NASA NSSDC catalog",nasa_instruments="181 instruments/experiments (NASA catalog descriptions)",atmospheres="NSSDC fact-sheet atmospheres",launch_vehicle_configs="532 launch vehicle configurations (Launch Library 2; aggregator)",spacex_launch_history="743 SpaceX launches (Launch Library 2; aggregator)",fluid_properties="NIST saturation properties of six fluids",sources="Retrieved sources with file hashes")
names=[f[:-5] for f in sorted(os.listdir(V)) if f.endswith(".json") and f not in ("quality_report.json","validation_report.json")]
search=[]; idx=[]; BIG=800
for n in names:
    d=json.load(open(os.path.join(V,n+".json"))); recs=d["records"]
    body=dict(collection=n,description=DESC.get(n,n),count=len(recs),mode="STRICT: verified data only",data_status=BANNER,**({"provenance":d["provenance"]} if "provenance" in d else {}),records=recs)
    W(f"{n}.json",body)
    per_record=len(recs)<=BIG
    if per_record:
        for r in recs: W(f"{n}/{r['id']}.json",dict(collection=n,data_status=BANNER,record=r))
    for r in recs: search.append(dict(c=n,id=r["id"],name=r.get("name") or r.get("full_name") or r.get("facility") or r.get("satellite") or r.get("designation") or r["id"]))
    idx.append(dict(collection=n,description=DESC.get(n,n),count=len(recs),url=f"{n}.json",record_url_template=(f"{n}/{{id}}.json" if per_record else None),note=(None if per_record else "large collection: use the collection file")))
W("search-index.json",dict(count=len(search),items=search))
W("analysis/light_time.json",dict(records=C["analysis"]["light_time"]))
W("missions/trajectory_reference.json",dict(records=C["missions"]["trajectory_reference"])); W("quality.json",C["metadata"]["quality"])
vr=os.path.join(V,"validation_report.json");
if os.path.exists(vr): W("validation.json",json.load(open(vr)))
extra=["search-index.json","analysis/light_time.json","missions/trajectory_reference.json","quality.json","validation.json"]
W("index.json",dict(api="Space Mission Research Data API (verified-only)",version="v1",mode="STRICT: verified data only",type="static JSON (read-only, CORS-enabled on GitHub Pages)",data_status=BANNER,openapi="openapi.json",collections=idx,other_endpoints=extra,
   conventions=["SI units unless the field name says otherwise (NHATS delta-v in km/s, durations in days; SBDB diameters in km; JPL satellite elements in km/deg/days)","null = not recorded","every record is verified against, or ingested directly from, a retrieved source","ids are unique within a collection"],license_note="See LICENSE-DATA.md"))
rec={"type":"object","required":["id"],"properties":{"id":{"type":"string"},"data_class":{"const":"verified"},"source_ids":{"type":"array","items":{"type":"string"}},"retrieval_status":{"type":"string"}},"additionalProperties":True}
paths={"/index.json":{"get":{"summary":"API index","responses":{"200":{"description":"OK"}}}},"/search-index.json":{"get":{"summary":"id/name index for client-side search","responses":{"200":{"description":"OK"}}}},"/quality.json":{"get":{"summary":"Quality report","responses":{"200":{"description":"OK"}}}}}
for n in names:
    paths[f"/{n}.json"]={"get":{"summary":f"List {n}: {DESC.get(n,n)}","tags":[n],"responses":{"200":{"description":"Collection","content":{"application/json":{"schema":{"type":"object","properties":{"collection":{"type":"string"},"count":{"type":"integer"},"records":{"type":"array","items":{"$ref":"#/components/schemas/Record"}}}}}}}}}}
    if any(i["collection"]==n and i["record_url_template"] for i in idx): paths[f"/{n}/{{id}}.json"]={"get":{"summary":f"Get one {n} record","tags":[n],"parameters":[{"name":"id","in":"path","required":True,"schema":{"type":"string"}}],"responses":{"200":{"description":"Record"},"404":{"description":"Unknown id"}}}}
for p,s in (("/analysis/light_time.json","One-way light-time ranges derived from verified orbits"),("/missions/trajectory_reference.json","Delta-v and transfer references derived from verified constants")):
    paths[p]={"get":{"summary":s,"tags":["analysis"],"responses":{"200":{"description":"OK"}}}}
W("openapi.json",{"openapi":"3.0.3","info":{"title":"Space Mission Research Data API (verified-only)","version":"1.0.0","description":"Static read-only JSON API. "+BANNER},"servers":[{"url":"https://kaungkhantko26.github.io/space-mission-dataset/api/v1"},{"url":"http://localhost:8001/api/v1"}],"paths":paths,"components":{"schemas":{"Record":rec}}})
# files the static site loads
os.makedirs(os.path.join(ROOT,"docs","data"),exist_ok=True)
shutil.copy(os.path.join(V,"combined","verified_space_mission_data.json"),os.path.join(ROOT,"docs","data","all_space_mission_data.json"))
for f in ("smallsat_components.json","nasa_instruments.json","launch_vehicle_configs.json","spacex_launch_history.json"): shutil.copy(os.path.join(V,f),os.path.join(ROOT,"docs","data",f))
if os.path.exists(vr): shutil.copy(vr,os.path.join(ROOT,"docs","data","validation_report.json"))
print("api built:",len(names),"collections,",sum(len(json.load(open(os.path.join(V,n+'.json')))['records']) for n in names),"records")
