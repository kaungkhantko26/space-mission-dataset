// Node 18+ quickstart. Works against the live static API (no install) or the local backend.
//   node examples/node_quickstart.mjs                                  (live GitHub Pages API)
//   BASE=http://127.0.0.1:8000 node examples/node_quickstart.mjs       (local backend: python3 tools/serve_api.py)
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const SpaceMissionAPI = require("../docs/client.js");
const base = process.env.BASE;

if (base) {                                    // local backend
  const j = (p, o) => fetch(base + p, o).then(r => r.json());
  const eng = await j("/collections/rocket_engines?isp_vac_s_gte=440&sort=-isp_vac_s&fields=id,name,isp_vac_s,data_class");
  console.log("High-Isp engines:", eng.records.map(e => `${e.name} ${e.isp_vac_s}s [${e.data_class}]`));
  const opt = await j("/optimize?scenario=mars_orbiter&objective=balanced&w_science=2");
  console.log("Balanced Mars orbiter:", opt.best.wet_kg.toFixed(0), "kg,", opt.best.cost.toFixed(0), "credits");
  const sim = await j("/simulate", { method: "POST", body: JSON.stringify({ scenario: "mars_orbiter", design: opt.best.design, samples: 1000, seed: 1 }) });
  console.log("Monte Carlo success rate:", (100 * sim.success_rate).toFixed(1) + "%", sim.failure_reasons);
} else {                                       // static API on GitHub Pages
  const api = new SpaceMissionAPI("https://kaungkhantko26.github.io/space-mission-dataset/api/v1");
  const stage = await api.expand(await api.get("rocket_stages", "saturn_v_s1c"));
  console.log("Saturn V S-IC:", stage.dry_mass_kg, "kg dry,", stage.data_class, "| engine:", stage._linked.engine_id.record.name);
  console.log("Search 'titan':", (await api.search("titan")).map(x => `${x.c}:${x.id}`));
}
