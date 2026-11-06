"""Orbital mechanics / rocket equation helpers (SI unless suffixed). Two-body, patched-conic approximations."""
import math
G0 = 9.80665
AU_KM = 149597870.7
C = 299792458.0
K_B = 1.380649e-23
MU_SUN = 132712440018.0  # km^3/s^2

def v_circ(mu, r): return math.sqrt(mu / r)
def v_esc(mu, r): return math.sqrt(2 * mu / r)
def period(mu, a): return 2 * math.pi * math.sqrt(a ** 3 / mu)
def hohmann(mu, r1, r2):
    """Return (dv1, dv2, total, transfer_time_s) for coplanar circular-to-circular Hohmann transfer."""
    at = (r1 + r2) / 2
    v1 = math.sqrt(mu / r1); v2 = math.sqrt(mu / r2)
    vp = math.sqrt(mu * (2 / r1 - 1 / at)); va = math.sqrt(mu * (2 / r2 - 1 / at))
    dv1, dv2 = abs(vp - v1), abs(v2 - va)
    return dv1, dv2, dv1 + dv2, math.pi * math.sqrt(at ** 3 / mu)
def plane_change(v, di_deg): return 2 * v * math.sin(math.radians(di_deg) / 2)
def tsiolkovsky_dv(isp, m0, mf): return isp * G0 * math.log(m0 / mf)
def mass_ratio(dv, isp): return math.exp(dv / (isp * G0))
def propellant_for(dv, isp, m_final): return m_final * (mass_ratio(dv, isp) - 1)
def eclipse_fraction(mu, R, h):
    """Max (beta=0) cylindrical-shadow eclipse fraction for circular orbit radius R+h (km)."""
    return math.asin(R / (R + h)) / math.pi
def synodic(p1, p2): return 1 / abs(1 / p1 - 1 / p2)
def depart_dv_from_circular(mu_body, r_park, v_inf):
    """Burn from circular parking orbit to hyperbolic excess speed v_inf (km/s, km)."""
    return math.sqrt(v_inf ** 2 + 2 * mu_body / r_park) - math.sqrt(mu_body / r_park)
def fspl_db(d_m, f_hz): return 20 * math.log10(4 * math.pi * d_m * f_hz / C)
def parabolic_gain_db(d_m, f_hz, eff=0.55): return 10 * math.log10(eff * (math.pi * d_m * f_hz / C) ** 2)
