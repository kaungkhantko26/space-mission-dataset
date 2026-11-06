// Node 18+ quickstart on the verified dataset. Works against the live static API (no install) or the local backend.
//   node examples/node_quickstart.mjs                                  (live GitHub Pages API)
//   BASE=http://127.0.0.1:8000 node examples/node_quickstart.mjs       (local backend: python3 tools/serve_api.py)
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const SpaceMissionAPI = require("../docs/client.js");
const base = process.env.BASE;

if (base) {                                    // local backend
  const j = (p, o) => fetch(base + p, o).then(r => r.json());
  const t = await j("/nhats/best?max_delta_v=6&min_size_m=100&limit=5");
  console.log("Lowest-delta-v NHATS targets >=100 m:", t.records.map(r => `${r.designation} ${r.min_delta_v_km_s} km/s / ${r.min_delta_v_trip_days} d`));
  const h = await j("/hohmann", { method: "POST", body: JSON.stringify({ body: "earth", altitude1_km: 400, altitude2_km: 35786 }) });
  console.log("LEO->GEO Hohmann:", h.total_m_s.toFixed(0), "m/s", `(GM ${h.gm_data_class})`);
  console.log("Mars light time:", (await j("/light-time?target=mars")).records[0].max_one_way_light_time_min.toFixed(1), "min max one-way");
} else {                                       // static API on GitHub Pages
  const api = new SpaceMissionAPI("https://kaungkhantko26.github.io/space-mission-dataset/api/v1");
  const stage = await api.expand(await api.get("rocket_stages", "saturn_v_s1c"));
  console.log("Saturn V S-IC:", stage.dry_mass_kg, "kg dry,", stage.data_class, "| engine record:", stage.engine_id);
  console.log("Search 'titan':", (await api.search("titan")).map(x => `${x.c}:${x.id}`).slice(0, 6));
}
