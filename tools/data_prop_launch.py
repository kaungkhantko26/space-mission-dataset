# Propulsion & launch data. Recalled from published sources; NOT retrieved this session (network blocked). None = not recorded.
# engines: id,name,maker,type,propellant,thrust_vac_N,thrust_sl_N,isp_vac_s,isp_sl_s,dry_kg,burn_s,restart,status,power_W,src,conf,note
E = lambda *a: dict(zip("id name maker type propellant thrust_vac_n thrust_sl_n isp_vac_s isp_sl_s dry_mass_kg burn_s restart status power_w src conf note".split(), a))
ENGINES = [
 E("rs25d","RS-25D (SSME)","Aerojet Rocketdyne","liquid","LOX/LH2",2279000,1859000,452,366,3177,None,False,"historical_operational",None,["S12"],"medium","109% rated power level; flown 135 Shuttle missions; re-used on SLS (RS-25 variants differ)."),
 E("rl10c1","RL10C-1","Aerojet Rocketdyne","liquid","LOX/LH2",106000,None,448,None,190,None,True,"operational",None,["S13"],"medium","Upper-stage expander cycle; thrust/Isp vary by RL10 variant."),
 E("merlin1d","Merlin 1D (sea-level, F9 v1.2)","SpaceX","liquid","LOX/RP-1",914000,845000,311,282,None,None,True,"operational",None,["S06"],"medium","Published nominal thrust; Falcon 9 first stage uses 9 engines."),
 E("mvac","Merlin Vacuum","SpaceX","liquid","LOX/RP-1",981000,None,348,None,None,None,True,"operational",None,["S06"],"medium","Falcon 9/Heavy second stage."),
 E("raptor2","Raptor 2","SpaceX","liquid","LOX/CH4",2300000*1.0,2300000,350,327,1600,None,True,"developmental_operational_testing",None,["S06"],"low","Vacuum thrust not separately recorded; thrust_vac_n is set equal to the sea-level figure as a LOWER bound and flagged. Isp and dry mass are approximate public figures."),
 E("rutherford","Rutherford","Rocket Lab","liquid_electric_pump","LOX/RP-1",25800,25000,343,311,35,None,False,"operational",None,["S10"],"medium","Electric-pump-fed; Electron stage 1 uses 9, stage 2 uses 1 vacuum variant."),
 E("f1","F-1","Rocketdyne","liquid","LOX/RP-1",7770000,6770000,304,263,8400,165,False,"historical",None,["S09"],"medium","Saturn V S-IC; five engines."),
 E("j2","J-2","Rocketdyne","liquid","LOX/LH2",1033000,None,421,None,1788,None,True,"historical",None,["S09"],"medium","Saturn V S-II (5) and S-IVB (1); S-IVB restart for TLI."),
 E("rd180","RD-180","NPO Energomash","liquid","LOX/RP-1",4150000,3830000,338,311,5393,None,False,"operational_legacy",None,["S07"],"medium","Atlas V first stage."),
 E("be4","BE-4","Blue Origin","liquid","LOX/LCH4",None,2400000,None,None,None,None,False,"operational",None,["S07"],"low","Only sea-level thrust recorded; Isp not published in recalled material."),
 E("vinci","Vinci","ArianeGroup","liquid","LOX/LH2",180000,None,457,None,280,None,True,"operational",None,["S11"],"medium","Ariane 6 upper stage, restartable."),
 E("vulcain2","Vulcain 2","ArianeGroup","liquid","LOX/LH2",1359000,960000,431,310,None,None,False,"operational",None,["S11"],"low","Variant 2.1 on Ariane 6 differs slightly."),
 E("rsrm","Shuttle RSRM","Thiokol/ATK","solid","PBAN/APCP",None,12500000,268,242,None,123,False,"historical",None,["S08"],"medium","Peak thrust at sea level; propellant ~503,500 kg per motor."),
 E("srb5","SLS 5-segment booster","Northrop Grumman","solid","PBAN/APCP",None,16000000,267,None,None,126,False,"operational",None,["S08"],"medium","Approximate thrust at liftoff (~16 MN)."),
 E("star48b","Star 48B","Northrop Grumman (Thiokol)","solid","APCP",66700,None,292,None,None,84.1,False,"operational",None,["S12"],"medium","Total motor mass ~2,140 kg incl ~2,010 kg propellant."),
 E("mr103","MR-103 (1 N class)","Aerojet Rocketdyne","monopropellant_thruster","N2H4",1.0,None,224,None,0.33,None,True,"operational",None,["S12"],"low","Thrust range ~0.2-1.1 N; Isp varies with feed pressure/pulse mode."),
 E("aj10_190","AJ10-190 (Shuttle OMS)","Aerojet","bipropellant_thruster","MMH/NTO",26700,None,316,None,118,None,True,"historical",None,["S12"],"medium",""),
 E("aj10_137","AJ10-137 (Apollo SPS)","Aerojet","bipropellant_thruster","Aerozine-50/NTO",91200,None,314,None,None,None,True,"historical",None,["S09"],"medium",""),
 E("draco","Draco (Dragon RCS)","SpaceX","reaction_control_thruster","MMH/NTO",400,None,300,None,None,None,True,"operational",None,["S06"],"low","Isp approximate."),
 E("nstar","NSTAR ion thruster","NASA JPL/Hughes","ion","Xe",0.092,None,3100,None,None,None,True,"operational_historical",2300,["S14"],"medium","Max throttle level (2.3 kW, 92 mN, ~3100 s); min ~0.5 kW/19 mN/~1900 s. Flown on DS1 and Dawn."),
 E("next","NEXT ion thruster","NASA GRC/Aerojet","ion","Xe",0.236,None,4190,None,None,None,True,"developmental_ground_tested",6900,["S14"],"medium","Peak throttle point; flight use of this thruster not recorded."),
 E("t6","T6 gridded ion thruster","QinetiQ","ion","Xe",0.145,None,4300,None,None,None,True,"operational",4500,["S14"],"low","BepiColombo MPO-MTM; peak point approximate."),
 E("bpt4000","BPT-4000 Hall thruster","Aerojet Rocketdyne","hall_effect","Xe",0.254,None,1850,None,None,None,True,"operational",4500,["S14"],"low","Approximate; dual-mode variants exist."),
 E("spt100","SPT-100 Hall thruster","Fakel","hall_effect","Xe",0.083,None,1600,None,3.5,None,True,"operational",1350,["S14"],"low","Approximate."),
]
# propellants: id,name,density_kg_m3,ref_condition,ideal note
PROPELLANTS = [
 dict(id="lox",name="Liquid oxygen",density_kg_m3=1141,condition="boiling point 90 K, 1 atm",src=["S15"],conf="medium"),
 dict(id="lh2",name="Liquid hydrogen",density_kg_m3=70.85,condition="boiling point 20 K, 1 atm",src=["S15"],conf="medium"),
 dict(id="lch4",name="Liquid methane",density_kg_m3=422.6,condition="boiling point 111 K, 1 atm",src=["S15"],conf="medium"),
 dict(id="rp1",name="RP-1 kerosene",density_kg_m3=820,condition="~15-20 C; varies 800-820",src=["S15"],conf="medium"),
 dict(id="n2o4",name="Nitrogen tetroxide (NTO)",density_kg_m3=1443,condition="20 C",src=["S15"],conf="medium"),
 dict(id="mmh",name="Monomethylhydrazine (MMH)",density_kg_m3=878,condition="20 C",src=["S15"],conf="medium"),
 dict(id="n2h4",name="Hydrazine",density_kg_m3=1004,condition="~25 C",src=["S15"],conf="medium"),
 dict(id="xe",name="Xenon (stored supercritical)",density_kg_m3=1600,condition="typical tank storage; varies with pressure/temperature",src=["S14"],conf="low"),
]
# launch vehicles. payload dicts: orbit label, kg, alt_km, incl_deg, mode, source note
V = lambda *a: dict(zip("id name maker country status height_m diameter_m stages liftoff_mass_kg thrust_sl_n reusable fairing_diam_m fairing_height_m price_usd price_year payloads sites src conf note".split(), a))
def P(orbit,kg,alt,inc,mode,note=""): return dict(orbit=orbit,payload_kg=kg,altitude_km=alt,inclination_deg=inc,mode=mode,assumption=note)
VEHICLES = [
 V("saturn_v","Saturn V","NASA/Boeing/NAA/Douglas","US","retired",110.6,10.1,3,2970000,33400000,False,None,None,None,None,
   [P("LEO",140000,190,28.5,"expended","Apollo 17 class, incl. S-IVB"),P("TLI",48600,None,None,"expended","Translunar injection")],["KSC LC-39"],["S09"],"medium","Thrust is nominal design value; actual Apollo thrust ~34.5-35.1 MN."),
 V("sls_b1","SLS Block 1","NASA","US","operational",98.0,8.4,2,2608000,39100000,False,5.1,None,None,None,
   [P("LEO",95000,None,None,"expended","Reference orbit not recorded"),P("TLI",27000,None,None,"expended","")],["KSC LC-39B"],["S08"],"medium","Thrust includes 2 SRBs + 4 RS-25; height of Block 1 stack."),
 V("falcon9_b5","Falcon 9 Block 5","SpaceX","US","operational",70.0,3.7,2,549054,7607000,True,5.2,13.1,None,None,
   [P("LEO",22800,None,None,"expended","Published figure; reference orbit details not recorded"),P("GTO",8300,None,None,"expended",""),P("GTO",5500,None,None,"droneship recovery","Reusable figure approximate")],["CCSFS SLC-40","KSC LC-39A","VSFB SLC-4E"],["S06"],"medium","Published price not recorded (varies; 2022 website value ~67M USD recalled but not retained)."),
 V("falcon_heavy","Falcon Heavy","SpaceX","US","operational",70.0,12.2,2,1420788,22819000,True,5.2,13.1,97000000,2022,
   [P("LEO",63800,None,None,"expended",""),P("GTO",26700,None,None,"expended",""),P("Mars transfer",16800,None,None,"expended","Direct transfer")],["KSC LC-39A"],["S06"],"medium","Price is a historical website figure (2022)."),
 V("starship","Starship (Super Heavy + Ship)","SpaceX","US","developmental",121.0,9.0,2,5000000,75900000,True,None,None,None,None,
   [P("LEO",100000,None,None,"fully reusable (target)","Target 100-150 t; not demonstrated operationally")],["Starbase"],["S06"],"low","Developmental; thrust computed as 33 x 2.3 MN nominal Raptor 2 (derived); liftoff mass approximate."),
 V("atlas_v_551","Atlas V 551","ULA","US","operational_retiring",58.3,3.81,2,590000,None,False,5.4,20.7,None,None,
   [P("LEO",18850,None,28.7,"expended",""),P("GTO",8900,None,None,"expended","")],["CCSFS SLC-41","VSFB SLC-3E"],["S07"],"medium","Thrust at liftoff not retained."),
 V("vulcan_vc6","Vulcan Centaur VC6","ULA","US","operational",61.6,5.4,2,None,None,False,5.4,None,None,None,
   [P("LEO",27200,None,None,"expended",""),P("GTO",14400,None,None,"expended","")],["CCSFS SLC-41"],["S07"],"low",""),
 V("electron","Electron","Rocket Lab","US/NZ","operational",18.0,1.2,2,12500,224000,False,1.2,2.4,7500000,2021,
   [P("SSO",300,500,97.4,"expended","Published capability ~300 kg to 500 km SSO")],["Mahia LC-1","Wallops LC-2"],["S10"],"medium","Price is a ~2021 figure; thrust sum of 9 Rutherford SL (derived 9 x 25 kN)."),
 V("ariane5_eca","Ariane 5 ECA","Arianespace","EU","retired",52.0,5.4,2,780000,None,False,5.4,17.0,None,None,
   [P("GTO",10500,None,None,"expended","Dual-launch figure approximate")],["Kourou ELA-3"],["S11"],"medium",""),
 V("ariane64","Ariane 64","Arianespace","EU","operational",62.0,5.4,2,None,None,False,5.4,20.0,None,None,
   [P("LEO",21650,None,None,"expended","Reference orbit details not recorded"),P("GTO",11500,None,None,"expended","")],["Kourou ELA-4"],["S11"],"low",""),
 V("ariane62","Ariane 62","Arianespace","EU","operational",62.0,5.4,2,None,None,False,5.4,20.0,None,None,
   [P("LEO",10350,None,None,"expended",""),P("GTO",4500,None,None,"expended","")],["Kourou ELA-4"],["S11"],"low",""),
 V("delta4_heavy","Delta IV Heavy","ULA","US","retired",72.0,5.1,2,733000,None,False,5.1,19.1,None,None,
   [P("LEO",28790,None,28.7,"expended",""),P("GTO",14220,None,None,"expended","")],["CCSFS SLC-37B","VSFB SLC-6"],["S07"],"medium",""),
 V("new_glenn","New Glenn","Blue Origin","US","operational",98.0,7.0,2,None,17100000,True,7.0,21.9,None,None,
   [P("LEO",45000,None,None,"booster recovery","Published capability"),P("GTO",13600,None,None,"booster recovery","")],["CCSFS LC-36"],["S07"],"low","Thrust = 7 x BE-4 SL (derived)."),
 V("vega_c","Vega-C","Arianespace/Avio","EU","operational",35.0,3.4,4,210000,None,False,3.3,8.1,None,None,
   [P("SSO",2300,700,None,"expended","")],["Kourou ELV"],["S11"],"low",""),
 V("soyuz_21b","Soyuz-2.1b","Roscosmos/TsSKB","RU","operational",46.3,2.95,3,312000,None,False,None,None,None,None,
   [P("LEO",8200,None,None,"expended","")],["Baikonur","Plesetsk","Vostochny","Kourou (historical)"],["S12"],"low",""),
 V("cz5","Long March 5","CASC","CN","operational",57.0,5.0,2,869000,10573000,False,5.2,12.0,None,None,
   [P("LEO",25000,None,None,"expended",""),P("GTO",14000,None,None,"expended","")],["Wenchang"],["S12"],"low","Thrust approximate."),
]
# stages: id,vehicle,stage,dry_kg,prop_kg,engine_id,n_engines,isp_vac_s
ST = lambda *a: dict(zip("id vehicle_id stage dry_mass_kg propellant_mass_kg engine_id n_engines src conf note".split(), a))
STAGES = [
 ST("saturn_v_s1c","saturn_v","S-IC",137000,2077000,"f1",5,["S09"],"medium",""),
 ST("saturn_v_s2","saturn_v","S-II",36200,456100,"j2",5,["S09"],"medium",""),
 ST("saturn_v_s4b","saturn_v","S-IVB",10600,109500,"j2",1,["S09"],"medium",""),
 ST("sls_core","sls_b1","Core stage",85300,987000,"rs25d",4,["S08"],"medium","RS-25 variants (RS-25D/E) approximated by rs25d record for engine linkage."),
 ST("f9_s1","falcon9_b5","Stage 1",25600,395700,"merlin1d",9,["S06"],"medium",""),
 ST("f9_s2","falcon9_b5","Stage 2",4000,92670,"mvac",1,["S06"],"medium",""),
 ST("electron_s1","electron","Stage 1",950,9250,"rutherford",9,["S10"],"low",""),
 ST("electron_s2","electron","Stage 2",250,2050,"rutherford",1,["S10"],"low","Vacuum-optimized Rutherford; sea-level record used as linkage."),
]
BOOSTERS = [
 dict(id="sls_srb",name="SLS 5-segment solid rocket booster",vehicle_id="sls_b1",count=2,thrust_sl_n=16000000,propellant_mass_kg=626400,burn_s=126,engine_id="srb5",src=["S08"],conf="medium",note="Approximate."),
 dict(id="stg_rsrm",name="Space Shuttle RSRM",vehicle_id=None,count=2,thrust_sl_n=12500000,propellant_mass_kg=503500,burn_s=123,engine_id="rsrm",src=["S08"],conf="medium",note="Historical."),
 dict(id="ariane5_eap",name="Ariane 5 EAP (P241)",vehicle_id="ariane5_eca",count=2,thrust_sl_n=7080000,propellant_mass_kg=237000,burn_s=130,engine_id=None,src=["S11"],conf="low",note="Peak thrust; approximate."),
 dict(id="fh_side",name="Falcon Heavy side booster (F9 core derivative)",vehicle_id="falcon_heavy",count=2,thrust_sl_n=7607000,propellant_mass_kg=395700,burn_s=None,engine_id="merlin1d",src=["S06"],conf="medium",note="Equivalent to Falcon 9 stage 1."),
]
