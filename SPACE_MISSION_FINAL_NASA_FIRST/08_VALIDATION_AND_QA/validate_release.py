#!/usr/bin/env python3
from pathlib import Path
import csv,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def load(rel):
 with (ROOT/rel).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
assert {r['vehicle_id'] for r in load('04_LAUNCH_AND_ASCENT/data/rocket_vehicle_catalog.csv')}=={'SLS_BLOCK1'}
assert all(r['vehicle_id']=='SLS_BLOCK1' for r in load('04_LAUNCH_AND_ASCENT/data/rocket_stage_engine_specs.csv'))
allowed={r['source_id'] for r in load('04_LAUNCH_AND_ASCENT/data/nasa_source_registry.csv')}
for fn in ['rocket_vehicle_catalog.csv','rocket_stage_engine_specs.csv','rocket_payload_performance_reference.csv','launch_site_specs.csv','launch_site_vehicle_compatibility.csv','launch_event_reference.csv','sls_ascent_reference_profile_approx.csv','sls_ascent_reference_profile_artemis_ii_prelaunch.csv','sls_rs25_thrust_schedule_reference.csv']:
 for row in load('04_LAUNCH_AND_ASCENT/data/'+fn):
  for key in ['source_id','source_ids']:
   for sid in filter(None, (row.get(key,'') or '').split(';')):
    assert sid in allowed, (fn,sid)
mar=load('03_SUN_EARTH_MARS/earth_mars_horizons_30day_TDB_ECLIPJ2000.csv')
assert len(mar)==244
assert all(r['frame']=='ECLIPJ2000' and r['origin']=='SSB' for r in mar)
assert {r['jd_tdb'] for r in mar if r['body']=='Earth'}=={r['jd_tdb'] for r in mar if r['body']=='Mars'}
for body in ['earth','moon','sun']:
 assert len(load('02_SUN_EARTH_MOON/QA_HOLD/'+body+'_state_vectors_uncertified_timestamps.csv'))==4018
with (ROOT/'04_LAUNCH_AND_ASCENT/data/launch_simulation_constants.json').open() as f:json.load(f)
print('PASS: NASA-SLS-only rows, source IDs, Mars shared epochs/metadata, Moon QA hold, JSON syntax')
