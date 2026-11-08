"""Rule engine for the mission-design dataset.

Physics (rocket equation, Hohmann, Friis, inverse-square irradiance) uses VERIFIED inputs (GM, radii, semi-major axes,
irradiance, component specs).  Thresholds marked basis="game-heuristic" are teaching assumptions, NOT real data.
Everything produced with it is data_class "derived" and labelled as rule-engine output.
"""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
G0, KB, C = 9.80665, 1.380649e-23, 299792458.0

HEUR = dict(  # basis: game-heuristic
    structure_overhead=0.25, mass_margin=0.90, dv_margin=1.10, power_margin=1.15, array_efficiency=0.80,
    bus_base_load_w=10.0, radio_load_w=10.0, unknown_instrument_w=5.0, unknown_chem_thruster_w=10.0,
    tx_power_w=5.0, ground_gain_dbi=35.0, link_losses_db=3.0, ebn0_db=10.0, noise_temp_k=290.0, link_margin_db=3.0,
    max_transfer_s=365.25 * 86400, leo_station_keeping_dv=100.0, default_freq_mhz=2200.0, overkill_ratio=50.0)
REQ_RATE_KBPS = dict(LEO=500.0, GTO=100.0, MOON=100.0, MARS=10.0)  # game parameter per destination
DESTS = ["LEO", "GTO", "MOON", "MARS"]


def _recs(c):
    return {r["id"]: r for r in json.load(open(os.path.join(ROOT, "verified", c + ".json")))["records"]}


def environment():
    pl, mo = _recs("planets"), _recs("moons")
    mu_e, R_e = pl["earth"]["gravitational_parameter_km3_s2"] * 1e9, pl["earth"]["mean_radius_m"]
    mu_s = pl["sun"]["gravitational_parameter_km3_s2"] * 1e9
    a_e, a_m = pl["earth"]["semi_major_axis_m"], pl["mars"]["semi_major_axis_m"]
    r1 = R_e + 200e3
    vc = math.sqrt(mu_e / r1)

    def hoh(r2):
        return (vc * (math.sqrt(2 * r2 / (r1 + r2)) - 1),
                math.sqrt(mu_e / r2) * (1 - math.sqrt(2 * r1 / (r1 + r2))))
    geo = 42164e3
    vinf = math.sqrt(mu_s / a_e) * (math.sqrt(2 * a_m / (a_e + a_m)) - 1)
    return dict(
        req_dv=dict(LEO=HEUR["leo_station_keeping_dv"], GTO=hoh(geo)[1], MOON=hoh(mo["moon"]["semi_major_axis_m"])[0],
                    MARS=math.sqrt(vinf ** 2 + 2 * mu_e / r1) - vc),
        distance_m=dict(LEO=1.0e6, GTO=3.6e7, MOON=mo["moon"]["semi_major_axis_m"], MARS=a_m),
        irradiance=dict(LEO=pl["earth"]["nssdc_fact_sheet"]["numeric"]["Solar irradiance (W/m 2 )"],
                        GTO=pl["earth"]["nssdc_fact_sheet"]["numeric"]["Solar irradiance (W/m 2 )"],
                        MOON=pl["earth"]["nssdc_fact_sheet"]["numeric"]["Solar irradiance (W/m 2 )"],
                        MARS=pl["mars"]["nssdc_fact_sheet"]["numeric"]["Solar irradiance (W/m 2 )"]))


def band(mhz):
    if mhz is None: return None
    for hi, nm in ((300, "VHF"), (1000, "UHF"), (2000, "L"), (4000, "S"), (8000, "C"), (12000, "X"), (18000, "Ku"), (40000, "Ka")):
        if mhz < hi: return nm
    return "mm"


def evaluate(d, cat, env):
    """d: design dict; cat: id->component dict. Returns (metrics, checks[list of (code, passed, text)])."""
    chk, m = [], {}
    dest = d["dest"]
    L, T, A, R, N = (cat.get(d.get(k)) for k in ("launcher", "thruster", "array", "radio", "antenna"))
    I = [cat[i] for i in (d.get("instruments") or []) if i in cat]
    for code, obj, nm in (("MISSING_LAUNCHER", L, "a launch vehicle"), ("MISSING_PROPULSION", T, "a propulsion system"),
                          ("MISSING_POWER", A, "a solar array"), ("MISSING_RADIO", R, "a radio"),
                          ("MISSING_ANTENNA", N, "an antenna"), ("MISSING_INSTRUMENT", I or None, "a science instrument")):
        if obj is None:
            chk.append((code, False, f"The design has no {nm}, so the mission cannot work."))
    if any(not p for _, p, _ in chk):
        return m, chk
    nt, na = d["n_thr"], d["n_arr"]
    comp = sum(i["mass_kg"] for i in I) + nt * T["mass_kg"] + na * A["mass_kg"] + R["mass_kg"] + N["mass_kg"]
    dry = comp * (1 + HEUR["structure_overhead"])
    total = dry + d["propellant_kg"]
    m.update(component_mass_kg=comp, dry_mass_kg=dry, total_mass_kg=total)
    # budget
    cost = L["launch_cost_usd"]
    m["launch_cost_usd"] = cost
    chk.append(("BUDGET_EXCEEDED", cost <= d["budget_usd"],
                f"Launch cost ${cost/1e6:.1f}M vs budget ${d['budget_usd']/1e6:.1f}M."))
    # launcher mass
    cap = L["gto_capacity_kg"] if dest == "GTO" else L["leo_capacity_kg"]
    m["launcher_capacity_kg"] = cap
    if cap is None:
        chk.append(("LAUNCHER_NO_CAPACITY", False, f"{L['name']} has no published {'GTO' if dest=='GTO' else 'LEO'} capacity, so this destination cannot be verified."))
    else:
        chk.append(("MASS_OVER_CAPACITY", total <= HEUR["mass_margin"] * cap,
                    f"Mass {total:.0f} kg vs {HEUR['mass_margin']*100:.0f}% of capacity {cap:.0f} kg = {HEUR['mass_margin']*cap:.0f} kg."))
        m["mass_margin_ratio"] = HEUR["mass_margin"] * cap / total
    # delta-v and burn time
    isp = T["isp_s"]
    dv = isp * G0 * math.log(total / dry)
    req = env["req_dv"][dest]
    m.update(dv_available_m_s=dv, dv_required_m_s=req)
    chk.append(("DELTA_V_SHORT", dv >= HEUR["dv_margin"] * req,
                f"Delta-v {dv:.0f} m/s (Isp {isp:.0f} s, mass {total:.0f}->{dry:.0f} kg) vs required {HEUR['dv_margin']*req:.0f} m/s."))
    used = total * (1 - math.exp(-req / (isp * G0)))
    F = nt * T["thrust_n"]
    tb = used * isp * G0 / F
    m["burn_time_days"] = tb / 86400
    chk.append(("THRUST_TOO_LOW", tb <= HEUR["max_transfer_s"],
                f"Burning {used:.0f} kg at {F:.3g} N takes {tb/86400:.0f} days (limit {HEUR['max_transfer_s']/86400:.0f})."))
    # power
    pw = na * A["power_w"] * HEUR["array_efficiency"] * env["irradiance"][dest] / env["irradiance"]["LEO"]
    load = HEUR["bus_base_load_w"] + HEUR["radio_load_w"] + sum((i["power_w"] if i["power_w"] is not None else HEUR["unknown_instrument_w"]) for i in I) \
        + nt * (T["power_w"] if T["power_w"] is not None else HEUR["unknown_chem_thruster_w"])
    m.update(array_power_w=pw, load_w=load)
    chk.append(("POWER_SHORT", pw >= HEUR["power_margin"] * load,
                f"Array gives {pw:.0f} W at {dest} vs load {load:.0f} W x {HEUR['power_margin']} = {HEUR['power_margin']*load:.0f} W."))
    # comms
    rb, ab = band(R["freq_mhz"]), band(N["freq_mhz"])
    ok_band = rb is None or ab is None or rb == ab
    chk.append(("BAND_MISMATCH", ok_band, f"Radio band {rb or 'unknown'} vs antenna band {ab or 'unknown'}."))
    need = REQ_RATE_KBPS[dest]
    chk.append(("DATA_RATE_LOW", R["rate_kbps"] >= need, f"Radio max {R['rate_kbps']:.0f} kbps vs {need:.0f} kbps needed at {dest}."))
    f = (R["freq_mhz"] or N["freq_mhz"] or HEUR["default_freq_mhz"]) * 1e6
    d_m = env["distance_m"][dest]
    fspl = 20 * math.log10(4 * math.pi * d_m * f / C)
    eirp = 10 * math.log10(HEUR["tx_power_w"]) + N["gain_dbi"]
    nrm = 10 * math.log10(KB * HEUR["noise_temp_k"] * need * 1e3)
    margin = eirp + HEUR["ground_gain_dbi"] - fspl - HEUR["link_losses_db"] - nrm - HEUR["ebn0_db"]
    m["link_margin_db"] = margin
    chk.append(("LINK_MARGIN_LOW", margin >= HEUR["link_margin_db"],
                f"Link margin {margin:.1f} dB (antenna {N['gain_dbi']:.1f} dBi, path loss {fspl:.0f} dB) vs {HEUR['link_margin_db']} dB needed."))
    m["warn_launcher_overkill"] = bool(cap and cap > HEUR["overkill_ratio"] * total)
    m["p_launch_success"] = L["success_rate"]
    return m, chk
