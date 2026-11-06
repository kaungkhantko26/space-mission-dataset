// Verifies docs/model.js reproduces the Python optimizer results stored in the dataset.
const M=require("../docs/model.js"), D=require("../space-mission-research/combined/all_space_mission_data.json");
const cons=D.optimization.constraints; let bad=0,n=0;
for(const sc of cons.scenarios){
  const des=M.enumerate(cons.global_parameters,sc,cons.catalog);
  for(const k of Object.keys(M.OBJ)){
    const e=D.optimization.experiments.find(x=>x.id===`opt_${sc.id}_${k}`), b=M.solve(des,k); n++;
    const same=JSON.stringify(b.design)===JSON.stringify(e.selected_components)&&Math.abs(b[M.OBJ[k][1]]-e.objective_value)<1e-6*Math.max(1,Math.abs(e.objective_value));
    if(!same){bad++;console.log("MISMATCH",sc.id,k);}
  }
  const bb=M.balanced(des), eb=D.optimization.experiments.find(x=>x.id===`opt_${sc.id}_balanced`); n++;
  if(JSON.stringify(bb.design)!==JSON.stringify(eb.selected_components)){bad++;console.log("MISMATCH balanced",sc.id);}
  const pf=M.pareto(des), pp=D.optimization.pareto.find(x=>x.scenario_id===sc.id);
  console.log(sc.id,"designs",des.length,"js pareto raw",pf.length,"py pareto (dedup)",pp.front_size);
}
console.log(bad===0?`PARITY OK (${n} comparisons)`:`PARITY FAILED (${bad}/${n})`); process.exit(bad?1:0);
