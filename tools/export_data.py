#!/usr/bin/env python3
"""Exports the STRICT verified dataset (verified/*.json) to exports/csv/<collection>.csv and exports/space_mission.sqlite.
Nested objects are flattened to dotted columns; lists/provenance dicts are kept as JSON text."""
import json, os, csv, sqlite3
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,".."); V=os.path.join(ROOT,"verified"); OUT=os.path.join(ROOT,"exports")
import shutil; shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT+"/csv")
def flat(o,pre=""):
    out={}
    for k,v in o.items():
        key=pre+k
        if isinstance(v,dict) and k not in ("field_verification","provenance"): out.update(flat(v,key+"."))
        elif isinstance(v,(list,dict)): out[key]=json.dumps(v,ensure_ascii=False)
        else: out[key]=v
    return out
db=os.path.join(OUT,"space_mission.sqlite"); con=sqlite3.connect(db); n_rows=0; names=[]
for f in sorted(os.listdir(V)):
    if not f.endswith(".json") or f in ("quality_report.json","validation_report.json"): continue
    name=f[:-5]; recs=json.load(open(os.path.join(V,f)))["records"]; rows=[flat(r) for r in recs]
    cols=[]; [cols.append(k) for r in rows for k in r if k not in cols]
    with open(f"{OUT}/csv/{name}.csv","w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); [w.writerow(r) for r in rows]
    q=lambda c:'"'+c.replace('"','""')+'"'
    con.execute(f'CREATE TABLE "{name}" ({", ".join(q(c) for c in cols)})')
    con.executemany(f'INSERT INTO "{name}" VALUES ({",".join("?"*len(cols))})',[[ (r.get(c) if not isinstance(r.get(c),bool) else int(r.get(c))) for c in cols] for r in rows]); n_rows+=len(rows); names.append(name)
con.execute("CREATE TABLE _readme (note TEXT)"); con.execute("INSERT INTO _readme VALUES (?)",(json.load(open(os.path.join(V,"quality_report.json")))["statement"],)); con.commit(); con.close()
print(f"exported {len(names)} tables, {n_rows} rows (verified data only) -> exports/csv and exports/space_mission.sqlite")
