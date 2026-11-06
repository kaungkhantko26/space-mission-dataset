"""Python client for the Space Mission Research Data API (stdlib only).

    from spacemission_client import SpaceMissionAPI
    api = SpaceMissionAPI()                                   # live GitHub Pages site
    api = SpaceMissionAPI("docs/api/v1")                      # offline: a local folder (after running tools/make_api.py)
    mars = api.get("planets", "mars"); api.expand(api.get("rocket_stages", "f9_s1"))

All data are UNVERIFIED unless a record says otherwise: check record["data_class"] and record["confidence"].
"""
import json, os, urllib.request

DEFAULT_BASE = "https://kaungkhantko26.github.io/space-mission-dataset/api/v1"
LINKS = {  # foreign-key field -> collections it points to
    "engine_id": ["rocket_engines", "electric_propulsion"], "vehicle_id": ["launch_vehicles"], "launch_vehicle_id": ["launch_vehicles"],
    "instrument_ids": ["instruments"], "parent_id": ["planets", "moons", "asteroids"], "body_id": ["planets", "moons", "asteroids"],
    "launch_site_id": ["launch_sites"], "source_ids": ["sources"], "scenario_id": ["mission_profiles"],
}

class SpaceMissionAPI:
    def __init__(self, base=DEFAULT_BASE):
        self.base = base.rstrip("/"); self._cache = {}

    def _get(self, path):
        if path in self._cache: return self._cache[path]
        if self.base.startswith(("http://", "https://")):
            with urllib.request.urlopen(urllib.request.Request(f"{self.base}/{path}", headers={"User-Agent": "spacemission-client/1.0"}), timeout=30) as r:
                data = json.load(r)
        else:
            with open(os.path.join(self.base, path), encoding="utf-8") as f: data = json.load(f)
        self._cache[path] = data; return data

    def index(self): return self._get("index.json")
    def list(self, collection): return self._get(f"{collection}.json")["records"]
    def get(self, collection, id): return self._get(f"{collection}/{id}.json")["record"]
    def search(self, text, limit=25):
        q = text.lower(); return [i for i in self._get("search-index.json")["items"] if q in (i["name"] + " " + i["id"]).lower()][:limit]
    def scenarios(self): return self._get("optimization/scenarios.json")
    def pareto(self, scenario_id): return self._get(f"optimization/pareto/{scenario_id}.json")
    def analysis(self, name): return self._get(f"analysis/{name}.json")

    def expand(self, record):
        """Follow foreign keys one level; adds '_linked'."""
        linked = {}
        for field, targets in LINKS.items():
            val = record.get(field)
            if val is None: continue
            out = []
            for id_ in (val if isinstance(val, list) else [val]):
                for c in targets:
                    try: out.append({"collection": c, "record": self.get(c, id_)}); break
                    except Exception: continue
            if out: linked[field] = out if isinstance(val, list) else out[0]
        return {**record, "_linked": linked}

    @staticmethod
    def ideal_delta_v(engine, m0, mf):
        """Tsiolkovsky delta-v in m/s; None when Isp is not recorded (never guessed)."""
        import math
        return engine["isp_vac_s"] * 9.80665 * math.log(m0 / mf) if engine.get("isp_vac_s") else None

if __name__ == "__main__":
    import sys
    api = SpaceMissionAPI(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE)
    ix = api.index(); print(ix["api"], ix["version"], "-", len(ix["collections"]), "collections")
    print("search 'falcon':", [i["id"] for i in api.search("falcon")][:5])
    st = api.expand(api.get("rocket_stages", "f9_s1")); print("f9_s1 engine ->", st["_linked"]["engine_id"]["record"]["name"])
