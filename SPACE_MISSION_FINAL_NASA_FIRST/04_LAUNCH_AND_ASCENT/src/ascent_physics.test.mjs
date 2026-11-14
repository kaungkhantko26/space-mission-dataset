import assert from 'node:assert/strict';
import { idealDeltaVMS, dynamicPressurePa, dragForceN, specificImpulseSeconds, propellantMassFlowKgS } from './ascent_physics.js';
const g0=9.80665;
assert.ok(Math.abs(idealDeltaVMS(300, 10000, 5000, g0) - 2039.0) < 2.0);
assert.ok(Math.abs(dynamicPressurePa(1.225, 10) - 61.25) < 1e-9);
assert.ok(Math.abs(dragForceN({densityKgM3:1.225, relativeSpeedMS:10, dragCoefficient:1, referenceAreaM2:1}) - 61.25) < 1e-9);
assert.ok(Math.abs(specificImpulseSeconds(300000, 100, g0) - 305.91) < 1.0);
assert.ok(Math.abs(propellantMassFlowKgS(300000, 300, g0) - 101.97) < 0.1);
console.log('ascent_physics smoke tests passed');
