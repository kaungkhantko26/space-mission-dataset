#!/usr/bin/env python3
"""Exports the combined dataset to hackathon-friendly formats: exports/csv/<collection>.csv and exports/space_mission.sqlite.
Nested objects are flattened to dotted columns; lists are stored as JSON text. Every table keeps data_class / confidence / source_ids."""
import json, os, csv, sqlite3
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,".."); OUT=os.path.join(ROOT,"exports")
D=json.load(open(os.path.join(ROOT,"space-mission-research","combined","all_space_mission_data.json")))
COL={"planets":D["celestial"]["planets"],"moons":D["celestial"]["moons"],"asteroids":D["celestial"]["asteroids"],"orbital_elements":D["celestial"]["orbital_elements"],"atmospheres":D["celestial"]["atmospheres"],
 "rocket_engines":D["propulsion"]["rocket_engines"],"electric_propulsion":D["propulsion"]["electric_propulsion"],"propellants":D["propulsion"]["propellants"],
 "launch_vehicles":D["launch"]["launch_vehicles"],"rocket_stages":D["launch"]["rocket_stages"],"boosters":D["launch"]["boosters"],"payload_capabilities":D["launch"]["payload_capabilities"],
 "components":D["spacecraft"]["components"],"ground_stations":D["spacecraft"]["ground_stations"],"instruments":D["instruments"],"missions":D["missions"]["historical"],
 "mission_profiles":D["missions"]["profiles"],"engineering_constraints":D["missions"]["engineering_constraints"],"spacex_launches":D["launch_history"]["launches"],"launch_sites":D["launch_history"]["sites"],
 "nasa_facilities":D["infrastructure"]["nasa_facilities"],"experiments":D["optimization"]["experiments"],"sources":D["metadata"]["sources"]}
def flat(o,pre=""):
    out={}
    for k,v in o.items():
        key=pre+k
        if isinstance(v,dict) and k not in ("field_verification",): out.update(flat(v,key+"."))
        elif isinstance(v,(list,dict)): out[key]=json.dumps(v,ensure_ascii=False)
        else: out[key]=v
    return out
os.makedirs(OUT+"/csv",exist_ok=True)
db=os.path.join(OUT,"space_mission.sqlite")
if os.path.exists(db): os.remove(db)
con=sqlite3.connect(db); n_rows=0
for name,recs in COL.items():
    rows=[flat(r) for r in recs]
    cols=[]; [cols.append(k) for r in rows for k in r if k not in cols]
    with open(f"{OUT}/csv/{name}.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); [w.writerow(r) for r in rows]
    def sqlname(c): return '"'+c.replace('"','""')+'"'
    con.execute(f'CREATE TABLE "{name}" ({", ".join(sqlname(c) for c in cols)})')
    con.executemany(f'INSERT INTO "{name}" VALUES ({",".join("?"*len(cols))})',[[ (r.get(c) if not isinstance(r.get(c),bool) else int(r.get(c))) for c in cols] for r in rows]); n_rows+=len(rows)
con.execute('CREATE TABLE _readme (note TEXT)'); con.execute("INSERT INTO _readme VALUES (?)",(D["metadata"]["quality"]["statement"],))
con.commit(); con.close()
print(f"exported {len(COL)} tables, {n_rows} rows -> exports/csv and exports/space_mission.sqlite")
