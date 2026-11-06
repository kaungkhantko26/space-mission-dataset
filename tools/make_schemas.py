import json, os
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","space-mission-research","schemas")
os.makedirs(R,exist_ok=True)
DC={"enum":["verified","derived","estimated","fictional","unverified"]}
common={"id":{"type":"string","pattern":"^[a-z0-9_]+$"},"data_class":DC,"confidence":{"enum":["low","medium","high"]},"source_ids":{"type":"array","items":{"type":"string","pattern":"^[SG][0-9]{2}$"}},"retrieval_status":{"enum":["not_retrieved","retrieved"]}}
num0=lambda: {"type":["number","null"],"minimum":0}
def env(rec): return {"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object","required":["schema_version","dataset","record_count","records"],"properties":{"schema_version":{"type":"string"},"dataset":{"type":"string"},"record_count":{"type":"integer"},"records":{"type":"array","items":rec}}}
def rec(required,props): return {"type":"object","required":["id"]+required+["data_class","confidence","source_ids","retrieval_status"],"properties":{**common,**props}}
S={
"planets":rec(["name","gravitational_parameter_km3_s2","mean_radius_m"],{"gravitational_parameter_km3_s2":{"type":"number","exclusiveMinimum":0},"mean_radius_m":{"type":"number","exclusiveMinimum":0},"mass_kg":num0(),"surface_gravity_m_s2":num0(),"eccentricity":{"type":["number","null"],"minimum":0,"maximum":1}}),
"moons":rec(["name","parent_id","gravitational_parameter_km3_s2","mean_radius_m"],{"gravitational_parameter_km3_s2":{"type":"number","exclusiveMinimum":0},"mean_radius_m":{"type":"number","exclusiveMinimum":0}}),
"asteroids":rec(["name","gravitational_parameter_km3_s2","mean_radius_m"],{}),
"rocket_engines":rec(["name","type","propellant"],{"thrust_vac_n":num0(),"thrust_sl_n":num0(),"isp_vac_s":{"type":["number","null"],"minimum":50,"maximum":600},"isp_sl_s":{"type":["number","null"],"minimum":50,"maximum":600},"dry_mass_kg":num0()}),
"electric_propulsion":rec(["name","type","propellant"],{"isp_vac_s":{"type":["number","null"],"minimum":500,"maximum":10000},"power_w":num0()}),
"launch_vehicles":rec(["name","status","payloads"],{"payloads":{"type":"array","minItems":1,"items":{"type":"object","required":["orbit","payload_kg","mode"],"properties":{"payload_kg":{"type":"number","exclusiveMinimum":0}}}},"liftoff_mass_kg":num0()}),
"rocket_stages":rec(["vehicle_id","stage","dry_mass_kg","propellant_mass_kg","engine_id"],{"dry_mass_kg":{"type":"number","exclusiveMinimum":0},"propellant_mass_kg":{"type":"number","exclusiveMinimum":0}}),
"boosters":rec(["name"],{}),
"payload_capabilities":{"type":"object","required":["vehicle_id","orbit","payload_kg","mode"],"properties":{"payload_kg":{"type":"number"},**{k:common[k] for k in("data_class","confidence","source_ids")}}},
"instrument":rec(["name","instrument_type","mass_kg","power_w"],{"mass_kg":num0(),"power_w":num0()}),
"component":rec(["name","category","record_kind"],{"record_kind":{"enum":["technology_class","named_item"]}}),
"historical_missions":rec(["name","launch_date","launch_mass_kg","record_type"],{"launch_date":{"type":"string","pattern":"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},"record_type":{"const":"historical"}}),
"experiment":{"type":"object","required":["id","scenario_id","objective","feasibility_status","solver","optimality_claim","selected_components"],"properties":{"feasibility_status":{"enum":["feasible_optimum_found","infeasible"]}}},
}
for k,v in S.items():
    if k=="payload_capabilities": json.dump(env(v),open(f"{R}/{k}.schema.json","w"),indent=1); continue
    json.dump(env(v),open(f"{R}/{k}.schema.json","w"),indent=1)
print("schemas",len(S))
