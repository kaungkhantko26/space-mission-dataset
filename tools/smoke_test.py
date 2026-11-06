#!/usr/bin/env python3
"""Starts tools/serve_api.py on a free port and exercises every endpoint (also used by CI). Exit code 0 = all passed."""
import json, subprocess, sys, os, time, urllib.request, urllib.error, socket, sqlite3, math
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,"..")
s=socket.socket(); s.bind(("127.0.0.1",0)); port=s.getsockname()[1]; s.close()
proc=subprocess.Popen([sys.executable,os.path.join(HERE,"serve_api.py"),"--port",str(port)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
base=f"http://127.0.0.1:{port}"; res=[]
def call(path,body=None):
    req=urllib.request.Request(base+path,data=(json.dumps(body).encode() if body is not None else None),headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=60) as r: return r.status,json.load(r)
    except urllib.error.HTTPError as e: return e.code,json.load(e)
def t(name,ok,detail=""): ok=bool(ok); res.append(ok); print(("PASS" if ok else "FAIL"),name,detail)
try:
    for _ in range(50):
        try: urllib.request.urlopen(base+"/health",timeout=1); break
        except Exception: time.sleep(0.2)
    c,j=call("/health"); t("health reports strict mode",c==200 and "STRICT" in j["mode"])
    c,j=call("/collections"); t("collections include real datasets",c==200 and j["launch_vehicle_configs"]>500 and j["spacex_launch_history"]>700 and j["planets"]==9,str(j))
    c,j=call("/collections/planets?limit=50"); t("every served planet is verified",c==200 and all(r["data_class"]=="verified" for r in j["records"]))
    c,j=call("/collections/electric_propulsion?sort=-isp_vac_s&fields=id,isp_vac_s,data_class"); t("sort by Isp (NEXT first)",c==200 and j["records"][0]["id"]=="next" and j["records"][0]["isp_vac_s"]==4190)
    c,j=call("/collections/launch_vehicles/saturn_v"); t("Saturn V thrust equals NASA press-kit value",c==200 and abs(j["record"]["thrust_sl_n"]-34046038.8)<1e3)
    c,j=call("/collections/planets/nope"); t("404 for unknown id",c==404)
    c,j=call("/collections/moon_mean_elements?satellite=Io"); t("JPL moon elements",c==200 and j["total"]>=1 and abs(j["records"][0]["semi_major_axis_km"]-421800)<1e3)
    c,j=call("/collections/planets/mars"); t("NSSDC solar irradiance for Mars (power sizing)",c==200 and abs(j["record"]["nssdc_fact_sheet"]["numeric"]["Solar irradiance (W/m 2 )"]-586.2)<0.5)
    c,j=call("/collections/nasa_instruments?q=Thermal%20Emission%20Spectrometer"); t("instrument with power stated in NASA text",c==200 and any(r["power_w_from_text"] for r in j["records"]))
    c,j=call("/collections/nasa_missions?q=LRO"); t("mission cost mention from NASA text",c==200 and any(r["cost_mentions_in_text"] for r in j["records"]))
    c,j=call("/light-time?target=mars"); t("light time to Mars from verified orbits",c==200 and 4<j["records"][0]["min_one_way_light_time_min"]<5 and 20<j["records"][0]["max_one_way_light_time_min"]<22)
    c,j=call("/delta-v",dict(isp_s=310,m0_kg=1000,mf_kg=400)); t("delta-v (Tsiolkovsky)",c==200 and abs(j["delta_v_m_s"]-310*9.80665*math.log(2.5))<1e-6)
    c,j=call("/hohmann",dict(body="earth",altitude1_km=400,altitude2_km=35786)); t("Hohmann LEO->GEO ~3.86 km/s from verified GM",c==200 and abs(j["total_m_s"]-3857)<40,f'{j["total_m_s"]:.0f}')
    c,j=call("/collections/launch_vehicle_configs?full_name=Falcon%209%20Block%205"); t("Launch Library: Falcon 9 Block 5 config",c==200 and j["total"]==1 and j["records"][0]["leo_capacity_kg"]==22800 and j["records"][0]["source_authority"].startswith("aggregator"))
    c,j=call("/collections/launch_vehicle_configs?leo_capacity_kg_gte=40000&active=true&sort=-leo_capacity_kg&fields=full_name,leo_capacity_kg"); t("filter vehicles by capacity and active flag",c==200 and j["total"]>=3 and j["records"][0]["leo_capacity_kg"]>=40000,str([r["full_name"] for r in j["records"][:4]]))
    c,j=call("/collections/spacex_launch_history?limit=1&sort=-date_utc"); t("SpaceX launch record (743+)",c==200 and j["total"]>=743)
    c,j=call("/collections/smallsat_components?domain=propulsion&limit=3"); t("NASA SoA propulsion components",c==200 and j["total"]>150 and j["records"][0]["attributes"] and j["records"][0]["data_class"]=="verified")
    c,j=call("/collections/nasa_instruments?q=LORRI"); t("NASA catalog instrument LORRI",c==200 and j["total"]>=1 and "aperture" in j["records"][0]["description"])
    c,j=call("/collections/atmospheres/atm_venus"); t("Venus atmosphere published text",c==200 and "92 bars" in j["record"]["published"]["surface_pressure"])
    c,j=call("/collections/fluid_properties/nist_oxygen"); t("NIST oxygen boiling point ~90 K",c==200 and abs(j["record"]["normal_boiling_point"]["temperature_k"]-90.19)<0.4)
    c,j=call("/optimize?scenario=leo_eo"); t("no synthetic optimizer is served",c==404)
    db=os.path.join(ROOT,"exports","space_mission.sqlite")
    if os.path.exists(db):
        con=sqlite3.connect(db); n=con.execute("select count(*) from planets where data_class='verified'").fetchone()[0]; m=con.execute("select count(*) from smallsat_components").fetchone()[0]; t("sqlite export readable",n==9 and m>1500,f"{n} planets, {m} components")
finally: proc.terminate()
print(f"{sum(res)}/{len(res)} passed"); sys.exit(0 if all(res) else 1)
