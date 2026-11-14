/**
 * Workstream 1 launch physics helpers.
 * Units: SI (N, kg, m, s, Pa, kg/m^3), angles in radians unless noted.
 * These helpers implement reference equations, not a flight-qualified launch simulator.
 */
export const G0 = 9.80665;
export const EARTH_MU_M3_S2 = 3.986004418e14;

function assertFinitePositive(name, value, allowZero = false) {
  if (!Number.isFinite(value) || (allowZero ? value < 0 : value <= 0)) {
    throw new RangeError(`${name} must be ${allowZero ? 'non-negative' : 'positive'} and finite`);
  }
}

/** General rocket thrust equation: F = mdot*Ve + Ae*(Pe - Pa). */
export function rocketThrustN({ massFlowRateKgS, exhaustVelocityMS, exitAreaM2 = 0,
  exitPressurePa = 0, ambientPressurePa = 0 }) {
  assertFinitePositive('massFlowRateKgS', massFlowRateKgS, true);
  assertFinitePositive('exhaustVelocityMS', exhaustVelocityMS, true);
  assertFinitePositive('exitAreaM2', exitAreaM2, true);
  assertFinitePositive('exitPressurePa', exitPressurePa, true);
  assertFinitePositive('ambientPressurePa', ambientPressurePa, true);
  return massFlowRateKgS * exhaustVelocityMS + exitAreaM2 * (exitPressurePa - ambientPressurePa);
}

/** Specific impulse in seconds from thrust and propellant mass flow. */
export function specificImpulseSeconds(thrustN, massFlowRateKgS, g0 = G0) {
  assertFinitePositive('thrustN', thrustN, true);
  assertFinitePositive('massFlowRateKgS', massFlowRateKgS);
  assertFinitePositive('g0', g0);
  return thrustN / (massFlowRateKgS * g0);
}

/** Ideal Tsiolkovsky delta-v in m/s; ignores gravity, drag and steering losses. */
export function idealDeltaVMS(ispSeconds, initialMassKg, finalMassKg, g0 = G0) {
  assertFinitePositive('ispSeconds', ispSeconds);
  assertFinitePositive('initialMassKg', initialMassKg);
  assertFinitePositive('finalMassKg', finalMassKg);
  assertFinitePositive('g0', g0);
  if (finalMassKg >= initialMassKg) throw new RangeError('finalMassKg must be less than initialMassKg');
  return ispSeconds * g0 * Math.log(initialMassKg / finalMassKg);
}

/** Propellant mass flow estimate from thrust and Isp, in kg/s. */
export function propellantMassFlowKgS(thrustN, ispSeconds, g0 = G0) {
  assertFinitePositive('thrustN', thrustN, true);
  assertFinitePositive('ispSeconds', ispSeconds);
  assertFinitePositive('g0', g0);
  return thrustN / (ispSeconds * g0);
}

/** Dynamic pressure q = 0.5*rho*v_relative^2, in Pa. */
export function dynamicPressurePa(densityKgM3, relativeSpeedMS) {
  assertFinitePositive('densityKgM3', densityKgM3, true);
  assertFinitePositive('relativeSpeedMS', relativeSpeedMS, true);
  return 0.5 * densityKgM3 * relativeSpeedMS ** 2;
}

/** Drag magnitude D = q*Cd*A, in N. */
export function dragForceN({ densityKgM3, relativeSpeedMS, dragCoefficient, referenceAreaM2 }) {
  assertFinitePositive('dragCoefficient', dragCoefficient, true);
  assertFinitePositive('referenceAreaM2', referenceAreaM2, true);
  return dynamicPressurePa(densityKgM3, relativeSpeedMS) * dragCoefficient * referenceAreaM2;
}

/** Central point-mass gravity magnitude at radius r from Earth's centre, m/s^2. */
export function earthGravityMS2(radiusFromEarthCenterM, mu = EARTH_MU_M3_S2) {
  assertFinitePositive('radiusFromEarthCenterM', radiusFromEarthCenterM);
  assertFinitePositive('mu', mu);
  return mu / radiusFromEarthCenterM ** 2;
}

/** Linear interpolation of a standard-atmosphere CSV parsed into row objects. */
export function interpolateAtmosphere(rows, geometricAltitudeM) {
  if (!Array.isArray(rows) || rows.length < 2) throw new TypeError('rows must contain at least two atmosphere rows');
  assertFinitePositive('geometricAltitudeM', geometricAltitudeM, true);
  const sorted = [...rows].sort((a, b) => Number(a.geometric_altitude_m) - Number(b.geometric_altitude_m));
  const minAlt = Number(sorted[0].geometric_altitude_m);
  const maxAlt = Number(sorted[sorted.length - 1].geometric_altitude_m);
  if (geometricAltitudeM < minAlt || geometricAltitudeM > maxAlt) {
    throw new RangeError(`Altitude outside atmosphere table range ${minAlt}..${maxAlt} m`);
  }
  let hi = sorted.findIndex(row => Number(row.geometric_altitude_m) >= geometricAltitudeM);
  if (hi === 0) return { ...sorted[0] };
  if (hi < 0) return { ...sorted[sorted.length - 1] };
  const lo = hi - 1;
  const a = sorted[lo], b = sorted[hi];
  const x0 = Number(a.geometric_altitude_m), x1 = Number(b.geometric_altitude_m);
  const f = (geometricAltitudeM - x0) / (x1 - x0);
  const out = { geometric_altitude_m: geometricAltitudeM };
  for (const key of ['temperature_K','pressure_Pa','density_kg_m3','speed_of_sound_m_s','local_gravity_m_s2']) {
    out[key] = Number(a[key]) + f * (Number(b[key]) - Number(a[key]));
  }
  return out;
}

/**
 * Along-flight-path acceleration estimate for a point-mass model.
 * flightPathAngleRad is measured from local horizontal; positive upward.
 * Does not include Earth rotation, lift, wind, guidance, curvature terms or J2.
 */
export function alongPathAccelerationMS2({ thrustN, dragN, massKg, earthGravityMS2: g = 9.80665,
  flightPathAngleRad }) {
  assertFinitePositive('massKg', massKg);
  assertFinitePositive('thrustN', thrustN, true);
  assertFinitePositive('dragN', dragN, true);
  assertFinitePositive('g', g, true);
  if (!Number.isFinite(flightPathAngleRad)) throw new RangeError('flightPathAngleRad must be finite');
  return (thrustN - dragN) / massKg - g * Math.sin(flightPathAngleRad);
}
