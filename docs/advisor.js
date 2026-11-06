// Mission-fit advisor. Pure functions (browser + node). All rules are transparent heuristics layered on UNVERIFIED data;
// relevance weights are fictional educational values. See docs: "Mission fit" tab.
const G0a=9.80665;
const MISSIONS={
 leo:{name:"Earth-observation satellite (LEO)",dv:150,dv_basis:"estimated drag make-up + deorbit",isp_ref:310,orbit:"LEO",scenario:"leo_eo",multi_burn:true,electric_ok:true},
 gto:{name:"Geostationary comsat (via GTO)",dv:1457,dv_basis:"derived: GTO→GEO circularisation ≈ LEO-GEO Hohmann second burn (no plane change)",isp_ref:310,orbit:"GTO",scenario:null,multi_burn:true,electric_ok:true},
 moon:{name:"Moon orbiter (100 km polar)",dv:4005,dv_after_tli:921,dv_basis:"derived: TLI 3084 + LOI 821 + 100 ops (from 400 km LEO)",isp_ref:310,orbit:"Moon",scenario:"lunar_orbiter",multi_burn:true,electric_ok:false},
 mars:{name:"Mars orbiter (400 km × 1 sol)",dv:1064,dv_basis:"derived: MOI 914 + 150 ops; launcher supplies departure",isp_ref:310,orbit:"Mars",scenario:"mars_orbiter",multi_burn:true,electric_ok:false}};
// educational relevance 0-3 by instrument type and mission (FICTIONAL weights; orbiter missions)
const REL={
 leo:{multispectral_camera:3,thermal_imager:3,optical_camera:2,imaging_spectrometer:2,multispectral_imager_spectrometer:2,particle_detector:1,radio_science:1,uv_spectrometer:1,lidar_altimeter:1,sounding_radar:1,dust_detector:0,mass_spectrometer_gas_chromatograph:0},
 gto:{particle_detector:3,radio_science:1,optical_camera:1,uv_spectrometer:1,dust_detector:1,multispectral_camera:0,thermal_imager:0,imaging_spectrometer:0,multispectral_imager_spectrometer:0,lidar_altimeter:0,sounding_radar:0,mass_spectrometer_gas_chromatograph:0},
 moon:{optical_camera:3,lidar_altimeter:3,imaging_spectrometer:2,multispectral_imager_spectrometer:2,sounding_radar:2,uv_spectrometer:2,particle_detector:1,multispectral_camera:1,thermal_imager:1,radio_science:1,dust_detector:1,mass_spectrometer_gas_chromatograph:0},
 mars:{optical_camera:3,imaging_spectrometer:3,multispectral_imager_spectrometer:3,sounding_radar:3,lidar_altimeter:2,uv_spectrometer:2,particle_detector:1,multispectral_camera:1,thermal_imager:1,radio_science:1,dust_detector:1,mass_spectrometer_gas_chromatograph:0}};
const payloadFor=(v,mission)=>{const P=v.payloads||[];const pick=(f)=>P.filter(f);
  const exp=(a)=>a.find(p=>/^expended/.test(p.mode))||a[0];
  if(mission==="leo"){const a=pick(p=>p.orbit==="LEO"||p.orbit==="SSO");return a.length?exp(a):null;}
  if(mission==="gto"){const a=pick(p=>p.orbit==="GTO");return a.length?exp(a):null;}
  if(mission==="moon"){const t=pick(p=>p.orbit==="TLI");if(t.length)return Object.assign({},t[0],{direct:true});const a=pick(p=>p.orbit==="LEO");return a.length?exp(a):null;}
  if(mission==="mars"){const a=pick(p=>/^Mars/.test(p.orbit));return a.length?exp(a):null;}return null;};
function vehicleFit(v,mission,dry,opt={}){const M=MISSIONS[mission],margin=opt.launchMargin??0.10,isp=opt.isp??M.isp_ref,p=payloadFor(v,mission);
  const r={id:v.id,name:v.name,status:v.status,price_usd:v.price_usd,verdict:"Not rated",score:null,reasons:[],capacity_kg:null,required_kg:null,margin_ratio:null,basis:null};
  if(!p){r.reasons.push(`No recorded ${M.orbit==="Moon"?"TLI/LEO":M.orbit==="Mars"?"Mars-transfer":M.orbit} capacity in the dataset — cannot rate (not guessed).`);return r;}
  let dv=M.dv,basis=`${p.orbit} capacity ${p.payload_kg.toLocaleString()} kg (${p.mode})`;
  if(mission==="moon"&&p.direct){dv=M.dv_after_tli;basis=`TLI capacity ${p.payload_kg.toLocaleString()} kg; spacecraft only needs LOI+ops ${dv} m/s`;}
  else if(mission==="moon") basis+="; spacecraft performs TLI itself";
  if(mission==="mars") basis+="; spacecraft only needs capture+ops";
  const req=dry*Math.exp(dv/(isp*G0a)),cap=p.payload_kg*(1-margin);r.capacity_kg=p.payload_kg;r.required_kg=req;r.margin_ratio=cap/req;r.basis=basis;
  r.reasons.push(`Needs ≈${Math.round(req).toLocaleString()} kg injected for ${dry} kg dry (${dv} m/s at Isp ${isp} s); usable capacity ${Math.round(cap).toLocaleString()} kg.`);
  if(!p.altitude_km&&!p.inclination_deg&&mission==="leo") r.reasons.push("Capacity quoted without full orbit conditions — comparison approximate.");
  if(r.margin_ratio<1){r.verdict="Not suitable";r.reasons.push("Capacity too small.");}
  else if(r.margin_ratio>20){r.verdict="Overkill";r.reasons.push("Capacity is "+r.margin_ratio.toFixed(0)+"× the requirement — wasteful for a dedicated launch; consider rideshare or a smaller vehicle.");}
  else if(r.margin_ratio<1.5){r.verdict="Marginal";r.reasons.push("Less than 50% spare capacity.");}
  else r.verdict="Suitable";
  if(/retired/.test(v.status)) {r.reasons.push("Vehicle is retired.");if(r.verdict==="Suitable")r.verdict="Historical";}
  if(/develop/.test(v.status)) {r.reasons.push("Developmental — capacity is a target, not demonstrated.");if(r.verdict==="Suitable")r.verdict="Unproven";}
  // rank by smallest sufficient capacity; price is shown when recorded but is missing for most vehicles, so it is not used to rank
  const ok=["Suitable","Marginal","Overkill","Unproven","Historical"].includes(r.verdict);r.score=ok?p.payload_kg:null;
  if(v.price_usd) r.reasons.push("Recorded price ≈ $"+(v.price_usd/1e6).toFixed(1)+"M ("+(v.price_year||"year n/a")+") ⇒ ≈ $"+Math.round(v.price_usd/p.payload_kg).toLocaleString()+"/kg of capacity.");
  return r;}
function engineFit(e,mission,dry,opt={}){const M=MISSIONS[mission],electric=e.type==="ion"||e.type==="hall_effect",F=e.thrust_vac_n,isp=e.isp_vac_s;
  const r={id:e.id,name:e.name,type:e.type,verdict:"Not rated",score:null,reasons:[],prop_kg:null,accel_g:null,burn:null};
  if(!F||!isp){r.reasons.push("Missing vacuum thrust or Isp — cannot rate (not guessed).");return r;}
  const MR=Math.exp(M.dv/(isp*G0a)),wet=dry*MR,prop=wet-dry,acc=F/(wet*G0a);r.prop_kg=prop;r.accel_g=acc;
  r.reasons.push(`Δv ${M.dv} m/s with Isp ${isp} s ⇒ ${prop.toFixed(0)} kg propellant for ${dry} kg dry (mass ratio ${MR.toFixed(2)}).`);
  if(electric){
    if(!M.electric_ok){r.verdict="Not modeled";r.reasons.push("Low-thrust spiral/capture trajectories are not modeled for this mission.");return r;}
    const days=wet*M.dv/F/86400;r.burn=`${days.toFixed(1)} days`;r.reasons.push(`Low-thrust burn ≈${days.toFixed(1)} days at ${F*1000} mN; needs ${e.power_w} W.`);
    if(days>120){r.verdict="Not suitable";r.reasons.push("Burn exceeds 120-day limit used by the optimizer.");}else{r.verdict=days>60?"Marginal":"Suitable";r.score=prop;}return r;}
  r.burn=`${(prop/(F/(isp*G0a))).toFixed(0)} s`;
  if(e.restart===false&&M.multi_burn){r.verdict="Not suitable";r.reasons.push("No restart capability; mission needs multiple burns.");return r;}
  if(F>5e5){r.verdict="Not suitable";r.reasons.push(`Launch-stage-class engine (${(F/1000).toFixed(0)} kN): ${acc.toFixed(1)} g on this spacecraft.`);return r;}
  if(acc>5){r.verdict="Overpowered";r.reasons.push(`Acceleration ${acc.toFixed(1)} g > 5 g structural/pointing limit (assumption).`);return r;}
  if(acc<0.02){r.verdict="Marginal";r.reasons.push(`Acceleration only ${acc.toFixed(3)} g — long burns incur gravity losses on departure/capture burns.`);r.score=prop;return r;}
  r.verdict="Suitable";r.score=prop;return r;}
function instrumentFit(i,mission){const rel=(REL[mission]||{})[i.instrument_type];const r={id:i.id,name:i.name,type:i.instrument_type,relevance:rel==null?null:rel,mass_kg:i.mass_kg,power_w:i.power_w,resource:null,verdict:"Not rated",score:null,reasons:[]};
  if(rel==null){r.reasons.push("Instrument type has no relevance weight for this mission.");return r;}
  r.resource=(i.mass_kg!=null&&i.power_w!=null)?i.mass_kg+i.power_w/10:null;
  r.reasons.push(`Relevance ${rel}/3 for ${MISSIONS[mission].name} (fictional educational weight).`);
  if(rel===0){r.verdict="Not useful";r.reasons.push("Not useful from orbit for this mission (e.g. surface-only instrument).");return r;}
  if(r.resource==null){r.verdict=rel>=2?"Relevant (cost unknown)":"Marginal";r.reasons.push("Mass or power not recorded — resource cost cannot be computed.");r.score=-rel*1e3+1e6;return r;}
  r.reasons.push(`Resource cost ≈ ${r.resource.toFixed(1)} (kg + W/10; assumption 10 W ≈ 1 kg). Value per resource = ${(rel/r.resource).toFixed(3)}.`);
  r.verdict=rel>=2?"Good fit":"Marginal";r.score=-rel*1e3+r.resource;return r;}
const VORDER={"Suitable":0,"Good fit":0,"Relevant (cost unknown)":1,"Marginal":1,"Unproven":2,"Historical":2,"Overkill":3,"Overpowered":4,"Not modeled":5,"Not rated":6,"Not useful":7,"Not suitable":8};
function rankFits(list){return list.slice().sort((a,b)=>(VORDER[a.verdict]??9)-(VORDER[b.verdict]??9)||((a.score??1e18)-(b.score??1e18)));}
function adviseAll(data,mission,dry){
  const veh=rankFits(data.launch.launch_vehicles.map(v=>vehicleFit(v,mission,dry)));
  const eng=rankFits(data.propulsion.rocket_engines.concat(data.propulsion.electric_propulsion).map(e=>engineFit(e,mission,dry)));
  const ins=rankFits(data.instruments.map(i=>instrumentFit(i,mission)));
  return {veh,eng,ins};}
if(typeof module!=="undefined") module.exports={MISSIONS,REL,vehicleFit,engineFit,instrumentFit,rankFits,adviseAll,payloadFor};
if(typeof window!=="undefined") window.ADV={MISSIONS,REL,vehicleFit,engineFit,instrumentFit,rankFits,adviseAll,payloadFor};
