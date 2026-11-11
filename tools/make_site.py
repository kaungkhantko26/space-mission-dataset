#!/usr/bin/env python3
"""Generate the static site pages (minimal monospace design): index, datasets, api, equations, guide.  explorer.html is the interactive app shell.
Run: python3 tools/make_site.py   (also called by make_guide.py / make site)"""
import html, json, os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DOCS = os.path.join(ROOT, "docs")
SITE = "https://kaungkhantko26.github.io/space-mission-dataset"
GH = "https://github.com/kaungkhantko26/space-mission-dataset"
RAW = "https://raw.githubusercontent.com/kaungkhantko26/space-mission-dataset/main"
NAV = [("index.html", "home"), ("datasets.html", "datasets"), ("api.html", "api"), ("equations.html", "equations"), ("guide.html", "guide"), ("explorer.html", "explorer")]


def shell(title, active, body, script="", desc="Verified space-mission engineering data for the Space Mission Design Game"):
    nav = " ".join(f'<a href="{h}"{" aria-current=page" if h == active else ""}>{n}</a>' for h, n in NAV) + f' <a href="{GH}">github</a>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="stylesheet" href="style.css"></head>
<body>
<header><a class="brand" href="index.html">space-mission-dataset</a><nav class="top">{nav}</nav></header>
<main>
{body}
</main>
<footer>verified data only &middot; <a href="{GH}/blob/main/LICENSE-DATA.md">licences</a> &middot; <a href="{GH}">source</a> &middot; not endorsed by NASA</footer>
{script}
</body></html>
'''


def load_index():
    return json.load(open(os.path.join(DOCS, "api", "v1", "index.json")))


def inline(t):
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", t)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)


def render_md(lines):
    out, i = [], 0
    slug = lambda t: re.sub(r"[^a-z0-9]+", "-", re.sub(r"^\d+\.\s*", "", t.lower())).strip("-")
    while i < len(lines):
        l = lines[i]
        if l.startswith("```"):
            j = i + 1; code = []
            while not lines[j].startswith("```"): code.append(lines[j]); j += 1
            out.append("<pre>" + html.escape("\n".join(code)) + "</pre>"); i = j + 1; continue
        if l.startswith("# "): i += 1; continue
        m = re.match(r"(#{2,3}) (.*)", l)
        if m:
            out.append(f'<h{len(m.group(1))} id="{slug(m.group(2))}">{inline(m.group(2))}</h{len(m.group(1))}>'); i += 1; continue
        if l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            out.append('<div class="tw"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr></thead><tbody>" +
                       "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[2:]) + "</tbody></table></div>"); continue
        if re.match(r"^(\*|\d+\.) ", l):
            ordered = l[0].isdigit(); items = []
            while i < len(lines) and re.match(r"^(\*|\d+\.) ", lines[i]):
                items.append(re.sub(r"^(\*|\d+\.) ", "", lines[i])); i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>"); continue
        if l.strip(): out.append(f"<p>{inline(l)}</p>")
        i += 1
    return "\n".join(out)


def write(name, content):
    open(os.path.join(DOCS, name), "w").write(content)
    print("docs/" + name, len(content), "bytes")


# ------------------------------------------------------------------ index
def page_index():
    ix = load_index(); cols = {c["collection"]: c["count"] for c in ix["collections"]}
    total = sum(cols.values())
    body = f'''<h1>Space Mission Dataset</h1>
<p class="lead">Verified engineering data for the <b>Space Mission Design Game</b>: spacecraft, instruments, launch vehicle, budget, mass, power, communication and orbit. Every value traces to a retrieved source.</p>
<p class="stats"><b>{total:,}</b> records &middot; <b>{len(cols)}</b> collections &middot; <b>{cols.get("launch_history_all", 0):,}</b> launches &middot; <b>{cols.get("launch_vehicle_configs", 0)}</b> launch vehicles &middot; <b>{cols.get("smallsat_components", 0):,}</b> components &middot; <b>{cols.get("launch_pads", 0)}</b> pads</p>

<h2>start</h2>
<ul class="links">
<li><a href="datasets.html">datasets</a> &mdash; download any collection as JSON, CSV or SQLite; training files</li>
<li><a href="api.html">api</a> &mdash; static JSON endpoints, no key, try it in the browser</li>
<li><a href="equations.html">equations</a> &mdash; rocket equation, transfers, power, link budget, cost: formulas + calculators</li>
<li><a href="explorer.html">explorer</a> &mdash; browse, compare, mission-fit</li>
<li><a href="guide.html">guide</a> &mdash; how to use everything</li>
</ul>

<h2>use it in 10 seconds</h2>
<pre>curl {SITE}/api/v1/planets/mars.json
curl {SITE}/api/v1/launch_vehicle_configs.json | jq '.records[0]'</pre>
<pre>import json, urllib.request
u = "{SITE}/api/v1/launch_pads.json"
pads = json.load(urllib.request.urlopen(u))["records"]
print(pads[0]["name"], pads[0]["latitude_deg"])</pre>

<h2>what the game needs &rarr; where it is</h2>
<div class="tw"><table><thead><tr><th>game need</th><th>collection</th><th>records</th></tr></thead><tbody>
<tr><td>orbit, destinations</td><td><code>planets</code> <code>moons</code> <code>orbital_elements</code> <code>atmospheres</code></td><td>{cols.get("planets", 0)} / {cols.get("moons", 0)} / {cols.get("orbital_elements", 0)} / {cols.get("atmospheres", 0)}</td></tr>
<tr><td>spacecraft parts</td><td><code>smallsat_components</code></td><td>{cols.get("smallsat_components", 0):,}</td></tr>
<tr><td>launch vehicle, budget</td><td><code>launch_vehicle_configs</code> <code>launch_pads</code></td><td>{cols.get("launch_vehicle_configs", 0)} / {cols.get("launch_pads", 0)}</td></tr>
<tr><td>launch success / failure</td><td><code>launch_history_all</code> <code>spacex_launch_history</code></td><td>{cols.get("launch_history_all", 0):,} / {cols.get("spacex_launch_history", 0)}</td></tr>
<tr><td>instruments, missions</td><td><code>nasa_instruments</code> <code>nasa_missions</code></td><td>{cols.get("nasa_instruments", 0)} / {cols.get("nasa_missions", 0)}</td></tr>
<tr><td>propellants</td><td><code>fluid_properties</code></td><td>{cols.get("fluid_properties", 0)}</td></tr>
<tr><td>model training</td><td><a href="datasets.html#training">training files</a></td><td>design, trajectories, reliability</td></tr>
</tbody></table></div>

<h2>trust</h2>
<ul>
<li><code>data_class</code> is <code>verified</code> (checked against a source) or <code>derived</code> (computed from verified inputs).</li>
<li>An empty value means unknown. It is never zero.</li>
<li>Estimates (component budgets, rule-engine labels) are marked as such. See <a href="guide.html#trust-rules-and-limits">limits</a>.</li>
</ul>'''
    write("index.html", shell("Space Mission Dataset", "index.html", body))


# ------------------------------------------------------------------ datasets
TRAIN = [
    ("training/qa_pairs.jsonl", "fact Q&A, chat format", "3,151"), ("training/physics_examples.jsonl", "Hohmann + rocket-equation examples", "110"),
    ("training/launch_outcome.csv", "SpaceX launch success/failure table", "743"), ("training/launcher_specs.csv", "launcher cost/capacity table", "532"),
    ("training/component_numeric.csv", "component numbers, long table", "2,544"), ("training/design/designs.csv", "mission designs: outcome, reasons, cost, duration", "6,000"),
    ("training/design/design_chat.jsonl", "design reviews, chat format", "6,000"), ("training/design/components_catalog.csv", "parts + verified specs + budget estimates", "308"),
    ("training/design/compatibility_pairs.csv", "what to attach / not attach", "3,018"), ("training/design/rules.json", "rules, thresholds, cost model", "-"),
    ("training/trajectories/transfers.csv", "Earth to Moon/planets: time, delta-v, windows", "9"), ("training/trajectories/transfer_paths.json", "path points for drawing", "9"),
    ("training/reliability/launch_outcomes_all.csv", "all launches, leak-free features, split", "7,657"), ("training/reliability/failure_reasons.csv", "failures with causes", "557"),
    ("training/reliability/reliability_by_vehicle.csv", "success rate by rocket (95% CI)", "-"), ("training/reliability/maturity_curve.csv", "success rate vs launch number", "5"),
    ("training/image_prompts.csv", "AI-image prompts per component", "327"),
]
CARDS = ["training/DATASET_CARD.md", "training/design/DESIGN_DATASET_CARD.md", "training/trajectories/TRAJECTORY_CARD.md", "training/reliability/RELIABILITY_CARD.md"]


def page_datasets():
    ix = load_index()
    rows = "".join(f'<tr data-q="{html.escape(c["collection"] + " " + (c["description"] or "")).lower()}"><td><code>{c["collection"]}</code></td><td class="n">{c["count"]:,}</td><td>{html.escape(c["description"] or "")}</td>'
                   f'<td><a href="api/v1/{c["url"]}">json</a> <a href="{RAW}/exports/csv/{c["collection"]}.csv">csv</a></td></tr>' for c in ix["collections"])
    tr = "".join(f'<tr data-q="{html.escape(p + " " + d).lower()}"><td><code>{p.replace("training/", "")}</code></td><td class="n">{n}</td><td>{d}</td><td><a href="{RAW}/{p}">download</a></td></tr>' for p, d, n in TRAIN)
    cards = " ".join(f'<a href="{GH}/blob/main/{c}">{c.split("/")[-1].replace(".md", "").lower()}</a>' for c in CARDS)
    body = f'''<h1>datasets</h1>
<p class="lead">All data is verified or marked derived. Download per collection, or everything at once.</p>
<p><input id="q" type="search" placeholder="filter..." aria-label="filter datasets"></p>

<h2>core collections</h2>
<div class="tw"><table class="filterable"><thead><tr><th>collection</th><th>records</th><th>description</th><th>get</th></tr></thead><tbody>{rows}</tbody></table></div>

<h2>everything at once</h2>
<ul>
<li><a href="{RAW}/exports/space_mission.sqlite">space_mission.sqlite</a> &mdash; all collections as SQL tables (8 MB)</li>
<li><a href="{RAW}/verified/combined/verified_space_mission_data.json">verified_space_mission_data.json</a> &mdash; one JSON file</li>
<li><a href="{GH}/archive/refs/heads/main.zip">full repository zip</a> &mdash; data, code, training files</li>
</ul>
<pre>git clone {GH}.git</pre>

<h2 id="training">training files</h2>
<p>Chat files use <code>{{"messages":[{{"role":"user",...}},{{"role":"assistant",...}}]}}</code> with a <code>split</code> field (train/val/test). Cards: {cards}.</p>
<div class="tw"><table class="filterable"><thead><tr><th>file</th><th>rows</th><th>content</th><th>get</th></tr></thead><tbody>{tr}</tbody></table></div>
<p class="note">Design labels come from a documented rule engine and component budgets are estimates, not real prices. Launch history and launch prices come from Launch Library 2 (aggregator).</p>'''
    script = '''<script>
const q=document.getElementById("q");q.addEventListener("input",()=>{const v=q.value.toLowerCase();document.querySelectorAll("table.filterable tbody tr").forEach(r=>r.hidden=v&&!r.dataset.q.includes(v));});
</script>'''
    write("datasets.html", shell("Datasets - Space Mission Dataset", "datasets.html", body, script))


# ------------------------------------------------------------------ api
def page_api():
    ix = load_index()
    names = [c["collection"] for c in ix["collections"]]
    opts = "".join(f"<option>{n}</option>" for n in names)
    body = f'''<h1>api</h1>
<p class="lead">Read-only static JSON. No key. CORS open. Verified data only.</p>
<pre>base  {SITE}/api/v1</pre>

<h2>try it</h2>
<div class="box">
<label>collection <select id="c">{opts}</select></label>
<label>record id (optional) <input id="i" placeholder="e.g. mars" autocomplete="off"></label>
<label>show first <input id="n" type="number" value="2" min="1" max="50"> records</label>
<p><button id="go">GET</button> <button id="cp">copy curl</button> <span id="st" class="mut"></span></p>
<pre id="cmd"></pre><pre id="out" class="out">press GET</pre>
</div>

<h2>endpoints</h2>
<div class="tw"><table><thead><tr><th>path</th><th>returns</th></tr></thead><tbody>
<tr><td><code>/index.json</code></td><td>collections, counts, URL templates, conventions</td></tr>
<tr><td><code>/{{collection}}.json</code></td><td><code>{{collection, count, data_status, provenance?, records[]}}</code></td></tr>
<tr><td><code>/{{collection}}/{{id}}.json</code></td><td>one record (collections up to 800 records)</td></tr>
<tr><td><code>/search-index.json</code></td><td>id and name list for client-side search</td></tr>
<tr><td><code>/analysis/light_time.json</code></td><td>one-way light time per planet (derived)</td></tr>
<tr><td><code>/missions/trajectory_reference.json</code></td><td>circular speed, Hohmann references (derived)</td></tr>
<tr><td><code>/quality.json</code> <code>/validation.json</code></td><td>quality report, validation results</td></tr>
<tr><td><code>/openapi.json</code></td><td>OpenAPI 3.0.3 spec</td></tr></tbody></table></div>
<p>Large collections (<code>smallsat_components</code>, <code>launch_vehicle_configs</code>, <code>launch_history_all</code>, <code>spacex_launch_history</code>, <code>moon_mean_elements</code>) are served as collection files only.</p>

<h2>examples</h2>
<h3>curl</h3>
<pre>curl {SITE}/api/v1/index.json
curl {SITE}/api/v1/planets/mars.json
curl -s {SITE}/api/v1/electric_propulsion.json | jq '.records[] | {{id, isp_vac_s, thrust_vac_n}}'</pre>
<h3>javascript</h3>
<pre>const base = "{SITE}/api/v1";
const get = p => fetch(`${{base}}/${{p}}.json`).then(r => r.json());
const mars = await get("planets/mars");
const {{records}} = await get("launch_vehicle_configs");
const heavy = records.filter(r => r.active && r.leo_capacity_kg &gt; 15000);</pre>
<h3>python</h3>
<pre>import json, urllib.request
base = "{SITE}/api/v1"
get = lambda p: json.load(urllib.request.urlopen(f"{{base}}/{{p}}.json"))
mars = get("planets/mars")
print(mars["gravitational_parameter_km3_s2"], mars["data_class"])</pre>
<p>Clients: <a href="client.js">client.js</a> (browser/Node), <a href="{GH}/blob/main/tools/spacemission_client.py">spacemission_client.py</a> (stdlib).</p>

<h2>local backend (filter, sort, calculate)</h2>
<pre>python3 tools/serve_api.py          # http://127.0.0.1:8000</pre>
<div class="tw"><table><thead><tr><th>endpoint</th><th>what</th></tr></thead><tbody>
<tr><td><code>GET /collections</code></td><td>collections and counts</td></tr>
<tr><td><code>GET /collections/{{c}}?q=&amp;field=value&amp;field_gte=&amp;field_lte=&amp;sort=-field&amp;limit=&amp;offset=&amp;fields=a,b</code></td><td>search, filter, sort, project</td></tr>
<tr><td><code>GET /collections/{{c}}/{{id}}</code></td><td>one record with <code>field_verification</code></td></tr>
<tr><td><code>GET /light-time?target=mars</code></td><td>one-way light time range</td></tr>
<tr><td><code>POST /delta-v</code></td><td>rocket equation</td></tr>
<tr><td><code>POST /hohmann</code></td><td>Hohmann transfer around any verified body</td></tr></tbody></table></div>
<pre>curl "localhost:8000/collections/launch_vehicle_configs?active=true&amp;leo_capacity_kg_gte=15000&amp;sort=-leo_capacity_kg&amp;limit=5"
curl -X POST localhost:8000/hohmann -d '{{"body":"earth","altitude1_km":400,"altitude2_km":35786}}'</pre>

<h2>conventions</h2>
<ul>
<li>SI units unless the field name says otherwise (<code>_km</code>, <code>_kg</code>, <code>_kn</code>, <code>_t</code>, <code>_days</code>).</li>
<li>Absent field = not verified. Never zero-filled.</li>
<li>Every record: <code>data_class</code>, <code>source_ids</code>, and <code>field_verification</code> or collection <code>provenance</code>. Aggregator and vendor data carry <code>source_authority</code>.</li>
<li>Ids are unique within a collection. v1 may gain fields but existing fields keep their meaning.</li>
</ul>'''
    script = f'''<script>
const B="{SITE}/api/v1",L="api/v1",$=i=>document.getElementById(i);
function path(){{const c=$("c").value,i=$("i").value.trim();return "/"+c+(i?"/"+encodeURIComponent(i):"")+".json";}}
function url(){{return B+path();}}
function upd(){{$("cmd").textContent="curl "+url();}}["c","i"].forEach(x=>$(x).addEventListener("input",upd));upd();
$("go").onclick=async()=>{{const u=L+path();$("st").textContent="loading...";try{{const r=await fetch(u);if(!r.ok)throw new Error(r.status+" "+r.statusText);const j=await r.json();
 if(j.records){{const n=+$("n").value||2;j.records=j.records.slice(0,n);j.note="showing first "+n+" of "+j.count;}}
 $("out").textContent=JSON.stringify(j,null,2).slice(0,20000);$("st").textContent="200 OK";}}catch(e){{$("out").textContent=String(e);$("st").textContent="error";}}}};
$("cp").onclick=()=>navigator.clipboard&&navigator.clipboard.writeText("curl "+url()).then(()=>$("st").textContent="copied");
</script>'''
    write("api.html", shell("API - Space Mission Dataset", "api.html", body, script))


# ------------------------------------------------------------------ equations
EQ = r'''<h1>equations</h1>
<p class="lead">The formulas used by the dataset, with live calculators. Constants for bodies load from the verified API.</p>
<p class="mut">g0 = 9.80665 m/s&sup2; &middot; c = 299 792 458 m/s &middot; k<sub>B</sub> = 1.380649e-23 J/K &middot; GM, radii, semi-major axes and irradiance come from <code>planets</code> / <code>moons</code>.</p>
<nav class="toc"><a href="#rocket">rocket</a> <a href="#orbit">orbit</a> <a href="#hohmann">hohmann</a> <a href="#interplanetary">interplanetary</a> <a href="#power">power</a> <a href="#link">link</a> <a href="#light">light time</a> <a href="#budget">mass &amp; cost</a> <a href="#reliability">reliability</a></nav>

<section id="rocket"><h2>1 &middot; rocket equation</h2>
<pre>dv = Isp * g0 * ln(m0 / mf)        mf = m0 * exp(-dv / (Isp*g0))
propellant = m0 - mf               burn time = (m0 - mf) * Isp * g0 / F
thrust-to-weight = F / (m0 * g0)</pre>
<div class="grid"><label>Isp (s)<input id="r_isp" type="number" value="311"></label><label>start mass m0 (kg)<input id="r_m0" type="number" value="1000"></label>
<label>end mass mf (kg)<input id="r_mf" type="number" value="600"></label><label>thrust F (N)<input id="r_f" type="number" value="3000"></label>
<label>required dv (m/s)<input id="r_dv" type="number" value="3000"></label></div>
<pre class="res" id="r_out"></pre></section>

<section id="orbit"><h2>2 &middot; circular orbit, escape, gravity</h2>
<pre>v_circ = sqrt(GM / r)     T = 2*pi*sqrt(r^3 / GM)     v_esc = sqrt(2*GM / r)     g = GM / r^2     r = R + altitude</pre>
<div class="grid"><label>body<select id="o_b" class="bodysel"></select></label><label>altitude (km)<input id="o_h" type="number" value="400"></label></div>
<pre class="res" id="o_out"></pre></section>

<section id="hohmann"><h2>3 &middot; Hohmann transfer between circular orbits (same body)</h2>
<pre>a_t = (r1 + r2)/2
dv1 = sqrt(GM/r1) * (sqrt(2*r2/(r1+r2)) - 1)
dv2 = sqrt(GM/r2) * (1 - sqrt(2*r1/(r1+r2)))
time = pi * sqrt(a_t^3 / GM)</pre>
<div class="grid"><label>body<select id="h_b" class="bodysel"></select></label><label>start altitude (km)<input id="h_1" type="number" value="400"></label><label>end altitude (km)<input id="h_2" type="number" value="35786"></label></div>
<pre class="res" id="h_out"></pre></section>

<section id="interplanetary"><h2>4 &middot; Earth to planet (patched conics, circular coplanar)</h2>
<pre>a_t = (a1 + a2)/2          time = pi * sqrt(a_t^3 / GM_sun)
v_inf_dep = sqrt(GM_sun/a1) * (sqrt(2*a2/(a1+a2)) - 1)
dv_depart = sqrt(v_inf^2 + 2*GM_E/r_leo) - sqrt(GM_E/r_leo)          (from circular LEO)
dv_capture = sqrt(v_inf_arr^2 + 2*GM_T/r_p) - sqrt(GM_T/r_p)          (to circular orbit radius r_p)
synodic = 1 / |1/T1 - 1/T2|     phase angle = 180 - 360 * time / T2</pre>
<div class="grid"><label>target planet<select id="p_t"></select></label><label>LEO altitude (km)<input id="p_l" type="number" value="200"></label><label>capture altitude (km)<input id="p_c" type="number" value="300"></label></div>
<pre class="res" id="p_out"></pre></section>

<section id="power"><h2>5 &middot; solar power and eclipse</h2>
<pre>S(d) = S_earth * (1 AU / d)^2       P = P_peak * S/S_earth * efficiency       needed = load * margin
eclipse time (circular, worst case) = T * asin(R / r) / pi          battery Wh = load * t_eclipse / DoD</pre>
<div class="grid"><label>array peak power at 1 AU (W)<input id="w_p" type="number" value="300"></label><label>destination<select id="w_b" class="bodysel"></select></label>
<label>efficiency (pointing, aging)<input id="w_e" type="number" value="0.8" step="0.05"></label><label>load (W)<input id="w_l" type="number" value="200"></label>
<label>margin<input id="w_m" type="number" value="1.15" step="0.05"></label><label>orbit altitude for eclipse (km)<input id="w_h" type="number" value="500"></label><label>depth of discharge<input id="w_d" type="number" value="0.3" step="0.05"></label></div>
<pre class="res" id="w_out"></pre></section>

<section id="link"><h2>6 &middot; radio link budget (Friis)</h2>
<pre>FSPL (dB) = 20*log10(4*pi*d*f / c)
EIRP (dBW) = 10*log10(Pt) + Gt
noise (dBW) = 10*log10(kB * T * R)
margin (dB) = EIRP + Gr - FSPL - losses - noise - Eb/N0_required</pre>
<div class="grid"><label>transmit power (W)<input id="l_p" type="number" value="5"></label><label>spacecraft antenna gain (dBi)<input id="l_g" type="number" value="10"></label><label>ground antenna gain (dBi)<input id="l_r" type="number" value="35"></label>
<label>frequency (MHz)<input id="l_f" type="number" value="2200"></label><label>distance (km)<input id="l_d" type="number" value="384400"></label><label>data rate (kbps)<input id="l_b" type="number" value="100"></label>
<label>Eb/N0 required (dB)<input id="l_e" type="number" value="10"></label><label>losses (dB)<input id="l_l" type="number" value="3"></label><label>noise temperature (K)<input id="l_t" type="number" value="290"></label></div>
<pre class="res" id="l_out"></pre></section>

<section id="light"><h2>7 &middot; light time</h2>
<pre>one-way = d / c        round trip = 2d / c</pre>
<div class="grid"><label>target<select id="t_b" class="bodysel"></select></label><label>or distance (km)<input id="t_d" type="number" placeholder="override"></label></div>
<pre class="res" id="t_out"></pre></section>

<section id="budget"><h2>8 &middot; mass and cost budget</h2>
<pre>dry = sum(parts) * (1 + structure)       total = dry + propellant       need: total &lt;= margin * launcher capacity
hardware cost = dry * USD_per_kg         total cost = hardware + launch price
USD_per_kg: low 149k / median 214k / high 428k  (ESTIMATE from NASA-stated development costs; launch price is real)</pre>
<div class="grid"><label>sum of part masses (kg)<input id="b_m" type="number" value="120"></label><label>structure overhead<input id="b_s" type="number" value="0.25" step="0.05"></label><label>propellant (kg)<input id="b_p" type="number" value="80"></label>
<label>launcher capacity (kg)<input id="b_c" type="number" value="22800"></label><label>capacity margin<input id="b_k" type="number" value="0.9" step="0.05"></label><label>launch price (USD)<input id="b_l" type="number" value="52000000"></label><label>budget (USD)<input id="b_b" type="number" value="80000000"></label></div>
<pre class="res" id="b_out"></pre></section>

<section id="reliability"><h2>9 &middot; launch reliability</h2>
<pre>rate = successes / launches
Wilson 95%: centre = (p + z^2/2n) / (1 + z^2/n),  half = z*sqrt(p(1-p)/n + z^2/4n^2) / (1 + z^2/n)
P(mission) = P(launch) * P(design checks pass)</pre>
<div class="grid"><label>launches<input id="s_n" type="number" value="400"></label><label>successes<input id="s_s" type="number" value="392"></label><label>P(design ok)<input id="s_d" type="number" value="0.95" step="0.01"></label></div>
<pre class="res" id="s_out"></pre></section>
'''
EQ_JS = r'''<script>
const B="api/v1/",G0=9.80665,C=299792458,KB=1.380649e-23,AU=1.495978707e11,$=i=>document.getElementById(i),num=i=>parseFloat($(i).value);
const f=(x,d=5)=>x==null||!isFinite(x)?"n/a":Math.abs(x)>=1e6||(Math.abs(x)<1e-3&&x!==0)?x.toExponential(4):(+x.toPrecision(d)).toLocaleString("en-US");
let BODIES={},PL={};
async function load(){const [a,b]=await Promise.all([fetch(B+"planets.json").then(r=>r.json()),fetch(B+"moons.json").then(r=>r.json())]);
 [...a.records,...b.records].forEach(r=>{BODIES[r.id]=r;});a.records.forEach(r=>PL[r.id]=r);
 document.querySelectorAll(".bodysel").forEach(s=>{Object.values(BODIES).filter(b=>b.id!=="sun"&&b.mean_radius_m&&b.gravitational_parameter_km3_s2).forEach(b=>s.append(new Option(b.name,b.id)));s.value=s.id==="w_b"||s.id==="t_b"?"mars":"earth";});
 const pt=$("p_t");["mercury","venus","mars","jupiter","saturn","uranus","neptune"].forEach(i=>pt.append(new Option(PL[i].name,i)));pt.value="mars";
 document.querySelectorAll("input,select").forEach(e=>e.addEventListener("input",run));run();}
const GM=b=>BODIES[b].gravitational_parameter_km3_s2*1e9,RAD=b=>BODIES[b].mean_radius_m;
function run(){try{
 {const isp=num("r_isp"),m0=num("r_m0"),mf=num("r_mf"),F=num("r_f"),dv=num("r_dv");const d=isp*G0*Math.log(m0/mf),mfn=m0*Math.exp(-dv/(isp*G0));
  $("r_out").textContent=`delta-v            ${f(d)} m/s\nmass ratio         ${f(m0/mf)}\npropellant         ${f(m0-mf)} kg\nburn time          ${f((m0-mf)*isp*G0/F/60)} min\nthrust/weight      ${f(F/(m0*G0))}\n--\nfor dv ${f(dv)} m/s: end mass ${f(mfn)} kg, propellant ${f(m0-mfn)} kg`;}
 {const b=$("o_b").value,mu=GM(b),r=RAD(b)+num("o_h")*1e3;$("o_out").textContent=`radius r           ${f(r/1e3)} km\ncircular speed     ${f(Math.sqrt(mu/r))} m/s\nperiod             ${f(2*Math.PI*Math.sqrt(r**3/mu)/60)} min\nescape speed       ${f(Math.sqrt(2*mu/r))} m/s\ngravity at r       ${f(mu/r**2)} m/s^2\nGM (verified)      ${f(mu/1e9)} km^3/s^2`;}
 {const b=$("h_b").value,mu=GM(b),R=RAD(b),r1=R+num("h_1")*1e3,r2=R+num("h_2")*1e3,v1=Math.sqrt(mu/r1),v2=Math.sqrt(mu/r2);
  const d1=v1*(Math.sqrt(2*r2/(r1+r2))-1),d2=v2*(1-Math.sqrt(2*r1/(r1+r2))),t=Math.PI*Math.sqrt(((r1+r2)/2)**3/mu);
  $("h_out").textContent=`dv1 (burn 1)       ${f(d1)} m/s\ndv2 (burn 2)       ${f(d2)} m/s\ntotal              ${f(Math.abs(d1)+Math.abs(d2))} m/s\ntransfer time      ${f(t/3600)} h`;}
 {const e=PL.earth,t=PL[$("p_t").value],mS=PL.sun.gravitational_parameter_km3_s2*1e9,mE=GM("earth"),a1=e.semi_major_axis_m,a2=t.semi_major_axis_m,rl=e.mean_radius_m+num("p_l")*1e3;
  const tof=Math.PI*Math.sqrt(((a1+a2)/2)**3/mS),vd=Math.sqrt(mS/a1)*(Math.sqrt(2*a2/(a1+a2))-1),va=Math.sqrt(mS/a2)*(1-Math.sqrt(2*a1/(a1+a2)));
  const dep=Math.sqrt(vd*vd+2*mE/rl)-Math.sqrt(mE/rl),rp=t.mean_radius_m+num("p_c")*1e3,mT=t.gravitational_parameter_km3_s2*1e9,cap=Math.sqrt(va*va+2*mT/rp)-Math.sqrt(mT/rp);
  const T1=2*Math.PI*Math.sqrt(a1**3/mS),T2=2*Math.PI*Math.sqrt(a2**3/mS),syn=Math.abs(1/(1/T1-1/T2));
  $("p_out").textContent=`transfer time      ${f(tof/86400)} days (${f(tof/86400/365.25)} yr)\nv_inf departure    ${f(Math.abs(vd))} m/s   C3 ${f((vd/1e3)**2)} km^2/s^2\ndeparture burn     ${f(dep)} m/s (from circular LEO)\nv_inf arrival      ${f(Math.abs(va))} m/s\ncapture burn       ${f(cap)} m/s (to circular ${f(num("p_c"))} km)\ntotal dv           ${f(dep+cap)} m/s\nlaunch windows     every ${f(syn/86400)} days\nphase angle        ${f(180-360*tof/T2)} deg (target ahead of Earth)`;}
 {const b=$("w_b").value,S0=PL.earth.nssdc_fact_sheet.numeric["Solar irradiance (W/m 2 )"],S=BODIES[b].nssdc_fact_sheet&&BODIES[b].nssdc_fact_sheet.numeric["Solar irradiance (W/m 2 )"]||(PL[b]?null:S0);
  const P=S?num("w_p")*S/S0*num("w_e"):null,need=num("w_l")*num("w_m");
  const mu=GM("earth"),r=RAD("earth")+num("w_h")*1e3,T=2*Math.PI*Math.sqrt(r**3/mu),te=T*Math.asin(RAD("earth")/r)/Math.PI,wh=num("w_l")*te/3600/num("w_d");
  $("w_out").textContent=`irradiance at dest ${S?f(S)+" W/m^2 (NASA NSSDC)":"n/a for moons; uses parent planet"}\navailable power    ${f(P)} W\nneeded             ${f(need)} W   ${P==null?"":P>=need?"OK":"SHORT by "+f(need-P)+" W"}\n--\nLEO eclipse (max)  ${f(te/60)} min per ${f(T/60)} min orbit\nbattery energy     ${f(wh)} Wh at DoD ${f(num("w_d"))}`;}
 {const Pt=10*Math.log10(num("l_p")),d=num("l_d")*1e3,fq=num("l_f")*1e6,fspl=20*Math.log10(4*Math.PI*d*fq/C),eirp=Pt+num("l_g"),nz=10*Math.log10(KB*num("l_t")*num("l_b")*1e3);
  const mg=eirp+num("l_r")-fspl-num("l_l")-nz-num("l_e");$("l_out").textContent=`path loss FSPL    ${f(fspl)} dB\nEIRP               ${f(eirp)} dBW\nnoise power        ${f(nz)} dBW\nmargin             ${f(mg)} dB   ${mg>=3?"OK (>= 3 dB)":"LOW (< 3 dB)"}`;}
 {const b=$("t_b").value,ov=num("t_d");let lo,hi;if(ov>0){lo=hi=ov*1e3;}else{const x=PL[b]||PL[BODIES[b].parent_id]||PL.earth,a=x.semi_major_axis_m,ae=PL.earth.semi_major_axis_m;lo=b==="moon"?3.844e8:Math.abs(a-ae);hi=b==="moon"?3.844e8:a+ae;}
  $("t_out").textContent=`distance           ${f(lo/1e9)}${hi!==lo?" to "+f(hi/1e9):""} million km\none-way            ${f(lo/C/60)}${hi!==lo?" to "+f(hi/C/60):""} min\nround trip         ${f(2*lo/C/60)}${hi!==lo?" to "+f(2*hi/C/60):""} min`;}
 {const dry=num("b_m")*(1+num("b_s")),tot=dry+num("b_p"),lim=num("b_k")*num("b_c"),L=num("b_l"),B=num("b_b");const h=r=>r*dry,tc=r=>h(r)+L;
  $("b_out").textContent=`dry mass           ${f(dry)} kg\ntotal mass         ${f(tot)} kg   limit ${f(lim)} kg   ${tot<=lim?"OK":"TOO HEAVY"}\nhardware (est.)    $${f(h(214240)/1e6)}M  (range $${f(h(149442)/1e6)}M - $${f(h(428000)/1e6)}M)\nlaunch (price)     $${f(L/1e6)}M\ntotal (est.)       $${f(tc(214240)/1e6)}M   budget $${f(B/1e6)}M   ${tc(214240)<=B?"OK":"OVER BUDGET"}`;}
 {const n=num("s_n"),s=num("s_s"),p=s/n,z=1.96,d=1+z*z/n,c=(p+z*z/(2*n))/d,h=z*Math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;
  $("s_out").textContent=`launch success rate ${f(100*p)} %\n95% interval       ${f(100*(c-h))} - ${f(100*(c+h))} %\nP(mission)         ${f(100*p*num("s_d"))} %`;}
}catch(e){console.error(e);}}
load();
</script>'''


def page_equations():
    write("equations.html", shell("Equations - Space Mission Dataset", "equations.html", EQ, EQ_JS))


# ------------------------------------------------------------------ guide
def page_guide():
    src = open(os.path.join(ROOT, "USER_GUIDE.md")).read().split("\n")
    write("guide.html", shell("Guide - Space Mission Dataset", "guide.html", "<h1>guide</h1>\n" + render_md(src)))


# ------------------------------------------------------------------ explorer (interactive app)
def page_explorer():
    body = '''<h1>explorer</h1>
<p class="lead">Browse, compare and check missions against verified data. Every record shows its source.</p>
<div id="banner" class="banner"></div>
<nav id="tabs" role="tablist"></nav>
<div id="view" tabindex="-1"></div>'''
    script = '<script src="advisor.js"></script><script src="extras.js"></script><script src="app.js"></script>'
    write("explorer.html", shell("Explorer - Space Mission Dataset", "explorer.html", body, script))


if __name__ == "__main__":
    for fn in (page_index, page_datasets, page_api, page_equations, page_guide, page_explorer):
        fn()
