// Cross-check: JS Monte Carlo (docs/app.js logic, re-declared here from the same formulas) vs Python-stored uncertainty results.
const M=require("../docs/model.js"),D=require("../space-mission-research/combined/all_space_mission_data.json");
const fs=require("fs");const src=fs.readFileSync(__dirname+"/../docs/app.js","utf8");
const grab=(name)=>{const i=src.indexOf(name);return src.slice(i,src.indexOf("\n",i));};
eval((grab("const rng32=")+";"+grab("const triD=")+";"+grab("const gaussD=")).replace(/const /g,"var "));
var evaluate=M.evaluate;
const cons=D.optimization.constraints,cat={arrays:cons.catalog.arrays,batteries:cons.catalog.batteries,computers:cons.catalog.computers,comms:cons.catalog.comms,propulsion:cons.catalog.propulsion};
function sim(G,sc,d,N,seed){const r=rng32(seed);const f=(a,id)=>a.find(x=>x.id===id);const sel=d.instruments.map(id=>sc.instruments.findIndex(i=>i.id===id));
 const comp=f(cat.computers,d.computer),comm=f(cat.comms,d.comm),arr=f(cat.arrays,d.array),bat=f(cat.batteries,d.battery),prop=f(cat.propulsion,d.propulsion),veh=f(sc.vehicles,d.vehicle);let ok=0;
 for(let k=0;k<N;k++){const g=Object.assign({},G,{mga:.10+.25*r(),dv_margin:.10*r(),power_margin:.05+.20*r()});const sh=gaussD(r)*1.5,gt={};for(const b in sc.gt_db)gt[b]=sc.gt_db[b]+sh;
  const s=Object.assign({},sc,{gt_db:gt,dv_ms:sc.dv_ms*triD(r,.95,1.10,1.0)});const e=evaluate(g,s,sel,comp,comm,arr,bat,prop,veh),c=e.cost*triD(r,.9,1.4,1.0);
  const fails=e.violations.filter(v=>v!=="exceeds_budget");if(c>sc.budget)fails.push("x");if(!fails.length)ok++;}return ok/N;}
let bad=0;
for(const m of D.optimization.uncertainty){const sc=cons.scenarios.find(s=>s.id===m.scenario_id),p=sim(cons.global_parameters,sc,m.design,40000,12345);
 const se=Math.sqrt(m.p_feasible*(1-m.p_feasible)/m.samples+p*(1-p)/40000),z=Math.abs(p-m.p_feasible)/Math.max(se,1e-9);
 const flag=z>4?"MISMATCH":"ok";if(z>4)bad++;console.log(m.scenario_id.padEnd(14),m.design_label.padEnd(24),"py",m.p_feasible.toFixed(3),"js",p.toFixed(3),"z",z.toFixed(1),flag);}
console.log(bad?"SIM CHECK FAILED":"SIM CHECK OK");process.exit(bad?1:0);
