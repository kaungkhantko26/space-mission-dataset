(async function(){
const $=s=>document.querySelector(s), el=(h)=>{const t=document.createElement("template");t.innerHTML=h.trim();return t.content.firstChild};
const fmt=(v,d=3)=>v==null?"—":typeof v==="number"?(Math.abs(v)>=1e6||(Math.abs(v)<1e-3&&v!==0)?v.toExponential(2):(+v.toPrecision(d+1)).toLocaleString()):String(v);
let D; try{D=await (await fetch("data/all_space_mission_data.json")).json();}catch(e){$("#view").textContent="Could not load data/all_space_mission_data.json: "+e;return;}
let VAL=null; try{VAL=await (await fetch("data/validation_report.json")).json();}catch(e){}
const Q=D.metadata.quality;
$("#banner").innerHTML=`<b>Data status:</b> ${Q.retrieval.sources_retrieved} of ${Q.retrieval.sources_listed} listed sources were retrieved. ${Q.statement}`;
const SETS={ // dataset -> [records, columns]
 "Planets & dwarf planets":[D.celestial.planets,["name","category","gravitational_parameter_km3_s2","mean_radius_m","mass_kg","surface_gravity_m_s2","derived.escape_velocity_m_s","derived.solar_irradiance_w_m2"]],
 "Moons":[D.celestial.moons,["name","parent_id","gravitational_parameter_km3_s2","mean_radius_m","surface_gravity_m_s2","semi_major_axis_m","orbital_period_days","derived.escape_velocity_m_s"]],
 "Chemical engines":[D.propulsion.rocket_engines,["name","type","propellant","thrust_vac_n","thrust_sl_n","isp_vac_s","isp_sl_s","dry_mass_kg","derived.engine_thrust_to_weight_vac","status"]],
 "Electric propulsion":[D.propulsion.electric_propulsion,["name","type","thrust_vac_n","isp_vac_s","power_w","derived.thrust_per_power_mN_per_kW","status"]],
 "Launch vehicles":[D.launch.launch_vehicles,["name","status","height_m","liftoff_mass_kg","thrust_sl_n","derived.liftoff_thrust_to_weight","price_usd","reusable"]],
 "Payload capabilities":[D.launch.payload_capabilities,["vehicle_id","orbit","payload_kg","altitude_km","inclination_deg","mode","reference_conditions_complete"]],
 "Stages":[D.launch.rocket_stages,["vehicle_id","stage","dry_mass_kg","propellant_mass_kg","engine_id","n_engines","derived.inert_mass_fraction"]],
 "Instruments":[D.instruments,["name","instrument_type","heritage_mission","mass_kg","power_w","derived.power_to_mass_w_per_kg"]],
 "Spacecraft components":[D.spacecraft.components,["name","category","record_kind","mass_kg","power_consumption_w","power_generation_w"]],
 "Historical missions":[D.missions.historical,["name","launch_date","launch_vehicle_note","launch_mass_kg","dry_mass_kg","destination","cost_musd_nominal","derived.dry_to_launch_mass"]],
 "Ground stations":[D.spacecraft.ground_stations,["name","operator","antenna_m","bands","lat","lon"]],
 "Engineering constraints":[D.missions.engineering_constraints,["type","statement","data_class"]],
};
const get=(o,p)=>p.split(".").reduce((a,k)=>a==null?a:a[k],o);
const DIRS={"Chemical engines":{isp_vac_s:1,"derived.engine_thrust_to_weight_vac":1,dry_mass_kg:-1},"Electric propulsion":{isp_vac_s:1,power_w:-1,"derived.thrust_per_power_mN_per_kW":1},
 "Launch vehicles":{price_usd:-1},"Instruments":{mass_kg:-1,power_w:-1,"derived.power_to_mass_w_per_kg":-1},"Stages":{"derived.inert_mass_fraction":-1},"Historical missions":{}};
SETS["SpaceX launch history (2010-2018)"]=[D.launch_history.launches,["id","date_utc","booster_family","booster_version_raw","launch_site_id","payload","payload_mass_kg","orbit_class","mission_outcome","landing_outcome_raw"]];
SETS["Launch sites"]=[D.launch_history.sites,["name","lat","lon","launches_in_file","first_launch","last_launch"]];
SETS["NASA facilities"]=[D.infrastructure.nasa_facilities,["center","facility","category","status","city","state","lat","lon","occupied_date","last_update"]];
window.UI={el,table,fmt,get,D,Q,SETS};
const COMPARE={ // dataset -> metrics (label, path, higher_is_better?)
 "Chemical engines":[["Vac thrust (N)","thrust_vac_n"],["Vac Isp (s)","isp_vac_s"],["Engine T/W (vac)","derived.engine_thrust_to_weight_vac"],["Dry mass (kg)","dry_mass_kg"]],
 "Electric propulsion":[["Thrust (N)","thrust_vac_n"],["Isp (s)","isp_vac_s"],["Power (W)","power_w"],["mN per kW","derived.thrust_per_power_mN_per_kW"]],
 "Launch vehicles":[["Liftoff mass (kg)","liftoff_mass_kg"],["Liftoff thrust (N)","thrust_sl_n"],["Liftoff T/W","derived.liftoff_thrust_to_weight"],["Height (m)","height_m"],["Price (USD)","price_usd"]],
 "Instruments":[["Mass (kg)","mass_kg"],["Power (W)","power_w"],["W per kg","derived.power_to_mass_w_per_kg"]],
 "Planets & dwarf planets":[["GM (km³/s²)","gravitational_parameter_km3_s2"],["Mean radius (m)","mean_radius_m"],["Gravity (m/s²)","surface_gravity_m_s2"],["Escape v (m/s)","derived.escape_velocity_m_s"],["Irradiance (W/m²)","derived.solar_irradiance_w_m2"]],
 "Moons":[["GM (km³/s²)","gravitational_parameter_km3_s2"],["Mean radius (m)","mean_radius_m"],["Gravity (m/s²)","surface_gravity_m_s2"],["Escape v (m/s)","derived.escape_velocity_m_s"]],
 "Historical missions":[["Launch mass (kg)","launch_mass_kg"],["Dry mass (kg)","dry_mass_kg"],["Cost (M$ nominal)","cost_musd_nominal"],["Dry/launch","derived.dry_to_launch_mass"]],
 "Stages":[["Dry mass (kg)","dry_mass_kg"],["Propellant (kg)","propellant_mass_kg"],["Inert fraction","derived.inert_mass_fraction"]],
};
const TABS=["Overview","Guide","Explorer","Compare","Mission fit","Calculators","Optimizer","Simulator","Launch & facilities","Sensitivity & risk","Benchmarks","API","Quality"];
let cur=TABS[0];
function tabs(){const n=$("#tabs");n.innerHTML="";TABS.forEach(t=>{const b=el(`<button role="tab" aria-selected="${t===cur}">${t}</button>`);b.onclick=()=>{cur=t;tabs();render();};n.append(b);});}
function render(){const v=$("#view");v.innerHTML="";({Overview:overview,Guide:guide,Benchmarks:benchmarks,Simulator:simulator,Explorer:explorer,Compare:compare,Calculators:calculators,Optimizer:optimizer,"Sensitivity & risk":sensitivity,Quality:quality,"Mission fit":v=>EXTRA.missionFit(v,UI),"Launch & facilities":v=>EXTRA.launchFacilities(v,UI),API:v=>EXTRA.apiTab(v,UI)})[cur](v);}
function table(rows,cols,opts={}){
  let sortK=null,dir=1; const wrap=el(`<div class="tw"><table></table></div>`),t=wrap.firstChild;
  function draw(){const rs=sortK==null?rows:[...rows].sort((a,b)=>{const x=get(a,sortK),y=get(b,sortK);if(x==null)return 1;if(y==null)return -1;return (x>y?1:x<y?-1:0)*dir});
   t.innerHTML="<thead><tr>"+cols.map(c=>`<th data-k="${c}">${c.split(".").pop().replace(/_/g," ")}${sortK===c?(dir>0?" ▲":" ▼"):""}</th>`).join("")+(opts.cls===false?"":"<th>class</th>")+"</tr></thead><tbody>"+
   rs.map(r=>"<tr>"+cols.map(c=>`<td>${fmt(get(r,c))}</td>`).join("")+(opts.cls===false?"":`<td><span class="tag ${r.data_class}">${r.data_class||""}</span></td>`)+"</tr>").join("")+"</tbody>";
   t.querySelectorAll("th[data-k]").forEach(h=>h.onclick=()=>{const k=h.dataset.k;dir=sortK===k?-dir:1;sortK=k;draw();});}
  draw();return wrap;}
let BM=null;
function guide(v){v.append(el(`<div class="card"><h2>How to use this site</h2><ol>
<li><b>Overview</b> – record counts vs the research targets and how many records are unverified (all of them).</li>
<li><b>Explorer</b> – pick a dataset, type to filter, click a column header to sort. “—” means not recorded.</li>
<li><b>Compare</b> – choose a dataset (engines, vehicles, instruments, bodies, missions), tick 2–4 records; bars are scaled to the largest value per row.</li>
<li><b>Calculators</b> – rocket equation, Hohmann transfer, link budget and solar/battery sizing; type in any box and results update.</li>
<li><b>Optimizer</b> – pick a scenario and objective, move the budget/margin sliders, then press <i>Re-run optimizer</i>. Choose <i>Balanced</i> and weight mass, cost and science to trade them off. The chart is the Pareto front (each dot is a non-dominated design; darker = more science; ringed = your pick). “No feasible design” means your constraints are too tight; the violation counts tell you which.</li>
<li><b>Sensitivity &amp; risk</b> – which assumptions move the optimum most, and the chance a chosen design stays feasible under uncertainty.</li>
<li><b>Compare</b> also marks the winner (✔) on metrics where better has a clear direction, then asks “which is better for a mission?” — choose Earth orbit, GTO, Moon or Mars and a dry mass to get a verdict per part.</li>
<li><b>Mission fit</b> – pick a mission and spacecraft dry mass; launch vehicles, engines and instruments are ranked with the reason shown (capacity vs needed mass, restart/acceleration limits, relevance vs mass+power). “Not rated” = data missing, never guessed.</li>
<li><b>Simulator</b> – choose or edit a design and scenario, set uncertainty, run a seeded Monte Carlo to get the success rate and failure reasons; <i>Suggest improvements</i> tests every single change and ranks them; part rankings are sortable. Tick the launch-reliability box to fold in the Falcon record from your uploaded launch table.</li>
<li><b>Launch &amp; facilities</b> – your uploaded SpaceX launch table (reliability, landings, payloads) and NASA facilities table (filter, map).</li>
<li><b>API</b> – try the JSON API live; <a href="api.html">api.html</a> has the full guide and JS/Python clients.</li>
<li><b>Benchmarks</b> – solver speed and how well heuristic solvers match the exact optimum.</li>
<li><b>Quality</b> – validation results, known conflicts and gaps.</li></ol>
<p class="mut">Reading results: costs are fictional credits; science points are educational weights; component values are estimates. Use the site to learn trade-offs, not to size real hardware.</p></div>`));}
async function benchmarks(v){
  if(!BM){try{BM=await (await fetch("data/benchmark_results.json")).json();}catch(e){v.append(el("<div class='card'>benchmark_results.json not found.</div>"));return;}}
  v.append(el(`<div class="card"><h2>Exactness &amp; speed</h2><div id="a"></div><p class="mut">Vectorized exact solver matches the scalar reference on every objective. Timings are single runs on the build machine.</p></div>`));
  v.firstChild.querySelector("#a").append(table(BM.timing.map(t=>({scenario:t.scenario_id,designs:t.designs,scalar_s:t.scalar_python_enumerate_s,vectorized_s:t.vectorized_one_full_pass_s,speedup:t.speedup,js_s:t.js_enumerate_s})),["scenario","designs","scalar_s","vectorized_s","speedup","js_s"],{cls:false}));
  const s=el(`<div class="card"><h2>Scaling (synthetic instruments)</h2><div id="b"></div></div>`);s.querySelector("#b").append(table(BM.scaling,["instruments","designs","vectorized_exact_solve_s","scalar_exact_solve_s","optimum_science"],{cls:false}));v.append(s);
  const h=el(`<div class="card"><h2>Heuristics vs exact optimum (2000 evals, 20 seeds)</h2><div id="c"></div></div>`);h.querySelector("#c").append(table(BM.heuristics.filter(x=>x.evaluations===2000).map(x=>({scenario:x.scenario_id,objective:x.objective,solver:x.solver,found_exact:x.runs_found_exact_optimum+"/"+x.runs,feasible:x.runs_feasible+"/"+x.runs,median_gap_pct:x.median_gap_pct})),["scenario","objective","solver","found_exact","feasible","median_gap_pct"],{cls:false}));v.append(h);
}

// ---------------- Simulator ----------------
const rng32=a=>()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
const triD=(r,lo,hi,mo)=>{const u=r(),c=(mo-lo)/(hi-lo);return u<c?lo+Math.sqrt(u*(hi-lo)*(mo-lo)):hi-Math.sqrt((1-u)*(hi-lo)*(hi-mo));};
const gaussD=r=>{let u=0,v=0;while(!u)u=r();while(!v)v=r();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);};
const DEF_UNC={mga:[0.10,0.35],dvm:[0,0.10],pm:[0.05,0.25],gt_sd:1.5,dvs:[0.95,1.10,1.0],cost:[0.9,1.4,1.0]};
function resolveDesign(sc,cat,d){const f=(arr,id)=>arr.find(x=>x.id===id);
  const sel=d.instruments.map(id=>sc.instruments.findIndex(i=>i.id===id)).filter(i=>i>=0);
  return {sel,comp:f(cat.computers,d.computer),comm:f(cat.comms,d.comm),arr:f(cat.arrays,d.array),bat:f(cat.batteries,d.battery),prop:f(cat.propulsion,d.propulsion),veh:f(sc.vehicles,d.vehicle)};}
function evalDesign(G,sc,cat,d){const x=resolveDesign(sc,cat,d);if(!x.sel.length||!x.comp||!x.comm||!x.arr||!x.bat||!x.prop||!x.veh)return null;return evaluate(G,sc,x.sel,x.comp,x.comm,x.arr,x.bat,x.prop,x.veh);}
function simulate(G,sc,cat,d,N,seed,u){
  const r=rng32(seed),wet=[],cost=[],reasons={};let ok=0;const x=resolveDesign(sc,cat,d);
  for(let k=0;k<N;k++){
    const g=Object.assign({},G,{mga:u.mga[0]+(u.mga[1]-u.mga[0])*r(),dv_margin:u.dvm[0]+(u.dvm[1]-u.dvm[0])*r(),power_margin:u.pm[0]+(u.pm[1]-u.pm[0])*r()});
    const sh=gaussD(r)*u.gt_sd,gt={};for(const b in sc.gt_db)gt[b]=sc.gt_db[b]+sh;
    const s=Object.assign({},sc,{gt_db:gt,dv_ms:sc.dv_ms*triD(r,u.dvs[0],u.dvs[1],u.dvs[2])});
    const e=evaluate(g,s,x.sel,x.comp,x.comm,x.arr,x.bat,x.prop,x.veh),c=e.cost*triD(r,u.cost[0],u.cost[1],u.cost[2]);
    const fails=e.violations.filter(v=>v!=="exceeds_budget");if(c>sc.budget)fails.push("exceeds_budget");
    fails.forEach(f=>reasons[f]=(reasons[f]||0)+1);if(!fails.length)ok++;wet.push(e.wet_kg);cost.push(c);}
  const q=(a,p)=>[...a].sort((m,n)=>m-n)[Math.min(a.length-1,Math.floor(p*a.length))];
  return {p:ok/N,N,reasons,wet,cost,wet50:q(wet,.5),wet95:q(wet,.95),cost50:q(cost,.5),cost95:q(cost,.95)};}
const ADVICE={exceeds_budget:"Raise the budget, drop the most expensive instrument, or choose cheaper comm/array/battery options. Cost growth (up to +40%) is the usual cause.",
 exceeds_launch_capacity:"Pick a larger launch vehicle, a more efficient propulsion option (higher Isp), or remove heavy instruments.",
 science_below_minimum:"Add an instrument, or raise downlink capability (bigger dish / more transmit power) so data is not lost.",
 radiation_tolerance:"Use a more radiation-tolerant computer (LEON3-class or RAD750-class).",
 link_rate_too_low:"Use a larger dish or higher transmit power; the distance is too large for the current antenna.",
 electric_burn_too_long:"Use chemical propulsion or reduce Δv; low-thrust burn exceeds the allowed duration.",
 propellant_tank_infeasible:"Δv is too large for this propulsion option; use a higher-Isp system."};
function simulator(v){
  const cons=D.optimization.constraints,cat={arrays:cons.catalog.arrays,batteries:cons.catalog.batteries,computers:cons.catalog.computers,comms:cons.catalog.comms,propulsion:cons.catalog.propulsion};
  const card=el(`<div class="card"><h2>Mission simulator &amp; modifier</h2><p class="mut">Choose or edit a design, add uncertainty, and run a seeded Monte Carlo to see the <b>success rate</b> (no constraint violated, cost growth included). Then ask for suggestions or rank parts.</p>
  <div class="row"><div><label>Scenario<select id="sc"></select></label><div class="chips" id="ins"></div>
   <label>Computer<select id="comp"></select></label><label>Comm system<select id="comm"></select></label><label>Solar array<select id="arr"></select></label><label>Battery<select id="bat"></select></label><label>Propulsion<select id="prop"></select></label><label>Launch vehicle<select id="veh"></select></label>
   <p><button class="act" id="load">Load balanced optimum</button> <button class="act" id="sim">Run simulation</button> <button class="act" id="sug">Suggest improvements</button></p></div>
  <div><h3>Modify scenario</h3><label>Budget (credits)<input type="number" id="bud"></label><label>Onboard Δv (m/s)<input type="number" id="dv"></label><label>Minimum science points<input type="number" id="ms"></label><label>Downlink hours/day<input type="number" step="0.1" id="dl"></label><label>Design life (years)<input type="number" step="0.5" id="life"></label>
   <h3>Uncertainty (assumed distributions)</h3><label>Mass growth allowance range <span id="u1"></span><input type="range" id="umga" min="0" max="0.5" step="0.01" value="0.35"></label><label>Cost growth upper bound <span id="u2"></span><input type="range" id="ucost" min="1" max="2" step="0.05" value="1.4"></label><label>Ground G/T uncertainty σ (dB) <span id="u3"></span><input type="range" id="ugt" min="0" max="4" step="0.5" value="1.5"></label><label>Samples <span id="u4"></span><input type="range" id="un" min="200" max="20000" step="200" value="3000"></label><label>Seed<input type="number" id="seed" value="20261106"></label><label><input type="checkbox" id="rel"> Multiply by launch reliability (Falcon family only: observed in your uploaded 2010–2018 launch table)</label></div></div>
  <div id="out"></div></div>`);
  v.append(card);const $c=s=>card.querySelector(s);
  cons.scenarios.forEach(s=>$c("#sc").append(new Option(s.name,s.id)));
  const fill=(id,arr)=>{$c(id).innerHTML="";arr.forEach(a=>$c(id).append(new Option(a.name||a.id,a.id)));};
  let sc,G,des=null,desKey="";
  function setScenario(){sc=JSON.parse(JSON.stringify(cons.scenarios.find(s=>s.id===$c("#sc").value)));G=Object.assign({},cons.global_parameters);
    $c("#ins").innerHTML=sc.instruments.map(i=>`<label><input type="checkbox" value="${i.id}"> ${i.name} <span class="mut">(${i.mass} kg, ${i.power} W)</span></label>`).join("");
    fill("#comp",cat.computers);fill("#comm",cat.comms);fill("#arr",cat.arrays);fill("#bat",cat.batteries);fill("#prop",cat.propulsion.filter(p=>!p.electric||sc.allow_electric));fill("#veh",sc.vehicles);
    $c("#bud").value=sc.budget;$c("#dv").value=Math.round(sc.dv_ms);$c("#ms").value=sc.min_science;$c("#dl").value=sc.dl_hours_per_day;$c("#life").value=sc.life_yr;loadOpt();}
  function applyEdits(){sc.budget=+$c("#bud").value;sc.dv_ms=+$c("#dv").value;sc.min_science=+$c("#ms").value;sc.dl_hours_per_day=+$c("#dl").value;sc.life_yr=+$c("#life").value;}
  const getDesign=()=>({instruments:[...card.querySelectorAll("#ins input:checked")].map(i=>i.value),computer:$c("#comp").value,comm:$c("#comm").value,array:$c("#arr").value,battery:$c("#bat").value,propulsion:$c("#prop").value,vehicle:$c("#veh").value});
  const setDesign=d=>{card.querySelectorAll("#ins input").forEach(i=>i.checked=d.instruments.includes(i.value));$c("#comp").value=d.computer;$c("#comm").value=d.comm;$c("#arr").value=d.array;$c("#bat").value=d.battery;$c("#prop").value=d.propulsion;$c("#veh").value=d.vehicle;};
  const unc=()=>({mga:[0.10,+$c("#umga").value],dvm:DEF_UNC.dvm,pm:DEF_UNC.pm,gt_sd:+$c("#ugt").value,dvs:DEF_UNC.dvs,cost:[0.9,+$c("#ucost").value,1.0]});
  function enumCached(){applyEdits();const k=JSON.stringify([sc.budget,sc.dv_ms,sc.min_science,sc.dl_hours_per_day,sc.life_yr,$c("#sc").value]);if(k!==desKey){des=enumerate(G,sc,cat);desKey=k;}return des;}
  function loadOpt(){const b=balanced(enumCached());if(b)setDesign(b.design);else $c("#out").innerHTML="<p class='bad'>No feasible design under the edited scenario; choose parts manually or relax constraints.</p>";}
  function hist(vals,label,w=300,h=90,bins=24){const lo=Math.min(...vals),hi=Math.max(...vals),span=(hi-lo)||1,c=new Array(bins).fill(0);vals.forEach(x=>c[Math.min(bins-1,Math.floor((x-lo)/span*bins))]++);const m=Math.max(...c);
    return `<svg viewBox="0 0 ${w} ${h+18}" width="100%" role="img" aria-label="${label} histogram">${c.map((n,i)=>`<rect x="${i*w/bins}" y="${h-h*n/m}" width="${w/bins-1}" height="${h*n/m}" fill="var(--ac)" fill-opacity=".7"/>`).join("")}<text x="0" y="${h+13}">${fmt(lo)}</text><text x="${w/2}" y="${h+13}" text-anchor="middle">${label}</text><text x="${w}" y="${h+13}" text-anchor="end">${fmt(hi)}</text></svg>`;}
  function runSim(){applyEdits();const d=getDesign(),e=evalDesign(G,sc,cat,d),out=$c("#out");if(!e){out.innerHTML="<p class='bad'>Select at least one instrument and all parts.</p>";return;}
    const r=simulate(G,sc,cat,d,+$c("#un").value,+$c("#seed").value,unc());
    const relOn=$c("#rel").checked&&/f9_class|falcon/.test(d.vehicle),relF=relOn?D.launch_history.analysis.mission_reliability.point_estimate:1,pAll=r.p*relF;r.pDesign=r.p;r.p=pAll;
    const se=Math.sqrt(r.p*(1-r.p)/r.N),col=r.p>=.9?"ok":r.p>=.6?"":"bad";
    const rs=Object.entries(r.reasons).sort((a,b)=>b[1]-a[1]);
    out.innerHTML=`<h3>Nominal design check</h3><p>${e.feasible?'<span class="ok">Feasible</span>':'<span class="bad">Violates: '+e.violations.join(", ")+'</span>'} · mass ${fmt(e.wet_kg)} kg · cost ${fmt(e.cost)} · science ${fmt(e.science)} · link margin ${fmt(e.link_margin_db)} dB · power ${fmt(e.avg_power_w)} W · mass margin ${fmt(100*e.mass_margin)}%</p>
     <h3>Monte Carlo result</h3><div class="kpi"><div><small>Success rate</small><div class="big ${col}">${fmt(100*r.p,3)}%</div><small>± ${fmt(196*se,2)} pp (95%, n=${r.N})${relOn?` · design ${fmt(100*r.pDesign,3)}% × launch reliability ${fmt(100*relF,3)}%`:""}</small></div><div><small>Mass median / p95</small><div class="big">${fmt(r.wet50)}</div><small>p95 ${fmt(r.wet95)} kg</small></div><div><small>Cost median / p95</small><div class="big">${fmt(r.cost50)}</div><small>p95 ${fmt(r.cost95)}</small></div></div>
     <div class="row"><div>${hist(r.wet,"launch mass (kg)")}</div><div>${hist(r.cost,"cost incl. growth (credits)")}</div></div>
     <h3>Why runs fail</h3>${rs.length?`<table><tbody>${rs.map(([k,n])=>`<tr><td>${k}</td><td>${fmt(100*n/r.N,3)}% of runs</td><td class="mut">${ADVICE[k]||""}</td></tr>`).join("")}</tbody></table>`:"<p class='ok'>No failures in this sample.</p>"}
     <p class="mut">Assumed uncertainty: mass growth U(0.10–${unc().mga[1]}), Δv margin U(0–0.10), power margin U(0.05–0.25), G/T N(0, ${unc().gt_sd} dB), Δv scale Tri(0.95,1.10,1.0), cost growth Tri(0.9,${unc().cost[1]},1.0). These are assumptions, not source uncertainties. Same seed ⇒ same result.</p>`;}
  function suggest(){applyEdits();const d=getDesign(),out=$c("#out");const base=evalDesign(G,sc,cat,d);if(!base){out.innerHTML="<p class='bad'>Select a complete design first.</p>";return;}
    const N=Math.min(600,+$c("#un").value),u=unc(),seed=+$c("#seed").value,cur=simulate(G,sc,cat,d,N,seed,u).p,cands=[];
    const add=(label,nd)=>{const e=evalDesign(G,sc,cat,nd);if(!e)return;const s=simulate(G,sc,cat,nd,N,seed,u);cands.push({label,design:nd,p:s.p,wet:e.wet_kg,cost:e.cost,science:e.science,nominal:e.feasible});};
    const groups=[["computer",cat.computers],["comm",cat.comms],["array",cat.arrays],["battery",cat.batteries],["propulsion",cat.propulsion.filter(p=>!p.electric||sc.allow_electric)],["vehicle",sc.vehicles]];
    groups.forEach(([g,opts])=>opts.forEach(o=>{if(o.id!==d[g])add(`${g}: ${d[g]} → ${o.id}`,Object.assign({},d,{[g]:o.id}));}));
    sc.instruments.forEach(i=>{const has=d.instruments.includes(i.id),ni=has?d.instruments.filter(x=>x!==i.id):d.instruments.concat(i.id);if(ni.length)add(`${has?"remove":"add"} instrument ${i.id}`,Object.assign({},d,{instruments:ni}));});
    cands.sort((a,b)=>b.p-a.p||a.cost-b.cost);const top=cands.slice(0,8);
    out.innerHTML=`<h3>Suggested single changes (common random numbers, ${N} samples)</h3><p>Current success rate: <b>${fmt(100*cur,3)}%</b></p><table><thead><tr><th>change</th><th>success</th><th>Δ</th><th>mass kg</th><th>cost</th><th>science</th><th>nominal</th><th></th></tr></thead><tbody>${top.map((c,i)=>`<tr><td>${c.label}</td><td>${fmt(100*c.p,3)}%</td><td class="${c.p>cur?"ok":"bad"}">${c.p>=cur?"+":""}${fmt(100*(c.p-cur),3)} pp</td><td>${fmt(c.wet)}</td><td>${fmt(c.cost)}</td><td>${fmt(c.science)}</td><td>${c.nominal?"ok":"violates"}</td><td><button class="act" data-i="${i}">Apply</button></td></tr>`).join("")}</tbody></table><p class="mut">Only one change at a time is tested; combined changes may do better. Cost/mass shown are nominal. Press Apply, then Run simulation.</p>`;
    out.querySelectorAll("button[data-i]").forEach(b=>b.onclick=()=>{setDesign(top[+b.dataset.i].design);runSim();});}
  const rank=el(`<div class="card"><h2>Part rankings (sortable)</h2><label>Rank parts by best achievable…<select id="ro"><option value="min_mass">lowest launch mass</option><option value="min_cost">lowest cost</option><option value="max_science">highest science</option><option value="max_feasibility_margin">largest worst-case margin</option><option value="max_link_margin">largest link margin</option><option value="min_power">lowest power</option></select></label><div id="rt"></div><p class="mut">For each part: the best value of the chosen objective over all feasible designs that include it, how many feasible designs include it, and how many Pareto-optimal (mass/cost/science) designs include it. Click a header to sort. Uses the scenario edits above.</p></div>`);
  function drawRank(){applyEdits();const des=enumCached(),key=rank.querySelector("#ro").value,[,fld,sg]=OBJ[key],feas=des.filter(d=>d.feasible),pf=pareto(des),rows=[];
    const grp=[["computer",cat.computers],["comm",cat.comms],["array",cat.arrays],["battery",cat.batteries],["propulsion",cat.propulsion],["vehicle",sc.vehicles]];
    const add=(g,id,name,test)=>{const f=feas.filter(test);if(!f.length&&!des.some(test))return;const best=f.length?f.reduce((b,d)=>sg*d[fld]<sg*b[fld]?d:b):null;rows.push({group:g,part:name||id,id,best_value:best?best[fld]:null,feasible_designs:f.length,pareto_designs:pf.filter(test).length,share_of_feasible_pct:feas.length?100*f.length/feas.length:0});};
    grp.forEach(([g,opts])=>opts.forEach(o=>add(g,o.id,o.name,d=>d.design[g]===o.id)));sc.instruments.forEach(i=>add("instrument",i.id,i.name,d=>d.design.instruments.includes(i.id)));
    rows.sort((a,b)=>a.best_value==null?1:b.best_value==null?-1:sg*(a.best_value-b.best_value));
    const t=rank.querySelector("#rt");t.innerHTML="";t.append(table(rows,["group","part","best_value","feasible_designs","pareto_designs","share_of_feasible_pct"],{cls:false}));}
  card.querySelectorAll("input[type=range]").forEach(i=>i.oninput=()=>{$c("#u1").textContent="max "+$c("#umga").value;$c("#u2").textContent="up to ×"+$c("#ucost").value;$c("#u3").textContent=$c("#ugt").value;$c("#u4").textContent=$c("#un").value;});
  $c("#sc").onchange=()=>{setScenario();drawRank();};$c("#load").onclick=()=>{applyEdits();loadOpt();runSim();};$c("#sim").onclick=runSim;$c("#sug").onclick=suggest;rank.querySelector("#ro").onchange=drawRank;
  ["#bud","#dv","#ms","#dl","#life"].forEach(s=>$c(s).onchange=()=>{desKey="";});
  setScenario();v.append(rank);drawRank();runSim();
}
function overview(v){
  const c=Q.record_counts,tg=Q.targets;
  v.append(el(`<div class="card"><h2>Dataset coverage vs targets</h2><div class="kpi">${Object.keys(c).map(k=>`<div><small>${k.replace(/_/g," ")}</small><div class="big">${c[k]}</div><small>${tg[k]!==undefined?`target ${tg[k]} · ${Q.target_attainment_pct[k]}%`:'user-supplied data'}</small></div>`).join("")}</div></div>`));
  v.append(el(`<div class="card"><h2>Data classes</h2><p>${Object.entries(Q.data_class_counts).map(([k,n])=>`<span class="tag ${k}">${k}: ${n}</span>`).join(" ")}</p><p class="mut">“verified” requires a retrieved source. None were retrieved, so no record is marked verified. Counts are targets from the research brief, not quotas; no records were invented to hit them.</p></div>`));
  const ex=D.optimization.experiments.filter(e=>e.objective==="balanced");
  v.append(el(`<div class="card"><h2>What you can do here</h2><ul><li><b>Explorer</b> – sort every dataset.</li><li><b>Compare</b> – up to 4 engines, vehicles, instruments, bodies or missions side by side.</li><li><b>Calculators</b> – rocket equation, Hohmann transfer, link budget, solar/battery sizing.</li><li><b>Optimizer</b> – change budget, margins and objective weights; the optimizer re-searches all ${D.optimization.constraints.scenarios.map(s=>s.id).length} scenarios live in your browser.</li><li><b>Sensitivity &amp; risk</b> – stored one-at-a-time sensitivities and Monte Carlo feasibility.</li><li><b>Quality</b> – known conflicts, gaps and validation results.</li></ul></div>`));
}
function explorer(v){
  const card=el(`<div class="card"><h2>Dataset explorer</h2><label>Dataset<select id="ds"></select></label><label>Filter<input type="text" id="q" placeholder="type to filter"></label><div id="tb"></div></div>`);v.append(card);
  Object.keys(SETS).forEach(k=>card.querySelector("#ds").append(new Option(k+` (${SETS[k][0].length})`,k)));
  const upd=()=>{const [rs,cols]=SETS[card.querySelector("#ds").value],q=card.querySelector("#q").value.toLowerCase();const f=q?rs.filter(r=>JSON.stringify(r).toLowerCase().includes(q)):rs;const tb=card.querySelector("#tb");tb.innerHTML="";tb.append(table(f,cols,{cls:f[0]&&f[0].data_class!==undefined}));};
  card.querySelector("#ds").onchange=upd;card.querySelector("#q").oninput=upd;upd();
}
function compare(v){
  const names=Object.keys(COMPARE);
  const card=el(`<div class="card"><h2>Compare records</h2><label>Dataset<select id="ds"></select></label><div class="chips" id="pick"></div><div id="out"></div></div>`);v.append(card);
  names.forEach(k=>card.querySelector("#ds").append(new Option(k,k)));
  function pick(){const rs=SETS[card.querySelector("#ds").value][0];const p=card.querySelector("#pick");p.innerHTML="";rs.slice(0,60).forEach((r,i)=>{const l=el(`<label><input type="checkbox" value="${i}"> ${r.name||r.id}</label>`);l.firstChild.onchange=out;p.append(l)});out();}
  function out(){const ds=card.querySelector("#ds").value,rs=SETS[ds][0],sel=[...card.querySelectorAll("#pick input:checked")].map(i=>rs[+i.value]).slice(0,4);const o=card.querySelector("#out");
    if(sel.length<2){o.innerHTML='<p class="mut">Tick 2–4 records.</p>';return;}
    let h="<table><thead><tr><th>metric</th>"+sel.map(r=>`<th>${r.name||r.id}</th>`).join("")+"</tr></thead><tbody>";
    const dirs=DIRS[ds]||{},wins=sel.map(()=>0);let scored=0;
    COMPARE[ds].forEach(([lab,p])=>{const vals=sel.map(r=>get(r,p)),known=vals.filter(x=>x!=null),mx=Math.max(...known,0),dir=dirs[p]||0;
      let best=null;if(dir&&known.length>=2){best=dir>0?Math.max(...known):Math.min(...known);if(known.filter(x=>x===best).length===known.length)best=null;}
      if(best!==null){scored++;vals.forEach((x,i)=>{if(x===best)wins[i]++;});}
      h+=`<tr><td>${lab}${dir?`<br><small class="mut">${dir>0?"higher":"lower"} is better</small>`:`<br><small class="mut">no winner (depends on mission)</small>`}</td>`+vals.map(x=>`<td${best!==null&&x===best?' style="background:rgba(22,163,74,.16)"':""}>${best!==null&&x===best?"✔ ":""}${fmt(x)}${x!=null&&mx>0?`<div class="bar" style="width:${Math.max(2,100*x/mx)}%"></div>`:""}</td>`).join("")+"</tr>";});
    if(scored)h+=`<tr><td><b>Metrics won</b><br><small class="mut">of ${scored} direction-coded</small></td>`+wins.map(w=>`<td><b>${w}</b></td>`).join("")+"</tr>";
    h+="</tbody></table><p class='mut'>✔ = best of the selected on a metric where “better” has an unambiguous direction (higher Isp, lower mass/power). Thrust, size and liftoff mass have no universal winner — see the mission verdict below. — = not recorded (never zero-filled).</p>";o.innerHTML=h;
    if(window.EXTRA)EXTRA.compareVerdict(o,ds,sel,UI);}
  card.querySelector("#ds").onchange=pick;pick();
}
function calculators(v){
  const G0=9.80665,AU=149597870.7,MUS=132712440018,C=299792458;
  const c1=el(`<div class="card"><h2>Rocket equation</h2><div class="row"><div><label>Δv (m/s)<input id="dv" type="number" value="4000"></label><label>Isp (s)<input id="isp" type="number" value="310"></label><label>Final (dry+payload) mass (kg)<input id="mf" type="number" value="500"></label></div><div id="o1"></div></div></div>`);
  const u1=()=>{const dv=+c1.querySelector("#dv").value,isp=+c1.querySelector("#isp").value,mf=+c1.querySelector("#mf").value,MR=Math.exp(dv/(isp*G0));c1.querySelector("#o1").innerHTML=`<p>Mass ratio <b>${fmt(MR)}</b><br>Propellant <b>${fmt(mf*(MR-1))} kg</b> (${fmt(100*(1-1/MR))}% of initial)<br>Initial mass <b>${fmt(mf*MR)} kg</b></p><p class="mut">Ideal, no tank mass or gravity/drag losses.</p>`};
  c1.querySelectorAll("input").forEach(i=>i.oninput=u1);u1();
  const bodies=D.celestial.planets.concat(D.celestial.moons);
  const c2=el(`<div class="card"><h2>Hohmann transfer &amp; circular orbit</h2><div class="row"><div><label>Central body<select id="b"></select></label><label>Orbit 1 altitude (km)<input id="h1" type="number" value="400"></label><label>Orbit 2 altitude (km)<input id="h2" type="number" value="35786"></label></div><div id="o2"></div></div></div>`);
  bodies.filter(b=>b.gravitational_parameter_km3_s2>1).forEach(b=>c2.querySelector("#b").append(new Option(b.name,b.id)));c2.querySelector("#b").value="earth";
  const u2=()=>{const b=bodies.find(x=>x.id===c2.querySelector("#b").value),mu=b.gravitational_parameter_km3_s2,R=b.mean_radius_m/1e3,r1=R+ +c2.querySelector("#h1").value,r2=R+ +c2.querySelector("#h2").value,at=(r1+r2)/2;
   const v1=Math.sqrt(mu/r1),v2=Math.sqrt(mu/r2),dv1=Math.abs(Math.sqrt(mu*(2/r1-1/at))-v1),dv2=Math.abs(v2-Math.sqrt(mu*(2/r2-1/at)));
   c2.querySelector("#o2").innerHTML=`<p>v<sub>circ</sub> orbit 1: <b>${fmt(v1*1e3)} m/s</b>, period ${fmt(2*Math.PI*Math.sqrt(r1**3/mu)/60)} min<br>Δv₁ <b>${fmt(dv1*1e3)}</b> + Δv₂ <b>${fmt(dv2*1e3)}</b> = <b>${fmt((dv1+dv2)*1e3)} m/s</b><br>Transfer time ${fmt(Math.PI*Math.sqrt(at**3/mu)/3600)} h</p><p class="mut">Coplanar, circular, impulsive. Add plane change separately.</p>`};
  c2.querySelectorAll("input,select").forEach(i=>i.oninput=u2);u2();
  const c3=el(`<div class="card"><h2>Link budget</h2><div class="row"><div><label>Distance (million km)<input id="d" type="number" value="225"></label><label>Frequency (GHz)<input id="f" type="number" value="8.4"></label><label>Spacecraft dish (m)<input id="D" type="number" value="3"></label><label>Tx power (W)<input id="p" type="number" value="100"></label><label>Ground G/T (dB/K)<input id="gt" type="number" value="53"></label><label>Required Eb/N0 + margin (dB)<input id="eb" type="number" value="5"></label><label>Misc losses (dB)<input id="ml" type="number" value="2"></label></div><div id="o3"></div></div></div>`);
  const u3=()=>{const q=i=>+c3.querySelector("#"+i).value,d=q("d")*1e9,f=q("f")*1e9,gain=10*Math.log10(.55*Math.pow(Math.PI*q("D")*f/C,2)),eirp=10*Math.log10(q("p"))+gain,fs=20*Math.log10(4*Math.PI*d*f/C),R=eirp+q("gt")-fs-q("ml")+228.6-q("eb");
   c3.querySelector("#o3").innerHTML=`<p>Antenna gain ${fmt(gain)} dBi · EIRP ${fmt(eirp)} dBW<br>Free-space loss <b>${fmt(fs)} dB</b><br>Max data rate <b>${fmt(Math.pow(10,R/10))} bit/s</b><br>One-way light time <b>${fmt(d/C/60)} min</b></p><p class="mut">0.55 aperture efficiency; no atmosphere/pointing detail beyond misc loss.</p>`};
  c3.querySelectorAll("input").forEach(i=>i.oninput=u3);u3();
  const c4=el(`<div class="card"><h2>Solar array &amp; battery sizing</h2><div class="row"><div><label>Average load (W)<input id="L" type="number" value="150"></label><label>Distance from Sun (AU)<input id="au" type="number" value="1"></label><label>Orbit period (min)<input id="T" type="number" value="95"></label><label>Eclipse (min)<input id="E" type="number" value="36"></label><label>Cell efficiency<input id="ef" type="number" step="0.01" value="0.29"></label><label>Degradation over life<input id="dg" type="number" step="0.01" value="0.1"></label><label>Battery DoD<input id="dod" type="number" step="0.05" value="0.3"></label></div><div id="o4"></div></div></div>`);
  const u4=()=>{const q=i=>+c4.querySelector("#"+i).value,flux=1361/q("au")**2,Td=q("T")-q("E"),eo=q("E")/60*q("L"),req=q("L")*(1+q("E")/(Td*.9))*1.15/(1-q("dg")),area=req/(q("ef")*flux*.85);
   c4.querySelector("#o4").innerHTML=`<p>Solar flux <b>${fmt(flux)} W/m²</b><br>Array BOL power needed <b>${fmt(req)} W</b> (15% margin, 90% battery efficiency)<br>Array area <b>${fmt(area)} m²</b><br>Eclipse energy ${fmt(eo)} Wh → battery <b>${fmt(eo/(q("dod")*.9))} Wh</b></p>`};
  c4.querySelectorAll("input").forEach(i=>i.oninput=u4);u4();
  v.append(c1,c2,c3,c4);
}
function optimizer(v){
  const cons=D.optimization.constraints,cat={arrays:cons.catalog.arrays,batteries:cons.catalog.batteries,computers:cons.catalog.computers,comms:cons.catalog.comms,propulsion:cons.catalog.propulsion};
  const card=el(`<div class="card"><h2>Optimizer with balance controls</h2><div class="row"><div>
   <label>Scenario<select id="sc"></select></label><label>Objective<select id="ob"></select></label>
   <label>Budget scale <span id="bv"></span><input id="bs" type="range" min="0.5" max="1.5" step="0.05" value="1"></label>
   <label>Mass growth allowance <span id="mv"></span><input id="mga" type="range" min="0" max="0.4" step="0.01" value="0.2"></label>
   <label>Δv margin <span id="dv"></span><input id="dvm" type="range" min="0" max="0.2" step="0.01" value="0.05"></label>
   <label>Power margin <span id="pv"></span><input id="pm" type="range" min="0" max="0.4" step="0.01" value="0.15"></label>
   <label>Min science points scale <span id="sv"></span><input id="ss" type="range" min="0" max="2" step="0.1" value="1"></label></div>
   <div><h3>Balanced objective weights</h3><p class="mut">Used when objective = Balanced: weighted distance to the best-achievable mass, cost and science.</p>
   <label>Weight: low mass <span id="w1v"></span><input id="w1" type="range" min="0" max="5" step="0.5" value="1"></label>
   <label>Weight: low cost <span id="w2v"></span><input id="w2" type="range" min="0" max="5" step="0.5" value="1"></label>
   <label>Weight: high science <span id="w3v"></span><input id="w3" type="range" min="0" max="5" step="0.5" value="1"></label>
   <p><button class="act" id="run">Re-run optimizer</button></p></div></div><div id="res"></div></div>`);v.append(card);
  cons.scenarios.forEach(s=>card.querySelector("#sc").append(new Option(s.name,s.id)));
  Object.entries(OBJ).forEach(([k,o])=>card.querySelector("#ob").append(new Option(o[0],k)));card.querySelector("#ob").append(new Option("Balanced (weights)","balanced"));card.querySelector("#ob").value="balanced";
  const q=i=>+card.querySelector("#"+i).value;
  const lab=()=>{[["bs","bv"],["mga","mv"],["dvm","dv"],["pm","pv"],["ss","sv"],["w1","w1v"],["w2","w2v"],["w3","w3v"]].forEach(([a,b])=>card.querySelector("#"+b).textContent="= "+q(a));};
  async function run(){
    lab();const res=card.querySelector("#res");res.innerHTML="<p class='mut'>Searching…</p>";await new Promise(r=>setTimeout(r,20));
    const sc0=cons.scenarios.find(s=>s.id===card.querySelector("#sc").value),sc=JSON.parse(JSON.stringify(sc0));
    sc.budget*=q("bs");sc.min_science*=q("ss");const G=Object.assign({},cons.global_parameters,{mga:q("mga"),dv_margin:q("dvm"),power_margin:q("pm")});
    const des=enumerate(G,sc,cat),feas=des.filter(d=>d.feasible),ob=card.querySelector("#ob").value;
    const best=ob==="balanced"?balanced(des,{wet_kg:q("w1"),cost:q("w2"),science:q("w3")}):solve(des,ob);
    if(!best){const cnt={};des.forEach(d=>d.violations.forEach(x=>cnt[x]=(cnt[x]||0)+1));res.innerHTML=`<p class="bad"><b>No feasible design</b> among ${des.length.toLocaleString()} evaluated.</p><p>Violation counts (overlapping): ${Object.entries(cnt).map(([k,n])=>`${k}: ${n}`).join(", ")}</p>`;return;}
    const pf=pareto(des).sort((a,b)=>a.wet_kg-b.wet_kg);
    res.innerHTML=`<h3>Result <span class="mut">(${feas.length.toLocaleString()} feasible of ${des.length.toLocaleString()} designs; global optimum within catalog)</span></h3>
     <div class="kpi"><div><small>Launch mass</small><div class="big">${fmt(best.wet_kg)} kg</div></div><div><small>Cost (credits)</small><div class="big">${fmt(best.cost)}</div></div><div><small>Science points</small><div class="big">${fmt(best.science)}</div></div><div><small>Link margin</small><div class="big">${fmt(best.link_margin_db)} dB</div></div><div><small>Avg power</small><div class="big">${fmt(best.avg_power_w)} W</div></div><div><small>Propellant</small><div class="big">${fmt(best.prop_kg)} kg</div></div><div><small>Array (BOL)</small><div class="big">${fmt(best.array_w_bol)} W</div></div><div><small>Mass margin</small><div class="big">${fmt(100*best.mass_margin)}%</div></div></div>
     <p><b>Design:</b> ${best.design.instruments.join(", ")} · ${best.design.computer} · ${best.design.comm} · ${best.design.array} · ${best.design.battery} · ${best.design.propulsion} · ${best.design.vehicle}</p>
     <p class="mut">Δv ${fmt(sc.dv_ms)} m/s — ${sc.dv_basis}</p><h3>Pareto front (${pf.length}): mass vs cost, shade = science</h3><div id="pf"></div>
     <div class="tw"><table><thead><tr><th>mass kg</th><th>cost</th><th>science</th><th>link dB</th><th>instruments</th><th>comm</th><th>prop</th><th>vehicle</th></tr></thead><tbody>${pf.map(d=>`<tr><td>${fmt(d.wet_kg)}</td><td>${fmt(d.cost)}</td><td>${fmt(d.science)}</td><td>${fmt(d.link_margin_db)}</td><td>${d.design.instruments.join(",")}</td><td>${d.design.comm}</td><td>${d.design.propulsion}</td><td>${d.design.vehicle}</td></tr>`).join("")}</tbody></table></div>`;
    scatter(res.querySelector("#pf"),pf,best);
  }
  function scatter(host,pf,best){const W=640,H=280,m=46,xs=pf.map(d=>d.wet_kg),ys=pf.map(d=>d.cost),mx=[Math.min(...xs),Math.max(...xs)],my=[Math.min(...ys),Math.max(...ys)],ms=[Math.min(...pf.map(d=>d.science)),Math.max(...pf.map(d=>d.science))];
   const X=x=>m+(W-m-10)*((x-mx[0])/((mx[1]-mx[0])||1)),Y=y=>H-m+(-(H-m-10))*((y-my[0])/((my[1]-my[0])||1));
   const pts=pf.map(d=>{const t=(d.science-ms[0])/((ms[1]-ms[0])||1);return `<circle cx="${X(d.wet_kg)}" cy="${Y(d.cost)}" r="${d===best||(d.design&&JSON.stringify(d.design)===JSON.stringify(best.design))?8:5}" fill="var(--ac)" fill-opacity="${.25+.75*t}" stroke="var(--fg)" stroke-width="${JSON.stringify(d.design)===JSON.stringify(best.design)?2:0}"><title>${fmt(d.wet_kg)} kg, ${fmt(d.cost)} cr, science ${fmt(d.science)}</title></circle>`}).join("");
   host.innerHTML=`<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Pareto scatter"><line x1="${m}" y1="${H-m}" x2="${W-10}" y2="${H-m}" stroke="var(--bd)"/><line x1="${m}" y1="10" x2="${m}" y2="${H-m}" stroke="var(--bd)"/><text x="${W/2}" y="${H-8}" text-anchor="middle">launch mass (kg)</text><text x="12" y="${H/2}" transform="rotate(-90 12 ${H/2})" text-anchor="middle">cost (credits)</text><text x="${m}" y="${H-m+14}">${fmt(mx[0])}</text><text x="${W-10}" y="${H-m+14}" text-anchor="end">${fmt(mx[1])}</text><text x="${m-4}" y="${H-m}" text-anchor="end">${fmt(my[0])}</text><text x="${m-4}" y="18" text-anchor="end">${fmt(my[1])}</text>${pts}</svg>`;}
  card.querySelectorAll("input[type=range]").forEach(i=>i.oninput=lab);card.querySelector("#run").onclick=run;card.querySelector("#sc").onchange=run;card.querySelector("#ob").onchange=run;lab();run();
}
function sensitivity(v){
  const S=D.optimization.sensitivity,U=D.optimization.uncertainty;
  const c=el(`<div class="card"><h2>One-at-a-time sensitivity (re-optimized)</h2><label>Scenario<select id="sc"></select></label><div id="t"></div><p class="mut">Δ vs baseline of the best achievable minimum mass / minimum cost / maximum science over all feasible designs. Blank = no feasible design or no baseline.</p></div>`);v.append(c);
  D.optimization.constraints.scenarios.forEach(s=>c.querySelector("#sc").append(new Option(s.name,s.id)));
  const u=()=>{const id=c.querySelector("#sc").value,rs=S.filter(r=>r.scenario_id===id);c.querySelector("#t").innerHTML="";c.querySelector("#t").append(table(rs.map(r=>({parameter:r.parameter+" = "+r.value,feasible_designs:r.result.feasible,baseline_feasible:r.baseline.feasible,d_min_mass_pct:r.delta_min_mass_pct,d_min_cost_pct:r.delta_min_cost_pct,d_max_science_pct:r.delta_max_science_pct})),["parameter","feasible_designs","baseline_feasible","d_min_mass_pct","d_min_cost_pct","d_max_science_pct"],{cls:false}));};
  c.querySelector("#sc").onchange=u;u();
  const m=el(`<div class="card"><h2>Monte Carlo feasibility of selected designs</h2><div id="mt"></div><p class="mut">Distributions are assumptions, not measured source uncertainties: ${U[0].distributions}. Seed ${U[0].seed}, ${U[0].samples} samples each.</p></div>`);
  m.querySelector("#mt").append(table(U.map(r=>({scenario:r.scenario_id,design:r.design_label,p_feasible:r.p_feasible,mass_mean_kg:r.wet_kg_mean,mass_p95_kg:r.wet_kg_p95,cost_mean:r.cost_mean,cost_p95:r.cost_p95,failures:JSON.stringify(r.failure_reason_counts)})),["scenario","design","p_feasible","mass_mean_kg","mass_p95_kg","cost_mean","cost_p95","failures"],{cls:false}));v.append(m);
}
function quality(v){
  v.append(el(`<div class="card"><h2>Validation</h2>${VAL?`<p><b>${VAL.passed}/${VAL.total}</b> automated checks passed (${VAL.run_date}).</p><div class="tw"><table><tbody>${VAL.checks.map(c=>`<tr><td class="${c.passed?"ok":"bad"}">${c.passed?"PASS":"FAIL"}</td><td>${c.check}</td></tr>`).join("")}</tbody></table></div><h3>Not performed</h3><ul>${VAL.not_performed.map(x=>`<li>${x}</li>`).join("")}</ul>`:"<p class='mut'>validation_report.json not found.</p>"}</div>`));
  v.append(el(`<div class="card"><h2>Known conflicts &amp; issues</h2><ul>${Q.known_conflicts.map(k=>`<li><b>${k.topic}</b>: ${k.note||k.values.join(" vs ")+" — "+k.preferred}</li>`).join("")}</ul></div>`));
  v.append(el(`<div class="card"><h2>Missing categories</h2><ul>${Q.missing_categories.map(x=>`<li>${x}</li>`).join("")}</ul></div>`));
  v.append(el(`<div class="card"><h2>Field completeness (% non-null)</h2>${Object.entries(Q.completeness_pct).map(([k,o])=>`<h3>${k}</h3><p>${Object.entries(o).map(([f,p])=>`<span class="tag">${f}: ${p}%</span>`).join(" ")}</p>`).join("")}</div>`));
  const sc=el(`<div class="card"><h2>Sources</h2><div id="s"></div></div>`);sc.querySelector("#s").append(table(D.metadata.sources.map(s=>({id:s.id,title:s.title,organization:s.organization,url:s.url,retrieved:s.retrieved})),["id","title","organization","url","retrieved"],{cls:false}));v.append(sc);
}
tabs();render();
})();
