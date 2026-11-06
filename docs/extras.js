// Extra tabs: Mission fit, compare verdicts, Launch & facilities, API. Loaded before app.js; app.js passes helpers (UI).
(function(){
const ST={mission:"moon",dry:300};
const VCOL={"Suitable":"ok","Good fit":"ok","Marginal":"","Relevant (cost unknown)":"","Unproven":"","Historical":"","Overkill":"","Overpowered":"bad","Not suitable":"bad","Not useful":"bad","Not modeled":"mut","Not rated":"mut"};
const esc=s=>String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
function fitRow(kind,r,fmt){
  let nums="";
  if(kind==="veh")nums=`${r.capacity_kg?fmt(r.capacity_kg)+" kg":"—"} · need ${r.required_kg?fmt(r.required_kg)+" kg":"—"} · ×${r.margin_ratio?r.margin_ratio.toFixed(1):"—"}`;
  if(kind==="eng")nums=`prop ${r.prop_kg!=null?fmt(r.prop_kg)+" kg":"—"} · ${r.accel_g!=null?r.accel_g.toFixed(3)+" g":"—"} · burn ${r.burn||"—"}`;
  if(kind==="ins")nums=`rel ${r.relevance??"—"}/3 · ${r.mass_kg??"—"} kg · ${r.power_w??"—"} W`;
  return `<tr><td>${esc(r.name)}</td><td class="${VCOL[r.verdict]||""}"><b>${r.verdict}</b></td><td>${nums}</td><td class="mut" style="white-space:normal;min-width:260px">${r.reasons.map(esc).join(" ")}</td></tr>`;}
function fitTable(kind,rows,fmt,limit){return `<div class="tw"><table><thead><tr><th>${kind==="veh"?"launch vehicle":kind==="eng"?"engine / thruster":"instrument"}</th><th>verdict</th><th>key numbers</th><th>why</th></tr></thead><tbody>${rows.slice(0,limit||rows.length).map(r=>fitRow(kind,r,fmt)).join("")}</tbody></table></div>`;}
function controls(el){const A=ADV;const c=el(`<div class="row"><div><label>Mission<select id="ms"></select></label></div><div><label>Spacecraft dry mass (kg) – everything except propellant<input id="dm" type="number" min="1" value="${ST.dry}"></label></div></div>`);
  Object.entries(A.MISSIONS).forEach(([k,m])=>c.querySelector("#ms").append(new Option(m.name,k)));c.querySelector("#ms").value=ST.mission;return c;}
function missionFit(v,UI){const {el,fmt,D}=UI,A=ADV;
  const card=el(`<div class="card"><h2>Mission fit — which parts are better for which mission</h2><p class="mut">Pick a mission and a spacecraft dry mass. Launch vehicles, engines and instruments are scored with <b>transparent rules</b> (shown in the “why” column) applied to the dataset (celestial constants are verified; launch-vehicle, engine and instrument values mostly are not). A part marked “Not rated” lacks the data needed — it is never guessed.</p></div>`);
  const c=controls(el);card.append(c);const out=el("<div></div>");card.append(out);v.append(card);
  function run(){ST.mission=c.querySelector("#ms").value;ST.dry=Math.max(1,+c.querySelector("#dm").value||300);const M=A.MISSIONS[ST.mission],R=A.adviseAll(D,ST.mission,ST.dry);
    const ok=r=>["Suitable","Good fit","Marginal"].includes(r.verdict);
    const bv=R.veh.find(r=>["Suitable","Marginal"].includes(r.verdict))||R.veh.find(r=>r.verdict==="Overkill"),be=R.eng.find(r=>r.verdict==="Suitable"),bi=R.ins.filter(r=>r.verdict==="Good fit").slice(0,3);
    const rel=D.launch_history.analysis.mission_reliability,fam=bv&&/Falcon/.test(bv.name);
    const pow=D.analysis.power.solar_flux,flux=ST.mission==="mars"?pow.find(x=>x.body_id==="mars").flux_w_m2:1361;
    const lt=ST.mission==="mars"?D.analysis.communications.light_time.find(x=>x.target==="Mars max").one_way_s/60:ST.mission==="moon"?D.analysis.communications.light_time[0].one_way_s/60:null;
    out.innerHTML=`<h3>Recommended starting build for: ${esc(M.name)}</h3><div class="kpi">
      <div><small>Launch vehicle</small><div style="font-weight:650">${bv?esc(bv.name):"none rated"}</div><small>${bv?`${bv.verdict} · ×${bv.margin_ratio.toFixed(1)} capacity margin`:"no vehicle with a recorded capacity fits"}</small></div>
      <div><small>In-space propulsion</small><div style="font-weight:650">${be?esc(be.name):"none rated"}</div><small>${be?`${fmt(be.prop_kg)} kg propellant, ${be.accel_g.toFixed(2)} g`:""}</small></div>
      <div><small>Instruments</small><div style="font-weight:650">${bi.length?bi.map(i=>esc(i.name)).join(", "):"none rated"}</div><small>by relevance then mass+power</small></div>
      <div><small>Onboard Δv</small><div class="big">${fmt(M.dv)}</div><small>m/s · ${esc(M.dv_basis)}</small></div>
      <div><small>Sunlight</small><div class="big">${fmt(flux)}</div><small>W/m²${lt?` · one-way light time ${lt.toFixed(1)} min`:""}</small></div></div>
      ${fam?`<p>Evidence for the Falcon family in your uploaded launch table: <b>${rel.successes}/${rel.launches}</b> missions successful (95% Wilson interval ${(100*rel.wilson95_low).toFixed(1)}–${(100*rel.wilson95_high).toFixed(1)}%), covering 2010–2018 only.</p>`:""}
      ${M.scenario?`<p class="mut">Next: open <b>Optimizer</b> or <b>Simulator</b> and choose scenario <code>${M.scenario}</code> to trade budget, mass and science for this mission and see its success rate.</p>`:`<p class="mut">No optimizer scenario exists for this mission yet.</p>`}
      <h3>Launch vehicles</h3>${fitTable("veh",R.veh,fmt)}<h3>Engines and thrusters (in-space burns)</h3>${fitTable("eng",R.eng,fmt)}<h3>Instruments</h3>${fitTable("ins",R.ins,fmt)}
      <p class="mut">Rules: vehicles — recorded capacity for the mission's orbit × 0.9 launch margin must exceed the injected mass needed for the Δv at Isp 310 s; ranked smallest-sufficient first; &gt;20× margin = “Overkill”. Engines — need restart (multi-burn), thrust under 500 kN, acceleration between 0.02 and 5 g (assumed limits); ion/Hall only for LEO/GTO missions with ≤120-day burns; ranked by propellant. Instruments — educational relevance weights (fictional) vs mass + power/10. Retired/developmental vehicles are flagged. These are teaching heuristics on unverified data, not design approval.</p>`;}
  c.querySelector("#ms").onchange=run;c.querySelector("#dm").oninput=run;run();}
function compareVerdict(o,ds,sel,UI){const {el,fmt}=UI,A=ADV;
  const kind={"Launch vehicles":"veh","Chemical engines":"eng","Electric propulsion":"eng","Instruments":"ins"}[ds];
  const box=el(`<div style="margin-top:12px"><h3>Which is better for a mission?</h3></div>`);o.append(box);
  if(!kind){box.append(el("<p class='mut'>Mission verdicts are available for launch vehicles, engines, electric propulsion and instruments.</p>"));return;}
  const c=controls(el);box.append(c);const out=el("<div></div>");box.append(out);
  function run(){ST.mission=c.querySelector("#ms").value;ST.dry=Math.max(1,+c.querySelector("#dm").value||300);
    const rows=sel.map(r=>kind==="veh"?A.vehicleFit(r,ST.mission,ST.dry):kind==="eng"?A.engineFit(r,ST.mission,ST.dry):A.instrumentFit(r,ST.mission));
    const ranked=A.rankFits(rows),best=ranked[0];
    const good=best&&["Suitable","Good fit","Marginal","Relevant (cost unknown)"].includes(best.verdict);
    out.innerHTML=`<p>${good?`<b>Best of your selection for ${esc(A.MISSIONS[ST.mission].name)}: <span class="ok">${esc(best.name)}</span></b> (${best.verdict}).`:`<b class="bad">None of the selected parts is suitable for ${esc(A.MISSIONS[ST.mission].name)}</b> at ${ST.dry} kg dry mass — see reasons.`}</p>${fitTable(kind,ranked,fmt)}`;}
  c.querySelector("#ms").onchange=run;c.querySelector("#dm").oninput=run;run();}
function bars(items,w,h,colA,colB){const mx=Math.max(...items.map(i=>i.a),1),bw=w/items.length;return `<svg viewBox="0 0 ${w} ${h+36}" width="100%" role="img">${items.map((i,k)=>`<rect x="${k*bw+3}" y="${16+h-h*i.a/mx}" width="${bw-6}" height="${h*i.a/mx}" fill="var(--ac)" fill-opacity=".35"><title>${i.label}: ${i.a} launches</title></rect><rect x="${k*bw+3}" y="${16+h-h*i.b/mx}" width="${bw-6}" height="${h*i.b/mx}" fill="var(--ac2)"><title>${i.label}: ${i.b} landing successes</title></rect><text x="${k*bw+bw/2}" y="${h+30}" text-anchor="middle">${i.label}</text><text x="${k*bw+bw/2}" y="${16+h-h*i.a/mx-4}" text-anchor="middle">${i.a}</text>`).join("")}</svg>`;}
function launchFacilities(v,UI){const {el,table,fmt,D}=UI,an=D.launch_history.analysis,fa=D.infrastructure.analysis,L=D.launch_history.launches;
  const yrs=Object.entries(an.launches_by_year).map(([y,o])=>({label:y,a:o.launches,b:o.landing_successes}));
  v.append(el(`<div class="card"><h2>SpaceX launch history (your uploaded file)</h2><p class="mut">${an.coverage.launches} launches, ${an.coverage.first} → ${an.coverage.last}. ${an.coverage.caveat}</p><div class="kpi">
   <div><small>Mission success</small><div class="big">${an.mission_reliability.successes}/${an.mission_reliability.launches}</div><small>95% Wilson ${(100*an.mission_reliability.wilson95_low).toFixed(1)}–${(100*an.mission_reliability.wilson95_high).toFixed(1)}%</small></div>
   <div><small>Landing success</small><div class="big">${an.landing.successes}/${an.landing.attempts}</div><small>pad/drone-ship attempts · ${(100*an.landing.success_rate).toFixed(0)}%</small></div>
   <div><small>Rows with a reflown booster</small><div class="big">${an.reflown_rows.count}</div><small>${(100*an.reflown_rows.fraction).toFixed(0)}% of rows</small></div>
   <div><small>Unknown payload mass</small><div class="big">${an.mass_unknown_rows}</div><small>classified/blank</small></div></div>
   <h3>Launches per year <span class="mut">(light = launches, dark = successful landings)</span></h3>${bars(yrs,520,110)}
   <h3>Payload mass by orbit class (kg)</h3><div id="pm"></div></div>`));
  const pm=Object.entries(an.payload_mass_by_orbit_class).map(([k,o])=>({orbit_class:k,n:o.n,min_kg:o.min_kg,median_kg:o.median_kg,max_kg:o.max_kg}));
  v.lastChild.querySelector("#pm").append(table(pm,["orbit_class","n","min_kg","median_kg","max_kg"],{cls:false}));
  const F=D.infrastructure.nasa_facilities,cats=[...new Set(F.map(f=>f.category))].sort(),cens=[...new Set(F.map(f=>f.center))].sort();
  const fc=el(`<div class="card"><h2>NASA facilities (your uploaded file)</h2><p class="mut">${fa.records} facilities. Category is keyword-derived from the facility name and unreviewed; ${fa.quality.missing_status} rows have no status. ${fa.antennas.length} look like antennas/ground stations.</p>
   <div class="row"><div><label>Center<select id="fc"><option value="">all</option>${cens.map(c=>`<option>${esc(c)}</option>`).join("")}</select></label></div><div><label>Category<select id="fk"><option value="">all</option>${cats.map(c=>`<option>${c}</option>`).join("")}</select></label></div><div><label>Status<select id="fs"><option value="">all</option><option>active</option><option>inactive</option><option>under_rehabilitation</option></select></label></div><div><label>Search<input type="text" id="fq"></label></div></div>
   <div id="fm"></div><div id="ft"></div></div>`);v.append(fc);
  function draw(){const c=fc.querySelector("#fc").value,k=fc.querySelector("#fk").value,s=fc.querySelector("#fs").value,q=fc.querySelector("#fq").value.toLowerCase();
    const rows=F.filter(f=>(!c||f.center===c)&&(!k||f.category===k)&&(!s||f.status===s)&&(!q||(f.facility+f.city).toLowerCase().includes(q)));
    const W=620,H=300,X=l=>20+(W-40)*((l+125)/59),Y=l=>H-20-(H-40)*((l-24)/26);
    fc.querySelector("#fm").innerHTML=`<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="facility map (lon/lat, contiguous US)"><rect x="20" y="20" width="${W-40}" height="${H-40}" fill="none" stroke="var(--bd)"/>${rows.filter(f=>f.lon>-125&&f.lon<-66&&f.lat>24&&f.lat<50).map(f=>`<circle cx="${X(f.lon)}" cy="${Y(f.lat)}" r="3.5" fill="var(--ac)" fill-opacity=".55"><title>${esc(f.facility)} — ${esc(f.center)}</title></circle>`).join("")}<text x="20" y="14">lon −125…−66, lat 24…50 (points outside not drawn)</text></svg><p class="mut">${rows.length} facilities shown.</p>`;
    const t=fc.querySelector("#ft");t.innerHTML="";t.append(table(rows,["center","facility","category","status","city","state","occupied_date"],{cls:false}));}
  fc.querySelectorAll("select,input").forEach(i=>i.oninput=draw);draw();}
function apiTab(v,UI){const {el,D}=UI;
  const card=el(`<div class="card"><h2>Data API</h2><p>Read-only static JSON API, versioned at <code>api/v1/</code>, CORS-enabled by GitHub Pages. Full guide with curl, JavaScript and Python examples: <a href="api.html">api.html</a> · OpenAPI spec: <a href="api/v1/openapi.json">api/v1/openapi.json</a>.</p>
   <label>Try an endpoint<select id="ep"></select></label><p><button class="act" id="go">Fetch</button></p><pre id="res" style="max-height:340px;overflow:auto;background:var(--bg);padding:10px;border-radius:8px;font-size:.78rem"></pre><div id="cols"></div></div>`);v.append(card);
  const base="api/v1/";card.querySelector("#res").textContent="Press Fetch.";
  fetch(base+"index.json").then(r=>r.json()).then(ix=>{const sel=card.querySelector("#ep");
    ["index.json",...ix.collections.map(c=>c.url),...ix.collections.slice(0,3).map(c=>c.record_url_template.replace("{id}",(D.celestial.planets.concat([]).length&&c.collection==="planets"?"mars":c.collection==="moons"?"titan":c.collection==="asteroids"?"bennu":"x"))),"analysis/power.json","optimization/pareto/lunar_orbiter.json","quality.json"].forEach(p=>sel.append(new Option("GET "+base+p,p)));
    card.querySelector("#cols").innerHTML=`<h3>Collections</h3><div class="tw"><table><thead><tr><th>collection</th><th>records</th><th>endpoint</th></tr></thead><tbody>${ix.collections.map(c=>`<tr><td>${c.collection}</td><td>${c.count}</td><td><code>${base}${c.url}</code></td></tr>`).join("")}</tbody></table></div>`;}).catch(e=>card.querySelector("#res").textContent="Could not load api/v1/index.json: "+e);
  card.querySelector("#go").onclick=async()=>{const p=card.querySelector("#ep").value;try{const r=await fetch(base+p);const t=await r.text();card.querySelector("#res").textContent=(r.status+" "+r.statusText+"\n"+t.slice(0,3000)+(t.length>3000?"\n… ("+t.length+" bytes total)":""));}catch(e){card.querySelector("#res").textContent=String(e);}};}
window.EXTRA={missionFit,compareVerdict,launchFacilities,apiTab};
})();
