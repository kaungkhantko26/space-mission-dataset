# Celestial body data. All values recalled from standard published references; NOT retrieved this session.
# Units: mu km^3/s^2, radius km, mass kg, g m/s^2, rotation hours (negative = retrograde), sma km, period days, incl deg.
SUN = dict(id="sun", name="Sun", category="star", mu=132712440018.0, r_mean=695700.0, r_eq=695700.0, mass=1.9885e30, g=274.0, rot_h=609.12, temp_mean_k=5772.0, parent=None, src=["S05","S01"], note="GM and nominal radius from IAU 2015 B3 nominal values; surface temp = effective temperature.")
# id,name,mu,r_mean,r_eq,mass,g,rot_h,a_AU,e,i,period_d,temp_k,mag_T(equatorial surface field tesla or None)
PLANETS = [
 ("mercury","Mercury",22031.86855,2439.4,2440.5,3.3011e23,3.70,1407.6,0.38709927,0.20563593,7.00497902,87.969,440,1.95e-7),
 ("venus","Venus",324858.592,6051.8,6051.8,4.8675e24,8.87,-5832.5,0.72333566,0.00677672,3.39467605,224.701,737,None),
 ("earth","Earth",398600.4418,6371.0,6378.137,5.9722e24,9.80665,23.9345,1.00000261,0.01671123,-0.00001531,365.256,288,3.07e-5),
 ("mars","Mars",42828.375,3389.5,3396.2,6.4171e23,3.71,24.6229,1.52371034,0.09339410,1.84969142,686.980,210,None),
 ("jupiter","Jupiter",126686534.0,69911.0,71492.0,1.8982e27,24.79,9.925,5.20288700,0.04838624,1.30439695,4332.589,165,4.28e-4),
 ("saturn","Saturn",37931207.8,58232.0,60268.0,5.6834e26,10.44,10.656,9.53667594,0.05386179,2.48599187,10759.22,134,2.1e-5),
 ("uranus","Uranus",5793951.3,25362.0,25559.0,8.6810e25,8.69,-17.24,19.18916464,0.04725744,0.77263783,30688.5,76,2.28e-5),
 ("neptune","Neptune",6835100.0,24622.0,24764.0,1.02413e26,11.15,16.11,30.06992276,0.00859048,1.77004347,60182.0,72,1.41e-5),
]
# dwarf planets & asteroids: id,name,cat,mu,r_mean,mass,g,rot_h,a_AU,e,i,period_d,temp_k
SMALL = [
 ("pluto","Pluto","dwarf_planet",869.6,1188.3,1.303e22,0.62,-153.29,39.48,0.2488,17.16,90560,44),
 ("ceres","Ceres","dwarf_planet",62.6284,469.7,9.384e20,0.27,9.074,2.7675,0.0758,10.59,1681,168),
 ("eris","Eris","dwarf_planet",1108.0,1163.0,1.66e22,0.82,380.0,67.78,0.4407,44.0,203830,None),
 ("vesta","4 Vesta","asteroid",17.288,262.7,2.59e20,0.25,5.342,2.3615,0.0887,7.14,1325.7,None),
 ("bennu","101955 Bennu","asteroid",4.892e-9,0.2455,7.329e10,8.0e-5,4.296,1.1264,0.2037,6.035,436.6,None),
]
# moons: id,name,parent,mu,r_mean,mass,g,a_km,period_d,e,i_deg,synchronous
MOONS = [
 ("moon","Moon","earth",4902.8,1737.4,7.346e22,1.62,384400,27.3217,0.0549,5.145),
 ("phobos","Phobos","mars",0.0007087,11.1,1.0659e16,0.0057,9376,0.3189,0.0151,1.08),
 ("deimos","Deimos","mars",0.0000962,6.2,1.4762e15,0.003,23463,1.2630,0.0005,1.79),
 ("io","Io","jupiter",5959.916,1821.6,8.932e22,1.796,421800,1.769,0.0041,0.04),
 ("europa","Europa","jupiter",3202.739,1560.8,4.800e22,1.314,671100,3.551,0.0094,0.47),
 ("ganymede","Ganymede","jupiter",9887.834,2631.2,1.4819e23,1.428,1070400,7.155,0.0013,0.20),
 ("callisto","Callisto","jupiter",7179.289,2410.3,1.0759e23,1.235,1882700,16.689,0.0074,0.19),
 ("titan","Titan","saturn",8978.14,2574.7,1.3452e23,1.352,1221870,15.945,0.0288,0.33),
 ("enceladus","Enceladus","saturn",7.2105,252.1,1.08e20,0.113,238020,1.370,0.0047,0.01),
 ("triton","Triton","neptune",1427.6,1353.4,2.14e22,0.779,354759,-5.877,0.0000,156.9),
 ("charon","Charon","pluto",105.88,606.0,1.586e21,0.288,19591,6.387,0.0002,0.0),
]
ATMOS = [
 dict(id="venus",surface_pressure_pa=9.2e6,temp_k=737,scale_height_km=15.9,composition_vol_pct={"CO2":96.5,"N2":3.5},note="Surface values (mean)."),
 dict(id="earth",surface_pressure_pa=101325,temp_k=288,scale_height_km=8.5,composition_vol_pct={"N2":78.08,"O2":20.95,"Ar":0.93}),
 dict(id="mars",surface_pressure_pa=636,temp_k=210,scale_height_km=11.1,composition_vol_pct={"CO2":95.3,"N2":2.7,"Ar":1.6},note="Pressure varies ~30% seasonally and with elevation."),
 dict(id="titan",surface_pressure_pa=146700,temp_k=93.7,scale_height_km=21.0,composition_vol_pct={"N2":95.0,"CH4":5.0},note="Composition approximate (CH4 ~1.4% stratosphere, higher near surface)."),
 dict(id="jupiter",surface_pressure_pa=100000,temp_k=165,scale_height_km=27.0,composition_vol_pct={"H2":89.8,"He":10.2},note="Reference 1-bar level, no solid surface."),
 dict(id="saturn",surface_pressure_pa=100000,temp_k=134,scale_height_km=59.5,composition_vol_pct={"H2":96.3,"He":3.25},note="Reference 1-bar level, no solid surface."),
 dict(id="uranus",surface_pressure_pa=100000,temp_k=76,scale_height_km=27.7,composition_vol_pct={"H2":82.5,"He":15.2,"CH4":2.3},note="Reference 1-bar level."),
 dict(id="neptune",surface_pressure_pa=100000,temp_k=72,scale_height_km=19.7,composition_vol_pct={"H2":80.0,"He":19.0,"CH4":1.5},note="Reference 1-bar level."),
 dict(id="pluto",surface_pressure_pa=1.0,temp_k=None,scale_height_km=None,composition_vol_pct={"N2":None,"CH4":None},note="Tenuous N2 atmosphere ~1 Pa (order of magnitude); fractions not recorded."),
 dict(id="mercury",surface_pressure_pa=None,temp_k=None,scale_height_km=None,composition_vol_pct={},note="Surface-bounded exosphere; no meaningful pressure recorded."),
 dict(id="moon",surface_pressure_pa=None,temp_k=None,scale_height_km=None,composition_vol_pct={},note="Negligible exosphere."),
]
