# Developer Handoff Notes — Browser Architecture

## Confirmed architecture
- React + TypeScript: application UI, mission controls, configuration, status panels.
- Scientific simulation module: independent of rendering and emits physical state/telemetry.
- Three.js: renders planets, spacecraft, trajectory geometry, event markers and camera movement from calculated state.
- JSON Schema: validate state, telemetry, event and handoff messages.

## Important implementation principle
Three.js is not the scientific truth source. The simulation module calculates positions and velocities in declared physical units and coordinate frames. A separate adapter transforms them for rendering.

## Scene scaling
Use a local render origin and a configurable `sceneUnitsPerKm`. Celestial body sizes, orbit distances and spacecraft model sizes may require different visual exaggeration factors. Record those as visual-only display parameters and never feed them back into physics.

## Integration boundary
The launch module should hand off a complete state to the transfer module. Transfer/landing researchers must agree on exact frame and origin names, time scale, epoch, units, and mass/propellant semantics before integration. The package schemas define the fields but do not select a mission-specific transfer solution.

## Optional services
DONKI, FIRMS, OSDR and SPHEREx should be non-blocking optional services. If a key is needed, keep it in a server-side/serverless proxy or environment secret. Do not make core simulation availability depend on an external NASA API response.
