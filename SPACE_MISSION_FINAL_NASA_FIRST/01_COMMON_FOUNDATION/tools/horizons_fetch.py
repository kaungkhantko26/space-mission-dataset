import os
import hashlib
import requests
import json
import pandas as pd
from io import StringIO
from datetime import datetime, timezone

# 1. Define folder paths based on your staged directory
BASE_DIR = os.getcwd()
RAW_DIR = os.path.join(BASE_DIR, "raw", "horizons")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed", "ephemeris")
VALIDATION_DIR = os.path.join(BASE_DIR, "validation")

# Ensure target directories exist (without deleting anything)
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(VALIDATION_DIR, exist_ok=True)

# Horizons query targets and configuration
TARGETS = {
    '399': ('earth', 'earth_horizons_2026_2036.json', 'earth_state_vectors_horizons.csv'),
    '301': ('moon', 'moon_horizons_2026_2036.json', 'moon_state_vectors_horizons.csv'),
    '10': ('sun', 'sun_horizons_2026_2036.json', 'sun_state_vectors_horizons.csv')
}

CROSS_CHECK_DATES = ['2026-Jan-01', '2031-Jan-01', '2036-Jan-01']

def fetch_horizons_data(command):
    url = "https://ssd.jpl.nasa.gov/api/horizons.api"
    params = {
        "format": "json",
        "COMMAND": f"'{command}'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'VECTORS'",
        "CENTER": "'@0'",
        "START_TIME": "'2026-01-01'",
        "STOP_TIME": "'2037-01-01'",
        "STEP_SIZE": "'1 d'",
        "REF_SYSTEM": "'ICRF'",
        "REF_PLANE": "'FRAME'",
        "VEC_CORR": "'NONE'",
        "OUT_UNITS": "'KM-S'",
        "VEC_LABELS": "'YES'",
        "VEC_TABLE": "'2'",
        "CSV_FORMAT": "'YES'",
        "TIME_TYPE": "'TDB'"
    }
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    return response.text, response.json()

retrieval_time = datetime.now(timezone.utc).isoformat()
print(f"Starting JPL Horizons Retrieval at {retrieval_time}...\n")

summary_lines = [
    "\n\n## JPL Horizons Retrieval & Cross-Check Summary",
    f"- **Retrieval Timestamp (UTC):** `{retrieval_time}`",
    "- **Query Settings:** `REF_SYSTEM='ICRF'`, `REF_PLANE='FRAME'`, `CENTER='@0'`, `OUT_UNITS='KM-S'`, `TIME_TYPE='TDB'`, `STEP_SIZE='1 d'`\n"
]

for cmd, (name, json_filename, csv_filename) in TARGETS.items():
    print(f"Fetching data for {name.upper()} (Command: {cmd})...")
    
    # Fetch Data
    raw_text, data = fetch_horizons_data(cmd)
    
    # Save Raw JSON unchanged (Step 1)
    raw_path = os.path.join(RAW_DIR, json_filename)
    with open(raw_path, 'w', encoding='utf-8') as f:
        f.write(raw_text)
        
    sha256_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()
    result_text = data.get('result', '')
    
    # Extract headers for validation report (Step 4 & Interpretation Limit)
    header_lines = result_text.split('\n')
    ephem_info = next((line.strip() for line in header_lines if 'Ephemeris' in line or 'DE4' in line), 'Unknown Ephem')
    frame_info = next((line.strip() for line in header_lines if 'Reference frame' in line or 'ICRF' in line or 'Ecliptic' in line), 'Unknown Frame')
    sig_info = data.get('signature', {})
    
    print(f"  -> Saved Raw JSON: {raw_path}")
    print(f"  -> SHA-256:        {sha256_hash}")
    print(f"  -> Ephemeris Info: {ephem_info}")
    print(f"  -> Frame Info:     {frame_info}")
    
    summary_lines.append(f"### Target: {name.capitalize()} (`COMMAND='{cmd}'`)")
    summary_lines.append(f"- **Raw File:** `raw/horizons/{json_filename}` (SHA-256: `{sha256_hash}`)")
    summary_lines.append(f"- **API Signature:** `{sig_info}`")
    summary_lines.append(f"- **Returned Header Source:** `{ephem_info}`")
    summary_lines.append(f"- **Returned Reference Frame:** `{frame_info}`")
    
    # Parse CSV block (Step 2)
    soe_idx = result_text.find('$$SOE')
    eoe_idx = result_text.find('$$EOE')
    
    if soe_idx != -1 and eoe_idx != -1:
        csv_body = result_text[soe_idx + 5:eoe_idx].strip()
        
        col_names = ['JDTDB', 'Calendar_Date_TDB', 'X_km', 'Y_km', 'Z_km', 'VX_km_s', 'VY_km_s', 'VZ_km_s', 'LT_s', 'RG_km', 'RR_km_s']
        df = pd.read_csv(StringIO(csv_body), names=col_names, usecols=range(11), skipinitialspace=True)
        
        # Strip string whitespace
        df['Calendar_Date_TDB'] = df['Calendar_Date_TDB'].astype(str).str.strip()
        
        # Save processed CSV
        csv_path = os.path.join(PROCESSED_DIR, csv_filename)
        df.to_csv(csv_path, index=False)
        
        missing_count = int(df[['JDTDB', 'Calendar_Date_TDB', 'X_km', 'Y_km', 'Z_km', 'VX_km_s', 'VY_km_s', 'VZ_km_s']].isna().sum().sum())
        print(f"  -> Saved Processed CSV: {csv_path} ({len(df)} rows, Missing required values: {missing_count})")
        
        summary_lines.append(f"- **Processed CSV:** `processed/ephemeris/{csv_filename}`")
        summary_lines.append(f"- **Row Count:** {len(df)} (Expected: 4,018) | **Missing Core Values:** {missing_count}")
        summary_lines.append("- **Cross-Check State Vectors (Horizons):**")
        
        # Cross-check extraction (Step 3)
        print("  -> Cross-Check Data (2026-01-01, 2031-01-01, 2036-01-01):")
        for date_str in CROSS_CHECK_DATES:
            match = df[df['Calendar_Date_TDB'].str.contains(date_str, na=False)]
            if not match.empty:
                row = match.iloc[0]
                pos_str = f"X={row['X_km']:.6f}, Y={row['Y_km']:.6f}, Z={row['Z_km']:.6f} km"
                vel_str = f"VX={row['VX_km_s']:.9f}, VY={row['VY_km_s']:.9f}, VZ={row['VZ_km_s']:.9f} km/s"
                print(f"       {date_str}: Pos[{pos_str}] | Vel[{vel_str}]")
                summary_lines.append(f"  - `{date_str}`: **Pos** ({pos_str}) | **Vel** ({vel_str})")
            else:
                print(f"       {date_str}: Data Missing!")
                summary_lines.append(f"  - `{date_str}`: Data Missing!")
    else:
        print("  -> ERROR: Could not locate $$SOE / $$EOE markers in response!")
        summary_lines.append("- **ERROR:** Could not locate `$$SOE` / `$$EOE` markers in response.")
        
    summary_lines.append("")
    print("-" * 60)

# Save a summary markdown snippet that can be appended to validation/ephemeris_validation_report.md
summary_path = os.path.join(VALIDATION_DIR, "horizons_retrieval_summary.md")
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(summary_lines))

print(f"\nProcess complete! Validation summary snippet written to: {summary_path}")
