# Launch Model Assumptions and Limits

## Recommended initial game model

For an educational web game, a point-mass three-degree-of-freedom (3-DOF) ascent model is a reasonable first implementation. The model should propagate vehicle position and velocity in a documented Earth-centred inertial frame while applying gravity, thrust, changing mass and atmospheric drag. Guidance/pitch history and stage events should be explicit inputs or game parameters.

## Required physics inputs

- Vehicle initial mass and stage-specific mass/propellant data.
- Engine or motor thrust as a function of time/altitude/command, or a clearly labelled simplified constant/nominal model when time histories are unavailable.
- Specific impulse or a directly supplied propellant mass-flow model.
- Stage separation and jettison event definitions.
- Atmospheric density and speed of sound versus altitude; optional wind profile.
- Drag coefficient versus Mach/flight condition and a reference area.
- Launch site coordinates, altitude datum, launch epoch and initial azimuth/pitch program.
- Earth gravitational parameter, Earth rotation model and coordinate transformations.

## Model equations (baseline)

Rocket thrust:

`F = mdot * Ve + Ae * (Pe - Pa)`

Ideal rocket equation:

`delta_v = Isp * g0 * ln(m0 / mf)`

Dynamic pressure:

`q = 0.5 * rho * v_relative^2`

Drag magnitude:

`D = q * Cd * A`

Gravity in a central point-mass approximation:

`a_g = -mu_E * r / |r|^3`

The vector acceleration should account for thrust direction, drag direction and gravity. The simplified along-path helper in `ascent_physics.js` is not a replacement for a vector state propagator.

## Reference-profile handling

The package contains distinct kinds of SLS ascent evidence: (1) Artemis I actual mission event times, (2) Artemis II launch-day event-time milestones whose times NASA says may vary by several seconds, (3) an earlier approximate SLS reference profile, and (4) an Artemis II prelaunch estimated time/speed/altitude profile. These are not interchangeable and must never be concatenated into one continuous as-flown telemetry series.

## Explicit exclusions from the current data package

- No proprietary flight guidance law or real-time control code.
- No complete time-dependent thrust curves for all four vehicles.
- No full stage mass and propellant tables for every vehicle.
- No complete continuous ascent telemetry time series for the selected vehicles.
- No launch-day weather or wind observations.
- No pad-grade site elevations with a verified vertical datum.
- No full aero database (Cd/lift vs Mach, angle of attack, Reynolds number).
- No flight qualification or operational safety certification.

## Data-handling rules

1. Keep thrust reference conditions separate: sea level, vacuum, peak, nominal, and unspecified.
2. Keep engine variants separate (e.g., Artemis I ICPS RL10B-2 vs later variant references).
3. Keep actual event timelines separate from preflight approximate reference profiles and launch-day event estimates.
4. If a value is unavailable in a reliable public source, mark it as missing or introduce it as a clearly labelled *game parameter* with an uncertainty/range.
5. Never interpolate sparse event points and label the result as real telemetry. A generated trajectory is a *simulation output*.
6. The v0.2 physics helpers implement equations, not a full numerical integrator, guidance law, or orbital insertion solver.
