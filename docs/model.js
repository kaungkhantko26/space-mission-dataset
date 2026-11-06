// JS port of tools/opt_model.py (same equations). Used by the browser and by tools/parity_check.js.
const G0=9.80665, C=299792458.0;
const fspl=(d,f)=>20*Math.log10(4*Math.PI*d*f/C);
const dishGain=(D,f,e=0.55)=>10*Math.log10(e*Math.pow(Math.PI*D*f/C,2));
function evaluate(G,sc,sel,comp,comm,arr,bat,prop,veh){
  const ins=sel.map(i=>sc.instruments[i]); const v=[];
  const Pinst=ins.reduce((a,i)=>a+i.power*i.duty,0), minst=ins.reduce((a,i)=>a+i.mass,0);
  const dutyDl=sc.dl_hours_per_day/24;
  const Pcomm=(comm.tx_w/G.tx_dc_eff+G.tx_overhead_w)*dutyDl;
  const base=sc.bus_power+comp.power+sc.heater_w, Pavg=base+Pinst+Pcomm;
  const S0=minst+comp.mass+comm.mass+sc.bus_mass+prop.engine_mass;
  const struct=G.struct_frac*S0, therm=G.thermal_frac*S0;
  const Te=sc.eclipse_s, Td=sc.period_s-Te, rec=1+Te/(Td*G.bat_eta), pm=1+G.power_margin;
  let Preq=Pavg*rec*pm; if(prop.electric) Preq=Math.max(Preq,(base+prop.power_w)*rec*pm);
  const Pbol=Preq/Math.max(1e-9,(1-arr.deg_per_yr*sc.life_yr));
  const fr=1/(sc.sun_au*sc.sun_au);
  const armass=(Pbol/fr)/arr.sp_w_per_kg, area=Pbol/(arr.eff*1361*fr*G.sa_pack);
  const dod=sc.body==="earth"?bat.dod_leo:bat.dod_deep;
  const Eecl=Pavg*Te/3600, cap=Math.max(G.bat_min_wh,Eecl/(dod*G.bat_eta)), bmass=cap/bat.spec_wh_per_kg;
  const dry=(S0+struct+therm+armass+bmass)*(1+G.mga);
  const MR=Math.exp(sc.dv_ms*(1+G.dv_margin)/(prop.isp*G0)), k=MR-1, den=1-prop.tank_frac*k;
  if(den<=0) return {feasible:false,violations:["propellant_tank_infeasible"],wet_kg:Infinity,cost:Infinity,science:0,prop_kg:Infinity,avg_power_w:Pavg,inst_mass:minst,link_margin_db:-99,margin_min:-9};
  const mprop=dry*k/den, tank=prop.tank_frac*mprop, wet=dry+tank+mprop;
  let burn=null;
  if(prop.electric){burn=wet*sc.dv_ms*(1+G.dv_margin)/prop.thrust_n/86400; if(burn>G.max_electric_burn_days) v.push("electric_burn_too_long");}
  const capkg=veh.capacity_kg*(1-G.launch_margin);
  if(wet>capkg) v.push("exceeds_launch_capacity");
  if(comp.tol_krad<sc.dose_krad*G.rad_design_margin) v.push("radiation_tolerance");
  const gt=comm.dish_m==null?comm.gain_dbi:dishGain(comm.dish_m,comm.freq_hz,0.55);
  const eirp=10*Math.log10(comm.tx_w)+gt;
  const baseDb=eirp+sc.gt_db[comm.band]-fspl(sc.dist_m,comm.freq_hz)-G.misc_loss_db+228.6-G.ebn0_req_db;
  const R=Math.min(sc.rate_cap_bps,comm.max_rate_bps,Math.pow(10,(baseDb-G.link_margin_req_db)/10));
  if(R<G.min_rate_bps) v.push("link_rate_too_low");
  const dls=sc.dl_hours_per_day*3600*G.dl_eff, down=R*dls;
  const gen=ins.reduce((a,i)=>a+i.rate_kbps*1000*i.duty,0)*86400;
  const frac=gen<=0?1:Math.min(1,down/gen);
  const science=ins.reduce((a,i)=>a+i.value,0)*frac;
  const margin=gen>0?(baseDb-10*Math.log10(Math.max(1e-9,gen/dls))):99;
  if(science<sc.min_science) v.push("science_below_minimum");
  const hw=ins.reduce((a,i)=>a+i.cost,0)+comp.cost+comm.cost+arr.cost_per_w*Pbol+bat.cost_per_wh*cap+prop.hw_cost+sc.bus_cost+6*(struct+therm)+prop.prop_cost_per_kg*mprop;
  const cost=hw*(1+G.integ_frac)+veh.cost;
  if(cost>sc.budget) v.push("exceeds_budget");
  const mm=(capkg-wet)/capkg, bm=(sc.budget-cost)/sc.budget, sm=(science-sc.min_science)/Math.max(1e-9,sc.min_science);
  return {feasible:v.length===0,violations:v,wet_kg:wet,dry_kg:dry,prop_kg:mprop,cost,science,avg_power_w:Pavg,inst_mass:minst,array_w_bol:Pbol,array_area_m2:area,battery_wh:cap,link_rate_bps:R,link_margin_db:margin,electric_burn_days:burn,margin_min:Math.min(mm,bm,sm),mass_margin:mm,budget_margin:bm};
}
function enumerate(G,sc,cat){
  const n=sc.instruments.length, out=[];
  for(let mask=1;mask<(1<<n);mask++){
    const sel=[];for(let i=0;i<n;i++) if(mask>>i&1) sel.push(i);
    for(const comp of cat.computers) for(const comm of cat.comms) for(const arr of cat.arrays) for(const bat of cat.batteries) for(const prop of cat.propulsion){
      if(prop.electric&&!sc.allow_electric) continue;
      for(const veh of sc.vehicles){
        const r=evaluate(G,sc,sel,comp,comm,arr,bat,prop,veh);
        r.design={instruments:sel.map(i=>sc.instruments[i].id),computer:comp.id,comm:comm.id,array:arr.id,battery:bat.id,propulsion:prop.id,vehicle:veh.id};
        out.push(r);
      }}
  }
  return out;
}
const OBJ={min_mass:["Minimum launch mass","wet_kg",1],min_cost:["Minimum cost","cost",1],min_propellant:["Minimum propellant","prop_kg",1],min_power:["Minimum average power","avg_power_w",1],
  max_science:["Maximum science","science",-1],max_payload:["Maximum instrument mass","inst_mass",-1],max_link_margin:["Maximum link margin","link_margin_db",-1],max_feasibility_margin:["Maximum worst-case margin","margin_min",-1]};
function solve(D,key){const f=D.filter(d=>d.feasible); if(!f.length) return null; const [,fld,sg]=OBJ[key];
  return f.reduce((b,d)=>{const a=[sg*d[fld],d.cost,d.wet_kg,JSON.stringify(d.design)],c=[sg*b[fld],b.cost,b.wet_kg,JSON.stringify(b.design)];
    for(let i=0;i<4;i++){if(a[i]<c[i])return d; if(a[i]>c[i])return b;} return b;});}
function balanced(D,w){ // w: {wet_kg,cost,science} weights; compromise programming, L2 to utopia on min-max normalized axes
  const f=D.filter(d=>d.feasible); if(!f.length) return null; w=w||{wet_kg:1,cost:1,science:1};
  const keys=[["wet_kg",1],["cost",1],["science",-1]]; const lo={},hi={};
  keys.forEach(([k])=>{lo[k]=Math.min(...f.map(d=>d[k]));hi[k]=Math.max(...f.map(d=>d[k]));});
  const score=d=>keys.reduce((s,[k,sg])=>{const span=hi[k]-lo[k]||1;const x=sg===1?(d[k]-lo[k])/span:(hi[k]-d[k])/span;return s+w[k]*x*x;},0);
  let best=null,bs=Infinity; for(const d of f){const s=score(d); if(s<bs-1e-15||(Math.abs(s-bs)<=1e-15&&JSON.stringify(d.design)<JSON.stringify(best.design))){bs=s;best=d;}} return best;}
function pareto(D){const f=D.filter(d=>d.feasible).map(d=>[d.wet_kg,d.cost,-d.science,d]);
  return f.filter(a=>!f.some(b=>b!==a&&b[0]<=a[0]&&b[1]<=a[1]&&b[2]<=a[2]&&(b[0]<a[0]||b[1]<a[1]||b[2]<a[2]))).map(a=>a[3]);}
if(typeof module!=="undefined") module.exports={evaluate,enumerate,solve,balanced,pareto,OBJ};
if(typeof window!=="undefined") window.SMODEL={OBJ,enumerate,solve,balanced,pareto};
