/**
 * Render-only adapter: physical coordinates remain in the simulation module.
 * The caller must transform the source vector into the selected render frame
 * before calling this function. This function only rebases, maps axes, and scales.
 */
export type Vec3 = readonly [number, number, number];
export type AxisToken = "x" | "-x" | "y" | "-y" | "z" | "-z";
export interface SceneMapping {
  /** scene units per kilometre; visual scale only, never a physics parameter */
  sceneUnitsPerKm: number;
  /** Each output scene axis selects one signed input axis; choose a documented mapping. */
  outputAxes: readonly [AxisToken, AxisToken, AxisToken];
}

function component(v: Vec3, token: AxisToken): number {
  const sign = token.startsWith("-") ? -1 : 1;
  const key = token.replace("-", "") as "x" | "y" | "z";
  const index = key === "x" ? 0 : key === "y" ? 1 : 2;
  return sign * v[index];
}

export function toScenePosition(
  worldPositionKm: Vec3,
  renderOriginKm: Vec3,
  mapping: SceneMapping,
): Vec3 {
  if (!Number.isFinite(mapping.sceneUnitsPerKm) || mapping.sceneUnitsPerKm <= 0) {
    throw new Error("sceneUnitsPerKm must be a finite positive number");
  }
  const local: Vec3 = [
    worldPositionKm[0] - renderOriginKm[0],
    worldPositionKm[1] - renderOriginKm[1],
    worldPositionKm[2] - renderOriginKm[2],
  ];
  const result: Vec3 = [
    component(local, mapping.outputAxes[0]) * mapping.sceneUnitsPerKm,
    component(local, mapping.outputAxes[1]) * mapping.sceneUnitsPerKm,
    component(local, mapping.outputAxes[2]) * mapping.sceneUnitsPerKm,
  ];
  if (!result.every(Number.isFinite)) throw new Error("Scene position contains a non-finite component");
  return result;
}
