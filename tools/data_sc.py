# Spacecraft subsystems, instruments, comms, missions. Recalled; NOT retrieved. None = not recorded.
# Spacecraft records are mostly TECHNOLOGY-CLASS entries with typical ranges (estimated), plus a few named flight items.
def C(id,name,cat,kind,mass=None,power_w=None,gen_w=None,cap_wh=None,extra=None,src=None,cls="estimated",conf="low",note=""):
    return dict(id=id,name=name,category=cat,record_kind=kind,mass_kg=mass,power_consumption_w=power_w,power_generation_w=gen_w,energy_capacity_wh=cap_wh,params=extra or {},src=src or ["S16"],data_class=cls,confidence=conf,note=note)
COMPONENTS = [
 # solar arrays: tech classes; specific power W/kg at array level (BOL, 1 AU) & cell efficiency
 C("sa_si","Silicon cell array (class)","solar_array","technology_class",extra={"cell_efficiency_bol":[0.14,0.17],"array_specific_power_w_per_kg":[30,60],"degradation_per_year":[0.02,0.04]},note="Typical ranges; legacy technology."),
 C("sa_3j_gaas","Triple-junction GaAs array (class)","solar_array","technology_class",extra={"cell_efficiency_bol":[0.28,0.30],"array_specific_power_w_per_kg":[60,120],"degradation_per_year":[0.01,0.03]},note="Cell efficiency ~28-30% (BOL) is typical for flight triple-junction cells."),
 C("sa_body","Body-mounted cells on 6U CubeSat (class)","solar_array","technology_class",extra={"typical_orbit_avg_power_w":[5,20]},note="Small-sat scale."),
 C("bat_li_ion","Li-ion battery (class)","battery","technology_class",extra={"specific_energy_wh_per_kg":[120,200],"max_dod_leo":[0.2,0.4],"round_trip_efficiency":[0.90,0.95]},note="Cell-to-pack ranges; LEO DoD limits drive life."),
 C("bat_nih2","NiH2 battery (class)","battery","technology_class",extra={"specific_energy_wh_per_kg":[30,60],"max_dod_leo":[0.3,0.4]},note="Legacy, e.g. long-life GEO/ISS-era."),
 C("rtg_mmrtg","MMRTG (Multi-Mission RTG)","power_source","named_item",mass=45.0,gen_w=110.0,extra={"thermal_power_w":2000,"fuel":"Pu-238 (GPHS modules)","power_decay_per_year":0.04},src=["S17"],cls="unverified",conf="medium",note="~110 W electrical at BOL; flown on MSL and Mars 2020."),
 C("rtg_gphs","GPHS-RTG","power_source","named_item",mass=55.9,gen_w=300.0,extra={"thermal_power_w":4400},src=["S17"],cls="unverified",conf="medium",note="Flown on Cassini, New Horizons (~245 W at launch for NH unit), others."),
 C("cpu_rad750","RAD750 flight computer (processor)","onboard_computer","named_item",power_w=5.0,extra={"clock_mhz":200,"rad_tolerance_krad_si":[200,1000]},src=["S18"],cls="unverified",conf="medium",note="Processor-only power figure approximate; board-level power higher."),
 C("cpu_leon3","LEON3-FT class processor","onboard_computer","technology_class",extra={"clock_mhz":[50,100]},note="Fault-tolerant SPARC V8; mass/power not recorded."),
 C("cpu_cots","Commercial off-the-shelf SoC (class)","onboard_computer","technology_class",extra={"radiation_note":"Limited tolerance; suited to LEO short missions or with mitigation"},note="Small-sat practice."),
 C("rw_small","Small reaction wheel (CubeSat class)","attitude_control","technology_class",mass=0.1,extra={"momentum_storage_nms":[0.001,0.02],"mass_kg_range":[0.05,0.3]},note="Order-of-magnitude class record; mass shown is representative midpoint-ish and ESTIMATED."),
 C("rw_large","Large reaction wheel (large satellite class)","attitude_control","technology_class",extra={"momentum_storage_nms":[10,200],"mass_kg_range":[5,20]},note="Order-of-magnitude."),
 C("st_star","Star tracker (class)","attitude_control","technology_class",extra={"accuracy_arcsec_1sigma":[1,30],"mass_kg_range":[0.2,3.0],"power_w_range":[0.5,10]},note="Wide range across small-sat to large-sat units."),
 C("mtq","Magnetorquer (class)","attitude_control","technology_class",extra={"usable_only_in":"low planetary orbit with magnetic field"},note="Not usable in interplanetary cruise."),
 C("rad_heater","Heaters & MLI thermal control (class)","thermal_control","technology_class",extra={"mli_areal_density_kg_m2":[0.05,0.5]},note="Deep-space missions need more heater power; cold-case driver."),
 C("rad_radiator","Radiator panel (class)","thermal_control","technology_class",extra={"areal_density_kg_m2":[2,10]},note="Heat rejection scales with T^4 (Stefan-Boltzmann)."),
 C("ant_patch","Patch antenna (S-band, class)","communications","technology_class",extra={"gain_dbi":[5,9],"band":"S"},note="Low gain; LEO/near-Earth."),
 C("ant_hga_1m","1 m parabolic HGA (X-band class)","communications","technology_class",extra={"diameter_m":1.0,"band":"X","efficiency":0.55},note="Gain derived from aperture in analysis files."),
 C("ant_hga_3m","3 m parabolic HGA (X/Ka-band class)","communications","technology_class",extra={"diameter_m":3.0,"efficiency":0.55},note="Typical outer-planet class size."),
 C("xpdr_deep_space","Deep-space transponder (class)","communications","technology_class",extra={"bands":["S","X","Ka"],"tx_power_w":[5,100]},note="Examples: NASA/JPL Small Deep Space Transponder family."),
 C("tank_ti","Titanium propellant tank (class)","structure","technology_class",extra={"tank_mass_fraction_of_propellant":[0.03,0.10]},note="Pressurized tank plus pressurant system typically a few percent."),
 C("struct_bus","Primary structure (class)","structure","technology_class",extra={"structure_fraction_of_dry_mass":[0.15,0.30]},note="Wide range by mission class."),
 C("shield_rad","Radiation shielding vault (class)","radiation_protection","technology_class",extra={"note":"Juno used a titanium vault for electronics"},note="Mass scales with dose requirement; not quantified here."),
]
# Instruments. fields: mass, power, resolution etc. Real flight instruments, some nulls.
def I(id,name,kind,mission,mass,power,params,src,conf="medium",note=""):
    return dict(id=id,name=name,instrument_type=kind,heritage_mission=mission,mass_kg=mass,power_w=power,params=params,src=src,data_class="unverified",confidence=conf,note=note)
INSTRUMENTS = [
 I("lorri","LORRI","optical_camera","New Horizons",8.8,5.8,{"aperture_cm":20.8,"ifov_urad":4.97,"fov_deg":0.29,"pixels":"1024x1024"},["S19"]),
 I("ralph","Ralph (MVIC + LEISA)","multispectral_imager_spectrometer","New Horizons",10.5,6.3,{"mvic_bands":"4 color + 2 panchromatic","leisa_range_um":[1.25,2.5]},["S19"]),
 I("alice","Alice","uv_spectrometer","New Horizons",4.4,4.4,{"range_nm":[52,187]},["S19"]),
 I("rex","REX","radio_science","New Horizons",0.1,2.1,{},["S19"],"low"),
 I("swap","SWAP","particle_detector","New Horizons",3.3,2.3,{"measures":"solar wind plasma"},["S19"]),
 I("pepssi","PEPSSI","particle_detector","New Horizons",1.5,2.5,{"measures":"energetic particles"},["S19"]),
 I("sdc","Student Dust Counter","dust_detector","New Horizons",1.9,5.0,{},["S19"]),
 I("hirise","HiRISE","optical_camera","Mars Reconnaissance Orbiter",65.0,60.0,{"aperture_m":0.5,"gsd_m_at_300km":0.3,"swath_km":6},["S20"],"medium","Mass/power approximate."),
 I("crism","CRISM","imaging_spectrometer","Mars Reconnaissance Orbiter",32.9,None,{"range_nm":[362,3920],"channels":544,"spectral_sampling_nm":6.55,"gsd_m_at_300km":18},["S20"]),
 I("sharad","SHARAD","sounding_radar","Mars Reconnaissance Orbiter",17.0,None,{"center_freq_mhz":20,"bandwidth_mhz":10,"vertical_resolution_m_free_space":15},["S20"],"low"),
 I("mola","MOLA","lidar_altimeter","Mars Global Surveyor",25.9,34.2,{"wavelength_nm":1064,"rate_hz":10,"footprint_m":160},["S21"],"low"),
 I("lroc_nac","LROC NAC","optical_camera","Lunar Reconnaissance Orbiter",None,None,{"gsd_m_at_50km":0.5,"pixels_across":5064,"fov_deg":2.86},["S22"]),
 I("sam","SAM","mass_spectrometer_gas_chromatograph","Mars Science Laboratory",40.0,None,{"target":"organics, volatiles"},["S23"],"low"),
 I("oli","OLI","multispectral_camera","Landsat 8",None,None,{"gsd_m":30,"pan_gsd_m":15,"bands":9,"swath_km":185},["S24"]),
 I("tirs","TIRS","thermal_imager","Landsat 8",None,None,{"gsd_m":100,"bands_um":[10.9,12.0],"swath_km":185},["S24"]),
 I("msi","MSI","multispectral_camera","Sentinel-2",None,None,{"gsd_m":[10,20,60],"bands":13,"swath_km":290},["S25"]),
]
GROUND = [
 dict(id="dsn_goldstone_dss14",name="DSN Goldstone DSS-14 (70 m)",operator="NASA DSN",lat=35.4259,lon=-116.8900,antenna_m=70.0,gain_dbi={"S":63.0,"X":74.0},bands=["S","X"],tx_power_w_max=20000,note="Gains approximate (DSN 810-005 expected).",src=["S26"],conf="low"),
 dict(id="dsn_canberra_dss43",name="DSN Canberra DSS-43 (70 m)",operator="NASA DSN",lat=-35.4014,lon=148.9817,antenna_m=70.0,gain_dbi={"S":63.0,"X":74.0},bands=["S","X"],tx_power_w_max=20000,note="Gains approximate.",src=["S26"],conf="low"),
 dict(id="dsn_madrid_dss63",name="DSN Madrid DSS-63 (70 m)",operator="NASA DSN",lat=40.4314,lon=-4.2481,antenna_m=70.0,gain_dbi={"S":63.0,"X":74.0},bands=["S","X"],tx_power_w_max=20000,note="Gains approximate.",src=["S26"],conf="low"),
 dict(id="dsn_34m_bwg",name="DSN 34 m beam-waveguide (generic)",operator="NASA DSN",lat=None,lon=None,antenna_m=34.0,gain_dbi={"X":68.0,"Ka":79.0},bands=["X","Ka"],tx_power_w_max=None,note="Gains approximate.",src=["S26"],conf="low"),
 dict(id="estrack_new_norcia",name="ESTRACK New Norcia (35 m)",operator="ESA",lat=-31.048,lon=116.191,antenna_m=35.0,gain_dbi={},bands=["S","X"],tx_power_w_max=None,note="Gain not recorded.",src=["S27"],conf="low"),
 dict(id="estrack_cebreros",name="ESTRACK Cebreros (35 m)",operator="ESA",lat=40.4528,lon=-4.3675,antenna_m=35.0,gain_dbi={},bands=["X","Ka"],tx_power_w_max=None,note="Gain not recorded.",src=["S27"],conf="low"),
 dict(id="estrack_malargue",name="ESTRACK Malargue (35 m)",operator="ESA",lat=-35.776,lon=-69.398,antenna_m=35.0,gain_dbi={},bands=["X","Ka"],tx_power_w_max=None,note="Gain not recorded.",src=["S27"],conf="low"),
 dict(id="ksat_svalbard",name="KSAT Svalbard (SvalSat)",operator="KSAT",lat=78.23,lon=15.39,antenna_m=None,gain_dbi={},bands=["S","X"],tx_power_w_max=None,note="Polar site: many passes per day for SSO satellites.",src=["S28"],conf="low"),
]
OPTICAL = [
 dict(id="llcd",name="LLCD (LADEE, lunar distance)",downlink_mbps=622,uplink_mbps=20,distance_km=384400,year=2013,src=["S29"],conf="medium",note="Demonstration."),
 dict(id="dsoc",name="DSOC (Psyche)",downlink_mbps=267,uplink_mbps=None,distance_km=33e6,year=2023,src=["S29"],conf="low",note="Peak demonstrated at ~0.2 AU; rate falls ~1/d^2."),
]
# missions: id,name,agency,launch_date,vehicle_id,launch_mass_kg,dry_mass_kg,destination,outcome,cost_musd(+scope),instruments,duration,power,comms,src,conf,note
def M(id,name,agency,launch,veh,lm,dm,dest,status,cost,cost_note,inst,power,comms,src,conf="medium",note=""):
    return dict(id=id,name=name,agency=agency,launch_date=launch,launch_vehicle_id=veh,launch_vehicle_note=None,launch_mass_kg=lm,dry_mass_kg=dm,destination=dest,outcome=status,cost_musd_nominal=cost,cost_scope=cost_note,instrument_ids=inst,power_system=power,comms=comms,src=src,confidence=conf,note=note,record_type="historical")
MISSIONS = [
 M("apollo11","Apollo 11","NASA","1969-07-16","saturn_v",43904,None,"Moon (landing)","success",None,"Program cost not apportioned to mission",[],"Fuel cells (CSM)","S-band unified",["S09"],"medium","CSM 28,801 kg + LM 15,103 kg approx."),
 M("voyager2","Voyager 2","NASA","1977-08-20","titan3e_centaur",825.5,None,"Jupiter, Saturn, Uranus, Neptune","success_extended",None,"",[],"MMRTG-class predecessor (MHW-RTG) ~470 W at launch","X-band 3.7 m HGA",["S30"],"low","Launch vehicle Titan IIIE-Centaur not in launch dataset."),
 M("cassini","Cassini-Huygens","NASA/ESA/ASI","1997-10-15","titan4b_centaur",5712,None,"Saturn orbiter + Titan probe","success",3900,"Total incl. operations, nominal USD, approx.",[],"3 RTGs (GPHS-RTG)","X/Ka-band 4 m HGA",["S31"],"low","Launch vehicle Titan IV-B/Centaur not in launch dataset."),
 M("lro","Lunar Reconnaissance Orbiter","NASA","2009-06-18","atlas_v_551",1916,1018,"Lunar polar orbit","success",504,"Approx, nominal USD",["lroc_nac"],"Solar array + battery","S/Ka-band",["S22"],"low","Launched on Atlas V 401 variant (not 551); vehicle id is nearest family record."),
 M("mro","Mars Reconnaissance Orbiter","NASA","2005-08-12","atlas_v_551",2180,1031,"Mars orbit","success",720,"Approx, nominal USD",["hirise","crism","sharad"],"Solar arrays ~1,000 W near Mars (approx)","X-band 3 m HGA, Ka demo",["S20"],"low","Launched on Atlas V 401; nearest family record used."),
 M("new_horizons","New Horizons","NASA","2006-01-19","atlas_v_551",478,None,"Pluto, Kuiper belt","success_extended",700,"Approx, nominal USD",["lorri","ralph","alice","rex","swap","pepssi","sdc"],"1 GPHS-RTG","X-band 2.1 m HGA",["S19"],"medium","Atlas V 551 + Star 48B third stage."),
 M("juno","Juno","NASA","2011-08-05","atlas_v_551",3625,1593,"Jupiter polar orbit","success_extended",1130,"Approx, nominal USD",[],"Solar arrays (large)","X/Ka-band",["S32"],"low"),
 M("curiosity","Mars Science Laboratory (Curiosity)","NASA","2011-11-26","atlas_v_551",3893,None,"Mars surface (Gale Crater)","success_extended",2500,"Approx, nominal USD",["sam"],"MMRTG","UHF relay + X-band",["S23"],"medium","Launched on Atlas V 541; nearest family record used."),
 M("jwst","James Webb Space Telescope","NASA/ESA/CSA","2021-12-25","ariane5_eca",6161,None,"Sun-Earth L2","success",10000,"Approx total life-cycle, nominal USD",[],"Solar array ~2 kW class (approx)","Ka-band science downlink",["S33"],"low"),
 M("landsat8","Landsat 8","NASA/USGS","2013-02-11","atlas_v_551",2623,None,"Sun-synchronous LEO ~705 km","success",None,"",["oli","tirs"],"Solar array + Li-ion/NiH2","X-band downlink",["S24"],"low","Launched on Atlas V 401; nearest family record used."),
 M("sentinel2a","Sentinel-2A","ESA","2015-06-23","vega_c",1140,None,"Sun-synchronous LEO ~786 km","success",None,"",["msi"],"Solar array","X-band + optical link (EDRS)",["S25"],"low","Launched on Vega (not Vega-C); nearest family record used."),
 M("dawn","Dawn","NASA","2007-09-27","delta2_7925h",1217.7,None,"Vesta, Ceres","success",446,"Approx, nominal USD",[],"Solar arrays + NSTAR ion engines","X-band",["S14"],"low","Delta II 7925H not in launch dataset; first ion propulsion mission to orbit two bodies."),
 M("osiris_rex","OSIRIS-REx","NASA","2016-09-08","atlas_v_551",2110,None,"Bennu sample return","success_extended",800,"Approx, excl launch; nominal USD",[],"Solar arrays","X-band",["S34"],"low","Atlas V 411; nearest family record used."),
 M("marco","MarCO-A/B (6U CubeSats)","NASA JPL","2018-05-05","atlas_v_551",13.5,None,"Mars flyby relay","success",18.5,"Approx, nominal USD",[],"Body/deployable solar panels","X-band, relayed InSight EDL",["S35"],"low","Rideshare with InSight on Atlas V 401; per-spacecraft mass ~13.5 kg."),
]
