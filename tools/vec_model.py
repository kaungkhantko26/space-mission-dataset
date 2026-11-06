"""Vectorized (numpy) exact evaluator: same equations as opt_model.evaluate, vectorized across all instrument subsets.
Enables exhaustive search at much larger instrument counts. Equivalence to the scalar model is tested in benchmark.py."""
import math, itertools
import numpy as np
from astro import G0, C

def _bits(n):
    m=np.arange(1,1<<n,dtype=np.int64)
    return m, ((m[:,None]>>np.arange(n))&1).astype(float)
def evaluate_masks(G, sc, comp, comm, arr, bat, prop, veh, B, instr_arrays):
    """B: (M,n) 0/1 selection matrix. instr_arrays: dict of per-instrument arrays."""
    ia=instr_arrays
    m_inst=B@ia["mass"]; P_inst=B@(ia["power"]*ia["duty"]); gen=(B@(ia["rate"]*1000*ia["duty"]))*86400; val=B@ia["value"]; icost=B@ia["cost"]
    duty_dl=sc["dl_hours_per_day"]/24.0
    P_comm=(comm["tx_w"]/G["tx_dc_eff"]+G["tx_overhead_w"])*duty_dl
    base=sc["bus_power"]+comp["power"]+sc["heater_w"]
    P_avg=base+P_inst+P_comm
    S0=m_inst+comp["mass"]+comm["mass"]+sc["bus_mass"]+prop["engine_mass"]
    struct=G["struct_frac"]*S0; therm=G["thermal_frac"]*S0
    Te=sc["eclipse_s"]; Td=sc["period_s"]-Te; rec=1+Te/(Td*G["bat_eta"]); pm=1+G["power_margin"]
    P_req=P_avg*rec*pm
    if prop["electric"]: P_req=np.maximum(P_req,(base+prop["power_w"])*rec*pm)
    P_bol=P_req/max(1e-9,(1-arr["deg_per_yr"]*sc["life_yr"]))
    fr=1.0/sc["sun_au"]**2
    arr_mass=(P_bol/fr)/arr["sp_w_per_kg"]
    dod=bat["dod_leo"] if sc["body"]=="earth" else bat["dod_deep"]
    cap=np.maximum(G["bat_min_wh"],P_avg*Te/3600.0/(dod*G["bat_eta"])); bat_mass=cap/bat["spec_wh_per_kg"]
    dry=(S0+struct+therm+arr_mass+bat_mass)*(1+G["mga"])
    MR=math.exp(sc["dv_ms"]*(1+G["dv_margin"])/(prop["isp"]*G0)); k=MR-1; den=1-prop["tank_frac"]*k
    if den<=0:
        z=np.full(len(m_inst),np.inf); return dict(feasible=np.zeros(len(m_inst),bool),wet_kg=z,cost=z,science=np.zeros(len(m_inst)),prop_kg=z,avg_power_w=P_avg,inst_mass=m_inst,link_margin_db=np.full(len(m_inst),-99.0),margin_min=np.full(len(m_inst),-9.0))
    m_prop=dry*k/den; tank=prop["tank_frac"]*m_prop; wet=dry+tank+m_prop
    ok=np.ones(len(m_inst),bool)
    if prop["electric"]:
        ok&=(wet*sc["dv_ms"]*(1+G["dv_margin"])/prop["thrust_n"]/86400.0)<=G["max_electric_burn_days"]
    capkg=veh["capacity_kg"]*(1-G["launch_margin"]); ok&=wet<=capkg
    if comp["tol_krad"]<sc["dose_krad"]*G["rad_design_margin"]: ok&=False
    gt=comm["gain_dbi"] if comm["dish_m"] is None else 10*math.log10(0.55*(math.pi*comm["dish_m"]*comm["freq_hz"]/C)**2)
    eirp=10*math.log10(comm["tx_w"])+gt
    fspl=20*math.log10(4*math.pi*sc["dist_m"]*comm["freq_hz"]/C)
    base_db=eirp+sc["gt_db"][comm["band"]]-fspl-G["misc_loss_db"]+228.6-G["ebn0_req_db"]
    R=min(sc["rate_cap_bps"],comm["max_rate_bps"],10**((base_db-G["link_margin_req_db"])/10))
    if R<G["min_rate_bps"]: ok&=False
    dl_s=sc["dl_hours_per_day"]*3600*G["dl_eff"]; down=R*dl_s
    frac=np.where(gen<=0,1.0,np.minimum(1.0,down/np.maximum(gen,1e-300)))
    science=val*frac
    margin_db=np.where(gen>0,base_db-10*np.log10(np.maximum(1e-9,gen/dl_s)),99.0)
    ok&=science>=sc["min_science"]
    hw=icost+comp["cost"]+comm["cost"]+arr["cost_per_w"]*P_bol+bat["cost_per_wh"]*cap+prop["hw_cost"]+sc["bus_cost"]+6.0*(struct+therm)+prop["prop_cost_per_kg"]*m_prop
    cost=hw*(1+G["integ_frac"])+veh["cost"]; ok&=cost<=sc["budget"]
    mm=(capkg-wet)/capkg; bm=(sc["budget"]-cost)/sc["budget"]; sm=(science-sc["min_science"])/max(1e-9,sc["min_science"])
    return dict(feasible=ok,wet_kg=wet,cost=cost,science=science,prop_kg=m_prop,avg_power_w=P_avg,inst_mass=m_inst,link_margin_db=margin_db,margin_min=np.minimum(np.minimum(mm,bm),sm))
def instr_arrays(sc):
    I=sc["instruments"]; f=lambda k: np.array([i[k] for i in I],float)
    return dict(mass=f("mass"),power=f("power"),duty=f("duty"),rate=f("rate_kbps"),value=f("value"),cost=f("cost"))
def combos(sc,cat):
    for comp,comm,arr,bat,prop,veh in itertools.product(cat["computers"],cat["comms"],cat["arrays"],cat["batteries"],cat["props"],sc["vehicles"]):
        if prop["electric"] and not sc["allow_electric"]: continue
        yield comp,comm,arr,bat,prop,veh
def solve_vec(G,sc,cat,objective,weights=None):
    """Exact optimum for a single objective over ALL designs. Returns (value, design dict) with the same tie-breaking as opt_model.solve (cost, wet mass, design string)."""
    n=len(sc["instruments"]); masks,B=_bits(n); ia=instr_arrays(sc)
    field,sgn={"min_mass":("wet_kg",1),"min_cost":("cost",1),"min_propellant":("prop_kg",1),"min_power":("avg_power_w",1),"max_science":("science",-1),"max_payload":("inst_mass",-1),"max_link_margin":("link_margin_db",-1),"max_feasibility_margin":("margin_min",-1)}[objective]
    best=None
    for c in combos(sc,cat):
        r=evaluate_masks(G,sc,*c,B,ia); idx=np.nonzero(r["feasible"])[0]
        if len(idx)==0: continue
        v=sgn*r[field][idx]; vmin=v.min(); cand=idx[np.isclose(v,vmin,rtol=0,atol=1e-12)] if False else idx[v==vmin]
        for j in cand:
            key=(vmin,r["cost"][j],r["wet_kg"][j],str(dict(instruments=[sc["instruments"][i]["id"] for i in range(n) if masks[j]>>i&1],computer=c[0]["id"],comm=c[1]["id"],array=c[2]["id"],battery=c[3]["id"],propulsion=c[4]["id"],vehicle=c[5]["id"])))
            if best is None or key<best[0]: best=(key,dict(instruments=[sc["instruments"][i]["id"] for i in range(n) if masks[j]>>i&1],computer=c[0]["id"],comm=c[1]["id"],array=c[2]["id"],battery=c[3]["id"],propulsion=c[4]["id"],vehicle=c[5]["id"]),float(r[field][j]))
    return None if best is None else (best[2],best[1])
