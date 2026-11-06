"""Spacecraft design optimization model. Exhaustive enumeration over a finite component catalog (global optimum WITHIN the catalog).
Costs are synthetic 'credits' (fictional) except launch prices where a published USD figure exists (1 credit = 10,000 USD notional).
Catalog performance numbers marked estimated are engineering estimates anchored on technology-class ranges, not product specs."""
import math, itertools, random
from astro import *

GLOBAL = dict(mga=0.20, dv_margin=0.05, power_margin=0.15, launch_margin=0.10, struct_frac=0.25, thermal_frac=0.04,
              bat_eta=0.90, ebn0_req_db=2.0, link_margin_req_db=3.0, misc_loss_db=2.0, tx_dc_eff=0.35, tx_overhead_w=5.0,
              integ_frac=0.30, sa_pack=0.85, dl_eff=0.80, rad_design_margin=2.0, max_electric_burn_days=120.0, min_rate_bps=1000.0, bat_min_wh=10.0)

ARRAYS = [dict(id="sa_3j_gaas",name="Triple-junction GaAs array",eff=0.29,sp_w_per_kg=80,deg_per_yr=0.02,cost_per_w=25,data_class="estimated"),
          dict(id="sa_si",name="Silicon array",eff=0.15,sp_w_per_kg=40,deg_per_yr=0.03,cost_per_w=10,data_class="estimated")]
BATTERIES = [dict(id="bat_li_ion",name="Li-ion",spec_wh_per_kg=160,dod_leo=0.30,dod_deep=0.60,cost_per_wh=2.0,data_class="estimated"),
             dict(id="bat_nih2",name="NiH2",spec_wh_per_kg=45,dod_leo=0.35,dod_deep=0.60,cost_per_wh=5.0,data_class="estimated")]
COMPUTERS = [dict(id="cpu_cots",name="COTS SoC",mass=0.2,power=3,cost=50,tol_krad=20,data_class="estimated"),
             dict(id="cpu_leon3",name="LEON3-FT class",mass=0.5,power=4,cost=400,tol_krad=100,data_class="estimated"),
             dict(id="cpu_rad750",name="RAD750 class",mass=1.5,power=10,cost=2500,tol_krad=200,data_class="estimated")]
COMMS = [dict(id="patch_s_5w",name="S-band patch 5 W",band="S",freq_hz=2.2e9,dish_m=None,gain_dbi=7.0,tx_w=5,mass=1.2,cost=150,max_rate_bps=2e6,data_class="estimated"),
         dict(id="hga1_x_20w",name="1 m HGA X-band 20 W",band="X",freq_hz=8.4e9,dish_m=1.0,gain_dbi=None,tx_w=20,mass=7.0,cost=900,max_rate_bps=1e8,data_class="estimated"),
         dict(id="hga1_x_50w",name="1 m HGA X-band 50 W",band="X",freq_hz=8.4e9,dish_m=1.0,gain_dbi=None,tx_w=50,mass=8.5,cost=1400,max_rate_bps=1e8,data_class="estimated"),
         dict(id="hga3_x_20w",name="3 m HGA X-band 20 W",band="X",freq_hz=8.4e9,dish_m=3.0,gain_dbi=None,tx_w=20,mass=18.0,cost=3000,max_rate_bps=1e8,data_class="estimated"),
         dict(id="hga3_x_100w",name="3 m HGA X-band 100 W",band="X",freq_hz=8.4e9,dish_m=3.0,gain_dbi=None,tx_w=100,mass=22.0,cost=4500,max_rate_bps=1e8,data_class="estimated")]
PROPS = [dict(id="mono_n2h4",name="Hydrazine monoprop",isp=220,engine_mass=2.0,tank_frac=0.08,hw_cost=400,prop_cost_per_kg=1.0,power_w=0,thrust_n=None,electric=False,data_class="estimated"),
         dict(id="bi_mmh_nto",name="MMH/NTO biprop",isp=310,engine_mass=6.0,tank_frac=0.10,hw_cost=1800,prop_cost_per_kg=1.0,power_w=0,thrust_n=None,electric=False,data_class="estimated"),
         dict(id="hall_xe",name="Low-power Hall (Xe)",isp=1200,engine_mass=4.0,tank_frac=0.12,hw_cost=3500,prop_cost_per_kg=5.0,power_w=200,thrust_n=0.012,electric=True,data_class="estimated")]

def _I(id,name,analog,m,p,duty,rate_kbps,value,cost,real=False): return dict(id=id,name=name,analog=analog,mass=m,power=p,duty=duty,rate_kbps=rate_kbps,value=value,cost=cost,mass_power_basis="reference flight value (unverified)" if real else "estimated")

def build_scenarios(ref):
    """ref: dict with mu_earth,r_earth,mu_moon,r_moon,mu_mars,r_mars (km units)"""
    muE,RE,muM,RM,muA,RA = ref["mu_earth"],ref["r_earth"],ref["mu_moon"],ref["r_moon"],ref["mu_mars"],ref["r_mars"]
    # LEO EO
    h=500; r=RE+h; per=period(muE,r); ecl=eclipse_fraction(muE,RE,h)*per
    # Lunar from 400 km LEO: TLI + LOI to 100 km circular
    rl=RE+400; dist_moon=384400.0; at=(rl+dist_moon)/2
    tli=math.sqrt(muE*(2/rl-1/at))-math.sqrt(muE/rl)
    v_apo=math.sqrt(muE*(2/dist_moon-1/at)); v_moon=math.sqrt(muE/dist_moon); vinf=abs(v_moon-v_apo)
    rlo=RM+100; loi=math.sqrt(vinf**2+2*muM/rlo)-math.sqrt(muM/rlo)
    per_l=period(muM,rlo); ecl_l=eclipse_fraction(muM,RM,100)*per_l
    # Mars: capture into 400 km x 1-sol orbit (launcher provides departure; onboard provides MOI)
    r1,r2=AU_KM,1.52371034*AU_KM
    vinf_m=math.sqrt(MU_SUN/r2)*(1-math.sqrt(2*r1/(r1+r2)))
    sol=88642.66; a_sol=(muA*(sol/(2*math.pi))**2)**(1/3); rp=RA+400
    vp=math.sqrt(muA*(2/rp-1/a_sol)); moi=math.sqrt(vinf_m**2+2*muA/rp)-vp
    ecl_m=2*RA/vp
    return [
     dict(id="leo_eo",name="Earth-observation satellite (500 km LEO)",body="earth",sun_au=1.0,period_s=per,eclipse_s=ecl,dv_ms=150.0,dv_basis="estimated: drag make-up + deorbit allowance (assumption)",
          life_yr=2.0,dl_hours_per_day=0.8,dist_m=1.5e6,gt_db={"S":30.0,"X":30.0},gt_basis="estimated ground G/T",rate_cap_bps=1e8,bus_mass=12.0,bus_power=12.0,heater_w=5.0,bus_cost=800,
          budget=12000,min_science=12,dose_krad=8,dose_basis="estimated",allow_electric=True,
          vehicles=[dict(id="electron",name="Electron",capacity_kg=300,orbit="SSO 500 km",cost=750,cost_basis="published ~7.5M USD (2021) /10k",ref="launch_vehicles:electron"),
                    dict(id="f9_class",name="Falcon 9 class (expended)",capacity_kg=22800,orbit="LEO (SSO figure not recorded)",cost=6700,cost_basis="fictional credit",ref="launch_vehicles:falcon9_b5")],
          instruments=[_I("ms_imager","Multispectral imager","OLI/MSI",18,30,0.25,20000,10,2500),_I("thermal_imager","Thermal imager","TIRS",12,20,0.25,3000,6,1800),
                       _I("gnss_ro","GNSS radio occultation","-",1.5,3,1.0,5,3,400),_I("small_cam","Small optical camera","-",6,12,0.2,8000,5,900),
                       _I("magnetometer","Magnetometer","-",1.2,1.5,1.0,2,2,300),_I("rad_detector","Radiation detector","-",0.8,1.0,1.0,1,2,250)]),
     dict(id="lunar_orbiter",name="Lunar polar orbiter (100 km)",body="moon",sun_au=1.0,period_s=per_l,eclipse_s=ecl_l,dv_ms=(tli+loi)*1000+100.0,
          dv_basis=f"derived: TLI {tli*1000:.0f} m/s + LOI {loi*1000:.0f} m/s (patched conic, 400 km LEO to 100 km circular) + 100 m/s ops",
          life_yr=1.0,dl_hours_per_day=8.0,dist_m=3.844e8,gt_db={"S":45.0,"X":53.0},gt_basis="estimated DSN 34 m G/T",rate_cap_bps=1e7,bus_mass=30.0,bus_power=35.0,heater_w=15.0,bus_cost=3000,
          budget=30000,min_science=15,dose_krad=15,dose_basis="estimated",allow_electric=False,
          vehicles=[dict(id="f9_class",name="Falcon 9 class (expended)",capacity_kg=22800,orbit="LEO",cost=6700,cost_basis="fictional credit",ref="launch_vehicles:falcon9_b5"),
                    dict(id="falcon_heavy",name="Falcon Heavy (expended)",capacity_kg=63800,orbit="LEO",cost=9700,cost_basis="published ~97M USD (2022) /10k",ref="launch_vehicles:falcon_heavy")],
          instruments=[_I("nac_cam","Narrow-angle camera","LROC NAC",10,20,0.2,6000,8,3000),_I("laser_alt","Laser altimeter","MOLA",25.9,34.2,1.0,0.62,7,3500,True),
                       _I("neutron_spec","Neutron/gamma spectrometer","-",12,15,1.0,1.5,6,2000),_I("uv_spec","UV spectrometer","Alice",4.4,4.4,0.5,5,5,1500,True),
                       _I("magnetometer","Magnetometer","-",1.2,1.5,1.0,2,2,300),_I("rad_detector","Radiation detector","-",0.8,1.0,1.0,1,2,250)]),
     dict(id="mars_orbiter",name="Mars science orbiter (400 km x 1 sol)",body="mars",sun_au=1.52371034,period_s=sol,eclipse_s=ecl_m,dv_ms=moi*1000+150.0,
          dv_basis=f"derived: MOI {moi*1000:.0f} m/s from Hohmann v_inf {vinf_m:.2f} km/s into 400 km x 1-sol orbit + 150 m/s ops; launcher supplies departure",
          life_yr=2.0,dl_hours_per_day=8.0,dist_m=2.67*AU_KM*1000,gt_db={"S":45.0,"X":53.0},gt_basis="estimated DSN 34 m G/T",rate_cap_bps=1e7,bus_mass=60.0,bus_power=70.0,heater_w=30.0,bus_cost=9000,
          budget=90000,min_science=20,dose_krad=20,dose_basis="estimated",allow_electric=False,
          vehicles=[dict(id="falcon_heavy",name="Falcon Heavy (expended, Mars transfer)",capacity_kg=16800,orbit="Mars transfer",cost=9700,cost_basis="published ~97M USD (2022) /10k",ref="launch_vehicles:falcon_heavy")],
          instruments=[_I("hirise_like","High-res imager","HiRISE",65,60,0.0015,100000,10,9000,True),_I("crism_like","Imaging spectrometer","CRISM",32.9,50,0.02,5000,8,6000),
                       _I("sharad_like","Sounding radar","SHARAD",17,40,0.1,1000,7,5000),_I("mola_like","Laser altimeter","MOLA",25.9,34.2,1.0,0.62,6,4000,True),
                       _I("uv_spec","UV spectrometer","Alice",4.4,4.4,0.3,3,4,1500,True),_I("particles","Particle/plasma package","SWAP+PEPSSI",4.8,4.8,1.0,2,3,1200,True)]),
    ]

def evaluate(G, sc, sel, comp, comm, arr, bat, prop, veh):
    """Return metrics dict; 'feasible' flag + 'violations'."""
    ins=[sc["instruments"][i] for i in sel]
    v=[]
    P_inst=sum(i["power"]*i["duty"] for i in ins); m_inst=sum(i["mass"] for i in ins)
    duty_dl=sc["dl_hours_per_day"]/24.0
    P_comm=(comm["tx_w"]/G["tx_dc_eff"]+G["tx_overhead_w"])*duty_dl
    base=sc["bus_power"]+comp["power"]+sc["heater_w"]
    P_avg=base+P_inst+P_comm
    S0=m_inst+comp["mass"]+comm["mass"]+sc["bus_mass"]+prop["engine_mass"]
    struct=G["struct_frac"]*S0; therm=G["thermal_frac"]*S0
    Te=sc["eclipse_s"]; Td=sc["period_s"]-Te
    rec=1+Te/(Td*G["bat_eta"]); pm=1+G["power_margin"]
    P_req=P_avg*rec*pm
    if prop["electric"]: P_req=max(P_req,(base+prop["power_w"])*rec*pm)
    P_bol=P_req/max(1e-9,(1-arr["deg_per_yr"]*sc["life_yr"]))
    flux_ratio=1.0/sc["sun_au"]**2
    arr_mass=(P_bol/flux_ratio)/arr["sp_w_per_kg"]; area=P_bol/(arr["eff"]*1361.0*flux_ratio*G["sa_pack"])
    dod=bat["dod_leo"] if sc["body"]=="earth" else bat["dod_deep"]
    E_ecl=P_avg*Te/3600.0
    cap=max(G["bat_min_wh"],E_ecl/(dod*G["bat_eta"])); bat_mass=cap/bat["spec_wh_per_kg"]
    dry=(S0+struct+therm+arr_mass+bat_mass)*(1+G["mga"])
    MR=math.exp(sc["dv_ms"]*(1+G["dv_margin"])/(prop["isp"]*G0)); k=MR-1; den=1-prop["tank_frac"]*k
    if den<=0: 
        return dict(feasible=False,violations=["propellant_tank_infeasible"],wet_kg=float("inf"),cost=float("inf"),science=0,prop_kg=float("inf"),avg_power_w=P_avg,inst_mass=m_inst,link_margin_db=-99,margin_min=-9)
    m_prop=dry*k/den; tank=prop["tank_frac"]*m_prop; wet=dry+tank+m_prop
    if prop["electric"]:
        burn_days=wet*sc["dv_ms"]*(1+G["dv_margin"])/prop["thrust_n"]/86400.0
        if burn_days>G["max_electric_burn_days"]: v.append("electric_burn_too_long")
    else: burn_days=None
    cap_kg=veh["capacity_kg"]*(1-G["launch_margin"])
    if wet>cap_kg: v.append("exceeds_launch_capacity")
    if comp["tol_krad"]<sc["dose_krad"]*G["rad_design_margin"]: v.append("radiation_tolerance")
    # comm
    gt=comm["gain_dbi"] if comm["dish_m"] is None else parabolic_gain_db(comm["dish_m"],comm["freq_hz"],0.55)
    eirp=10*math.log10(comm["tx_w"])+gt
    base_db=eirp+sc["gt_db"][comm["band"]]-fspl_db(sc["dist_m"],comm["freq_hz"])-G["misc_loss_db"]+228.6-G["ebn0_req_db"]
    R=min(sc["rate_cap_bps"],comm["max_rate_bps"],10**((base_db-G["link_margin_req_db"])/10))
    if R<G["min_rate_bps"]: v.append("link_rate_too_low")
    dl_s=sc["dl_hours_per_day"]*3600*G["dl_eff"]
    down=R*dl_s; gen=sum(i["rate_kbps"]*1000*i["duty"] for i in ins)*86400
    frac=1.0 if gen<=0 else min(1.0,down/gen)
    science=sum(i["value"] for i in ins)*frac
    margin_db=(base_db-10*math.log10(max(1e-9,gen/dl_s))) if gen>0 else 99.0
    if science<sc["min_science"]: v.append("science_below_minimum")
    prop_kg=m_prop
    hw=sum(i["cost"] for i in ins)+comp["cost"]+comm["cost"]+arr["cost_per_w"]*P_bol+bat["cost_per_wh"]*cap+prop["hw_cost"]+sc["bus_cost"]+6.0*(struct+therm)+prop["prop_cost_per_kg"]*m_prop
    cost=hw*(1+G["integ_frac"])+veh["cost"]
    if cost>sc["budget"]: v.append("exceeds_budget")
    mass_m=(cap_kg-wet)/cap_kg; bud_m=(sc["budget"]-cost)/sc["budget"]; sci_m=(science-sc["min_science"])/max(1e-9,sc["min_science"])
    return dict(feasible=not v,violations=v,wet_kg=wet,dry_kg=dry,prop_kg=prop_kg,cost=cost,science=science,avg_power_w=P_avg,inst_mass=m_inst,
                array_w_bol=P_bol,array_area_m2=area,battery_wh=cap,link_rate_bps=R,link_margin_db=margin_db,data_gen_bits_day=gen,data_down_bits_day=down,
                electric_burn_days=burn_days,margin_min=min(mass_m,bud_m,sci_m),mass_margin=mass_m,budget_margin=bud_m)

def enumerate_designs(G, sc, catalog=None):
    cat=catalog or dict(arrays=ARRAYS,batteries=BATTERIES,computers=COMPUTERS,comms=COMMS,props=PROPS)
    n=len(sc["instruments"]); out=[]
    for mask in range(1,1<<n):
        sel=[i for i in range(n) if mask>>i&1]
        for comp in cat["computers"]:
          for comm in cat["comms"]:
            for arr in cat["arrays"]:
              for bat in cat["batteries"]:
                for prop in cat["props"]:
                  if prop["electric"] and not sc["allow_electric"]: continue
                  for veh in sc["vehicles"]:
                    r=evaluate(G,sc,sel,comp,comm,arr,bat,prop,veh)
                    r["design"]=dict(instruments=[sc["instruments"][i]["id"] for i in sel],computer=comp["id"],comm=comm["id"],array=arr["id"],battery=bat["id"],propulsion=prop["id"],vehicle=veh["id"])
                    out.append(r)
    return out

OBJECTIVES = {
 "min_mass":("Minimum launch (wet) mass","wet_kg",1),
 "min_cost":("Minimum total cost","cost",1),
 "min_propellant":("Minimum propellant mass","prop_kg",1),
 "min_power":("Minimum average power demand","avg_power_w",1),
 "max_science":("Maximum science within budget","science",-1),
 "max_payload":("Maximum instrument payload mass","inst_mass",-1),
 "max_link_margin":("Maximum communication link margin","link_margin_db",-1),
 "max_feasibility_margin":("Maximum worst-case margin (mass/budget/science)","margin_min",-1),
}
def solve(designs, key):
    feas=[d for d in designs if d["feasible"]]
    if not feas: return None
    name,f,sgn=OBJECTIVES[key]
    # deterministic tie-break: secondary cost then wet mass then design string
    return min(feas,key=lambda d:(sgn*d[f],d["cost"],d["wet_kg"],str(d["design"])))
def balanced(designs, weights=None):
    feas=[d for d in designs if d["feasible"]]
    if not feas: return None
    w=weights or dict(wet_kg=1,cost=1,science=1)
    keys=[("wet_kg",1),("cost",1),("science",-1)]
    lo={k:min(d[k] for d in feas) for k,_ in keys}; hi={k:max(d[k] for d in feas) for k,_ in keys}
    def score(d):
        s=0
        for k,sg in keys:
            span=hi[k]-lo[k] or 1.0
            x=(d[k]-lo[k])/span if sg==1 else (hi[k]-d[k])/span   # 0 = utopia
            s+=w[k]*x*x
        return s
    return min(feas,key=lambda d:(score(d),str(d["design"])))
def pareto(designs, keys=(("wet_kg",1),("cost",1),("science",-1))):
    feas=[d for d in designs if d["feasible"]]
    # unique by objective tuple
    pts={}
    for d in feas:
        t=tuple(round(sg*d[k],6) for k,sg in keys); 
        if t not in pts or str(d["design"])<str(pts[t]["design"]): pts[t]=d
    items=sorted(pts.items())
    front=[]
    for t,d in items:
        if not any(all(o<=x for o,x in zip(t2,t)) and t2!=t for t2,_ in items): front.append(d)
    return front
