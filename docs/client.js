/* Space Mission Research Data API — JavaScript client (browser or Node 18+). No dependencies.
 *   <script src="client.js"></script>   const api = new SpaceMissionAPI();           // defaults to the site this script is served from
 *   const api = new SpaceMissionAPI("https://kaungkhantko26.github.io/space-mission-dataset/api/v1");
 * All data are UNVERIFIED unless a record says otherwise: always read record.data_class / confidence. */
(function (root, factory) { if (typeof module !== "undefined" && module.exports) module.exports = factory(); else root.SpaceMissionAPI = factory(); })(typeof self !== "undefined" ? self : this, function () {
  // foreign-key fields -> collections they point to (the API's "linkage")
  const LINKS = {
    engine_id: ["rocket_engines", "electric_propulsion"], vehicle_id: ["launch_vehicles"], launch_vehicle_id: ["launch_vehicles"],
    instrument_ids: ["instruments"], parent_id: ["planets", "moons"], body_id: ["planets", "moons"],
    launch_site_id: ["launch_sites"], source_ids: ["sources"], scenario_id: ["mission_profiles"]
  };
  class SpaceMissionAPI {
    constructor(base) {
      if (!base) base = (typeof location !== "undefined") ? new URL("api/v1", location.href.replace(/[^/]*$/, "")).href : "https://kaungkhantko26.github.io/space-mission-dataset/api/v1";
      this.base = base.replace(/\/$/, ""); this._cache = new Map();
    }
    async _get(path) {
      if (this._cache.has(path)) return this._cache.get(path);
      const r = await fetch(`${this.base}/${path}`);
      if (!r.ok) throw new Error(`GET ${path} -> ${r.status}`);
      const j = await r.json(); this._cache.set(path, j); return j;
    }
    index() { return this._get("index.json"); }
    openapi() { return this._get("openapi.json"); }
    quality() { return this._get("quality.json"); }
    async list(collection) { return (await this._get(`${collection}.json`)).records; }
    async get(collection, id) { return (await this._get(`${collection}/${id}.json`)).record; }
    async search(text, limit = 25) {
      const q = text.toLowerCase(), ix = (await this._get("search-index.json")).items;
      return ix.filter(i => (i.name + " " + i.id).toLowerCase().includes(q)).slice(0, limit);
    }
    scenarios() { return this._get("optimization/scenarios.json"); }
    pareto(scenarioId) { return this._get(`optimization/pareto/${scenarioId}.json`); }
    analysis(name) { return this._get(`analysis/${name}.json`); }
    /** Follow foreign keys one level: returns the record plus `_linked` { field: record(s) }. */
    async expand(record) {
      const linked = {};
      for (const [field, targets] of Object.entries(LINKS)) {
        const val = record[field]; if (val == null) continue;
        const ids = Array.isArray(val) ? val : [val], out = [];
        for (const id of ids) {
          for (const c of targets) { try { out.push({ collection: c, record: await this.get(c, id) }); break; } catch (e) { /* try next collection */ } }
        }
        if (out.length) linked[field] = Array.isArray(val) ? out : out[0];
      }
      return Object.assign({}, record, { _linked: linked });
    }
    /** Convenience: ideal delta-v (Tsiolkovsky) for any engine record; returns null when Isp is missing (never guessed). */
    idealDeltaV(engine, m0, mf) { return engine.isp_vac_s ? engine.isp_vac_s * 9.80665 * Math.log(m0 / mf) : null; }
  }
  SpaceMissionAPI.LINKS = LINKS;
  return SpaceMissionAPI;
});
