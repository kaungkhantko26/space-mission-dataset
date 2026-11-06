// Space Mission Research Explorer — STRICT mode: only verified data (see Quality tab). No estimated, fictional or merely recalled values are shown.
(async function(){
const $=s=>document.querySelector(s), el=h=>{const t=document.createElement("template");t.innerHTML=h.trim();return t.content.firstChild};
const fmt=(v,d=3)=>v==null?"—":typeof v==="number"?(Math.abs(v)>=1e6||(Math.abs(v)<1e-3&&v!==0)?v.toExponential(2):(+v.toPrecision(d+1)).toLocaleString()):String(v);
const esc=s=>String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
let D; try{D=await (await fetch("data/all_space_mission_data.json")).json();}catch(e){$("#view").textContent="Could not load data/all_space_mission_data.json: "+e;return;}
let VAL=null; try{VAL=await (await fetch("data/validation_report.json")).json();}catch(e){}
const Q=D.metadata.quality, get=(o,p)=>p.split(".").reduce((a,k)=>a==null?a:a[k],o);
$("#banner").innerHTML=`<b>Strict mode — verified data only.</b> ${esc(Q.statement)}`;
const SETS={
 "Planets & dwarf planets":[D.celestial.planets,["name","category","gravitational_parameter_km3_s2","mean_radius_m","mass_kg","surface_gravity_m_s2","derived.escape_velocity_m_s","semi_major_axis_m"]],
 "Moons":[D.celestial.moons,["name","parent_id","gravitational_parameter_km3_s2","mean_radius_m","mass_kg","derived.escape_velocity_m_s"]],
 "Asteroids":[D.celestial.asteroids,["name","gravitational_parameter_km3_s2","mean_radius_m","mass_kg","rotation_period_h"]],
 "Moon mean elements (JPL)":[D.real_data.moon_mean_elements,["planet","satellite","semi_major_axis_km","eccentricity","inclination_deg","period_days","frame","epoch_tdb"]],
 "Chemical engines (verified fields)":[D.propulsion.rocket_engines,["name","thrust_vac_n","thrust_sl_n","isp_sl_s","isp_vac_s","dry_mass_kg"]],
 "Electric thrusters":[D.propulsion.electric_propulsion,["name","type","thrust_vac_n","isp_vac_s","power_w","dry_mass_kg"]],
 "Launch vehicles (verified fields)":[D.launch.launch_vehicles,["name","height_m","liftoff_mass_kg","thrust_sl_n","derived.liftoff_thrust_to_weight","fairing_diam_m","stages"]],
 "Payload capacities":[D.launch.payload_capabilities,["vehicle_id","orbit","payload_kg","altitude_km","inclination_deg","mode"]],
 "Stages (Saturn V)":[D.launch.rocket_stages,["vehicle_id","stage","dry_mass_kg","propellant_mass_kg","n_engines"]],
 "Missions (verified fields)":[D.missions.historical,["name","launch_date","launch_vehicle_family","launch_mass_kg"]],
 "NASA facilities":[D.infrastructure.nasa_facilities,["center","facility","status","occupied","city","state","lat","lon"]],
};
const COMPARE={
 "Chemical engines (verified fields)":[["Vac thrust (N)","thrust_vac_n"],["SL thrust (N)","thrust_sl_n"],["Vac Isp (s)","isp_vac_s"],["SL Isp (s)","isp_sl_s"],["Dry mass (kg)","dry_mass_kg"]],
 "Electric thrusters":[["Thrust (N)","thrust_vac_n"],["Isp (s)","isp_vac_s"],["Power (W)","power_w"],["Mass (kg)","dry_mass_kg"]],
 "Launch vehicles (verified fields)":[["Liftoff mass (kg)","liftoff_mass_kg"],["Liftoff thrust (N)","thrust_sl_n"],["Liftoff T/W","derived.liftoff_thrust_to_weight"],["Height (m)","height_m"],["Fairing dia (m)","fairing_diam_m"]],
 "Planets & dwarf planets":[["GM (km³/s²)","gravitational_parameter_km3_s2"],["Mean radius (m)","mean_radius_m"],["Gravity (m/s²)","surface_gravity_m_s2"],["Escape v (m/s)","derived.escape_velocity_m_s"]],
 "Moons":[["GM (km³/s²)","gravitational_parameter_km3_s2"],["Mean radius (m)","mean_radius_m"],["Escape v (m/s)","derived.escape_velocity_m_s"]],
 "Stages (Saturn V)":[["Dry mass (kg)","dry_mass_kg"],["Propellant (kg)","propellant_mass_kg"]],
};
const DIRS={"Chemical engines (verified fields)":{isp_vac_s:1,isp_sl_s:1,dry_mass_kg:-1},"Electric thrusters":{isp_vac_s:1,power_w:-1,dry_mass_kg:-1}};
window.UI={el,table:(...a)=>table(...a),fmt,get,D,Q,SETS,esc};
const TABS=["Overview","Guide","Explorer","Compare","Mission fit","Calculators","Asteroid targets","Facilities","API","Quality"];
let cur=TABS[0];
function tabs(){const n=$("#tabs");n.innerHTML="";TABS.forEach(t=>{const b=el(`<button role="tab" aria-selected="${t===cur}">${t}</button>`);b.onclick=()=>{cur=t;tabs();render();};n.append(b);});}
function render(){const v=$("#view");v.innerHTML="";({Overview:overview,Guide:guide,Explorer:explorer,Compare:compare,"Mission fit":v=>EXTRA.missionFit(v,UI),Calculators:calculators,"Asteroid targets":v=>EXTRA.asteroids(v,UI),Facilities:v=>EXTRA.facilities(v,UI),API:v=>EXTRA.apiTab(v,UI),Quality:quality})[cur](v);}
function table(rows,cols,opts={}){
  let sortK=null,dir=1; const lim=opts.limit||1000; const wrap=el(`<div class="tw"><table></table></div>`),t=wrap.firstChild;
  function draw(){const rs=sortK==null?rows:[...rows].sort((a,b)=>{const x=get(a,sortK),y=get(b,sortK);if(x==null)return 1;if(y==null)return -1;return (x>y?1:x<y?-1:0)*dir});
   t.innerHTML="<thead><tr>"+cols.map(c=>`<th data-k="${c}">${c.split(".").pop().replace(/_/g," ")}${sortK===c?(dir>0?" ▲":" ▼"):""}</th>`).join("")+"</tr></thead><tbody>"+
   rs.slice(0,lim).map(r=>"<tr>"+cols.map(c=>`<td>${typeof get(r,c)==="string"?esc(get(r,c)):fmt(get(r,c))}</td>`).join("")+"</tr>").join("")+"</tbody>"+(rs.length>lim?`<caption class="mut">showing ${lim} of ${rs.length}; sort or filter to see others</caption>`:"");
   t.querySelectorAll("th[data-k]").forEach(h=>h.onclick=()=>{const k=h.dataset.k;dir=sortK===k?-dir:1;sortK=k;draw();});}
  draw();return wrap;}
window.TABLE=table;
function overview(v){
  const c=Q.record_counts,names={planets:"planets & dwarf planets",moons:"moons",asteroids:"asteroids",orbital_elements:"orbital element sets",rocket_engines:"chemical engines (verified fields)",electric_propulsion:"electric thrusters",launch_vehicles:"launch vehicles (verified fields)",rocket_stages:"Saturn V stages",boosters:"boosters",payload_capabilities:"payload capacities",missions:"missions (verified fields)",nasa_facilities:"NASA facilities (official)",nhats_targets:"NHATS asteroid targets",neo_catalog:"near-Earth objects (SBDB)",moon_mean_elements:"moon mean-element sets",sources:"retrieved sources"};
  v.append(el(`<div class="card"><h2>What is in the verified dataset</h2><div class="kpi">${Object.keys(names).map(k=>`<div><small>${names[k]}</small><div class="big">${(c[k]||0).toLocaleString()}</div></div>`).join("")}</div>
   <p class="mut">Every record is <b>verified</b>: compared with a retrieved source (field-by-field provenance) or ingested directly from an authoritative dataset. Values that could not be verified were removed, not zero-filled — coverage is partial by design.</p></div>`));
  v.append(el(`<div class="card"><h2>What was left out, and why</h2><ul><li>Instruments, spacecraft components, propellants, atmospheres, ground stations — no retrievable source stated the numbers.</li><li>Falcon, Starship, Electron and most engine specifications — vendor pages are JavaScript-only, blocked, or unavailable.</li><li>The optimizer, costs and science weights — they depended on estimated/fictional catalog values.</li><li>The SpaceX launch table — its origin could not be verified (the API was down).</li></ul><p class="mut">See the Quality tab for conflicts found (recalled values replaced by sourced ones) and the validation results.</p></div>`));
}
function guide(v){v.append(el(`<div class="card"><h2>How to use this site</h2><ol>
<li><b>Explorer</b> – browse and sort every verified collection (click a column header).</li>
<li><b>Compare</b> – tick 2–4 engines, thrusters, vehicles, planets or moons; ✔ marks the best on metrics where “better” is unambiguous, and the mission verdict applies the Mission-fit rules to your selection.</li>
<li><b>Mission fit</b> – choose Moon, Mars or GTO and a spacecraft dry mass; vehicles with a <i>recorded</i> capacity and engines with recorded thrust/Isp are ranked with reasons. Parts lacking verified numbers are shown as “Not rated”.</li>
<li><b>Calculators</b> – rocket equation, Hohmann transfer (uses verified GM/radius), link budget, light time.</li>
<li><b>Asteroid targets</b> – JPL NHATS accessible near-Earth targets (lowest delta-v) and the SBDB NEO catalog with measured diameters.</li>
<li><b>Facilities</b> – the official NASA Facilities table with filters and a map.</li>
<li><b>API</b> – try the JSON API live; <a href="api.html">api.html</a> has the guide and clients.</li>
<li><b>Quality</b> – validation checks, sources with file hashes, and the recalled values that were corrected.</li></ol>
<p class="mut">Mission-fit limits (restart needed, 0.02–5 g acceleration, 20× “overkill”) are teaching heuristics, not data. Rankings use only verified fields.</p></div>`));}
function explorer(v){
  const card=el(`<div class="card"><h2>Dataset explorer</h2><label>Dataset<select id="ds"></select></label><label>Filter<input type="text" id="q" placeholder="type to filter"></label><div id="tb"></div></div>`);v.append(card);
  Object.keys(SETS).forEach(k=>card.querySelector("#ds").append(new Option(k+` (${SETS[k][0].length})`,k)));
  const upd=()=>{const [rs,cols]=SETS[card.querySelector("#ds").value],q=card.querySelector("#q").value.toLowerCase();const f=q?rs.filter(r=>JSON.stringify(r).toLowerCase().includes(q)):rs;const tb=card.querySelector("#tb");tb.innerHTML="";tb.append(table(f,cols,{limit:500}));};
  card.querySelector("#ds").onchange=upd;card.querySelector("#q").oninput=upd;upd();
}
function compare(v){
  const card=el(`<div class="card"><h2>Compare records</h2><label>Dataset<select id="ds"></select></label><div class="chips" id="pick"></div><div id="out"></div></div>`);v.append(card);
  Object.keys(COMPARE).forEach(k=>card.querySelector("#ds").append(new Option(k,k)));
  function pick(){const rs=SETS[card.querySelector("#ds").value][0];const p=card.querySelector("#pick");p.innerHTML="";rs.slice(0,60).forEach((r,i)=>{const l=el(`<label><input type="checkbox" value="${i}"> ${esc(r.name||r.id)}</label>`);l.firstChild.onchange=out;p.append(l)});out();}
  function out(){const ds=card.querySelector("#ds").value,rs=SETS[ds][0],sel=[...card.querySelectorAll("#pick input:checked")].map(i=>rs[+i.value]).slice(0,4);const o=card.querySelector("#out");
    if(sel.length<2){o.innerHTML='<p class="mut">Tick 2–4 records.</p>';return;}
    let h="<table><thead><tr><th>metric</th>"+sel.map(r=>`<th>${esc(r.name||r.id)}</th>`).join("")+"</tr></thead><tbody>";
    const dirs=DIRS[ds]||{},wins=sel.map(()=>0);let scored=0;
    COMPARE[ds].forEach(([lab,p])=>{const vals=sel.map(r=>get(r,p)),known=vals.filter(x=>x!=null),mx=Math.max(...known,0),dir=dirs[p]||0;
      let best=null;if(dir&&known.length>=2){best=dir>0?Math.max(...known):Math.min(...known);if(known.filter(x=>x===best).length===known.length)best=null;}
      if(best!==null){scored++;vals.forEach((x,i)=>{if(x===best)wins[i]++;});}
      h+=`<tr><td>${lab}${dir?`<br><small class="mut">${dir>0?"higher":"lower"} is better</small>`:`<br><small class="mut">no winner (depends on mission)</small>`}</td>`+vals.map(x=>`<td${best!==null&&x===best?' style="background:rgba(22,163,74,.16)"':""}>${best!==null&&x===best?"✔ ":""}${fmt(x)}${x!=null&&mx>0?`<div class="bar" style="width:${Math.max(2,100*x/mx)}%"></div>`:""}</td>`).join("")+"</tr>";});
    if(scored)h+=`<tr><td><b>Metrics won</b><br><small class="mut">of ${scored} direction-coded</small></td>`+wins.map(w=>`<td><b>${w}</b></td>`).join("")+"</tr>";
    h+="</tbody></table><p class='mut'>— = not verified/recorded (omitted, never zero-filled). ✔ = best of the selection where a direction is unambiguous.</p>";o.innerHTML=h;EXTRA.compareVerdict(o,ds,sel,UI);}
  card.querySelector("#ds").onchange=pick;pick();
}
function calculators(v){
  const G0=9.80665,C=299792.458,AU=149597870.7;
  const c1=el(`<div class="card"><h2>Rocket equation</h2><div class="row"><div><label>Δv (m/s)<input id="dv" type="number" value="4000"></label><label>Isp (s) — e.g. NEXT 4190, BPT-4000 2150<input id="isp" type="number" value="310"></label><label>Final (dry+payload) mass (kg)<input id="mf" type="number" value="500"></label></div><div id="o1"></div></div></div>`);
  const u1=()=>{const dv=+c1.querySelector("#dv").value,isp=+c1.querySelector("#isp").value,mf=+c1.querySelector("#mf").value,MR=Math.exp(dv/(isp*G0));c1.querySelector("#o1").innerHTML=`<p>Mass ratio <b>${fmt(MR)}</b><br>Propellant <b>${fmt(mf*(MR-1))} kg</b> (${fmt(100*(1-1/MR))}% of initial)<br>Initial mass <b>${fmt(mf*MR)} kg</b></p><p class="mut">Ideal Tsiolkovsky; no tank mass, gravity or drag losses.</p>`};
  c1.querySelectorAll("input").forEach(i=>i.oninput=u1);u1();
  const bodies=D.celestial.planets.concat(D.celestial.moons).filter(b=>b.gravitational_parameter_km3_s2>1&&b.mean_radius_m);
  const c2=el(`<div class="card"><h2>Hohmann transfer between circular orbits <span class="tag verified">GM &amp; radius verified</span></h2><div class="row"><div><label>Central body<select id="b"></select></label><label>Orbit 1 altitude (km)<input id="h1" type="number" value="400"></label><label>Orbit 2 altitude (km)<input id="h2" type="number" value="35786"></label></div><div id="o2"></div></div></div>`);
  bodies.forEach(b=>c2.querySelector("#b").append(new Option(b.name,b.id)));c2.querySelector("#b").value="earth";
  const u2=()=>{const b=bodies.find(x=>x.id===c2.querySelector("#b").value),mu=b.gravitational_parameter_km3_s2,R=b.mean_radius_m/1e3,r1=R+ +c2.querySelector("#h1").value,r2=R+ +c2.querySelector("#h2").value,at=(r1+r2)/2;
   const v1=Math.sqrt(mu/r1),v2=Math.sqrt(mu/r2),dv1=Math.abs(Math.sqrt(mu*(2/r1-1/at))-v1),dv2=Math.abs(v2-Math.sqrt(mu*(2/r2-1/at)));
   c2.querySelector("#o2").innerHTML=`<p>v<sub>circ</sub> orbit 1: <b>${fmt(v1*1e3)} m/s</b>, period ${fmt(2*Math.PI*Math.sqrt(r1**3/mu)/60)} min<br>Δv₁ <b>${fmt(dv1*1e3)}</b> + Δv₂ <b>${fmt(dv2*1e3)}</b> = <b>${fmt((dv1+dv2)*1e3)} m/s</b><br>Transfer time ${fmt(Math.PI*Math.sqrt(at**3/mu)/3600)} h</p><p class="mut">Derived: coplanar, circular, impulsive.</p>`};
  c2.querySelectorAll("input,select").forEach(i=>i.oninput=u2);u2();
  const c3=el(`<div class="card"><h2>Link budget (physics only — you supply the hardware numbers)</h2><div class="row"><div><label>Distance (million km)<input id="d" type="number" value="225"></label><label>Frequency (GHz)<input id="f" type="number" value="8.4"></label><label>Spacecraft dish (m)<input id="D" type="number" value="3"></label><label>Aperture efficiency<input id="e" type="number" step="0.05" value="0.55"></label><label>Tx power (W)<input id="p" type="number" value="100"></label><label>Ground G/T (dB/K)<input id="gt" type="number" value="53"></label><label>Required Eb/N0 + margin (dB)<input id="eb" type="number" value="5"></label><label>Misc losses (dB)<input id="ml" type="number" value="2"></label></div><div id="o3"></div></div></div>`);
  const u3=()=>{const q=i=>+c3.querySelector("#"+i).value,d=q("d")*1e9,f=q("f")*1e9,c=299792458,gain=10*Math.log10(q("e")*Math.pow(Math.PI*q("D")*f/c,2)),eirp=10*Math.log10(q("p"))+gain,fs=20*Math.log10(4*Math.PI*d*f/c),R=eirp+q("gt")-fs-q("ml")+228.6-q("eb");
   c3.querySelector("#o3").innerHTML=`<p>Antenna gain ${fmt(gain)} dBi · EIRP ${fmt(eirp)} dBW<br>Free-space loss <b>${fmt(fs)} dB</b><br>Max data rate <b>${fmt(Math.pow(10,R/10))} bit/s</b><br>One-way light time <b>${fmt(d/c/60)} min</b></p><p class="mut">Friis equation; inputs are yours, not dataset values.</p>`};
  c3.querySelectorAll("input").forEach(i=>i.oninput=u3);u3();
  const lt=el(`<div class="card"><h2>One-way light time from verified orbits <span class="tag verified">derived</span></h2><div id="lt"></div></div>`);
  lt.querySelector("#lt").append(table(D.analysis.light_time,["target","min_distance_km","max_distance_km","min_one_way_light_time_min","max_one_way_light_time_min"],{}));
  v.append(c1,c2,c3,lt);
}
function quality(v){
  v.append(el(`<div class="card"><h2>Validation</h2>${VAL?`<p><b>${VAL.passed}/${VAL.total}</b> automated checks passed (${VAL.run_date}). They re-read values from the raw retrieved files and scan for any unverified, estimated or fictional marker.</p><div class="tw"><table><tbody>${VAL.checks.map(c=>`<tr><td class="${c.passed?"ok":"bad"}">${c.passed?"PASS":"FAIL"}</td><td>${esc(c.check)}</td></tr>`).join("")}</tbody></table></div><h3>Not performed</h3><ul>${VAL.not_performed.map(x=>`<li>${esc(x)}</li>`).join("")}</ul>`:"<p class='mut'>validation_report.json not found.</p>"}</div>`));
  const V=D.verification&&D.verification.celestial;
  if(V){const ck=V.checks,nv=ck.filter(c=>c.status==="verified").length,nc=(Q.conflicts_resolved||[]).length;
   const card=el(`<div class="card"><h2>Verification against retrieved sources</h2><p><b>${nv}</b> celestial field checks matched the retrieved JPL/NASA page; <b>${nc}</b> recalled values disagreed and were <b>replaced by the sourced value</b>. Launch/engine/mission checks are in each record's <code>field_verification</code>. Retrieved files: ${D.verification.retrieved_files.length} (SHA-256 stored).</p><div id="vc"></div></div>`);
   card.querySelector("#vc").append(table((Q.conflicts_resolved||[]).map(c=>({record:c.record_id,field:c.field,recalled_value:c.recalled_value,source_value:c.source_value,source_text:c.source_text,source:c.source_id})),["record","field","recalled_value","source_value","source_text","source"],{}));v.append(card);}
  v.append(el(`<div class="card"><h2>Known issues &amp; scope</h2><ul>${Q.known_conflicts.map(k=>`<li><b>${esc(k.topic)}</b>: ${esc(k.note)}</li>`).join("")}</ul><h3>Not included (no verified source)</h3><ul>${Q.missing_categories.map(x=>`<li>${esc(x)}</li>`).join("")}</ul></div>`));
  const sc=el(`<div class="card"><h2>Sources (all retrieved)</h2><div id="s"></div></div>`);sc.querySelector("#s").append(table(D.metadata.sources.map(s=>({id:s.id,title:s.title,organization:s.organization,url:s.url,retrieved:s.retrieval_date})),["id","title","organization","url","retrieved"],{}));v.append(sc);
}
tabs();render();
})();
