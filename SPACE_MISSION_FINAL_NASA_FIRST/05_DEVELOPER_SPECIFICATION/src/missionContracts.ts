export type Vec3 = readonly [number, number, number];
export type DataQualityStatus =
  | "published" | "reconstructed" | "calculated"
  | "estimated" | "game_configurable" | "unknown";

export interface SpacecraftState {
  schema_version: "1.0.0";
  mission_id: string;
  mission_phase: string;
  epoch_utc?: string | null;
  epoch_tdb_seconds_past_j2000: number;
  mission_elapsed_s?: number | null;
  reference_frame: string;
  origin: string;
  position_km: Vec3;
  velocity_km_s: Vec3;
  spacecraft_mass_kg?: number | null;
  remaining_propellant_kg?: number | null;
  target_body?: string | null;
  data_quality_status: DataQualityStatus;
  source_ids?: string[];
  quality_flags?: string[];
}

export interface MissionEvent {
  event_id: string;
  mission_id: string;
  event_type: string;
  event_name: string;
  time_basis: "MET_SECONDS" | "TDB_SECONDS_PAST_J2000" | "UTC_ISO8601";
  time_value: number | string;
  epoch_utc?: string | null;
  event_status?: string | null;
  source_id?: string | null;
  data_quality_status: DataQualityStatus;
  notes?: string | null;
}

export interface TelemetryRecord {
  schema_version: "1.0.0";
  mission_id: string;
  simulation_time_s: number;
  mission_phase: string;
  data_quality_status: DataQualityStatus;
  epoch_utc?: string | null;
  epoch_tdb_seconds_past_j2000?: number | null;
  mission_elapsed_s?: number | null;
  reference_frame?: string | null;
  origin?: string | null;
  position_km?: Vec3 | null;
  velocity_km_s?: Vec3 | null;
  speed_km_s?: number | null;
  altitude_km?: number | null;
  spacecraft_mass_kg?: number | null;
  remaining_propellant_kg?: number | null;
  thrust_N?: number | null;
  dynamic_pressure_Pa?: number | null;
  delta_v_used_km_s?: number | null;
  target_body?: string | null;
  distance_to_target_km?: number | null;
  estimated_arrival_utc?: string | null;
  source_ids?: string[];
  quality_flags?: string[];
}

export interface ModuleHandoff {
  contract_version: "1.0.0";
  mission_id: string;
  from_module: string;
  to_module: string;
  handoff_type: "launch_to_transfer" | "transfer_to_arrival" | "arrival_to_landing" | "module_checkpoint";
  spacecraft_state: SpacecraftState;
  maneuver_events?: MissionEvent[];
  quality_flags: string[];
  created_at_utc?: string | null;
}
