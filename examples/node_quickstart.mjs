// Node 18+ quickstart on the verified, game-scoped dataset. Works against the live static API (no install) or the local backend.
//   node examples/node_quickstart.mjs                                  (live GitHub Pages API)
//   BASE=http://127.0.0.1:8000 node examples/node_quickstart.mjs       (local backend: python3 tools/serve_api.py)
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const SpaceMissionAPI = require("../docs/client.js");
const base = process.env.BASE;

if (base) {                                    // local backend
  const j = (p, o) => fetch(base + p, o).then(r => r.json());
  const v = await j("/collections/launch_vehicle_configs?active=true&leo_capacity_kg_gte=15000&sort=-leo_capacity_kg&fields=full_name,leo_capacity_kg,launch_cost_usd&limit=5");
  console.log("Heavy active launchers:", v.records.map(r => `${r.full_name} ${r.leo_capacity_kg} kg`));
  const h = await j("/hohmann", { method: "POST", body: JSON.stringify({ body: "earth", altitude1_km: 400, altitude2_km: 35786 }) });
  console.log("LEO->GEO Hohmann:", h.total_m_s.toFixed(0), "m/s", `(GM ${h.gm_data_class})`);
  console.log("Mars light time:", (await j("/light-time?target=mars")).records[0].max_one_way_light_time_min.toFixed(1), "min max one-way");
} else {                                       // static API on GitHub Pages
  const api = new SpaceMissionAPI("https://kaungkhantko26.github.io/space-mission-dataset/api/v1");
  const mars = await api.get("planets", "mars");
  console.log("Mars:", mars.gravitational_parameter_km3_s2, "km3/s2;", mars.nssdc_fact_sheet.numeric["Solar irradiance (W/m 2 )"], "W/m2", `[${mars.data_class}]`);
  console.log("Search 'titan':", (await api.search("titan")).map(x => `${x.c}:${x.id}`).slice(0, 6));
}
